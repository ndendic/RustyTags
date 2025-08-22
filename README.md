# RustyTags

⚠️ **Early Beta** - This library is in active development and APIs may change.

A high-performance HTML generation library that provides a Rust-based Python extension for building HTML/SVG tags. RustyTags offers significant speed improvements over pure Python HTML generation libraries through memory optimization and Rust-powered performance, now featuring FastHTML-style callable syntax and comprehensive Datastar integration for modern reactive web development.

## What RustyTags Does

RustyTags generates HTML and SVG content programmatically with:
- **Speed**: Rust-powered performance with memory optimization and caching
- **Modern Syntax**: FastHTML-style callable chaining with minimal performance overhead
- **Datastar Integration**: Complete reactive web development with shorthand attributes
- **Type Safety**: Smart type conversion for Python objects (booleans, numbers, strings)
- **Framework Integration**: Supports `__html__`, `_repr_html_`, and `render()` methods
- **Advanced Features**: Custom tags, attribute mapping, complete HTML5/SVG support

## Quick Start

### Installation (Development)

```bash
# Clone and build from source
git clone <repository>
cd rustyTags
maturin develop

# Or build for release
maturin build --release
```

### Basic Usage

```python
from rusty_tags import Div, P, A, Html, Head, Body, Script, CustomTag, Svg, Circle, Text
from rusty_tags.datastar import signals, reactive_class, DS

# Simple HTML generation
content = Div(
    P("Hello World", cls="greeting"),
    A("Click here", href="https://example.com", target="_blank")
)
print(content)
# Output: <div><p class="greeting">Hello World</p><a href="https://example.com" target="_blank">Click here</a></div>

# FastHTML-style callable chaining (NEW!)
content = Div(cls="container")(
    P("Hello World", cls="greeting"),
    A("Click here", href="https://example.com")
)
print(content)
# Output: <div class="container"><p class="greeting">Hello World</p><a href="https://example.com">Click here</a></div>

# Flexible chaining patterns
link = A("Click me", href="/path")
wrapper = Div(cls="max-w-full")(link)
print(wrapper)
# Output: <div class="max-w-full"><a href="/path">Click me</a></div>

# Complete HTML document
page = Html(
    Head(
        Script("console.log('Hello');")
    ),
    Body(
        Div("Main content")
    ),
    lang="en"
)
print(page)
# Output: <!doctype html><html lang="en"><head><script>console.log('Hello');</script></head><body><div>Main content</div></body></html>

# Custom tags
custom = CustomTag("my-component", "Content", data_value="123")
print(custom)
# Output: <my-component data-value="123">Content</my-component>

# SVG graphics
svg_graphic = Svg(
    Circle(cx="50", cy="50", r="40", fill="blue"),
    Text("Hello SVG!", x="10", y="30", fill="white"),
    width="100", height="100"
)
print(svg_graphic)
# Output: <svg width="100" height="100"><circle cx="50" cy="50" r="40" fill="blue"></circle><text x="10" y="30" fill="white">Hello SVG!</text></svg>

# Datastar reactive components (NEW!)
reactive_counter = Div(
    P(text="$count", cls="counter-display"),
    Button("+", on_click="$count++"),
    Button("-", on_click="$count--"),
    signals={"count": 0},
    cls="counter-app"
)
print(reactive_counter)
# Output: <div class="counter-app" data-signals='{"count":0}'><p class="counter-display" data-text="$count"></p><button data-on-click="$count++">+</button><button data-on-click="$count--">-</button></div>
```

## Features

### Datastar Reactive Integration
- **Shorthand Attributes**: Clean syntax with `signals`, `bind`, `show`, `text`, `on_click`, etc.
- **Backward Compatible**: Full support for `ds_*` prefixed attributes
- **Event Handling**: Comprehensive `on_*` event attribute support
- **State Management**: Built-in signals, computed values, and effects
- **Performance Optimized**: Zero overhead for Datastar attribute processing

### FastHTML-Style Callable API
- **Chainable Syntax**: Support for `Div(cls="container")(children...)` patterns
- **Flexible Composition**: Mix traditional and callable styles seamlessly
- **Performance Optimized**: Minimal overhead (6-8%) for callable functionality
- **Smart Returns**: Empty tags return callable builders, populated tags return HTML

### Performance Optimizations
- **Memory Pooling**: Thread-local string pools for efficient memory reuse
- **Lock-free Caching**: Global caches for attribute and tag name transformations
- **String Interning**: Pre-allocated common HTML strings
- **SIMD Ready**: Optimized for modern CPU instruction sets
- **Stack Allocation**: SmallVec for small collections to avoid heap allocation

