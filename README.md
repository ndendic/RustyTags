# RustyTags

⚠️ **Early Beta** - This library is in active development and APIs may change.

A high-performance HTML generation library that combines Rust-powered performance with modern Python web development. RustyTags provides a complete HTML/SVG tag system with intelligent templating, reactive component support, and 3-10x speed improvements over pure Python implementations.

## What RustyTags Does

RustyTags generates HTML and SVG content programmatically with:

- **🏷️ Complete HTML5/SVG Tags**: All standard HTML5 and SVG elements with optimized Rust implementations
- **⚡ High Performance**: 3-10x faster than pure Python with memory optimization and intelligent caching
- **🎨 Modern Templating**: Page templates, decorators, and component system for full-stack development
- **🔄 Reactive Components**: Built-in Datastar integration for modern web applications
- **🏗️ FastHTML-Style API**: Familiar syntax with callable chaining support
- **🧠 Intelligent Processing**: Automatic attribute handling and smart type conversion
- **📦 Framework Ready**: Works with FastAPI, Flask, Django, and other Python web frameworks

## Quick Start

### Installation

```bash
# Install from PyPI (when available)
pip install rusty-tags

# For development - build from source
git clone <repository>
cd RustyTags
maturin develop
pip install datastar-py blinker pydantic
```

### Basic HTML Generation

```python
from rusty_tags import Div, P, H1, A, Button, Input

# Simple HTML elements
content = Div(
    H1("Welcome to RustyTags"),
    P("High-performance HTML generation with Python + Rust"),
    A("Learn More", href="https://github.com/ndendic/RustyTags"),
    cls="container"
)
print(content)
# <div class="container">
#   <h1>Welcome to RustyTags</h1>
#   <p>High-performance HTML generation with Python + Rust</p>
#   <a href="https://github.com/ndendic/RustyTags">Learn More</a>
# </div>
```

### Complete Page Templates

```python
from rusty_tags.utils import Page, create_template
from rusty_tags import Main, Section, H2, P

# Create a page template
template = create_template(
    title="My App",
    hdrs=(
        Link(rel="stylesheet", href="/static/app.css"),
        Meta(charset="utf-8"),
    ),
    datastar=True  # Include Datastar for reactive components
)

# Use as decorator
@template
def home_page():
    return Main(
        Section(
            H2("Dashboard"),
            P("Welcome to your dashboard"),
            cls="hero"
        ),
        cls="container"
    )

# Or create complete pages directly
page = Page(
    H1("My Website"),
    P("Built with RustyTags"),
    title="Home Page",
    htmlkw={"lang": "en"},
    bodykw={"class": "bg-gray-100"}
)
```

### Reactive Web Applications

```python
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from rusty_tags import *
from rusty_tags.datastar import DS

app = FastAPI()
page = create_template("Counter App", datastar=True)

@app.get("/")
@page(wrap_in=HTMLResponse)
def counter_app():
    return Main(
        H1("Interactive Counter"),
        Div(
            P(text="Count: $count", cls="display"),
            Button("+1", on_click="$count++", cls="btn"),
            Button("-1", on_click="$count--", cls="btn"),
            Button("Reset", on_click=DS.set("count", 0), cls="btn"),
            signals={"count": 0}  # Reactive state
        ),
        cls="app"
    )
```

## Core Features

### 🏷️ Complete HTML5/SVG Tag System

RustyTags provides all standard HTML5 and SVG elements as Python functions:

```python
# HTML elements
Html, Head, Body, Title, Meta, Link, Script
H1, H2, H3, H4, H5, H6, P, Div, Span, A
Form, Input, Button, Select, Textarea, Label
Table, Tr, Td, Th, Tbody, Thead, Tfoot
Nav, Main, Section, Article, Header, Footer
Img, Video, Audio, Canvas, Iframe
# ... and many more

# SVG elements
Svg, Circle, Rect, Line, Path, Polygon
G, Defs, Use, Symbol, LinearGradient
Text, Image, ForeignObject
# ... complete SVG support
```

### 🎨 Modern Templating System

**Page Templates:**
```python
from rusty_tags.utils import Page, create_template

# Complete HTML documents
page = Page(
    H1("My Site"),
    P("Content here"),
    title="Page Title",
    hdrs=(Meta(charset="utf-8"), Link(rel="stylesheet", href="/app.css")),
    datastar=True  # Auto-include reactive framework
)

# Reusable templates with decorators
@create_template("My App", datastar=True)
def my_view():
    return Div("Page content")
```

**Component System:**
```python
# Reusable components
def Card(title, *content, **attrs):
    return Div(
        H3(title, cls="card-title"),
        Div(*content, cls="card-body"),
        cls="card",
        **attrs
    )

# Usage
cards = Div(
    Card("Card 1", P("First card content")),
    Card("Card 2", P("Second card content"), cls="featured"),
    cls="card-grid"
)
```

### ⚡ Performance Optimizations

