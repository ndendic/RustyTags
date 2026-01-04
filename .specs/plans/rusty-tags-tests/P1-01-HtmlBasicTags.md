# Feature: HTML Basic Tags Testing

## Overview

This specification covers comprehensive testing of all HTML tag generation functionality in RustyTags. The tests ensure that all HTML tags render correctly with proper attributes, children, and edge cases.

### Tasks

- [ ] Create test file `tests/test_html_tags.py`
- [ ] Test basic tag generation (Div, Span, P, etc.)
- [ ] Test attributes (id, cls, custom attributes)
- [ ] Test boolean attributes (required, disabled, checked)
- [ ] Test nested children
- [ ] Test multiple children
- [ ] Test mixed text and element children
- [ ] Test numeric children (int, float)
- [ ] Test None children handling
- [ ] Test empty elements
- [ ] Test heading tags H1-H6
- [ ] Test form tags (Form, Input, Button, Label, Select, Textarea)
- [ ] Test table tags (Table, Thead, Tbody, Tfoot, Tr, Th, Td)
- [ ] Test list tags (Ul, Ol, Li)
- [ ] Test semantic tags (Header, Footer, Nav, Main, Article, Section, Aside)
- [ ] Test media tags (Img, Audio, Video, Source)
- [ ] Test document tags (Html, Head, Body, Title, Meta, Link, Script)

### Technical Details

**Test File Location:** `tests/test_html_tags.py`

**Imports:**
```python
import pytest
from rusty_tags import (
    Div, Span, P, A, B, I, Em, Strong, Code,
    H1, H2, H3, H4, H5, H6,
    Form, Input, Button, Label, Select, Textarea,
    Table, Thead, Tbody, Tfoot, Tr, Th, Td, Caption,
    Ul, Ol, Li,
    Header, Footer, Nav, Main, Article, Section, Aside,
    Img, Audio, Video, Source,
    Html, Head, Body, Title, Meta, Link, Script,
    Br, Hr, Iframe, Details, Summary, Figure, Figcaption,
    Address, Pre, Blockquote
)
```

**Test Patterns:**
```python
def test_div_with_text_content():
    result = str(Div("Hello World"))
    assert result == "<div>Hello World</div>"

def test_div_with_id_attribute():
    result = str(Div("Content", id="main"))
    assert 'id="main"' in result
    assert "<div" in result

def test_input_with_boolean_required():
    result = str(Input(type="text", required=True))
    assert "required" in result
    assert 'required=""' not in result  # Should be valueless

def test_html_document_structure():
    result = str(Html(Head(Title("Test")), Body(Div("Content"))))
    assert "<!doctype html>" in result
    assert "<html>" in result
    assert "<head>" in result
    assert "<body>" in result
```

### Handover notes for next developer
------------------------------------

------------------------------------
Remove resolved and obsolete comments and leave relevant instructions between markers! <--DO NOT DELETE THIS SENTANCE
