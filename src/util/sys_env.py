"""
Import before logging, use print() here, should not import any dependency files
"""

import sys

def get_is_dev_mode() -> bool:
    """
    return true if it is dev mode
    """
    return get_mode() != "prod"

def get_mode() -> str:
    """
    return mode, prod is default, default is empty
    """
    return sys.argv[1] if len(sys.argv) > 1 and sys.argv[1]!="" else "prod"