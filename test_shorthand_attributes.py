#!/usr/bin/env python3
"""
Comprehensive tests for Datastar shorthand attributes in RustyTags.
Tests both the new shorthand syntax and backward compatibility with ds_ prefixes.
"""

import rusty_tags as rt
from rusty_tags.datastar import signals, reactive_class

def test_core_shorthand_attributes():
    """Test the most commonly used shorthand attributes"""
    print("=== Testing Core Shorthand Attributes ===")
    
    # Test signals shorthand
    print("\n1. Testing 'signals' shorthand:")
    div1 = rt.Div(signals={"count": 0, "active": True})
    result1 = str(div1)
    print(f"signals result: {result1}")
    assert 'data-signals=' in result1
    assert "'count':0" in result1 or "'count': 0" in result1
    assert "'active':true" in result1 or "'active': true" in result1
    
    # Test bind shorthand
    print("\n2. Testing 'bind' shorthand:")
    input1 = rt.Input(bind="$value", type="text")
    result2 = str(input1)
    print(f"bind result: {result2}")
    assert 'data-bind="$value"' in result2
    assert 'type="text"' in result2
    
    # Test show shorthand
    print("\n3. Testing 'show' shorthand:")
    div3 = rt.Div("Conditional content", show="$isVisible")
    result3 = str(div3)
    print(f"show result: {result3}")
    assert 'data-show="$isVisible"' in result3
    assert 'Conditional content' in result3
    
    # Test text shorthand
    print("\n4. Testing 'text' shorthand:")
    span1 = rt.Span(text="$message")
    result4 = str(span1)
    print(f"text result: {result4}")
    assert 'data-text="$message"' in result4
    
    # Test attrs shorthand
    print("\n5. Testing 'attrs' shorthand:")
    button1 = rt.Button("Submit", attrs="{'disabled': $loading}")
    result5 = str(button1)
    print(f"attrs result: {result5}")
    assert 'data-attr=' in result5
    assert "{'disabled': $loading}" in result5
    
    # Test style shorthand
    print("\n6. Testing 'style' shorthand:")
    div4 = rt.Div(style="{'color': $themeColor}")
    result6 = str(div4)
    print(f"style result: {result6}")
    assert 'data-style=' in result6


def test_event_shorthand_attributes():
    """Test generic event shorthand attributes"""
    print("\n=== Testing Event Shorthand Attributes ===")
    
    # Test common events
    events_to_test = [
        ("on_click", "$count++"),
        ("on_hover", "$showTooltip()"),
        ("on_submit", "$handleForm()"),
        ("on_focus", "$highlight = true"),
        ("on_blur", "$highlight = false"),
        ("on_keydown", "$handleKey($event)"),
        ("on_change", "$updateValue($event.target.value)"),
        ("on_input", "$liveUpdate($event.target.value)")
    ]
    
    for i, (event_attr, action) in enumerate(events_to_test, 1):
        print(f"\n{i}. Testing '{event_attr}' shorthand:")
        kwargs = {event_attr: action}
        div = rt.Div(**kwargs)
        result = str(div)
        print(f"{event_attr} result: {result}")
        
        # Convert event_attr to expected data attribute
        expected_data_attr = event_attr.replace("on_", "data-on-")
        assert f'{expected_data_attr}="{action}"' in result


def test_advanced_shorthand_attributes():
    """Test advanced/pro shorthand attributes"""
    print("\n=== Testing Advanced Shorthand Attributes ===")
    
    advanced_attrs = [
        ("effect", "console.log($count)"),
        ("computed", "fullName = $firstName + ' ' + $lastName"),
        ("ref", "$refs.myElement"),
        ("indicator", "$loading"),
        ("on_load", "$initialize()"),
        ("on_intersect", "$lazyLoad()"),
        ("on_interval", "$updateClock()"),
        ("persist", "local"),
        ("ignore", "true")
    ]
    
    for i, (attr_name, attr_value) in enumerate(advanced_attrs, 1):
        print(f"\n{i}. Testing '{attr_name}' shorthand:")
        kwargs = {attr_name: attr_value}
        div = rt.Div(**kwargs)
        result = str(div)
        print(f"{attr_name} result: {result}")
        
        # Convert to expected data attribute
        expected_attr = attr_name.replace("_", "-")
        if not expected_attr.startswith("data-"):
            expected_attr = f"data-{expected_attr}"
        
        assert f'{expected_attr}="{attr_value}"' in result


