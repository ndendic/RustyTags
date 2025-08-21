#!/usr/bin/env python3

"""
Comprehensive test to verify all fixes are working correctly
"""

import sys
sys.path.insert(0, '.')

import rusty_tags as rt
from rusty_tags.datastar import signals, reactive_class, DS

def test_comprehensive_fixes():
    """Test all aspects of the fixes"""
    
    print("=== Comprehensive Fix Verification ===")
    
    # Test 1: Quote formatting is correct (double quotes for HTML attributes)
    print("\n1. Testing HTML attribute quote formatting:")
    div1 = rt.Div(id="test", class_="container", ds_text="Hello")
    result1 = str(div1)
    print(f"Result: {result1}")
    assert 'id="test"' in result1, "Regular attributes should use double quotes"
    assert 'class="container"' in result1, "Regular attributes should use double quotes"
    assert 'data-text="Hello"' in result1, "Datastar attributes should use double quotes"
    print("✅ HTML attribute quoting is correct")
    
    # Test 2: JSON uses single quotes inside HTML attributes
    print("\n2. Testing JSON quote formatting inside HTML attributes:")
    div2 = rt.Div(ds_signals={"count": 0, "active": True})
    result2 = str(div2)
    print(f"Result: {result2}")
    assert 'data-signals="' in result2, "Should use double quotes for HTML attribute"
    assert "'count':0" in result2 and "'active':true" in result2, "JSON should use single quotes inside"
    print("✅ JSON quote formatting is correct")
    
    # Test 3: Complex nested data is preserved (caching fix)
    print("\n3. Testing complex nested data preservation:")
    complex_data = {
        "users": [
            {"id": 1, "name": "Alice", "roles": ["admin", "user"]},
            {"id": 2, "name": "Bob", "roles": ["user"]}
        ],
        "meta": {"total": 2, "page": 1, "limit": 10},
        "config": {
            "theme": "dark",
            "features": {
                "notifications": True,
                "darkMode": True,
                "beta": False
            }
        }
    }
    
    div3 = rt.Div(ds_signals=complex_data)
    result3 = str(div3)
    print(f"Complex result length: {len(result3)} chars")
    
    # Check that all keys and nested values are preserved
    expected_values = ["users", "Alice", "Bob", "admin", "user", "meta", "total", "config", 
                      "theme", "dark", "features", "notifications", "darkMode", "beta"]
    
    missing_values = []
    for value in expected_values:
        if value not in result3:
            missing_values.append(value)
    
    if missing_values:
        print(f"❌ Missing values: {missing_values}")
        print(f"Full result: {result3}")
        assert False, f"Missing values in complex data: {missing_values}"
    else:
        print("✅ All complex nested data is preserved")
    
    # Test 4: Multiple different complex objects don't interfere (no caching pollution)
    print("\n4. Testing no caching pollution between different objects:")
    
    data1 = {"type": "user", "name": "Alice", "id": 1}
    data2 = {"type": "product", "name": "Widget", "price": 29.99}
    data3 = {"type": "order", "items": ["widget", "gadget"], "total": 59.98}
    
    div_a = rt.Div(ds_signals=data1)
    div_b = rt.Div(ds_signals=data2)  
    div_c = rt.Div(ds_signals=data3)
    
    result_a = str(div_a)
    result_b = str(div_b)
    result_c = str(div_c)
    
    # Each should contain its own data and not the others
    assert "Alice" in result_a and "Widget" not in result_a and "gadget" not in result_a
    assert "Widget" in result_b and "Alice" not in result_b and "gadget" not in result_b
    assert "gadget" in result_c and "Alice" not in result_c and "Widget" not in result_c
    
    print("✅ No caching pollution between different objects")
    
    # Test 5: signals() and reactive_class() helpers work correctly
    print("\n5. Testing helper functions:")
    
    div5 = rt.Div(
        ds_signals=signals(counter=0, user={"name": "test", "active": True}),
        cls=reactive_class(highlighted="$isActive", disabled="$counter === 0")
    )
    result5 = str(div5)
    print(f"Helper result: {result5}")
    
    assert "counter" in result5, "signals() should preserve counter"
    assert "user" in result5, "signals() should preserve user object"
    assert "highlighted" in result5, "reactive_class() should preserve highlighted"
    assert "disabled" in result5, "reactive_class() should preserve disabled"
    
    print("✅ Helper functions work correctly")
    
    # Test 6: Mixed regular and Datastar attributes
    print("\n6. Testing mixed attribute types:")
    
    div6 = rt.Div(
        id="mixed-test",
        class_="container",
        ds_signals={"count": 5},
        ds_text="$message",
        data_custom="regular-data",
        aria_label="Accessible label"
    )
    result6 = str(div6)
    print(f"Mixed result: {result6}")
    
    # All should be present with correct formatting
    assert 'id="mixed-test"' in result6
    assert 'class="container"' in result6  
    assert 'data-signals="' in result6 and "count" in result6
    assert 'data-text="$message"' in result6
    assert 'data-custom="regular-data"' in result6
    assert 'aria-label="Accessible label"' in result6
    
    print("✅ Mixed attributes work correctly")
    
    print("\n🎉 All comprehensive tests passed!")
    print("✅ Quote formatting is correct")
    print("✅ Complex nested data is preserved")  
    print("✅ No caching pollution")
    print("✅ Helper functions work")
    print("✅ Mixed attributes work")

if __name__ == "__main__":
    test_comprehensive_fixes()