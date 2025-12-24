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
- **⚛️ Powerful Datastar SDK**: Type-safe `Signal` system with Python operator overloading, conditional logic, validation, and HTTP actions
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

### Reactive Components with Datastar SDK

Inspired by the awesome [StarHTML](https://starhtml.com/), RustyTags Core now includes an even more powerfull **Datastar SDK** that provides a Pythonic API for building reactive components with type-safe signals and expressions:

#### Quick Start with Signals

```python
from rusty_tags import Div, Button, P, Input, Label, Span, Page
from rusty_tags.datastar import Signal, Signals

# Create signals using the Signals class
sigs = Signals(counter=0, user_name="John", is_active=True)

# Basic reactive counter with Signal methods
counter = Div(
    P(text=sigs.counter, cls="display"),
    Button("-", on_click=sigs.counter.sub(1)),
    Button("+", on_click=sigs.counter.add(1)),
    Button("Reset", on_click=sigs.counter.set(0)),
    cls="counter-widget",
    signals=sigs  # Signals object automatically converts to data-signals
)

# Create a complete page with Datastar CDN
page = Page(counter, title="Reactive App", datastar=True)
```

#### Signal Operations - Pythonic Reactive Expressions

The Signal SDK provides **full Python operator overloading** for building reactive JavaScript expressions:

**Arithmetic Operators:**
```python
from rusty_tags.datastar import Signals

numbers = Signals(x=10, y=3)
demo = Div(
    P(text="X: " + numbers.x),                           # → "X: ${$x}"
    P(text="Y: " + numbers.y),                           # → "Y: ${$y}"
    P(text="Sum: " + (numbers.x + numbers.y)),           # → "Sum: ${$x + $y}"
    P(text="Product: " + (numbers.x * numbers.y)),       # → "Product: ${$x * $y}"
    P(text="Division: " + (numbers.x / numbers.y)),      # → "Division: ${$x / $y}"
    P(text="Modulo: " + (numbers.x % numbers.y)),        # → "Modulo: ${$x % $y}"

    Button("X +5", on_click=numbers.x.add(5)),
    Button("Y +1", on_click=numbers.y.add(1)),
    signals=numbers
)
```

**Comparison & Logical Operators:**
```python
from rusty_tags.datastar import Signal

age = Signal("age", 25)
has_license = Signal("has_license", True)

validation = Div(
    P(text="Age: " + age),
    P(text="Has License: " + has_license),
    P(text="Is Adult (≥18): " + (age >= 18)),            # → ($age >= 18)
    P(text="Can Drive: " + ((age >= 18) & has_license)), # → (($age >= 18) && $has_license)
    P(text="Is Minor: " + (age < 18)),                   # → ($age < 18)
    P(text="No License: " + (~has_license)),             # → (!$has_license)

    Button("Age +1", on_click=age.add(1)),
    Button("Toggle License", on_click=has_license.toggle()),
    signals={"age": 25, "has_license": True}
)
```

**String Methods:**
```python
text = Signal("text", "Hello World")

string_demo = Div(
    Input(type="text", bind=text, placeholder="Enter text"),
    P(text="Original: " + text),
    P(text="Uppercase: " + text.upper()),                # → $text.toUpperCase()
    P(text="Lowercase: " + text.lower()),                # → $text.toLowerCase()
    P(text="Length: " + text.length),                    # → $text.length
    P(text="Contains 'Hello': " + text.contains("Hello")), # → $text.includes('Hello')
    signals={"text": "Hello World"}
)
```

**Array Methods:**
```python
items = Signal("items", ["Apple", "Banana"])
new_item = Signal("new_item", "Orange")

array_demo = Div(
    Input(type="text", bind=new_item, placeholder="New item"),
    # Chaining multiple actions with semicolons
    Button("Add Item", data_on_click=items.append(new_item).to_js() + "; " + new_item.set("").to_js()),
    Button("Remove Last", data_on_click=items.pop()),
    Button("Clear All", data_on_click=items.set([])),

    P("Count: ", Span(text=items.length)),               # → $items.length
    P("Items: ", Span(text=items.join(", "))),           # → $items.join(', ')
    P("Empty: ", Span(text=items.length == 0)),          # → $items.length === 0
    signals={"items": ["Apple", "Banana"], "new_item": ""}
)
```

**Math Methods:**
```python
value = Signal("value", 7.825)

math_demo = Div(
    P("Value: ", Span(text=value)),
    P("Rounded: ", Span(text=value.round())),            # → Math.round($value)
    P("Rounded (2 decimals): ", Span(text=value.round(2))),
    P("Absolute: ", Span(text=value.abs())),             # → Math.abs($value)
    P("Min with 5: ", Span(text=value.min(5))),          # → Math.min($value, 5)
    P("Max with 10: ", Span(text=value.max(10))),        # → Math.max($value, 10)
    P("Clamped (0-10): ", Span(text=value.clamp(0, 10))), # → Math.max(0, Math.min(10, $value))

    Button("+0.5", data_on_click=value.add(0.5)),
    Button("-0.5", data_on_click=value.sub(0.5)),
    signals={"value": 7.825}
)
```

#### Advanced Features - Conditionals, Patterns & Templates

**Conditional Expressions with `if_()`:**
```python
from rusty_tags.datastar import if_

score = Signal("score", 75)

conditional = Div(
    P("Score: ", Span(text=score)),
    # Simple ternary
    P("Grade: ", Span(text=if_(score >= 90, "A", "B"))),  # → ($score >= 90) ? 'A' : 'B'
    P("Status: ", text=if_(score >= 60, "Pass", "Fail")),

    # Nested conditionals
    P("Grade: ", Span(text=if_(score >= 90, "A",
                              if_(score >= 80, "B",
                                 if_(score >= 70, "C", "F"))))),

    # Conditional rendering with data-show
    Div(text=if_(score >= 90, "🎉 Excellent!",
                 if_(score >= 70, "👍 Good", "📚 Keep trying")),
        style="font-size: 2rem; text-align: center;"),

    Button("+10", data_on_click=score.add(10)),
    Button("-10", data_on_click=score.sub(10)),
    signals={"score": 75}
)
```

**Pattern Matching with `match()`:**
```python
from rusty_tags.datastar import match

status = Signals(status="idle")

status_demo = Div(
    P("Current Status: ", Span(text=status.status)),
    Div(
        text=match(
            status.status,
            idle="⏸️ Ready to start",
            loading="⏳ Processing...",
            success="✅ Completed!",
            error="❌ Failed!",
            default="❓ Unknown"
        ),
        style="font-size: 1.5rem; text-align: center; padding: 1rem;"
    ),

    Button("Idle", on_click=status.status.set("idle")),
    Button("Loading", on_click=status.status.set("loading")),
    Button("Success", on_click=status.status.set("success")),
    Button("Error", on_click=status.status.set("error")),
    signals=status
)
```

**Template Literals with `f()`:**
```python
from rusty_tags.datastar import f

user = Signals(first_name="John", last_name="Doe", age_val=25)

template = Div(
    Input(type="text", bind=user.first_name, placeholder="First name"),
    Input(type="text", bind=user.last_name, placeholder="Last name"),
    Input(type="number", bind=user.age_val, placeholder="Age"),

    P(text=f("Hello, {fn} {ln}!", fn=user.first_name, ln=user.last_name)),
    P(text=f("You are {age} years old.", age=user.age_val)),
    P(text=f("In 10 years, you'll be {future}.", future=user.age_val + 10)),
    signals=user
)
```

#### Dynamic CSS Classes

**Using `collect()` for conditional class joining:**
```python
from rusty_tags.datastar import collect

is_large = Signal("is_large", False)
is_bold = Signal("is_bold", False)
is_italic = Signal("is_italic", False)

collect_demo = Div(
    Label(Input(type="checkbox", bind=is_large), " Large"),
    Label(Input(type="checkbox", bind=is_bold), " Bold"),
    Label(Input(type="checkbox", bind=is_italic), " Italic"),

    P(
        "Styled Text",
        data_class=collect([
            (is_large, "large"),
            (is_bold, "bold"),
            (is_italic, "italic")
        ], join_with=" "),
        style="transition: all 0.3s;"
    ),
    signals={"is_large": False, "is_bold": False, "is_italic": False}
)
```

**Using `classes()` for Datastar's `data-class` (object literal):**
```python
from rusty_tags.datastar import classes

cls_large = Signal("cls_large", False)
cls_bold = Signal("cls_bold", False)
cls_blue = Signal("cls_blue", False)

classes_demo = Div(
    Label(Input(type="checkbox", bind=cls_large), " Large"),
    Label(Input(type="checkbox", bind=cls_bold), " Bold"),
    Label(Input(type="checkbox", bind=cls_blue), " Blue"),

    P(
        "Styled Text with data-class",
        data_class=classes(large=cls_large, bold=cls_bold, blue=cls_blue),
        style="transition: all 0.3s;"
    ),
    signals={"cls_large": False, "cls_bold": False, "cls_blue": False}
)
```

#### Form Validation with Logical Aggregation

**Using `all()` and `any()` for validation:**
```python
from rusty_tags.datastar import all, any, if_

form_name = Signal("form_name", "")
form_email = Signal("form_email", "")
form_age = Signal("form_age", 0)
form_agree = Signal("form_agree", False)

# Define validation rules
name_valid = form_name.length >= 3
email_valid = form_email.contains("@")
age_valid = form_age >= 18
can_submit = all(name_valid, email_valid, age_valid, form_agree)

registration_form = Div(
    # Name field with validation
    Div(
        Label("Name:"),
        Input(type="text", bind=form_name, placeholder="Enter name (min 3 chars)"),
        P("✓ Valid", data_show=name_valid, style="color: green;"),
        P("✗ Too short", data_show=~name_valid, style="color: red;")
    ),

    # Email field with validation
    Div(
        Label("Email:"),
        Input(type="email", bind=form_email, placeholder="Enter email"),
        P("✓ Valid", data_show=email_valid, style="color: green;"),
        P("✗ Invalid", data_show=~email_valid, style="color: red;")
    ),

    # Age field with validation
    Div(
        Label("Age:"),
        Input(type="number", bind=form_age, placeholder="Enter age"),
        P("✓ Valid", data_show=age_valid, style="color: green;"),
        P("✗ Must be 18+", data_show=~age_valid, style="color: red;")
    ),

    # Terms checkbox
    Div(
        Label(Input(type="checkbox", bind=form_agree), " I agree to terms")
    ),

    # Submit button - disabled until all valid
    Button(
        "Submit",
        data_disabled=~can_submit,
        data_attr_style=if_(can_submit, "opacity: 1; cursor: pointer;",
                                        "opacity: 0.5; cursor: not-allowed;")
    ),
    P(text=f("Hello, {name}!", name=form_name), data_show=can_submit),

    signals={"form_name": "", "form_email": "", "form_age": 0, "form_agree": False}
)
```

#### HTTP Actions and Server Communication

```python
from rusty_tags.datastar import post, get, put, patch, delete

# HTTP action helpers generate @action() expressions
api_demo = Div(
    Input(bind="$name", placeholder="Enter name"),
    Input(bind="$email", placeholder="Enter email"),

    # POST with reactive data (signals are automatically passed)
    Button(
        "Save User",
        on_click=post("/api/users", name="$name", email="$email"),
        cls="btn-primary"
    ),

    # GET request
    Button("Load Data", on_click=get("/api/data")),

    # PUT request
    Button("Update", on_click=put("/api/users/1", name="$name")),

    # PATCH request
    Button("Partial Update", on_click=patch("/api/users/1", email="$email")),

    # DELETE request
    Button("Delete", on_click=delete("/api/users/1")),

    Div(id="results"),
    signals={"name": "", "email": ""}
)
```

#### Property Access for Nested Data

```python
# Access nested object properties naturally
user = Signal("user", {"name": "Alice", "age": 30, "email": "alice@example.com"})

user_profile = Div(
    P("Name: ", Span(text=user.name)),         # → $user.name
    P("Age: ", Span(text=user.age)),           # → $user.age
    P("Email: ", Span(text=user.email)),       # → $user.email
    P("Adult: ", Span(text=(user.age >= 18))), # → ($user.age >= 18)

    Button("Birthday", on_click=user.age.add(1)),
    Button("Change Name", on_click=user.name.set("Bob")),
    signals={"user": {"name": "Alice", "age": 30, "email": "alice@example.com"}}
)
```

#### Keyboard Shortcuts with data-on-keys Plugin

RustyTags supports the [data-on-keys](https://mbolli.github.io/datastar-attribute-on-keys/) Datastar plugin for handling keyboard shortcuts:

```python
from rusty_tags import Div, Input, Button

# Global keyboard shortcuts (window-scoped)
shortcuts = Div(
    "Press Ctrl+K to search, Escape to close",
    on_keys_ctrl_k="openSearch()",           # → data-on-keys:ctrl-k
    on_keys_escape="closeModal()",           # → data-on-keys:escape
    on_keys_ctrl_s="saveDocument()",         # → data-on-keys:ctrl-s
    on_keys_f1="showHelp()",                 # → data-on-keys:f1
)

# Element-scoped shortcuts (requires focus)
search_input = Input(
    type="text",
    placeholder="Search...",
    on_keys_enter__el="submitSearch()",      # → data-on-keys:enter__el
    on_keys_escape__el="clearInput()",       # → data-on-keys:escape__el
)

# With timing modifiers
throttled = Div(
    on_keys_space__throttle_1s="$counter++",           # → data-on-keys:space__throttle.1s
    on_keys_ctrl_s__debounce_500ms="saveDocument()",   # → data-on-keys:ctrl-s__debounce.500ms
)

# Capture all keys
keylogger = Div(on_keys="console.log($event.key)")     # → data-on-keys
```

**Supported modifiers:**
- `__el` - Element-scoped (requires focus)
- `__stop` - Stop event propagation
- `__noprevent` - Allow default browser behavior
- `__throttle_Xs` - Throttle execution (e.g., `__throttle_1s`)
- `__debounce_Xms` - Debounce execution (e.g., `__debounce_500ms`)

**Complete Datastar SDK Features:**
- **Type-Safe Signals**: `Signal` and `Signals` classes with automatic type inference
- **Python Operators**: Full operator overloading (`+`, `-`, `*`, `/`, `%`, `==`, `!=`, `<`, `>`, `<=`, `>=`, `&`, `|`, `~`)
- **Signal Methods**: `.add()`, `.sub()`, `.set()`, `.toggle()`, `.append()`, `.pop()`, `.remove()`
- **String Methods**: `.upper()`, `.lower()`, `.strip()`, `.contains()`, `.length`
- **Math Methods**: `.round()`, `.abs()`, `.min()`, `.max()`, `.clamp()`
- **Array Methods**: `.append()`, `.prepend()`, `.pop()`, `.remove()`, `.join()`, `.slice()`, `.length`
- **Conditionals**: `if_()` for ternary expressions, `match()` for pattern matching
- **Templates**: `f()` for JavaScript template literals with embedded expressions
- **Dynamic Classes**: `collect()` for joining, `classes()` for object literals
- **Validation**: `all()` and `any()` for logical aggregation
- **HTTP Actions**: `get()`, `post()`, `put()`, `patch()`, `delete()` action generators
- **Keyboard Shortcuts**: `on_keys_*` for the data-on-keys plugin with modifier support
- **Raw JavaScript**: `js()` function for raw JavaScript when needed
- **Property Access**: Natural Python syntax for nested object properties

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
- **Utilities** (`utils.py`): Essential helpers (Page, page_template, show, AttrDict)
- **Datastar SDK** (`datastar.py`): Type-safe Signal system with Python operator overloading for reactive expressions
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
| **Datastar SDK** | ✅ **Enhanced** | Type-safe `Signal` & `Signals` with full Python operator overloading |
| `Page()` function | ✅ **Enhanced** | Simple templating with optional Datastar CDN |
| `page_template()`, `page_template()` | ✅ **Kept** | Essential templating functions |
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
# Core HTML generation + Datastar SDK (RustyTags)
from rusty_tags import Div, Page, page_template, Button, Input
from rusty_tags.datastar import Signal, Signals, if_, match, f, all, any
from rusty_tags.datastar import post, get, put, patch, delete  # HTTP actions

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

3. **Datastar SDK** (Completely rewritten with Signal system):
```python
# ✅ New Signal-based API in v0.6.0+
from rusty_tags.datastar import Signal, Signals, post, if_, all

# Create type-safe signals
sigs = Signals(name="", email="")

# Use Python operators for reactive expressions
form = Div(
    Input(bind=sigs.name, placeholder="Name"),
    Input(bind=sigs.email, placeholder="Email"),

    # New HTTP action helpers
    Button("Submit", on_click=post("/api/submit", name=sigs.name, email=sigs.email)),

    # Conditional logic with if_()
    P(text=if_(sigs.name.length >= 3, "Valid name", "Too short")),

    # Validation with all()
    Button("Save", data_disabled=~all(sigs.name.length >= 3, sigs.email.contains("@"))),

    signals=sigs
)
```

4. **Page Templates** (Minor changes):
```python
# ✅ Still works in RustyTags Core
from rusty_tags import Page, page_template

# Basic templating stays the same
page = Page(content, title="My App", datastar=True)
template = page_template("My App", datastar=True)

# ❌ Advanced CDN features moved to Nitro
# highlightjs=True, lucide=True parameters now in Nitro
```

### Why This Change?

- **Performance**: Core package is now 10x smaller and has zero dependencies
- **Flexibility**: Choose your complexity level - core HTML or full framework
- **Maintenance**: Clear separation of concerns between HTML generation and web framework
- **Adoption**: Lower barrier to entry for simple HTML generation needs

The new **Datastar SDK** in RustyTags Core provides a powerful, type-safe reactive system with Python operator overloading - giving you excellent reactive capabilities without requiring the full Nitro framework.

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