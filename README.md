# RustyTags

⚠️ **Early Beta** - This library is in active development and APIs may change.

A high-performance HTML generation library that provides a Rust-based Python extension for building HTML/SVG tags. RustyTags offers significant speed improvements over pure Python HTML generation libraries through memory optimization and Rust-powered performance, now featuring FastHTML-style callable syntax for modern web development.

## What RustyTags Does

RustyTags generates HTML and SVG content programmatically with:
- **Speed**: Rust-powered performance with memory optimization and caching
- **Modern Syntax**: FastHTML-style callable chaining with minimal performance overhead
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
```

## Features

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