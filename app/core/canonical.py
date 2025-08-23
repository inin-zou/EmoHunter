#!/usr/bin/env python3
"""
Canonical JSON serialization for deterministic hashing
Ensures consistent ordering and formatting for cryptographic operations
"""

import json
from typing import Dict, Any, Union


def canonical_json(data: Dict[str, Any]) -> bytes:
    """
    Convert dictionary to canonical JSON bytes for deterministic hashing
    
    Rules:
    - Sort keys lexicographically
    - UTF-8 encoding
    - No whitespace
    - Numbers as plain JSON numbers
    - Timestamps as integers (seconds)
    - Omit null/empty fields
    - Ensure deterministic dict order
    
    Args:
        data: Dictionary to canonicalize
        
    Returns:
        UTF-8 encoded canonical JSON bytes
    """
    # Remove null and empty fields
    cleaned_data = _remove_empty_fields(data)
    
    # Ensure deterministic ordering for nested dicts
    normalized_data = _normalize_nested_dicts(cleaned_data)
    
    # Serialize with sorted keys, no whitespace
    json_str = json.dumps(
        normalized_data,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False
    )
    
    return json_str.encode('utf-8')


def _remove_empty_fields(data: Any) -> Any:
    """
    Recursively remove null, empty string, and empty dict/list fields
    
    Args:
        data: Data to clean
        
    Returns:
        Cleaned data
    """
    if isinstance(data, dict):
        cleaned = {}
        for key, value in data.items():
            cleaned_value = _remove_empty_fields(value)
            # Only include non-empty values
            if cleaned_value is not None and cleaned_value != "" and cleaned_value != {} and cleaned_value != []:
                cleaned[key] = cleaned_value
        return cleaned
    elif isinstance(data, list):
        return [_remove_empty_fields(item) for item in data if item is not None]
    else:
        return data


def _normalize_nested_dicts(data: Any) -> Any:
    """
    Recursively ensure all nested dictionaries are properly ordered
    
    Args:
        data: Data to normalize
        
    Returns:
        Normalized data with sorted dictionaries
    """
    if isinstance(data, dict):
        # Sort dictionary keys and recursively normalize values
        normalized = {}
        for key in sorted(data.keys()):
            normalized[key] = _normalize_nested_dicts(data[key])
        return normalized
    elif isinstance(data, list):
        return [_normalize_nested_dicts(item) for item in data]
    else:
        return data


def validate_canonical_determinism(data: Dict[str, Any], iterations: int = 10) -> bool:
    """
    Validate that canonical_json produces deterministic output
    
    Args:
        data: Test data
        iterations: Number of iterations to test
        
    Returns:
        True if output is deterministic
    """
    first_result = canonical_json(data)
    
    for _ in range(iterations - 1):
        if canonical_json(data) != first_result:
            return False
    
    return True


# Test data for validation
TEST_DATA = {
    "session_id": "s_abc123",
    "consent_id": "c_xyz789", 
    "user_uid": "u_123",
    "model_hashes": {
        "tts": "h_tts",
        "cnn": "h_cnn", 
        "llm": "h_llm"
    },
    "risk_bucket": "low",
    "cost_cents": 50,
    "timestamp": 1724390000,
    "empty_field": None,
    "empty_string": "",
    "empty_dict": {},
    "empty_list": []
}


if __name__ == "__main__":
    # Test canonical JSON determinism
    print("Testing canonical JSON determinism...")
    
    result = canonical_json(TEST_DATA)
    print(f"Canonical JSON: {result.decode('utf-8')}")
    
    is_deterministic = validate_canonical_determinism(TEST_DATA)
    print(f"Deterministic: {is_deterministic}")
    
    # Test with reordered model_hashes
    reordered_data = TEST_DATA.copy()
    reordered_data["model_hashes"] = {
        "llm": "h_llm",
        "cnn": "h_cnn",
        "tts": "h_tts"
    }
    
    reordered_result = canonical_json(reordered_data)
    print(f"Reordered result matches: {result == reordered_result}")
