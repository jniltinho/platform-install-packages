#!/usr/bin/env python3
"""Validate separate lab-selected metadata without changing reviewed preparation."""
import argparse
import copy
import json
from pathlib import Path
import stage

PREPARED_PIN = 'dd9243b654a98385a30dd87a3bbf6e20a3034c9106311d135b57bc9f35696eb2'
SELECTED = stage.REPO / 'doc/php83/evidence/exp11-candidate/selected-manifest.json'
STATUS = 'EXPERIMENTAL_SELECTED_LAB_ONLY_NOT_FOR_PRODUCTION'


def make_selected(payload):
    stage.require(stage.digest(payload) == PREPARED_PIN, 'Reviewed preparation manifest drift')
    prepared = json.loads(payload)
    stage.require(prepared['status'] == 'PREPARED_NOT_SELECTED', 'Wrong preparation state')
    selected = copy.deepcopy(prepared)
    selected['status'] = STATUS
    selected['selection_authorization'] = {
        'reviewed_prepared_manifest': 'doc/php83/evidence/exp11-candidate/manifest.json',
        'reviewed_prepared_manifest_sha256': PREPARED_PIN,
        'decision': 'Coordinator explicitly approved exactly reviewed59+4 for lab-only exp11 source artifact after independent composition and ternary evidence',
        'lab_build_approved': True,
        'production_approved': False,
        'package_ci_integration_approved': False,
        'release_publication_approved': False,
        'runtime_acceptance': False,
    }
    selected['known_limitations'][0] = 'Selected only for lab source artifact construction; exp11 artifact-based runtime and full application acceptance remain unproven'
    selected['known_limitations'][3] = 'Anonymous SPL append has a documented composition delta; bounded independent composition results do not establish universal loader/application parity'
    return selected


def validate_selected(payload, selected_payload):
    expected = make_selected(payload)
    actual = json.loads(selected_payload)
    stage.require(actual == expected, 'Selected manifest differs beyond exact authorized metadata transition')
    stage.require(actual['patches'] == json.loads(payload)['patches'], 'Selected patch drift')
    return actual


def stage_inputs(archive, output):
    stage.require(not output.exists(), 'Refuse existing selected staging directory')
    payload, patches, report = stage.validate(archive)
    selected_bytes = SELECTED.read_bytes()
    selected = validate_selected(payload, selected_bytes)
    output.mkdir(parents=True, exist_ok=False)
    (output / 'manifest.json').write_bytes(selected_bytes)
    for name, data in patches.items():
        (output / name).write_bytes(data)
    return {'status': selected['status'], 'selected_manifest_sha256': stage.digest(selected_bytes),
            'reviewed_prepared_manifest_sha256': PREPARED_PIN, 'targets': len(patches),
            'exact_private_replays': len(report['exact_private_copy_replays']),
            'zip_built': False, 'application_acceptance': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(stage_inputs(args.original, args.output), sort_keys=True))


if __name__ == '__main__':
    main()
