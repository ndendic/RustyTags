# RustyTags

⚠️ **Early Beta** - This library is in active development and APIs may change.

A high-performance HTML generation library that provides a Rust-based Python extension for building HTML/SVG tags. RustyTags offers significant speed improvements over pure Python HTML generation libraries through memory optimization and Rust-powered performance, featuring FastHTML-style syntax, comprehensive Datastar integration, and full-stack web development utilities.

## What RustyTags Does

RustyTags generates HTML and SVG content programmatically with:
- **Speed**: Rust-powered performance with memory optimization and caching
- **Modern Syntax**: FastHTML-style callable chaining with minimal performance overhead
- **Automatic Mapping Expansion**: Dictionaries automatically expand as tag attributes
- **Datastar Integration**: Complete reactive web development with shorthand attributes and server-sent events
- **Full-Stack Utilities**: Page templates, decorators, async backends, and event handling
- **Type Safety**: Smart type conversion for Python objects (booleans, numbers, strings)
- **Framework Integration**: Supports `__html__`, `_repr_html_`, and `render()` methods
- **Advanced Features**: Custom tags, attribute mapping, complete HTML5/SVG support

## Quick Start

### Installation

```bash
# Install from PyPI (recommended)
pip install rusty-tags

# For development/customization - build from source
git clone <repository>
cd rustyTags
maturin develop
```

### FastAPI Full-Stack Application Example

Here's a complete reactive web application demonstrating RustyTags' CQRS (Command Query Responsibility Segregation) capabilities with real-time server-sent events:

```python
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from rusty_tags import *
from rusty_tags.utils import create_template
from rusty_tags.datastar import DS, signals
from rusty_tags.backend import on_event, send_stream, process_queue, event
from datastar_py.fastapi import datastar_response, ReadSignals, ServerSentEventGenerator as SSE
from datastar_py.consts import ElementPatchMode
import asyncio

# Setup page template with UI framework (Franken UI in this example)
hdrs = (
    Link(rel='stylesheet', href='https://cdn.jsdelivr.net/npm/franken-ui@2.1.0/dist/css/core.min.css'),
    Script(src='https://cdn.jsdelivr.net/npm/franken-ui@2.1.0/dist/js/core.iife.js', type='module'),
)
page = create_template(hdrs=hdrs, htmlkw=dict(cls="bg-background"), bodykw=dict(cls="p-16"))

app = FastAPI()

# Reusable UI component with automatic mapping expansion
def Section(title, *content):
    return Div(
        H2(title, dict(cls="uk-h2 mb-4")),  # Mapping expansion in action!
        Div(*content, cls="border rounded-md p-4"),
        cls="my-4 max-w-md"
    )

# QUERY side: Main application page
@app.get("/")
@page(title="Reactive FastAPI App", wrap_in=HTMLResponse)
def index():
    return Main(
        Section("Server Event Updates Demo 🚀",
            Form(
                Input(
                    placeholder="Send message and press Enter",
                    type="text", 
                    bind="message", 
                    cls="uk-input"
                ),
                # COMMAND: Trigger server-side event processing
                on_submit=DS.get("/queries/user", contentType="form")
            ),
            Div(id="updates")  # Real-time updates container
        ),
        signals=signals(message=""),  # Client state
        on_load=DS.get("/updates")    # Connect to SSE stream
    )

# Event system setup for CQRS pattern
events_signal = event("events")
results_queue = asyncio.Queue()

# COMMAND side: Process user actions
@app.get("/queries/{sender}")
async def queries(sender: str, request: Request, signals: ReadSignals):
    """COMMAND: Trigger events and process user inputs"""
    send_stream(events_signal, sender, results_queue, 
                signals=signals, request=request)

# QUERY side: Real-time updates stream  
@app.get("/updates")
@datastar_response
async def event_stream(request: Request, signals: ReadSignals):
    """QUERY: SSE endpoint for real-time UI updates"""
    return process_queue(results_queue)

# Event handlers: Business logic with HTML responses
@on_event("events", sender="user") 
def notify(sender, request: Request, signals: dict | None):
    """Process user message and return HTML updates"""
    message = (signals or {}).get("message", "No message provided")
    
    # Execute client-side notification
    yield SSE.execute_script(f"UIkit.notification({{message: '{message}'}})")
    
    # Update UI with new content (using mapping expansion)
    yield SSE.patch_elements(
        Div(f"Server processed: {message}", dict(cls="text-lg font-bold mt-2")),
        selector="#updates", 
        mode=ElementPatchMode.APPEND
    )
    
    # Reset form state
    yield SSE.patch_signals({"message": ""})

# Additional event handlers can be added easily
@events_signal.connect
def log_messages(sender, request: Request, signals: dict | None):
    message = (signals or {}).get("message", "")
    print(f"📝 Message logged: {message}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Key Features Demonstrated:**
- **🆕 Mapping Expansion**: `dict(cls="...")` automatically becomes `cls="..."`
- **🏗️ CQRS Pattern**: Separate command (`/queries`) and query (`/updates`) endpoints
- **⚡ Real-time Updates**: Server-sent events with automatic HTML patching
- **🎨 Framework Integration**: Works seamlessly with any CSS framework
- **🔄 Reactive State**: Client-server state synchronization
- **📡 Event-Driven**: Scalable event handling with multiple subscribers

### Simple Usage Examples

```python
from rusty_tags import Div, P, A, Button, Input
from rusty_tags.datastar import signals, DS

