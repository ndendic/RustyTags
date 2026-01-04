# Feature: Datastar Keys Plugin Testing

## Overview

This specification covers testing of the data-on-keys plugin support for keyboard shortcuts. The on_keys_* pattern transforms differently than regular events, using `data-on-keys:*` format.

### Tasks

- [ ] Test on_keys_* -> data-on-keys:* transformation
- [ ] Test keyboard combinations (ctrl_k, alt_enter, meta_s)
- [ ] Test element-scoped modifier (__el)
- [ ] Test timing modifiers (__throttle, __debounce)
- [ ] Test bare on_keys for capturing all keys
- [ ] Test function keys (f1, f2, etc.)

### Technical Details

**Transformation Rules:**
- `on_keys_escape` -> `data-on-keys:escape`
- `on_keys_ctrl_k` -> `data-on-keys:ctrl-k`
- `on_keys_enter__el` -> `data-on-keys:enter__el`
- `on_keys_space__throttle_1s` -> `data-on-keys:space__throttle.1s`
- `on_keys` (bare) -> `data-on-keys`

**Important:** Note that this is `data-on-keys:*` NOT `data-on:keys-*`

**Test Patterns:**
```python
def test_simple_key():
    result = str(Div("Test", on_keys_escape="close()"))
    assert 'data-on-keys:escape="close()"' in result

def test_key_combination():
    result = str(Div("Test", on_keys_ctrl_k="search()"))
    assert 'data-on-keys:ctrl-k' in result

def test_key_with_el_modifier():
    result = str(Input(on_keys_enter__el="submit()"))
    assert 'data-on-keys:enter__el' in result

def test_bare_on_keys():
    result = str(Div("Test", on_keys="logKey($event)"))
    assert 'data-on-keys="logKey($event)"' in result
```

### Handover notes for next developer
------------------------------------

------------------------------------
Remove resolved and obsolete comments and leave relevant instructions between markers! <--DO NOT DELETE THIS SENTANCE
