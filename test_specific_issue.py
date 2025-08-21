#!/usr/bin/env python3

"""
Test script to investigate the specific issue mentioned by the user
"""

import sys
sys.path.insert(0, '.')

import rusty_tags as rt
from rusty_tags.datastar import signals, reactive_class

def test_specific_issue():
    """Test the specific issue mentioned with signals namespacing"""
    
    print("=== Testing Specific Issue ===")
    
    # Test 1: Complex nested signals 
    print("\n1. Testing complex nested signals:")
    div1 = rt.Div(ds_signals={"count": 0, "user": {"name": "test", "age": 20}})
    result1 = str(div1)
    print(f"Input: {{'count': 0, 'user': {{'name': 'test', 'age': 20}}}}")
    print(f"Output: {result1}")
    print(f"Expected: data-signals=\"{{'count':0,'user':{{'name':'test','age':20}}}}\"")
    
    # Test 2: Using signals() helper function
    print("\n2. Testing signals() helper function:")
    div2 = rt.Div(ds_signals=signals(count=0, user={"name": "test", "age": 20}))
    result2 = str(div2)
    print(f"Input via signals(): count=0, user={{'name': 'test', 'age': 20}}")
    print(f"Output: {result2}")
    
    # Test 3: More complex nested structure
    print("\n3. Testing more complex nested structure:")
    complex_data = {
        "users": [
            {"id": 1, "name": "Alice", "active": True},
            {"id": 2, "name": "Bob", "active": False}
        ],
        "meta": {
            "total": 2,
            "page": 1
        },
        "settings": {
            "theme": "dark",
            "notifications": True
        }
    }
    div3 = rt.Div(ds_signals=complex_data)
    result3 = str(div3)
    print(f"Complex input: {complex_data}")
    print(f"Output: {result3}")
    
    # Test 4: Check if all keys/values are preserved
    print("\n4. Analyzing preservation of data:")
    expected_keys = ["users", "meta", "settings"]
    for key in expected_keys:
        if key in result3:
            print(f"✅ Key '{key}' found in output")
        else:
            print(f"❌ Key '{key}' MISSING from output")
    
    # Check specific nested values
    nested_checks = ["Alice", "Bob", "total", "theme", "notifications"]
    for check in nested_checks:
        if check in result3:
            print(f"✅ Value '{check}' found in output")
        else:
            print(f"❌ Value '{check}' MISSING from output")

if __name__ == "__main__":
    test_specific_issue()