# Basic HTML generation with mapping expansion
content = Div(
    P("Hello World", dict(cls="greeting", id="welcome")),
    Button("Click me", dict(type="button", disabled=False)),
    cls="container"
)
print(content)
# <div class="container"><p class="greeting" id="welcome">Hello World</p><button type="button">Click me</button></div>

# Reactive component with Datastar
counter = Div(
    P(text="$count", cls="display"),
    Button("+", on_click="$count++"),
    Button("-", on_click="$count--"),
    signals=signals(count=0)
)

# Advanced actions with DS utilities
form = Div(
    Input(bind="$email", placeholder="Email"),
    Button("Submit", on_click=DS.post("/api/submit", data="$email")),
    signals=signals(email="")
)
```

## Features

### 🆕 Automatic Mapping Expansion
RustyTags now automatically expands Python dictionaries passed as positional arguments into tag attributes:

```python
# Before: Manual unpacking required
Div("Content", **{"id": "main", "class": "container", "hidden": False})

# Now: Automatic expansion!
Div("Content", dict(id="main", class_="container", hidden=False))
# Output: <div id="main" class="container">Content</div>

# Works with any mapping type and combines with regular kwargs
attrs = {"data-value": 123, "title": "Tooltip"}
Div("Text", attrs, id="element", cls="active")
# Output: <div data-value="123" title="Tooltip" id="element" class="active">Text</div>
```

**Key Features:**
- **Automatic Detection**: Any dict in positional args is expanded as attributes
- **Type Preservation**: Booleans, numbers, strings handled correctly
- **Datastar Compatible**: `ds_` attributes and reactive `cls` dicts preserved
- **Performance Optimized**: Zero overhead expansion at the Rust level

### 🏗️ CQRS (Command Query Responsibility Segregation) Architecture

RustyTags enables clean separation of commands and queries for scalable reactive applications:

```python
# COMMAND side: Handle user actions
@app.post("/commands/user/{action}")
async def handle_command(action: str, request: Request, signals: ReadSignals):
    """Process user commands and trigger events"""
    send_stream(user_events, action, updates_queue, 
                signals=signals, request=request)

# QUERY side: Real-time UI updates
@app.get("/queries/updates") 
@datastar_response
async def query_updates(request: Request):
    """Stream UI updates based on processed events"""
    return process_queue(updates_queue)

# Event handlers: Business logic with HTML responses
@on_event("user_events", sender="create_todo")
def create_todo_handler(sender, signals: dict, **kwargs):
    # Business logic
    todo = create_todo(signals.get("todo_text"))
    
    # Return HTML update
    yield SSE.patch_elements(
        TodoItem(todo, dict(id=f"todo-{todo.id}")),
        selector="#todo-list",
        mode=ElementPatchMode.APPEND
    )
```

**CQRS Benefits:**
- **📝 Commands**: Separate endpoints for state-changing operations
- **📖 Queries**: Dedicated streams for real-time UI updates  
- **🔄 Event-Driven**: Loose coupling between commands and UI updates
- **🚀 Scalable**: Event handlers can be distributed across services
- **🧪 Testable**: Clear separation of concerns and business logic

### 🌟 Full-Stack Web Development Utilities

**Page Templates & Decorators:**
```python
from rusty_tags.utils import Page, create_template

# Production-ready page template
page = create_template(
    "My App",
    hdrs=(
        Meta(charset="utf-8"),
        Meta(name="viewport", content="width=device-width, initial-scale=1"),
        Link(rel="stylesheet", href="/static/app.css")
    ),
    datastar=True
)

@page(title="Dashboard")
def dashboard():
    return Main(
        Section("Analytics", dict(role="main", cls="dashboard")),
        Nav(A("Home", href="/"), A("Settings", href="/settings"))
    )
```

**Async Backend Integration:**
```python
from rusty_tags.backend import on_event, send_stream, process_queue
import asyncio

# Multi-subscriber event system
@on_event("user_action", sender="notification")
async def send_notification(sender, **data):
    yield Div(f"📬 {data['message']}", cls="notification")

@on_event("user_action", sender="analytics") 
async def track_analytics(sender, **data):
    # Log to analytics service
    print(f"📊 Event tracked: {data}")