def test_backward_compatibility():
    """Test that ds_ prefixes still work alongside shorthand"""
    print("\n=== Testing Backward Compatibility ===")
    
    # Mix shorthand and ds_ attributes
    print("\n1. Testing mixed shorthand and ds_ attributes:")
    div1 = rt.Div(
        "Mixed attributes",
        signals={"count": 0},          # shorthand
        ds_text="$message",            # ds_ prefix
        show="$isVisible",             # shorthand  
        ds_on_click="$increment()",    # ds_ prefix
        on_hover="$showTooltip()"      # shorthand
    )
    result1 = str(div1)
    print(f"mixed result: {result1}")
    
    assert 'data-signals=' in result1
    assert 'data-text="$message"' in result1
    assert 'data-show="$isVisible"' in result1
    assert 'data-on-click="$increment()"' in result1
    assert 'data-on-hover="$showTooltip()"' in result1
    
    # Test that both produce same output
    print("\n2. Testing equivalent outputs:")
    div_shorthand = rt.Div(signals={"test": 123})
    div_ds_prefix = rt.Div(ds_signals={"test": 123})
    
    result_shorthand = str(div_shorthand)
    result_ds_prefix = str(div_ds_prefix)
    
    print(f"shorthand: {result_shorthand}")
    print(f"ds_ prefix: {result_ds_prefix}")
    
    # Both should produce the same data-signals attribute
    assert 'data-signals=' in result_shorthand
    assert 'data-signals=' in result_ds_prefix
    assert "'test':123" in result_shorthand or "'test': 123" in result_shorthand
    assert "'test':123" in result_ds_prefix or "'test': 123" in result_ds_prefix


def test_complex_combinations():
    """Test complex real-world combinations"""
    print("\n=== Testing Complex Combinations ===")
    
    # Complex form example
    print("\n1. Testing complex form with multiple shorthand attributes:")
    form = rt.Form(
        rt.Input(
            type="text",
            bind="$formData.name",
            attrs="{'required': true}",
            on_focus="$fieldFocus('name')",
            on_blur="$fieldBlur('name')"
        ),
        rt.Button(
            "Submit",
            show="$formValid",
            on_click="$submitForm()",
            attrs="{'disabled': $submitting}"
        ),
        rt.Div(
            text="$errorMessage",
            show="$hasError",
            style="{'color': 'red'}"
        ),
        signals={
            "formData": {"name": ""},
            "formValid": False,
            "hasError": False,
            "submitting": False,
            "errorMessage": ""
        },
        on_submit="$handleSubmit($event)"
    )
    
    result = str(form)
    print(f"complex form: {result}")
    
    # Verify all shorthand attributes are converted
    assert 'data-signals=' in result
    assert 'data-bind="$formData.name"' in result
    assert 'data-show="$formValid"' in result
    assert 'data-on-click="$submitForm()"' in result
    assert 'data-on-submit="$handleSubmit($event)"' in result
    assert 'data-text="$errorMessage"' in result
    assert 'data-style=' in result
    assert 'data-attr=' in result


def test_cls_reactive_compatibility():
    """Test that cls reactive behavior still works with shorthand"""
    print("\n=== Testing cls Reactive Compatibility ===")
    
    # Mix cls with shorthand attributes
    div = rt.Div(
        "Reactive styling",
        cls=reactive_class(
            active="$isActive",
            disabled="$isDisabled"
        ),
        signals={"isActive": True, "isDisabled": False},
        show="$isVisible",
        on_click="$toggle()"
    )
    
    result = str(div)
    print(f"cls + shorthand: {result}")
    
    # Should have both data-class (from reactive cls) and other shorthand attrs
    assert 'data-class=' in result
    assert 'data-signals=' in result  
    assert 'data-show="$isVisible"' in result
    assert 'data-on-click="$toggle()"' in result
    assert "'active':'$isActive'" in result or "'active': '$isActive'" in result
    assert "'disabled':'$isDisabled'" in result or "'disabled': '$isDisabled'" in result


def main():
    """Run all tests"""
    print("🧪 Testing RustyTags Datastar Shorthand Attributes")
    print("=" * 60)
    
    try:
        test_core_shorthand_attributes()
        test_event_shorthand_attributes()
        test_advanced_shorthand_attributes()
        test_backward_compatibility()
        test_complex_combinations()
        test_cls_reactive_compatibility()
        
        print("\n" + "=" * 60)
        print("✅ All shorthand attribute tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    main()