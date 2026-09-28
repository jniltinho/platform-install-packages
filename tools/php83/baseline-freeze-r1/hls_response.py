"""Pure response checks extracted from frozen short_delivery443.fetch; no URL rewriting."""
import re
from short_delivery443 import Rejected,require
def validate(response,limit=65536,status=200):
    require(type(response) is tuple and len(response)==3,'RESPONSE')
    code,pairs,body=response
    require(type(code) is int and code==status,'STATUS')
    require(type(body) is bytes and len(body)<=limit,'BODY_LIMIT')
    require(type(pairs) in (list,tuple) and len(pairs)<=100,'HEADERS')
    selected={}
    for pair in pairs:
        require(type(pair) in (list,tuple) and len(pair)==2 and all(type(v) is str for v in pair),'HEADERS')
        k,v=pair
        require(re.fullmatch(r"[!#$%&'*+.^_`|~0-9A-Za-z-]+",k),'HEADER_NAME')
        k=k.lower()
        require(not any(c in v for c in '\r\n\0'),'HEADERS')
        if k in {'content-length','content-range','content-encoding','location'}:
            require(k not in selected,'DUPLICATE_HEADER');selected[k]=v
    require('location' not in selected and selected.get('content-encoding','identity')=='identity','ENCODING_REDIRECT')
    if 'content-length' in selected:
        require(re.fullmatch(r'0|[1-9][0-9]*',selected['content-length']) and int(selected['content-length'])==len(body),'LENGTH')
    return selected,body
