import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import freeze_media as m

class MediaPreparationTests(unittest.TestCase):
    def probe(self, case):
        _,duration,width,height,fps=case
        return {'streams':[{'codec_type':'video','codec_name':'h264','width':width,'height':height,'pix_fmt':'yuv420p','avg_frame_rate':f'{fps}/1','r_frame_rate':f'{fps}/1','nb_read_frames':str(duration*fps),'duration':str(duration)}, {'codec_type':'audio','codec_name':'aac','sample_rate':'48000','channels':2,'duration':str(duration)}], 'format':{'duration':str(duration)}}
    @patch('freeze_media.subprocess.run')
    def test_existing_directory_does_not_write_manifest_or_execute(self, run):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td); f=p/'manifest.json'; f.write_bytes(b'preserve-existing')
            with self.assertRaisesRegex(ValueError,'existing'):m.generate(p)
            self.assertEqual(f.read_bytes(),b'preserve-existing')
            self.assertEqual(list(p.iterdir()),[f]);run.assert_not_called()
    @patch('freeze_media.subprocess.run')
    def test_existing_file_unchanged(self, run):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'file';p.write_bytes(b'keep')
            with self.assertRaisesRegex(ValueError,'existing'):m.generate(p)
            self.assertEqual(p.read_bytes(),b'keep');run.assert_not_called()
    def test_two_valid_expected_streams(self):
        for case in m.CASES:self.assertEqual(m.verify(self.probe(case),case)['decoded_video_frames'],case[1]*case[4])
    def test_wrong_decoded_frames(self):
        case=m.CASES[1];p=self.probe(case);p['streams'][0]['nb_read_frames']='3599'
        with self.assertRaises(ValueError):m.verify(p,case)
    def test_wrong_raster(self):
        case=m.CASES[1];p=self.probe(case);p['streams'][0]['height']=720
        with self.assertRaises(ValueError):m.verify(p,case)
    def test_duration_rejected(self):
        case=m.CASES[0];p=self.probe(case);p['format']['duration']='11'
        with self.assertRaises(ValueError):m.verify(p,case)
    def test_extra_stream_rejected(self):
        case=m.CASES[0];p=self.probe(case);p['streams'].append(copy.deepcopy(p['streams'][1]))
        with self.assertRaises(ValueError):m.verify(p,case)
    def test_bad_schema_fails_closed(self):
        with self.assertRaises(KeyError):m.verify({},m.CASES[0])
    def test_command_no_overwrite_and_expected_encoder(self):
        c=m.command('/usr/bin/ffmpeg',m.CASES[1],Path('/tmp/new.mp4'))
        self.assertIn('-n',c);self.assertNotIn('-y',c)
        self.assertEqual(c[c.index('-c:v')+1],'libx264')
        self.assertEqual(c[c.index('-c:a')+1],'aac')
        self.assertEqual(c[c.index('-threads:v')+1],'1')

if __name__=='__main__':unittest.main()
