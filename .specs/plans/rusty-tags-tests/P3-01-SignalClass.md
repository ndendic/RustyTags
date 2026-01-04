# Feature: Datastar SDK Signal Class Testing

## Overview

This specification covers testing of the Signal class in the Datastar SDK Python API. Signal provides a type-safe reactive state reference with automatic JavaScript generation.

### Tasks

- [ ] Test Signal creation with name and initial value
- [ ] Test to_js() returns $name format
- [ ] Test to_dict() for signals attribute
- [ ] Test Signal with namespace
- [ ] Test Signal type inference
- [ ] Test Signal hashing and equality

### Technical Details

**Test File Location:** `tests/test_datastar_sdk.py`

**Imports:**
```python
import pytest
from rusty_tags.datastar import Signal, Signals
```

**Test Patterns:**
```python
def test_signal_creation():
    sig = Signal("count", 0)
    assert sig.to_js() == "$count"

def test_signal_to_dict():
    sig = Signal("name", "test")
    assert sig.to_dict() == {"name": "test"}

def test_signal_with_namespace():
    sig = Signal("count", 0, namespace="app")
    assert sig.to_js() == "$app.count"

def test_signal_str():
    sig = Signal("value", 42)
    assert str(sig) == "$value"

def test_signal_type_inference():
    int_sig = Signal("num", 42)
    assert int_sig.type_ == int

    str_sig = Signal("text", "hello")
    assert str_sig.type_ == str

    bool_sig = Signal("flag", True)
    assert bool_sig.type_ == bool
```

### Handover notes for next developer
------------------------------------

------------------------------------
Remove resolved and obsolete comments and leave relevant instructions between markers! <--DO NOT DELETE THIS SENTANCE
