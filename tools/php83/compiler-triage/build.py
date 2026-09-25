#!/usr/bin/env python3
"""Identity-gated compiler rejection classification; no PHP or application execution."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import zipfile

ORIGINAL = '58d534d09b3b75c9a8333957268c884f79032638b2d44a278b1992fda1b0ab28'
EXP9 = 'cb61e4cd11009bbf9e6e362dfafa5ef2f4af22da817c75fedbd7741a08e44cbc'
ROOT = 'server-Rigel-18.20.0/'
TEMPLATES = {
    'vendor/symfony-data/generator/sfPropelAdmin/default/skeleton/actions/actions.class.php',
    'vendor/symfony-data/generator/sfPropelCrud/default/skeleton/actions/actions.class.php',
    'vendor/symfony-data/skeleton/batch/default.php',
    'vendor/symfony-data/skeleton/batch/rotate_log.php',
    'vendor/symfony-data/skeleton/controller/controller.php',
    'vendor/symfony-data/skeleton/module/module/actions/actions.class.php',
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def indexed(rows, key='path'):
    result = {}
    for row in rows:
        if row[key] in result:
            raise ValueError('Duplicate evidence key: ' + str(row[key]))
        result[row[key]] = row
    return result


def safe_path(path):
    if not path or path.startswith('/') or '..' in PurePosixPath(path).parts or '\\' in path:
        raise ValueError('Unsafe source path')
    return path


def classify(path, diagnostic, text):
    lines = text.splitlines()
    fatals = [line for line in diagnostic.splitlines() if line.startswith(('Fatal error:', 'Parse error:'))]
    if len(fatals) != 1:
        raise ValueError('Expected one compiler rejection diagnostic')
    fatal = fatals[0]
    match = re.search(r' in (.+) on line (\d+)$', fatal)
    if not match or match.group(1) != path:
        raise ValueError('Diagnostic path mismatch')
    number = int(match.group(2))
    if not 1 <= number <= len(lines):
        raise ValueError('Diagnostic line outside source')
    window = '\n'.join(lines[max(0,number-4):number+3])
    at_line = lines[number-1]
    if 'Array and string offset access syntax with curly braces is no longer supported' in fatal and re.search(r'(?:\$\w+(?:->\w+)*|\])\{', at_line):
        category = 'removed_curly_brace_offset'
    elif 'Unparenthesized `a ? b : c ? d : e` is not supported' in fatal and window.count('?') >= 2:
        category = 'unparenthesized_nested_ternary'
    elif '__autoload() is no longer supported' in fatal and re.search(r'function\s+__autoload\s*\(', at_line):
        category = 'removed_autoload_declaration'
    elif "Cannot use Riak\\Object as Object because 'Object' is a special class name" in fatal and at_line.strip() == 'use Riak\\Object;':
        category = 'reserved_object_import_alias'
    elif path in TEMPLATES and fatal.startswith('Parse error:') and (
            re.search(r'^class ##MODULE_NAME##Actions\b', text, re.M)
            or re.search(r"define\('SF_DEBUG',\s*##DEBUG##\);", text)):
        category = 'unexpanded_generator_skeleton_placeholder'
    else:
        raise ValueError('Unclassified or source-unsubstantiated rejection: ' + path)
    excerpt = [{'line':i+1,'text':lines[i]} for i in range(max(0,number-4),min(len(lines),number+3))]
    placeholders = [{'line':i+1,'text':line} for i,line in enumerate(lines)
        if '##' in line] if category == 'unexpanded_generator_skeleton_placeholder' else []
    return category, number, excerpt, placeholders


def historical_join(path, candidate_sha, package, historical):
    if not package or not historical:
        return {'status':'unresolved_missing_evidence','baseline_classification':None}
    if package['sha256'] != historical['sha256']:
        raise ValueError('Conflicting historical/package bytes: ' + path)
    if candidate_sha != package['sha256']:
        return {'status':'not_comparable_different_candidate_bytes','baseline_classification':None,
            'historical_sha256':historical['sha256'],'package_sha256':package['sha256']}
    before, after = historical['php74_returncode'], historical['php83_returncode']
    if type(before) is not int or before not in (0, 255) or type(after) is not int or after != 255:
        raise ValueError('Historical compiler exit status invalid or incomplete')
    return {'status':'exact_source_identity_match',
        'baseline_classification':'new_php83_rejection' if before == 0 else 'baseline_rejection_retained',
        'php74_exit':before,'historical_php83_exit':after,'historical_sha256':historical['sha256'],
        'historical_report_classification':historical['classification'],'package_owners':package['owners']}


def archive(path, expected):
    if sha(path.read_bytes()) != expected:
        raise ValueError('Archive hash mismatch')
    z = zipfile.ZipFile(path)
    names = z.namelist()
    if len(names) != len(set(names)):
        z.close(); raise ValueError('Duplicate archive member')
    return z


def build(repo, source_root, original, candidate):
    inputs = {}
    def read(relative):
        data = (repo / relative).read_bytes(); inputs[relative] = sha(data)
        return json.loads(data)
    scan = read('doc/php83/evidence/candidate-syntax/primary-r2.json')
    history = read('doc/php83/evidence/source-audit/php74-vs-php83-compile.json')
    packages = read('doc/php83/evidence/package-identities/primary.json')
    coverage = read('doc/php83/evidence/compiler-triage/coverage.json')
    manifest = read('doc/php83/evidence/exp9-candidate/manifest.json')
    held = read('patches/php83/held/symfony-bootstrap.json')
    if not scan['collection_complete'] or scan['variants']['exp9']['zip_sha256'] != EXP9 or scan['variants']['original']['zip_sha256'] != ORIGINAL:
        raise ValueError('Wrong or incomplete paired scan')
    if packages['original_archive_sha256'] != ORIGINAL:
        raise ValueError('Wrong package/source identity context')
    variants = {name:indexed(scan['variants'][name]['records']) for name in ('original','exp9')}
    for records in variants.values():
        for record in records.values():
            if type(record['exit']) is not int or record['exit'] not in (0, 255):
                raise ValueError('Paired compiler exit status invalid or incomplete')
    rejected = {p:r for p,r in variants['exp9'].items() if r['exit'] == 255}
    if len(rejected) != 54 or scan['variants']['exp9']['summary']['compiler_rejected'] != 54:
        raise ValueError('Rejection denominator changed')
    history = indexed(history['files'])
    coverage_rows = indexed(coverage['paths'])
    if set(rejected) != set(coverage_rows):
        raise ValueError('Coverage paths do not match all rejected files')
    held_rows = indexed(held['files'])
    selected = indexed(manifest['patches'])
    rows = []
    with archive(original, ORIGINAL) as old_zip, archive(candidate, EXP9) as new_zip:
        for path, row in sorted(rejected.items()):
            safe_path(path)
            original_data = old_zip.read(ROOT + path)
            candidate_data = new_zip.read(ROOT + path)
            old_sha, current_sha = sha(original_data), sha(candidate_data)
            if row['sha256'] != current_sha or variants['original'][path]['sha256'] != old_sha:
                raise ValueError('Compiler/source hash conflict')
            local = source_root / path
            if not local.resolve().is_relative_to(source_root.resolve()) or local.is_symlink() or local.read_bytes() != original_data:
                raise ValueError('Immutable source fallback identity conflict')
            if current_sha != old_sha:
                raise ValueError('Unexpected changed source in this fixed 54-row cohort')
            text = original_data.decode('utf-8', errors='replace')
            category, line, excerpt, placeholders = classify(path,row['diagnostics'],text)
            c = coverage_rows[path]
            fallback = []
            lines = text.splitlines()
            # Retain direct-source evidence for all reported missed ranges, not graph absence.
            for issue in c['coverage']:
                for interval in issue.get('ranges',[]):
                    start,end = interval['start'],interval['end']
                    if start < 1 or end < start:
                        raise ValueError('Invalid coverage interval')
                    fallback.append({'requested_start':start,'requested_end':end,
                        'available_end':min(end,len(lines)),
                        'lines':[{'line':i+1,'text':lines[i]} for i in range(start-1,min(end,len(lines)))]})
            packaged_path = 'opt/kaltura/app/' + path
            joined = historical_join(path,current_sha,packages['files'].get(packaged_path),history.get(packaged_path))
            patch = held_rows.get(path)
            held_match = None
            if patch and patch['before_sha256'] == current_sha:
                if sha((repo / patch['patch']).read_bytes()) != patch['patch_sha256']:
                    raise ValueError('Held patch hash conflict')
                held_match = {**patch,'status':'held metadata identity match only; no application or promotion in this audit'}
            rows.append({'path':path,'source_sha256':current_sha,'original_exp9_bytes_equal':True,
                'compiler_exit':row['exit'],'compiler_diagnostics':row['diagnostics'],
                'category':category,'compiler_line':line,'source_excerpt':excerpt,
                'placeholder_lines':placeholders,'historical_baseline':joined,
                'graph_coverage_status':c['status'],'graph_coverage_freshness':c['freshness'],
                'direct_source_fallback':fallback,'selected_in_exp9':path in selected,
                'matching_held_patch':held_match,'runtime_reachability':'unresolved; no dead-code or inactive-path conclusion',
                'acceptance':'OPEN; rendering/output tests required for templates, focused repair/integration for language incompatibilities'})
    return {'schema':1,'scope':'54 compiler-rejected exp9 files; exact source identity and syntax-cause classification only',
        'inputs':inputs,'builder_sha256':sha(Path(__file__).read_bytes()),
        'original_archive_sha256':ORIGINAL,'candidate_archive_sha256':EXP9,
        'graph_project':coverage['project'],'graph_generation':coverage['indexed_at'],
        'graph_usage':'Parent-supplied Tier2 search/coverage; every diagnostic and missed source range read directly from hash-verified immutable bytes. No caller inference.',
        'rows':rows,'summary':{'rejected_denominator':len(rows),
            'categories':dict(sorted(Counter(r['category'] for r in rows).items())),
            'baseline_classifications':dict(sorted(Counter(r['historical_baseline']['baseline_classification'] or 'unresolved' for r in rows).items())),
            'baseline_join_status':dict(Counter(r['historical_baseline']['status'] for r in rows)),
            'graph_coverage_statuses':dict(Counter(r['graph_coverage_status'] for r in rows)),
            'matching_held_patches':sum(r['matching_held_patch'] is not None for r in rows),
            'selected_in_exp9':sum(r['selected_in_exp9'] for r in rows),
            'removed_or_waived_rejections':0},
        'template_consumer_analysis':'Separate worker; no consumer or generated-output claim imported here',
        'candidate_all_files_compile':False,'application_acceptance':False,'t0_04_complete':False}


def main():
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[3])
    p.add_argument('--source-root',type=Path,required=True);p.add_argument('--original',type=Path,required=True)
    p.add_argument('--candidate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise ValueError('Refusing existing output')
    report=build(a.repo,a.source_root,a.original,a.candidate)
    with a.output.open('x') as output:json.dump(report,output,indent=2);output.write('\n')
    print(json.dumps(report['summary'],sort_keys=True))
if __name__=='__main__':main()
