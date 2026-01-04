# RustyTags Comprehensive Test Suite - Overview

## About this plan

This plan establishes a comprehensive test suite for the RustyTags library, ensuring full coverage of all functionalities including HTML tag generation, Datastar SDK integration, attribute transformations, utility functions, and parsing capabilities. The goal is to create a robust test suite with 100+ tests that validates all existing functionality and serves as a regression safety net for future development.

## Phases

### Phase 1: Core HTML Tag Generation Tests (40+ tests)
Tests for all HTML/SVG tag functions, covering basic usage, attributes, nested children, and edge cases.

### Phase 2: Datastar Attribute Transformation Tests (30+ tests)
Tests for the Datastar handler system including event handlers, bind handlers, signals, class handlers, and keyed plugins.

### Phase 3: Datastar SDK Python API Tests (25+ tests)
Tests for the Python Datastar SDK including Signal class, expression system, operators, and helper functions.

### Phase 4: Utility Functions and Page Templates (15+ tests)
Tests for Page, page_template, show, AttrDict, when, unless, and other utilities.

### Phase 5: HTML Parsing and HtmlElement Tests (15+ tests)
Tests for the parse() method, HtmlElement manipulation, and roundtrip serialization.

## Rules - CRITICAL

### Technical Rules

**DOs:**
- Always run `maturin develop` before running tests if any Rust changes were made
- Use pytest as the test framework
- Test both positive cases (expected behavior) and edge cases
- Verify HTML output using string assertions
- Test Datastar attribute transformations by checking the resulting HTML attributes
- Use descriptive test names that explain what is being tested
- Group related tests into test classes

**DON'Ts:**
- Don't modify the Rust source code (`src/lib.rs`) as part of test implementation
- Don't skip tests without documenting why
- Don't use hardcoded paths - use relative imports
- Don't create tests that depend on external services or network

### Architecture

The test files should be organized under `tests/` directory:

```
tests/
├── test_html_tags.py          # Phase 1: Core HTML tag tests
├── test_svg_tags.py           # Phase 1: SVG tag tests
├── test_datastar_attrs.py     # Phase 2: Datastar attribute transformation tests
├── test_datastar_sdk.py       # Phase 3: Datastar SDK Python API tests
├── test_utilities.py          # Phase 4: Utility function tests
├── test_parse.py              # Phase 5: HTML parsing tests (already exists)
├── test_datastar.py           # Phase 2: Datastar colon syntax tests (already exists)
└── conftest.py                # Shared fixtures if needed
```

### Other

**Running Tests:**
```bash
cd /home/ndendic/Projects/nitro-systems/RustyTags
maturin develop  # Required after Rust changes
pytest tests/ -v
```

**Test Naming Convention:**
- Test functions: `test_<feature>_<scenario>`
- Test classes: `Test<Feature>` (e.g., `TestDivTag`, `TestDatastarBindHandler`)

**Assertions:**
- Use `assert 'expected_string' in result` for partial HTML matching
- Use `assert result == 'exact_string'` for exact matching
- Use `str(html_element)` to convert HtmlString to string for comparison
