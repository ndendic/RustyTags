#!/usr/bin/env python3
"""Test that $ stripping works for bind, ds_bind, and data_bind."""

from rusty_tags import Input
from rusty_tags.datastar import Signal

print("Testing bind attribute $ stripping across all variants")
print("=" * 70)

test_signal = Signal("test_value", "hello")

# Test all three variants
variants = [
    ("bind", test_signal),
    ("ds_bind", test_signal),
    ("data_bind", test_signal),
]

all_passed = True

for i, (attr_name, signal_value) in enumerate(variants, 1):
    kwargs = {attr_name: signal_value}
    result = str(Input(type="text", **kwargs))
    
    # Should have data-bind="test_value" (without $)
    expected = 'data-bind="test_value"'
    passed = expected in result
    
    # Should NOT have $ prefix
    has_dollar = 'data-bind="$' in result
    
    status = "✓" if (passed and not has_dollar) else "✗"
    
    print(f"Test {i}: {attr_name}={signal_value._name}")
    print(f"  Expected: {expected}")
    print(f"  Has $:    {has_dollar}")
    print(f"  Result:   {status} {'PASS' if passed and not has_dollar else 'FAIL'}")
    
    if not passed or has_dollar:
        print(f"  Output:   {result}")
        all_passed = False
    
    print()

print("=" * 70)
if all_passed:
    print("✓ All bind variants work correctly!")
else:
    print("✗ Some variants failed - see details above")
print("=" * 70)

