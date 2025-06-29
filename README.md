# RustyTags

⚠️ **Early Beta** - This library is in active development and APIs may change.

A high-performance HTML generation library that provides a Rust-based Python extension for building HTML/SVG tags. RustyTags is designed as a performance-optimized alternative to pure Python HTML generation libraries like Air, offering significant speed improvements while maintaining API compatibility.

## What RustyTags Does

RustyTags generates HTML and SVG content programmatically with:
- **Speed**: Rust-powered performance with memory optimization and caching
- **Compatibility**: Drop-in replacement for Air library with same API
- **Type Safety**: Smart type conversion for Python objects (booleans, numbers, strings)
- **Framework Integration**: Supports `__html__`, `_repr_html_`, and `render()` methods
- **Advanced Features**: Custom tags, automatic head/body separation, attribute mapping

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
from rusty_tags import Div, P, A, Html, Script, CustomTag, Svg, Circle, Text

# Simple HTML generation
content = Div(
    P("Hello World", cls="greeting"),
    A("Click here", href="https://example.com", target="_blank")
)
print(content)
# Output: <div><p class="greeting">Hello World</p><a href="https://example.com" target="_blank">Click here</a></div>

# Complete HTML document with automatic head/body separation
page = Html(
    Script("console.log('Hello');"),  # Goes to <head>
    Div("Main content"),              # Goes to <body>
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
- **Head/Body Separation**: Automatic placement of head-specific content
- **Custom Tags**: Dynamic tag creation with any tag name
- **Attribute Processing**: Smart attribute key transformation and value conversion

## API Compatibility

RustyTags maintains compatibility with the Air library:

```python
# Air-style usage works unchanged
from rusty_tags import Div, P
content = Div(P("Text", _class="highlight"), cls="container")
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
- ✅ Smart type conversion and attribute mapping
- ✅ Memory optimization and caching
- ✅ Air library compatibility
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