# Feature: Page Function Testing

## Overview

This specification covers testing of the Page() utility function that creates complete HTML documents with proper structure, Datastar CDN integration, and customizable headers/footers.

### Tasks

- [x] Test Page creates DOCTYPE and html structure
- [x] Test title parameter sets page title
- [x] Test datastar=True includes CDN script
- [x] Test datastar=False excludes script
- [x] Test hdrs parameter adds elements to head
- [x] Test ftrs parameter adds elements to body end
- [x] Test htmlkw passes attributes to html tag
- [x] Test bodykw passes attributes to body tag
- [x] Test ds_version parameter for CDN version

### Technical Details

**Test File Location:** `tests/test_utilities.py`

**Imports:**
```python
import pytest
from rusty_tags import Page, Div, H1, Meta, Link, Script
```

**Test Patterns:**
```python
def test_page_creates_html_structure():
    result = str(Page(Div("content"), title="Test"))
    assert "<!doctype html>" in result
    assert "<html>" in result
    assert "<head>" in result
    assert "<body>" in result
    assert "<title>Test</title>" in result

def test_page_with_datastar():
    result = str(Page(Div("content"), datastar=True))
    assert "datastar" in result
    assert "jsdelivr" in result

def test_page_without_datastar():
    result = str(Page(Div("content"), datastar=False))
    assert "datastar" not in result

def test_page_with_hdrs():
    result = str(Page(
        Div("content"),
        hdrs=(Meta(charset="utf-8"), Link(rel="stylesheet", href="/style.css"))
    ))
    assert 'charset="utf-8"' in result
    assert 'href="/style.css"' in result
```

### Handover notes for next developer
------------------------------------
**PHASE 4 - COMPLETE (2026-01-04)**

Successfully implemented comprehensive test suite for all Phase 4 utility functions:

**Completed:**
- Created `tests/test_utilities.py` with 42 tests covering all P4 features
- All tests passing (42/42)
- Test coverage includes:
  - Page() function (11 tests): document structure, title, datastar integration, hdrs/ftrs, htmlkw/bodykw
  - page_template() and create_template() (7 tests): decorator functionality, backwards compatibility
  - AttrDict utility (7 tests): attribute and dict access, setting values, copy
  - when() and unless() helpers (6 tests): conditional rendering
  - HtmlString methods (9 tests): render(), encode(), __str__(), __html__() protocol
  - Integration tests (3 tests): combining multiple utilities
- Updated plan_progress.json: all 11 P4 tests marked as passing
- Overall test suite: 228 tests passing

**Test File:** `/home/ndendic/Projects/nitro-systems/RustyTags/tests/test_utilities.py`

**Next Steps:**
- Phase 1 (P1): 32 HTML/SVG basic tag tests remaining (8/40 complete)
- Phase 3 (P3): 28 Datastar SDK Python API tests remaining (0/28 complete)

**Notes:**
- show() function test handles both IPython installed and not installed cases
- All utilities from rusty_tags.utils are now comprehensively tested
- Tests verify both functionality and edge cases
------------------------------------
Remove resolved and obsolete comments and leave relevant instructions between markers! <--DO NOT DELETE THIS SENTANCE