```

### Datastar Reactive Integration
- **Shorthand Attributes**: Clean syntax with `signals`, `bind`, `show`, `text`, `on_click`, etc.
- **Action Generators**: Built-in `DS` class for common patterns (`DS.post()`, `DS.get()`, etc.)
- **Backward Compatible**: Full support for `ds_*` prefixed attributes
- **Event Handling**: Comprehensive `on_*` event attribute support
- **State Management**: Built-in signals, computed values, and effects
- **Server-Sent Events**: Full SSE support with `datastar-py` integration
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

## API Features & Architecture

RustyTags provides clean, intuitive APIs with multiple styles and full-stack capabilities:

```python
# Traditional style with mapping expansion
from rusty_tags import Div, P, Input, Button
content = Div(
    P("Text", dict(class_="highlight", data_id="p1")),
    cls="container"
)

# FastHTML-style callable chaining
content = Div(cls="container")(P("Text", _class="highlight"))

# Full-stack reactive application
from rusty_tags.datastar import signals, reactive_class, DS
from rusty_tags.backend import on_event
from rusty_tags.utils import Page, create_template

# Backend event handler
@on_event("todo_updated")
async def handle_todo_update(sender, **data):
    # Return HTML update
    yield Div(f"Todo {data['id']} updated!", cls="notification")

# Interactive todo application
def todo_app():
    return Page(
        Div(
            Input(
                type="text", 
                bind="$newTodo", 
                placeholder="Add todo...",
                on_keyup="event.key === 'Enter' && $addTodo()"
            ),
            Button("Add", on_click="$addTodo()"),
            Div(
                # Dynamic todo list
                show="$todos.length > 0",
                effect="console.log('Todos updated:', $todos)"
            ),
            signals=signals(
                newTodo="",
                todos=[]
            ),
            cls="todo-app"
        ),
        title="Todo App",
        datastar=True
    )

# Page template decorator
template = create_template("My App", datastar=True)

@template.page("Dashboard")  
def dashboard():
    return Div("Welcome to dashboard!", dict(role="main", cls="dashboard"))
```

### 📦 **Module Structure**

**Core Engine (`rusty_tags.*`):**
- High-performance Rust-based HTML/SVG tag generation
- Automatic mapping expansion and type conversion
- FastHTML-style callable syntax support

**Datastar Integration (`rusty_tags.datastar`):**
- Shorthand attribute support and action generators
- Server-sent events with `datastar-py` integration
- Reactive state management utilities

**Full-Stack Utilities (`rusty_tags.utils`):**
- Page templates and layout management  
- Function decorators for view composition
- IPython/Jupyter integration with `show()`

**Async Backend (`rusty_tags.backend`):**
- Event-driven architecture with Blinker signals
- Async SSE streaming and queue processing
- Concurrent event handler execution

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

### Current Features ✅
- **Core Engine**: All HTML5 and SVG tags with Rust performance
- **Mapping Expansion**: Automatic dict-to-attributes expansion
- **Callable API**: FastHTML-style chainable syntax
- **Datastar Integration**: Complete reactive web development stack
- **Full-Stack Utilities**: Page templates, decorators, async backends
- **Event System**: Blinker-based event handling with async support
- **Server-Sent Events**: Real-time updates with datastar-py integration
- **Type Safety**: Smart type conversion and attribute mapping
- **Performance**: Memory optimization, caching, and Rust-powered speed
- **Custom Tags**: Dynamic tag creation and framework integration

### Planned Features 🔄
- **Template Engine**: Jinja2/Mako integration for server-side rendering  
- **Streaming HTML**: Chunked response generation for large documents
- **PyPI Distribution**: Official package releases and versioning
- **Developer Tools**: Hot reload, debugging utilities, and performance profilers

### Dependencies & Integration

**Core Dependencies:**
- `datastar-py`: Official Datastar Python SDK for SSE and attributes
- `blinker`: Signal/event system for backend event handling
- `maturin`: Rust-Python build system for performance-critical code

**Framework Integration:**
- **FastAPI**: Native async support with SSE streaming
- **Flask**: Compatible with Jinja2 templates and request contexts
- **Django**: Template integration and ORM query rendering
- **IPython/Jupyter**: Built-in `show()` function for notebook display
- **Starlette**: ASGI compatibility with streaming responses

## Development & Customization

### Build from Source

```bash
# Clone repository for customization
git clone <repository>
cd rustyTags

# Development build  
maturin develop

# Release build with optimizations
maturin build --release

# Run tests and benchmarks
python test_complex.py
python stress_test.py
python benchmark_comparison.py
```

### Running the FastAPI Example

```bash
# Install RustyTags and FastAPI dependencies
pip install rusty-tags fastapi uvicorn datastar-py

# Run the example application
python lab/FastapiApp.py

# Open browser to http://localhost:8000
# Try sending messages to see real-time CQRS in action!
```

## Requirements

**Runtime:**
- Python 3.8+
- `datastar-py` (official Datastar Python SDK)
- `blinker` (signal/event system)

**Development/Building:**
- Rust 1.70+
- Maturin for building Rust extensions
- Optional: IPython/Jupyter for `show()` functionality

## License

MIT