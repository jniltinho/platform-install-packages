"""One finite API observation; injected caller owns authentication/TLS/privacy windows.
No network, credential access, URLs, or playback claims in this module.
"""
import re

ENTRY = '0_wzmt2sfy'
PARTNER = 102
ORIGINAL = '0_ewuu0o46'
MAX_ASSETS = 50

class Rejected(ValueError):
    pass

def need(ok, code):
    if not ok:
        raise Rejected(code)

def integer(value, code, maximum=2**31-1):
    # API int/string representations only, never float/bool or coercive whitespace.
    need(type(value) is int or (type(value) is str and re.fullmatch(r'0|[1-9][0-9]{0,9}', value)), code)
    n = int(value)
    need(0 <= n <= maximum, code)
    return n

def collect(call):
    """call(**form) must use pinned TLS transport and complete saved privacy windows.
    No success here authorizes requests outside that enclosing lifecycle.
    Exceptions are replaced, never rendered with request/response details.
    """
    try:
        result = call(service='flavorasset', action='list',
                      **{'filter:objectType': 'KalturaFlavorAssetFilter',
                         'filter:entryIdEqual': ENTRY,
                         'pager:pageSize': str(MAX_ASSETS + 1), 'pager:pageIndex': '1'})
    except Exception:
        raise Rejected('API_CALL_FAILED') from None
    need(type(result) is dict and result.get('objectType') == 'KalturaFlavorAssetListResponse', 'RESPONSE_TYPE')
    total = integer(result.get('totalCount'), 'TOTAL', MAX_ASSETS)
    rows = result.get('objects')
    need(type(rows) is list and len(rows) == total and total > 0, 'CARDINALITY')
    safe, seen = [], set()
    for row in rows:
        need(type(row) is dict and row.get('objectType') == 'KalturaFlavorAsset', 'ASSET_TYPE')
        ident = row.get('id')
        need(type(ident) is str and re.fullmatch(r'[01]_[a-z0-9]{8}', ident), 'ASSET_ID')
        need(ident not in seen, 'DUPLICATE'); seen.add(ident)
        need(row.get('entryId') == ENTRY and integer(row.get('partnerId'), 'PARTNER') == PARTNER, 'OWNERSHIP')
        raw_status = row.get('status')
        status = -1 if type(raw_status) in (int, str) and raw_status in (-1, '-1') else integer(raw_status, 'STATUS', 9)
        # Observation, not an enum reinterpretation: READY is native status 2.
        original = row.get('isOriginal')
        need(type(original) is bool, 'ORIGINAL_TYPE')
        version = integer(row.get('version'), 'VERSION')
        params = integer(row.get('flavorParamsId'), 'PARAMS')
        size = integer(row.get('size'), 'SIZE', 2**40)
        ext = row.get('fileExt')
        need(ext is None or (type(ext) is str and re.fullmatch(r'[a-zA-Z0-9]{1,12}', ext)), 'EXTENSION')
        safe.append(dict(id=ident, entryId=ENTRY, partnerId=PARTNER, status=status,
                         isOriginal=original, version=version, flavorParamsId=params,
                         size=size, fileExt=ext))
    originals = [r for r in safe if r['isOriginal']]
    need(len(originals) == 1 and originals[0]['id'] == ORIGINAL and originals[0]['version'] == 2, 'SOURCE_BINDING')
    return {'case': 'EXISTING_SHORT_FLAVOR_METADATA', 'api_calls': 1,
            'assets': sorted(safe, key=lambda r: r['id']),
            'playback_tested': False, 'full_acceptance': False}
