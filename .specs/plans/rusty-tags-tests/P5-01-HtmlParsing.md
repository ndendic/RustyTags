# Feature: HTML Parsing Testing

## Overview

This specification covers testing of the parse() method on HtmlString that converts rendered HTML back into a manipulable HtmlElement tree.

### Tasks

- [ ] Test parse() on simple element returns HtmlElement
- [ ] Test parsed element has correct tag property
- [ ] Test parsed element has correct attributes dict
- [ ] Test parsed element has correct children list
- [ ] Test text nodes preserved as strings in children
- [ ] Test element nodes preserved as HtmlElement in children
- [ ] Test deeply nested structures
- [ ] Test mixed content (text + elements)
- [ ] Test empty elements

### Technical Details

**Test File Location:** `tests/test_parse.py` (extend existing)

**Imports:**
```python
import pytest
from rusty_tags import Div, Input, Button, Form, Span, HtmlElement
```

**Test Patterns:**
```python
def test_parse_simple_element():
    html = Div("content", id="test")
    doc = html.parse()

    assert isinstance(doc, HtmlElement)
    assert doc.tag == "div"
    assert doc.attributes["id"] == "test"
    assert "content" in doc.children

def test_parse_nested_structure():
    html = Div(Div(Span("inner")))
    doc = html.parse()

    assert doc.tag == "div"
    assert len(doc.children) == 1

    child = doc.children[0]
    assert hasattr(child, 'tag')
    assert child.tag == "div"

def test_parse_mixed_content():
    html = Div("text", Span("span"), "more")
    doc = html.parse()

    assert len(doc.children) == 3
    assert doc.children[0] == "text"
    assert hasattr(doc.children[1], 'tag')
    assert doc.children[2] == "more"
```

### Handover notes for next developer
------------------------------------
**Completed (2026-01-04):**
- All Phase 5 HTML Parsing tests have been implemented and are passing (18 tests total)
- Extended tests/test_parse.py with comprehensive coverage of:
  - Basic parsing functionality (simple elements, nested structures, mixed content)
  - HtmlElement attribute modification and access
  - Parse/modify/serialize roundtrip functionality
  - HtmlElement __html__ protocol for use as children
  - HtmlElement __repr__ for debugging
  - Deep nesting traversal
  - Form validation use case
- All 10 P5 test requirements from plan_progress.json are marked as passing
- Tests verify that underscores in attribute names are properly converted to hyphens
- Tests handle edge cases like empty elements

**Status:** Phase 5 complete - all tests passing
------------------------------------
Remove resolved and obsolete comments and leave relevant instructions between markers! <--DO NOT DELETE THIS SENTANCE
