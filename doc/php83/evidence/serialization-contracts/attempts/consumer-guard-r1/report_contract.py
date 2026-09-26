"""Pure report-envelope checks. No filesystem, PHP, SSH, or acceptance semantics."""
KINDS = ('plain', 'null', 'decorator', 'role', 'profile', 'cacheable')
OPS = ('roundtrip', 'malformed', 'invalid-utf8')
CACHE = ('hit', 'expired', 'malformed', 'refresh-hit', 'refresh-miss', 'invalid-utf8', 'read-C', 'read-O')


def expected_keys74():
    rows = [('original', kind, op, None) for kind in KINDS for op in OPS]
    for writer in ('original83', 'candidate83'):
        rows.extend(('original', kind, 'read', writer) for kind in KINDS)
    rows.extend(('original', 'cache', case,
                 'recorded83-C' if case == 'read-C' else 'recorded83-O' if case == 'read-O' else None)
                for case in CACHE)
    return rows


def check_records74(records):
    if type(records) is not list:
        raise ValueError('Records must be an ordered list')
    actual = []
    for row in records:
        if type(row) is not dict:
            raise ValueError('Record must be an object')
        key = tuple(row.get(field) for field in ('variant', 'kind', 'operation', 'writer'))
        if any(type(value) is not str for value in key[:3]) or (key[3] is not None and type(key[3]) is not str):
            raise ValueError('Invalid case key types')
        actual.append(key)
        if type(row.get('exit')) is not int or row['exit'] != 0:
            raise ValueError('Nonzero or noninteger process exit')
        if type(row.get('stdout')) is not str or type(row.get('stderr')) is not str:
            raise ValueError('Raw output channels must be strings')
    if actual != expected_keys74():
        raise ValueError('Exact ordered case inventory mismatch')


def check_prior74(report, manifest_pin):
    if type(report) is not dict:
        raise ValueError('Prior report must be an object')
    if (report.get('mode') != '74' or report.get('status') != 'OBSERVED_NOT_ACCEPTED'
            or report.get('application_acceptance') is not False or report.get('errors') != []
            or report.get('stage_manifest_sha256') != manifest_pin):
        raise ValueError('Wrong or incomplete original74 report envelope')
    check_records74(report.get('records'))
