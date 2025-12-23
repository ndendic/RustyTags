# RustyTags Copilot Instructions

RustyTags is a high-performance HTML generation library combining Rust-powered performance with modern Python web development, featuring FastHTML-style syntax and Datastar integration for reactive web applications.

## Architecture Overview

**🦀 Rust Core (`src/lib.rs`)**: Single 1700+ line file with PyO3 bindings providing:
- High-performance HTML/SVG generation with memory pooling and string interning
- Advanced Datastar attribute processing with intelligent JavaScript expression detection
- Complete HTML5/SVG tag system generated via macros
- Thread-local caching and lock-free concurrent data structures

**🐍 Python Layer (`rusty_tags/`)**: Modular API providing:
- All HTML/SVG tags imported from Rust extension (circular import issue currently exists - import from `rusty_tags.rusty_tags` directly)
- Template system with decorators (`utils.py`: `Page`, `page_template`)
- Datastar integration (`datastar.py`: `DS` action generators, `Signals`)
- Event system (`events.py`: Enhanced Blinker with async support)
- UI components (`xtras/`: accordion, dialog, tabs, sheet, sidebar)

**💻 Examples (`lab/`)**: FastAPI applications demonstrating real-world patterns

## Critical Development Workflows

### Building & Testing
```bash
# ALWAYS rebuild after Rust changes - extension won't update otherwise
maturin develop  # Fast dev builds
maturin develop --release  # For performance testing

# Run test suite (requires rebuild first)
pytest tests/

# Benchmarks (resource intensive - use sparingly)
python tests/benchmarks/run_all.py
python tests/stress_test.py
```

### FastAPI Development Pattern
```bash
python lab/FastapiApp.py  # Reference playground server
```

## Project-Specific Patterns

### Datastar Integration (Core Feature)
- **Signals**: `signals=Signals(count=0, message="")` on any element for reactive state
- **Event Binding**: `on_click='$count++'` or `on_submit=DS.get('/api/endpoint')`
- **Dynamic Styles**: `data_style="{borderRadius: $rounded ? 'var(--radius-5)' : 'var(--radius-2)'}"` 
- **Class Binding**: `data_class="{active: $isActive, dark: $darkMode}"`
- **Expression Detection**: Rust core auto-detects JS expressions (`$signals`, `@actions`, function calls)

### Template System
```python
# Page templates with decorators
page = page_template("App Title", datastar=True, htmlkw={"lang": "en"})

@page(wrap_in=HTMLResponse)
def view_func():
    return Main(H1("Content"))

# Complete pages
Page(H1("Title"), title="Page", bodykw={"class": "theme-dark"})
```

### Open Props + OPUI Integration
- Use CSS custom properties: `style="gap: var(--size-4); border-radius: var(--radius-3)"`
- Array lookups for dynamic tokens: `['var(--shadow-1)', 'var(--shadow-2)'][$intensity - 1]`
- Component classes: `cls="button filled|outlined|tonal|elevated"`

### Component Patterns
```python
# Reusable components return elements
def Card(title, *content, **attrs):
    return Div(H3(title, cls="card-title"), Div(*content, cls="card-body"), cls="card", **attrs)

# UI components from xtras/ with signal-based reactivity
Sheet(SheetContent(...), signal="sheet_right", side="right", modal=True)
```

## Key Technical Details

### Import Workaround
Current circular import issue requires: `from rusty_tags.rusty_tags import Div, Button` instead of `from rusty_tags import Div, Button`

### Attribute Processing
- Dictionaries in positional args auto-expand to attributes: `Div("content", {"id": "main", "class": "active"})`
- Boolean attributes handled correctly: `Input(required=True, hidden=False)`
- Datastar shorthand: `signals={}`, `show="$condition"` auto-converts to `data-*` attributes

### Performance Considerations
- Rust uses thread-local string pools and memory arenas
- Lock-free caching with DashMap for attribute transformations
- Expression detection cached to avoid repeated parsing
- String interning for common HTML tokens

### Testing Strategy
Tests live in `tests/` with patterns like:
- Parametrized tests for different tag types (`test_datastar_basic.py`)
- Boolean attribute validation (`test_boolean_attributes.py`) 
- Performance harnesses (`tests/benchmarks/`)
- Must run `maturin develop` before testing

## Development Priorities
1. **Critical**: Fix circular imports in `__init__.py`
2. **High**: Add comprehensive pytest suite 
3. **Medium**: Performance benchmarking infrastructure
4. **Enhancement**: Async/streaming support, more framework integrations

When working with this codebase:
- Always rebuild with `maturin develop` after touching Rust code
- Test Datastar reactive patterns with browser dev tools + `<datastar-inspector />`
- Use examples in `lab/` as reference implementations
- Follow Open Props token patterns in `instructions/README.md`
- New components should support signal-based reactivity like existing `xtras/`