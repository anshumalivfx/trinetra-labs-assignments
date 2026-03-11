"""
Helper Utilities
"""

from typing import Any, Dict
import hashlib
import json


def generate_checksum(data: bytes) -> str:
    """Generate SHA256 checksum"""
    return hashlib.sha256(data).hexdigest()


def safe_json_loads(data: str, default: Any = None) -> Any:
    """Safely parse JSON with fallback"""
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return default


def truncate_string(text: str, max_length: int = 1000) -> str:
    """Truncate string to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."
