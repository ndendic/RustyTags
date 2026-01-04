# Feature: Datastar Event Attributes Testing

## Overview

This specification covers testing of Datastar event attribute transformations. Events use the `on_*` shorthand which transforms to `data-on:*` colon syntax in Datastar v1.0+.

### Tasks

- [ ] Test on_click -> data-on:click transformation
- [ ] Test underscore to hyphen conversion in event names
- [ ] Test event modifiers with double underscore (__debounce, __throttle)
- [ ] Test modifier values with single underscore becoming dot
- [ ] Test multiple modifiers (window, throttle combined)
- [ ] Test expression preservation in event values

### Technical Details

**Test File Location:** `tests/test_datastar_attrs.py` (add to existing or create new)

**Transformation Rules:**
- `on_click` -> `data-on:click`
- `on_custom_event` -> `data-on:custom-event`
- `on_input__debounce_500ms` -> `data-on:input__debounce.500ms`
- `on_click__window__throttle_1s` -> `data-on:click__window__throttle.1s`

**Test Patterns:**
```python
def test_on_click_colon_syntax():
    result = str(Div("Click", on_click="$count++"))
    assert 'data-on:click="$count++"' in result

def test_event_with_modifiers():
    result = str(Input(on_input__debounce_500ms="search()"))
    assert 'data-on:input__debounce.500ms="search()"' in result

def test_multiple_modifiers():
    result = str(Div("Test", on_click__window__throttle_1s="global()"))
    assert 'data-on:click__window__throttle.1s' in result
```

### Handover notes for next developer
------------------------------------

------------------------------------
Remove resolved and obsolete comments and leave relevant instructions between markers! <--DO NOT DELETE THIS SENTANCE