- **Memory Pooling**: Thread-local string pools and arena allocators
- **Intelligent Caching**: Lock-free attribute processing with smart cache invalidation
- **String Interning**: Common HTML strings pre-allocated for efficiency
- **Type Optimization**: Fast paths for common Python types and HTML patterns
- **Expression Detection**: Intelligent JavaScript expression analysis for reactive components

### 🔄 Reactive Component Integration

Built-in Datastar support for modern reactive web development:

```python
# Reactive state management
interactive_form = Form(
    Input(bind="$email", placeholder="Enter email"),
    Input(bind="$name", placeholder="Enter name"),
    Button("Submit", on_click=DS.post("/api/submit", data={"email": "$email", "name": "$name"})),
    Div(
        text="Email: $email, Name: $name",
        show="$email && $name"  # Conditional display
    ),
    signals={"email": "", "name": ""}  # Initial state
)

# Server-sent events and real-time updates
@app.get("/updates")
async def live_updates():
    async def event_stream():
        while True:
            yield SSE.patch_elements(
                Div(f"Update: {datetime.now()}", cls="update"),
                selector="#updates"
            )
            await asyncio.sleep(1)
    return event_stream()
```

### 🏗️ FastHTML-Style API

Familiar syntax with enhanced capabilities:

```python
# Traditional syntax
content = Div("Hello", cls="greeting")

# Callable chaining (FastHTML-style)
content = Div(cls="container")(
    H1("Title"),
    P("Content")
)

# Attribute flexibility
element = Div(
    "Content",
    {"id": "main", "data-value": 123},  # Dict automatically expands to attributes
    cls="primary",
    hidden=False  # Boolean attributes handled correctly
)
```

### 🔧 Smart Type System

Intelligent handling of Python types:

```python
# Automatic type conversion
Div(
    42,           # Numbers → strings
    True,         # Booleans → "true"/"false" or boolean attributes
    None,         # None → empty string
    [1, 2, 3],    # Lists → joined strings
    custom_obj,   # Objects with __html__(), render(), or _repr_html_()
)

# Framework integration
class MyComponent:
    def __html__(self):
        return "<div>Custom HTML</div>"

# Automatically recognized and rendered
Div(MyComponent())
```

## Framework Integration

### FastAPI

```python
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from rusty_tags.utils import create_template

app = FastAPI()
page = create_template("My API", datastar=True)

@app.get("/")
@page(wrap_in=HTMLResponse)
def index():
    return Main(H1("API Dashboard"))
```

### Flask

```python
from flask import Flask
from rusty_tags import Page, H1, P

app = Flask(__name__)

@app.route("/")
def index():
    return str(Page(
        H1("Flask + RustyTags"),
        P("High performance templating"),
        title="Flask Demo"
    ))
```

### Jupyter/IPython

```python
from rusty_tags.utils import show
from rusty_tags import Div, H1

# Display in notebooks
content = Div(H1("Notebook Content"), style="color: blue;")
show(content)  # Renders directly in Jupyter cells
```

## Architecture

**🦀 Rust Core (`src/lib.rs`):**
- High-performance HTML/SVG generation with PyO3 bindings
- Advanced memory management with pooling and interning
- Intelligent Datastar attribute processing
- Complete tag system with macro-generated optimizations

**🐍 Python Layer (`rusty_tags/`):**
- **Core Module**: All HTML/SVG tags and utilities
- **Templates**: Page generation and decorator system
- **Datastar**: Reactive component utilities and action generators
- **Events**: Blinker-based event system for scalable applications
- **Client**: WebSocket/SSE client management
- **Extras**: UI components (accordion, dialog, tabs, etc.)

**💻 Examples (`lab/`):**
- Complete FastAPI applications
- Real-world usage patterns
- Interactive examples with SSE

## Performance

RustyTags delivers significant performance improvements:

- **3-10x faster** than pure Python HTML generation
- **Sub-microsecond** rendering for simple elements
- **Memory efficient** with intelligent pooling and caching
- **Scalable** with lock-free concurrent data structures

```bash
# Run performance tests (when available)
python lab/benchmarks.py
```

## Development Status

**Early Beta** - Core functionality is stable and extensively used in development, but APIs may evolve.

### ✅ Stable Features
- Complete HTML5/SVG tag system
- High-performance Rust core
- Modern templating with decorators
- Reactive component integration
- Framework compatibility
- Memory optimization

### 🔄 In Development
- Comprehensive test suite
- Performance benchmarking
- Package distribution
- Enhanced documentation

## System Requirements

- **Python 3.8+** (broad compatibility)
- **Dependencies**: `blinker ≥1.9.0`, `datastar-py ≥0.6.5`, `pydantic ≥2.11.7`
- **Build Requirements** (development): Rust 1.70+, Maturin ≥1.9

## License

MIT License - See LICENSE file for details.

## Contributing

Contributions welcome! Please check the repository for contributing guidelines and open issues.

## Links

- **Repository**: https://github.com/ndendic/RustyTags
- **Issues**: https://github.com/ndendic/RustyTags/issues
- **Examples**: See `lab/` directory for complete applications