### Smart Type Conversion
- **Automatic Type Handling**: Booleans, integers, floats, strings
- **Framework Integration**: `__html__()`, `_repr_html_()`, `render()` method support
- **Attribute Mapping**: `cls` → `class`, `_for` → `for`, etc.
- **Error Handling**: Clear error messages for unsupported types

### HTML Features
- **All Standard Tags**: Complete HTML5 tag set with optimized generation
- **Automatic DOCTYPE**: Html tag includes `<!doctype html>` 
- **Custom Tags**: Dynamic tag creation with any tag name
- **Attribute Processing**: Smart attribute key transformation and value conversion

## API Features

RustyTags provides clean, intuitive APIs with multiple styles:

```python
# Traditional style
from rusty_tags import Div, P
content = Div(P("Text", _class="highlight"), cls="container")

# FastHTML-style callable chaining
content = Div(cls="container")(P("Text", _class="highlight"))

# Datastar reactive components
from rusty_tags.datastar import signals, reactive_class, DS

# Interactive todo item with Datastar
todo_item = Div(
    Input(type="checkbox", bind="$todo.completed"),
    Span(
        text="$todo.text",
        cls=reactive_class(completed="$todo.completed")
    ),
    Button("Delete", on_click=DS.delete("/todos/123")),
    signals={"todo": {"text": "Learn RustyTags", "completed": False}}
)

# Mixed approach for complex layouts
page = Div(id="app")(
    Header(cls="top-nav")(
        Nav(A("Home", href="/"), A("About", href="/about"))
    ),
    Main(cls="content")(
        H1("Welcome"),
        P("Content here")
    )
)
```

## Datastar Integration

RustyTags provides comprehensive Datastar support for building reactive web applications:

### Shorthand Attributes

All Datastar attributes support clean shorthand syntax:

```python
# Before (still supported)
Div(ds_signals={"count": 0}, ds_show="$visible", ds_on_click="$increment()")

# After (new shorthand)
Div(signals={"count": 0}, show="$visible", on_click="$increment()")
```

### Supported Datastar Attributes

**Core Attributes:**
- `signals` → `data-signals` - Component state management
- `bind` → `data-bind` - Two-way data binding
- `show` → `data-show` - Conditional visibility
- `text` → `data-text` - Dynamic text content
- `attrs` → `data-attrs` - Dynamic attributes
- `style` → `data-style` - Dynamic styling

**Event Attributes:**
- `on_click`, `on_hover`, `on_submit`, `on_focus`, `on_blur`
- `on_keydown`, `on_change`, `on_input`, `on_load`
- `on_intersect`, `on_interval`, `on_raf`, `on_resize`

**Advanced Attributes:**
- `effect` → `data-effect` - Side effects
- `computed` → `data-computed` - Computed values
- `ref` → `data-ref` - Element references
- `indicator` → `data-indicator` - Loading states
- `persist` → `data-persist` - State persistence
- `ignore` → `data-ignore` - Skip processing

### Complete Example

```python
from rusty_tags import Div, Button, Input, Span
from rusty_tags.datastar import signals, reactive_class, DS

# Interactive counter with Datastar
counter_app = Div(
    Span(text="$count", cls="display"),
    Div(
        Button("-", on_click="$count--"),
        Button("+", on_click="$count++"),
        Button("Reset", on_click=DS.set("count", 0)),
        cls="controls"
    ),
    Input(
        type="range",
        bind="$count",
        attrs={"min": "0", "max": "100"}
    ),
    signals={"count": 50},
    effect="console.log('Count changed:', $count)",
    cls="counter-app"
)
```

## Performance

RustyTags significantly outperforms pure Python HTML generation:
- 3-10x faster than equivalent Python code
- Optimized memory usage with pooling and interning
- Aggressive compiler optimizations in release builds

## Development Status

🚧 **Early Beta**: While the core functionality is stable and tested, this library is still in early development. Breaking changes may occur in future versions. Production use is not recommended yet.

### Current Features
- ✅ All HTML5 tags implemented
- ✅ Complete SVG tag support
- ✅ FastHTML-style callable API
- ✅ Complete Datastar integration with shorthand attributes
- ✅ Reactive state management and event handling
- ✅ Smart type conversion and attribute mapping
- ✅ Memory optimization and caching
- ✅ Custom tag support

### Planned Features
- 🔄 Template engine integration
- 🔄 Streaming HTML generation
- 🔄 PyPI package distribution

## Build from Source

```bash
# Development build
maturin develop

# Release build with optimizations
maturin build --release

# Run tests
python test_complex.py
python stress_test.py
```

## Requirements

- Python 3.8+
- Rust 1.70+
- Maturin for building

## License

[Add your license here]