#!/usr/bin/env python3
"""
Test boolean attribute handling in RustyTags
Tests that boolean values are properly converted to HTML5 standard format
"""

import rusty_tags as rt

def test_boolean_attributes():
    print("Testing Boolean Attribute Handling")
    print("=" * 40)
    
    # Test case 1: True boolean should create attribute without value
    print("1. disabled=True should create 'disabled' attribute:")
    input_disabled = rt.Input(disabled=True, type="text")
    print(f"   {input_disabled}")
    result = str(input_disabled)
    assert 'disabled' in result and 'disabled=' not in result, f"Expected 'disabled' without value, got {input_disabled}"
    
    # Test case 2: False boolean should omit attribute entirely
    print("2. disabled=False should omit 'disabled' attribute:")
    input_enabled = rt.Input(disabled=False, type="text")
    print(f"   {input_enabled}")
    result = str(input_enabled)
    assert 'disabled' not in result, f"Expected NO 'disabled' attribute, got {input_enabled}"
    
    # Test case 3: Multiple boolean attributes
    print("3. Multiple boolean attributes:")
    input_multi = rt.Input(disabled=True, required=True, readonly=False, type="text")
    print(f"   {input_multi}")
    result = str(input_multi)
    assert 'disabled' in result, "Should have disabled attribute"
    assert 'required' in result, "Should have required attribute"
    assert 'readonly' not in result, "Should NOT have readonly attribute"
    assert 'type="text"' in result, "Should have type attribute"
    
    # Test case 4: Boolean with other attribute types
    print("4. Boolean mixed with other types:")
    button = rt.Button("Click me", disabled=True, id="mybutton", count=42)
    print(f"   {button}")
    result = str(button)
    assert 'disabled' in result, "Should have disabled attribute"
    assert 'id="mybutton"' in result, "Should have id attribute"
    assert 'count="42"' in result, "Should have count attribute"
    
    # Test case 5: Custom boolean attribute (not standard HTML)
    print("5. Custom boolean attribute:")
    div_custom = rt.Div("Content", my_custom_flag=True, another_flag=False)
    print(f"   {div_custom}")
    result = str(div_custom)
    assert 'my-custom-flag' in result, "Should have custom flag attribute"
    assert 'another-flag' not in result, "Should NOT have false custom flag"
    
    # Test case 6: String values should still work normally
    print("6. String values unchanged:")
    div_string = rt.Div("Content", cls="container", data_value="test")
    print(f"   {div_string}")
    result = str(div_string)
    assert 'class="container"' in result, "Should have class attribute"
    assert 'data-value="test"' in result, "Should have data-value attribute"
    
    print("\n✅ All boolean attribute tests passed!")
    
def test_common_html_boolean_attributes():
    """Test common HTML boolean attributes"""
    print("\nTesting Common HTML Boolean Attributes")
    print("=" * 40)
    
    # Form elements
    input_elem = rt.Input(
        type="text",
        disabled=True,
        required=True, 
        readonly=False,
        autofocus=True,
        multiple=False
    )
    print(f"Input: {input_elem}")
    result = str(input_elem)
    assert 'disabled' in result
    assert 'required' in result
    assert 'autofocus' in result
    assert 'readonly' not in result
    assert 'multiple' not in result
    
    # Select element
    select_elem = rt.Select(
        rt.OptionEl("Option 1", selected=True),
        rt.OptionEl("Option 2", selected=False),
        multiple=True,
        required=False
    )
    print(f"Select: {select_elem}")
    result = str(select_elem)
    assert 'multiple' in result
    assert 'required' not in result
    
    # Details element  
    details_elem = rt.Details(
        rt.Summary("Click to expand"),
        "Hidden content",
        open=True
    )
    print(f"Details: {details_elem}")
    result = str(details_elem)
    assert 'open' in result
    
    print("✅ Common HTML boolean attributes work correctly!")

if __name__ == "__main__":
    test_boolean_attributes()
    test_common_html_boolean_attributes()
    print("\n🎉 All tests passed! Boolean attributes are working correctly.")