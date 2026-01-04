# Feature: Datastar SDK Expression Operators Testing

## Overview

This specification covers testing of Python operator overloading on Signal and Expr classes. Operators generate JavaScript expressions for reactive computations.

### Tasks

- [ ] Test arithmetic operators (+, -, *, /, %)
- [ ] Test comparison operators (==, !=, <, >, <=, >=)
- [ ] Test logical operators (&, |, ~)
- [ ] Test reverse operators (__radd__, __rsub__, etc.)
- [ ] Test chained expressions

### Technical Details

**Operator Mappings:**
- `+` -> `+`
- `-` -> `-`
- `*` -> `*`
- `/` -> `/`
- `%` -> `%`
- `==` -> `===` (strict equality)
- `!=` -> `!==`
- `<`, `>`, `<=`, `>=` -> same
- `&` -> `&&`
- `|` -> `||`
- `~` -> `!`

**Test Patterns:**
```python
def test_arithmetic_addition():
    sigs = Signals(x=10, y=5)
    result = (sigs.x + sigs.y).to_js()
    assert result == "($x + $y)"

def test_comparison_equality():
    sig = Signal("count", 0)
    result = (sig == 0).to_js()
    assert result == "($count === 0)"

def test_logical_and():
    s1 = Signal("a", True)
    s2 = Signal("b", True)
    result = (s1 & s2).to_js()
    assert result == "($a && $b)"

def test_logical_not():
    sig = Signal("flag", True)
    result = (~sig).to_js()
    assert result == "!($flag)"

def test_complex_expression():
    sigs = Signals(age=25, licensed=True)
    result = ((sigs.age >= 18) & sigs.licensed).to_js()
    assert "$age" in result
    assert ">=" in result
    assert "&&" in result
```

### Handover notes for next developer
------------------------------------

------------------------------------
Remove resolved and obsolete comments and leave relevant instructions between markers! <--DO NOT DELETE THIS SENTANCE
