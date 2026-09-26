#!/usr/bin/env python3
"""Create source-only synthetic fixtures; no upload or workload acceptance."""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

CASES = [('short360', 10, 640, 360, 25), ('fullhd60', 60, 1920, 1080, 60)]
sha = lambda data: hashlib.sha256(data).hexdigest()

def command(ffmpeg, case, output):
    name, duration, width, height, fps = case
    return [ffmpeg, '-nostdin', '-hide_banner', '-loglevel', 'error', '-n',
        '-filter_threads', '1', '-filter_complex_threads', '1',
        '-f', 'lavfi', '-i', f'testsrc2=size={width}x{height}:rate={fps}:duration={duration}',
        '-f', 'lavfi', '-i', f'sine=frequency=440:sample_rate=48000:duration={duration}',
        '-map', '0:v:0', '-map', '1:a:0', '-t', str(duration),
        '-c:v', 'libx264', '-threads:v', '1', '-preset', 'medium', '-crf', '18',
        '-pix_fmt', 'yuv420p', '-r', str(fps), '-fps_mode', 'cfr',
        '-g', str(fps*2), '-keyint_min', str(fps*2), '-sc_threshold', '0',
        '-c:a', 'aac', '-threads:a', '1', '-b:a', '128k', '-ar', '48000', '-ac', '2',
        '-map_metadata', '-1', '-fflags', '+bitexact', '-flags:v', '+bitexact',
        '-flags:a', '+bitexact', '-movflags', '+faststart', str(output)]

def verify(probe, case):
    _, duration, width, height, fps = case
    streams = probe['streams']
    if len(streams) != 2:
        raise ValueError('Expected exactly two streams')
    videos = [s for s in streams if s['codec_type'] == 'video']
    audios = [s for s in streams if s['codec_type'] == 'audio']
    if len(videos) != 1 or len(audios) != 1:
        raise ValueError('Expected one video and one audio stream')
    v, a = videos[0], audios[0]
    if (v['codec_name'], v['width'], v['height'], v['pix_fmt']) != ('h264', width, height, 'yuv420p'):
        raise ValueError('Video format mismatch')
    if Fraction(v['avg_frame_rate']) != fps or Fraction(v['r_frame_rate']) != fps or int(v['nb_read_frames']) != duration*fps:
        raise ValueError('Decoded frame count/rate mismatch')
    if (a['codec_name'], int(a['sample_rate']), a['channels']) != ('aac', 48000, 2):
        raise ValueError('Audio format mismatch')
    tolerance = Fraction(1, fps) + Fraction(1024, 48000)
    for value in [v['duration'], a['duration'], probe['format']['duration']]:
        if abs(Fraction(value) - duration) > tolerance:
            raise ValueError('Duration outside predeclared frame/AAC tolerance')
    return {'decoded_video_frames': duration*fps, 'duration_tolerance_seconds': str(tolerance)}

def generate(output):
    if output.exists():
        raise ValueError('Refuse existing fixture directory')
    programs = {p: shutil.which(p) for p in ['ffmpeg', 'ffprobe']}
    if not all(programs.values()):
        raise ValueError('Missing media tools')
    identities = {p: {'path': path, 'sha256': sha(Path(path).read_bytes()),
        'version': subprocess.run([path, '-version'], check=True, capture_output=True,
            text=True, timeout=10).stdout} for p,path in programs.items()}
    output.mkdir(parents=True, exist_ok=False)
    manifest = {'status': 'RUNNING', 'tools': identities, 'fixtures': [],
        'application_acceptance': False, 'cross_build_reproducibility': False}
    report = output/'manifest.json'
    try:
        for case in CASES:
            media = output/(case[0]+'.mp4')
            cmd = command(programs['ffmpeg'], case, media)
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=1200)
            row = {'case': list(case), 'command': cmd, 'exit': result.returncode, 'stderr': result.stderr}
            manifest['fixtures'].append(row)
            if result.returncode:
                raise ValueError('Fixture generation failed')
            probe_cmd = [programs['ffprobe'], '-v', 'error', '-count_frames', '-show_streams', '-show_format', '-of', 'json', str(media)]
            p = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=180)
            row.update({'probe_command': probe_cmd, 'probe_exit': p.returncode, 'probe_stderr': p.stderr})
            if p.returncode:
                raise ValueError('Fixture probe failed')
            probe = json.loads(p.stdout)
            row.update({'probe': probe, 'validation': verify(probe, case),
                'sha256': sha(media.read_bytes()), 'bytes': media.stat().st_size})
        for name, ident in identities.items():
            if sha(Path(ident['path']).read_bytes()) != ident['sha256']:
                raise ValueError('Encoder/prober drift')
        manifest['status'] = 'SOURCE_FIXTURES_VALIDATED_PENDING_INDEPENDENT_REVIEW'
    except Exception as exc:
        manifest['status'] = 'FAILED'
        manifest['error_type'] = type(exc).__name__
        raise
    finally:
        report.write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    result = generate(args.output)
    print(json.dumps({'status': result['status'], 'fixtures': len(result['fixtures'])}))
