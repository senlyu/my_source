import json
import hashlib
import os

def hash_data_40_chars(data):
    canonical_bytes = json.dumps(
        data,
        sort_keys=True,
        separators=(',', ':')
    ).encode('utf-8')
    return hashlib.sha1(canonical_bytes).hexdigest() # 40 chars

def get_env_or_config(key, default=None):
    # Try to get from environment variable first
    val = os.getenv(key)
    if val:
        return val
    return default
