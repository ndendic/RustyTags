#!/usr/bin/env python3

"""
Comprehensive test for HTML attribute quote formatting
"""

import sys
sys.path.insert(0, '.')

import rusty_tags as rt
from rusty_tags.datastar import signals, reactive_class, DS

def test_quote_formatting():
    """Test that all HTML attribute quote formatting is correct"""
    
    print("=== HTML Attribute Quote Formatting Test ===")
    
    # Test 1: signals() function
    print("\n1. Testing signals() function:")
    div1 = rt.Div(ds_signals=signals(count=0, name="test")) # type: ignore
    result1 = str(div1)
    print(f"signals result: {result1}")
    assert 'data-signals="{\'count\':0,\'name\':\'test\'}"' in result1, "signals() should use double quotes outside, single quotes inside JSON"
    
    # Test 2: reactive_class() function  
    print("\n2. Testing reactive_class() function:")
    div2 = rt.Div(cls=reactive_class(active="$isActive", disabled="$count === 0")) # type: ignore
    result2 = str(div2)
    print(f"reactive_class result: {result2}")
    assert 'data-class="{\'active\':\'$isActive\',\'disabled\':\'$count === 0\'}"' in result2, "reactive_class() should use double quotes outside, single quotes inside JSON"
    
    # Test 3: Direct JSON object  
    print("\n3. Testing direct JSON object:")
    # div3 = rt.Div(ds_signals={"count": 0, "user": {"name": "test", "age": 20}})
    div3 = rt.Div(ds_signals=signals(count=0, user=dict(name="test", age=25))) # type: ignore
    result3 = str(div3)
    print(f"direct JSON result: {result3}")
    # Check that JSON is properly formatted with double quotes outside, single quotes inside
    assert 'data-signals="' in result3, "Should use double quotes for HTML attribute"
    assert "'" in result3, "Should use single quotes inside JSON"
    
    # Test 3b: More complex nested JSON
    print("\n3b. Testing complex nested JSON:")
    div3b = rt.Div(ds_signals=dict(users=[dict(id=1, name="test")], active=True)) # type: ignore
    result3b = str(div3b)
    print(f"complex JSON result: {result3b}")
    assert 'data-signals="' in result3b, "Should use double quotes for HTML attribute"
    
    # Test 4: String values
    print("\n4. Testing string values:")
    div4 = rt.Div(ds_text="Hello World")
    result4 = str(div4)
    print(f"string value result: {result4}")
    assert 'data-text="Hello World"' in result4, "String values should use double quotes"
    
    # Test 5: JavaScript expressions  
    print("\n5. Testing JavaScript expressions:")
    div5 = rt.Div(ds_text="$message")
    result5 = str(div5)
    print(f"expression result: {result5}")
    assert 'data-text="$message"' in result5, "Expressions should use double quotes"
    
    # Test 6: Strings with single quotes that need escaping
    print("\n6. Testing strings with single quotes:")
    div6 = rt.Div(ds_text="Don't worry")
    result6 = str(div6)
    print(f"escaped quotes result: {result6}")
    assert 'data-text="Don\\\'t worry"' in result6, "Single quotes should be escaped properly within double quotes"
    
    # Test 7: Regular HTML attributes (should still use double quotes)
    print("\n7. Testing regular HTML attributes:")
    div7 = rt.Div(id="test-id", class_="my-class")
    result7 = str(div7)
    print(f"regular attributes result: {result7}")
    assert 'id="test-id"' in result7, "Regular attributes should use double quotes"
    assert 'class="my-class"' in result7, "Regular attributes should use double quotes"
    
    # Test 8: Mixed regular and Datastar attributes
    print("\n8. Testing mixed attributes:")
    div8 = rt.Div(id="mixed", ds_text="$value", class_="container")
    result8 = str(div8)
    print(f"mixed attributes result: {result8}")
    assert 'id="mixed"' in result8, "Regular attributes should use double quotes"
    assert 'data-text="$value"' in result8, "Datastar attributes should use double quotes"
    assert 'class="container"' in result8, "Regular attributes should use double quotes"
    
    print("\n✅ All quote formatting tests passed!")
    print("All HTML attributes use double quotes: attr=\"value\"")
    print("JSON inside Datastar attributes use single quotes: data-attr=\"{'key': 'value'}\"")

if __name__ == "__main__":
    test_quote_formatting()