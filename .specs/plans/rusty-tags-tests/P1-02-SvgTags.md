# Feature: SVG Tags Testing

## Overview

This specification covers testing of all SVG tag generation functionality in RustyTags. SVG elements have specific attributes and structure that need to be tested for proper rendering.

### Tasks

- [x] Create test file `tests/test_svg_tags.py`
- [x] Test Svg container with viewBox, width, height
- [x] Test basic shapes (Circle, Rect, Ellipse)
- [x] Test line elements (Line, Polyline, Polygon)
- [x] Test Path with d attribute
- [x] Test grouping elements (G, Defs, Use, Symbol)
- [x] Test gradients (LinearGradient, RadialGradient, Stop)
- [x] Test Text element
- [x] Test special tags (Fragment, Safe, CustomTag)
- [ ] Test Marker, Pattern, ClipPath, Mask (if available)
- [ ] Test Image and ForeignObject (if available)

### Technical Details

**Test File Location:** `tests/test_svg_tags.py`

**Imports:**
```python
import pytest
from rusty_tags import (
    Svg, Circle, Rect, Line, Path, Polygon, Polyline, Ellipse,
    Text, G, Defs, Use, Symbol, Marker,
    LinearGradient, RadialGradient, Stop,
    Pattern, ClipPath, Mask, Image, ForeignObject
)
```

**Test Patterns:**
```python
def test_svg_container():
    result = str(Svg(width="200", height="200", viewBox="0 0 200 200"))
    assert "<svg" in result
    assert 'width="200"' in result
    assert 'viewBox="0 0 200 200"' in result

def test_circle_shape():
    result = str(Circle(cx="50", cy="50", r="40", fill="blue"))
    assert "<circle" in result
    assert 'cx="50"' in result
    assert 'r="40"' in result

def test_path_d_attribute():
    result = str(Path(d="M10 10 L90 90", stroke="black"))
    assert 'd="M10 10 L90 90"' in result

def test_gradient_with_stops():
    result = str(LinearGradient(
        Stop(offset="0%", stop_color="red"),
        Stop(offset="100%", stop_color="blue"),
        id="gradient1"
    ))
    assert "<lineargradient" in result.lower()
    assert "<stop" in result.lower()
```

### Handover notes for next developer
------------------------------------

**COMPLETED (2026-01-04):**
- Created comprehensive test file `tests/test_svg_tags.py` with 48 tests
- All SVG shape tests passing (Circle, Rect, Ellipse, Line, Polygon, Polyline, Path)
- All SVG grouping tests passing (G, Defs, Use, Symbol)
- All gradient tests passing (LinearGradient, RadialGradient, Stop)
- SVG Text element tests passing
- All special tags tests passing (Fragment, Safe, CustomTag)
- Verified all 228 tests in test suite passing
- Updated plan_progress.json to reflect completion

**Test Coverage:**
- 8 test classes with 48 individual tests
- TestSvgContainer (3 tests)
- TestSvgShapes (8 tests)
- TestSvgGrouping (5 tests)
- TestSvgGradients (5 tests)
- TestSvgText (3 tests)
- TestFragmentTag (3 tests)
- TestSafeTag (5 tests)
- TestCustomTag (5 tests)
- Plus 3 additional classes for complex structures and edge cases

**Notes:**
- Fragment correctly renders children without wrapper element
- Safe properly escapes HTML entities (<, >, &, quotes)
- CustomTag allows creation of arbitrary custom elements
- SVG gradients use lowercase tag names in output
- Empty SVG elements may render as self-closing tags

**Next Steps:**
- Phase 1 still needs remaining HTML tag tests (html-basic-tags, html-heading-tags, etc.)
- Advanced SVG features (Marker, Pattern, ClipPath, Mask, Image, ForeignObject) not tested yet
  - Check if these are available in rusty_tags first

------------------------------------
Remove resolved and obsolete comments and leave relevant instructions between markers! <--DO NOT DELETE THIS SENTANCE
