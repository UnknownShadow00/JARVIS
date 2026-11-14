"""Strict, non-executing data primitives. Errors never echo supplied values."""
import datetime as dt
import hashlib
import json
import re

def need(ok, reason):
    if not ok:
        raise ValueError('BLOCKED: ' + reason)

def integer(x, minimum=0, maximum=10**16):
    need(type(x) is int and minimum <= x <= maximum, 'integer schema')
    return x

def text(x):
    need(type(x) is str and 0 < len(x) <= 128 and re.fullmatch('[A-Za-z0-9_.:-]+', x), 'identifier schema')
    return x

def digest(x):
    need(type(x) is str and re.fullmatch('[0-9a-f]{64}', x), 'digest required')
    return x

def boot(x):
    need(type(x) is str and re.fullmatch(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}', x), 'boot UUID required')
    return x

def utc(x):
    need(type(x) is str and re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ', x), 'explicit UTC required')
    return dt.datetime.strptime(x, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=dt.timezone.utc)

def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def exact(x, keys):
    need(type(x) is dict and set(x) == set(keys), 'missing or extra fields')

def unique(rows):
    result = {}
    for k, v in rows:
        need(k not in result, 'duplicate JSON key')
        result[k] = v
    return result

def decode(raw, limit=8*1024*1024):
    need(type(raw) is bytes and len(raw) <= limit, 'JSON input bound')
    try:
        return json.loads(raw, object_pairs_hook=unique,
                          parse_constant=lambda _: need(False, 'nonfinite JSON'))
    except (UnicodeError, json.JSONDecodeError, RecursionError, MemoryError) as exc:
        raise ValueError('BLOCKED: malformed JSON') from None
