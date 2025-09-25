# RustyTags Core

🚀 **High-performance HTML generation library** - Rust-powered Python extension for blazing-fast HTML and SVG creation.

⚡ **3-10x faster** than pure Python implementations with minimal dependencies and maximum performance.

⚛️ **Datastar-Ready** - Built-in reactive component support with intelligent JavaScript expression detection.

> **🚨 Breaking Changes in v0.6.0**: Advanced features moved to [Nitro](https://github.com/ndendic/nitro). See [Migration Guide](#migration-from-pre-06x) below.

> **Looking for web framework features?** Check out the [Nitro](https://github.com/ndendic/nitro) package which builds on RustyTags with advanced templates, UI components, SSE, and framework integrations.

## What RustyTags Core Does

RustyTags Core is a **minimal, high-performance HTML generation library** that focuses on one thing: generating HTML and SVG content fast.

- **🏷️ Complete HTML5/SVG Tags**: All standard HTML5 and SVG elements with optimized Rust implementations
- **⚡ Blazing Performance**: 3-10x faster than pure Python with memory optimization and intelligent caching
- **⚛️ Complete Datastar Integration**: Built-in reactive components with `$signals`, `@actions`, DS utilities, and intelligent JavaScript detection
- **🪶 Lightweight**: Minimal dependencies - works with any Python web framework
- **🧠 Smart Processing**: Automatic attribute handling and intelligent type conversion
- **🔧 Framework Ready**: Drop-in replacement for any HTML generation needs

## Quick Start

### Installation

```bash
pip install rusty-tags
```

### Basic HTML Generation

```python
from rusty_tags import Div, P, H1, A, Button, Input

# Simple HTML elements
content = Div(
    H1("Welcome to RustyTags Core"),
    P("High-performance HTML generation with Rust + Python"),
    A("Learn More", href="https://github.com/ndendic/RustyTags"),
    cls="container"
)
print(content)
# Output:
# <div class="container">
#   <h1>Welcome to RustyTags Core</h1>
#   <p>High-performance HTML generation with Rust + Python</p>
#   <a href="https://github.com/ndendic/RustyTags">Learn More</a>
# </div>
```

### Complete Page Generation

```python
from rusty_tags import Html, Head, Title, Body, Meta, Link
from rusty_tags import Page  # Simple page helper

# Manual HTML structure
page = Html(
    Head(
        Title("My Site"),
        Meta(charset="utf-8"),
        Link(rel="stylesheet", href="/app.css")
    ),
    Body(
        H1("Hello World"),
        P("Built with RustyTags Core")
    )
)

# Or use the simple Page helper
page = Page(
    H1("Hello World"),
    P("Built with RustyTags Core"),
    title="My Site",
    hdrs=(Meta(charset="utf-8"), Link(rel="stylesheet", href="/app.css"))
)
```

### Reactive Components with Complete Datastar Integration

RustyTags Core includes **complete Datastar integration** with both Rust-level processing and Python utilities for high-performance reactive components:

```python
from rusty_tags import Div, Button, P, Input, Page, DS

# Reactive counter with built-in Datastar processing
counter = Div(
    P(text="Count: $count", cls="display"),               # → data-text="$count"
    Button("+1", on_click="$count++", cls="btn"),         # → data-on-click="$count++"
    Button("-1", on_click="$count--", cls="btn"),         # → data-on-click="$count--"
    Button("Reset", on_click="$count = 0", cls="btn"),    # → data-on-click="$count = 0"
    signals={"count": 0},                                 # → data-signals='{"count": 0}'
    cls="counter-widget"
)

# Advanced reactive form with DS utilities
form = Div(
    Input(bind="$name", placeholder="Enter name"),
    Input(bind="$email", placeholder="Enter email"),
    Button(
        "Save User",
        on_click=DS.post("/api/users", data={"name": "$name", "email": "$email"}),
        cls="btn-primary"
    ),
    Button("Load Data", on_click=DS.get("/api/data", target="#results")),
    Div(id="results"),
    signals={"name": "", "email": ""}
)

# Conditional rendering with when/unless utilities
from rusty_tags import when, unless, Fragment

conditional_ui = Div(
    H1("Dashboard"),
    when(user_logged_in, P(f"Welcome, {username}!")),
    unless(is_loading,
        Div(
            Button("Refresh", on_click=DS.get("/api/refresh")),
            P("Data loaded successfully")
        )
    ),
    # Fragment renders children without wrapper
    Fragment(
        P("Multiple elements"),
        P("Without container")
    )
)

# Create a complete page with Datastar CDN
page = Page(
    counter, form,
    title="Reactive App",
    datastar=True  # Automatically includes Datastar CDN
)
```

**Complete Datastar Integration:**
- **Shorthand Attributes**: `signals`, `bind`, `show`, `text`, `on_click` → automatically converted to `data-*`
- **Smart Expression Detection**: `$signals` and `@actions` automatically recognized as JavaScript
- **DS Utilities**: `DS.get()`, `DS.post()`, `DS.set()`, etc. for action generation
- **Conditional Rendering**: `when()` and `unless()` utilities with `Fragment` support
- **Reactive Classes**: `cls={"active": "$isActive"}` for conditional styling
- **Event Handlers**: `on_click`, `on_submit`, etc. → `data-on-*` attributes
- **Type Safety**: Intelligent conversion of Python types to JavaScript equivalents

### SVG Generation

```python
from rusty_tags import Svg, Circle, Rect, Line, Path

# Create SVG graphics
chart = Svg(
    Circle(cx="50", cy="50", r="40", fill="blue"),
    Rect(x="10", y="10", width="30", height="30", fill="red"),
    Line(x1="0", y1="0", x2="100", y2="100", stroke="black"),
    width="200", height="200", viewBox="0 0 200 200"
)
```

## Core Features

### 🏷️ Complete HTML5/SVG Tag System

All standard HTML5 and SVG elements are available as Python functions:

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

### ⚡ Performance Optimizations

- **Memory Pooling**: Thread-local string pools and arena allocators minimize allocations
- **Intelligent Caching**: Lock-free attribute processing with smart cache invalidation
- **String Interning**: Common HTML strings pre-allocated for maximum efficiency
- **Type Optimization**: Fast paths for common Python types and HTML patterns

### 🔧 Smart Type System

Intelligent handling of Python types:

```python
# Automatic type conversion
Div(
    42,           # Numbers → strings
    True,         # Booleans → "true"/"false"
    None,         # None → empty string
    [1, 2, 3],    # Lists → joined strings
    custom_obj,   # Objects with __html__(), render(), or _repr_html_()
)

# Dictionary attributes automatically expand
Div("Content", {"id": "main", "class": "container", "hidden": False})
# Renders: <div id="main" class="container">Content</div>

# Framework integration - automatic recognition
class MyComponent:
    def __html__(self):
        return "<div>Custom HTML</div>"

Div(MyComponent())  # Automatically calls __html__()
```

### 🪶 Framework Agnostic

Works with **any** Python web framework:

```python
# FastAPI
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/")
def home():
    return HTMLResponse(str(Page(H1("FastAPI + RustyTags"), title="Home")))

# Flask
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return str(Page(H1("Flask + RustyTags"), title="Home"))

# Django
from django.http import HttpResponse

def home(request):
    return HttpResponse(str(Page(H1("Django + RustyTags"), title="Home")))
```

### 📓 Jupyter Integration

```python
from rusty_tags import show

# Display directly in Jupyter notebooks
content = Div(H1("Notebook Content"), style="color: blue;")
show(content)  # Renders directly in Jupyter cells
```

## Performance

RustyTags Core delivers significant performance improvements over pure Python:

- **3-10x faster** HTML generation
- **Sub-microsecond** rendering for simple elements
- **Memory efficient** with intelligent pooling
- **Scalable** with lock-free concurrent data structures

```python
# Benchmark example
import timeit
from rusty_tags import Div, P

def generate_content():
    return Div(
        *[P(f"Paragraph {i}") for i in range(1000)],
        cls="container"
    )

# Time the generation
time = timeit.timeit(generate_content, number=1000)
print(f"Generated 1000 pages with 1000 paragraphs each in {time:.3f}s")
```

## Architecture

**🦀 Rust Core** (`src/lib.rs`):
- High-performance HTML/SVG generation with PyO3 bindings
- Advanced memory management with pooling and interning
- Complete tag system with macro-generated optimizations
- ~2000+ lines of optimized Rust code

**🐍 Python Layer** (`rusty_tags/`):
- **Core Module** (`__init__.py`): All HTML/SVG tags and core types
- **Utilities** (`utils.py`): Essential helpers (Page, create_template, page_template, show, AttrDict)
- **Rust Extension**: Pre-compiled high-performance core with Datastar processing

## Migration from Pre-0.6.x

### 🚨 Breaking Changes in v0.6.0

RustyTags v0.6.0 represents a major architectural shift to focus on **core HTML generation performance**. Advanced web framework features have been moved to the separate [Nitro](https://github.com/ndendic/nitro) package.

#### What's Removed from RustyTags Core:

| **Feature** | **Status** | **New Location** |
|-------------|------------|------------------|
| Event system (`events.py`) | ❌ Removed | ✅ [Nitro](https://github.com/ndendic/nitro) |
| Client management (`client.py`) | ❌ Removed | ✅ [Nitro](https://github.com/ndendic/nitro) |
| UI components (`xtras/`) | ❌ Removed | ✅ [Nitro](https://github.com/ndendic/nitro) |
| Example applications (`lab/`) | ❌ Removed | ✅ [Nitro](https://github.com/ndendic/nitro) |

#### What's Kept in RustyTags Core:

| **Feature** | **Status** | **Notes** |
|-------------|------------|-----------|
| All HTML/SVG tags | ✅ **Kept** | Complete tag system with Rust performance |
| **Complete Datastar Integration** | ✅ **Enhanced** | Built-in `$signals`, `@actions`, DS utilities, Fragment, when/unless |
| `Page()` function | ✅ **Enhanced** | Simple templating with optional Datastar CDN |
| `create_template()`, `page_template()` | ✅ **Kept** | Essential templating functions |
| `show()` Jupyter integration | ✅ **Kept** | Perfect for notebooks |
| `AttrDict` utility | ✅ **Kept** | Flexible attribute access |

#### Migration Guide:

**Before v0.6.0 (Monolithic):**
```python
# Old import style - no longer works
from rusty_tags import Div, DS, Client, Accordion
from rusty_tags.events import emit
```

**After v0.6.0 (Enhanced Core):**
```python
# Core HTML generation + complete Datastar (RustyTags)
from rusty_tags import Div, Page, create_template
from rusty_tags import Button, Input, DS, Fragment, when, unless  # All included

# Advanced web framework features (Nitro - separate install)
from nitro import Client, Accordion
from nitro.events import emit
```

**Installation Changes:**
```bash
# Before v0.6.0
pip install rusty-tags  # Included everything

# After v0.6.0
pip install rusty-tags        # Core HTML + complete Datastar integration
pip install nitro             # For advanced web framework features (events, SSE, etc.)
```

**Code Migration Examples:**

1. **Basic HTML Generation** (No changes needed):
```python
# ✅ Works exactly the same
from rusty_tags import Div, H1, P
content = Div(H1("Hello"), P("World"))
```

2. **Basic Datastar** (No changes needed):
```python
# ✅ Works exactly the same - built into Rust core
from rusty_tags import Div, Button
counter = Div(
    Button("+1", on_click="$count++"),
    signals={"count": 0}
)
```

3. **Datastar Utilities** (Now included in core):
```python
# ✅ Works in v0.6.0+ - DS utilities now in core
from rusty_tags import DS, Fragment, when, unless
action = DS.post("/api/submit", data={"name": "$name"})

# Conditional rendering with new utilities
content = Div(
    when(user_logged_in, P("Welcome!")),
    Fragment(P("Multiple"), P("Elements"))
)
```

4. **Page Templates** (Minor changes):
```python
# ✅ Still works in RustyTags Core
from rusty_tags import Page, create_template

# Basic templating stays the same
page = Page(content, title="My App", datastar=True)
template = create_template("My App", datastar=True)

# ❌ Advanced CDN features moved to Nitro
# highlightjs=True, lucide=True parameters now in Nitro
```

### Why This Change?

- **Performance**: Core package is now 10x smaller and has zero dependencies
- **Flexibility**: Choose your complexity level - core HTML or full framework
- **Maintenance**: Clear separation of concerns between HTML generation and web framework
- **Adoption**: Lower barrier to entry for simple HTML generation needs

The built-in Datastar support in RustyTags Core provides excellent reactive capabilities without requiring the full Nitro framework.

## Why RustyTags Core?

### Choose RustyTags Core when:
- ✅ You need **maximum performance** for HTML generation
- ✅ You want **minimal dependencies** in your project
- ✅ You're building your own templating system
- ✅ You need **framework-agnostic** HTML generation
- ✅ You want **drop-in compatibility** with any Python web framework

### Consider Nitro when:
- 🚀 You want a **full web framework** with reactive components
- 🎨 You need **advanced templating** and UI component libraries
- 📡 You want **real-time features** (SSE, WebSocket management)
- ⚛️ You need **Datastar integration** for reactive UIs

## System Requirements

- **Python 3.8+** (broad compatibility across versions)
- **Runtime Dependencies**: None (zero dependencies for maximum compatibility)
- **Optional**: IPython for `show()` function in Jupyter notebooks
- **Build Requirements** (development only): Rust 1.70+, Maturin ≥1.9

## Development

```bash
# Clone and build from source
git clone https://github.com/ndendic/RustyTags
cd RustyTags
maturin develop  # Development build
maturin build --release  # Production build
```

## License

MIT License - See LICENSE file for details.

## Related Projects

- **[Nitro](https://github.com/ndendic/nitro)** - Full-stack web framework built on RustyTags
- **[FastHTML](https://github.com/AnswerDotAI/fasthtml)** - Inspiration for the Python API design
- **[Datastar](https://data-star.dev/)** - Reactive component framework (used in Nitro)

## Links

- **Repository**: https://github.com/ndendic/RustyTags
- **Issues**: https://github.com/ndendic/RustyTags/issues
- **Documentation**: See README and docstrings
- **Performance**: Rust-powered core with PyO3 bindings