# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RustyTags is a high-performance HTML generation library that combines Rust-powered performance with a comprehensive Python API for modern web development. The project provides FastHTML-style syntax, automatic mapping expansion, and complete Datastar integration for building reactive web applications.

**Architecture:**
- **Rust Core** (`src/lib.rs`): High-performance HTML/SVG generation using PyO3 bindings with advanced memory optimizations
- **Python Integration Layer** (`rusty_tags/`): Full-featured Python API with Datastar integration, event system, and utilities
- **Example Applications** (`lab/`): FastAPI demonstration applications showing real-world usage patterns
- **UI Components** (`rusty_tags/xtras/`): Pre-built components for common UI patterns

## Core Technologies

- **Rust**: PyO3 0.25.0 bindings with performance dependencies (ahash, smallvec, itoa, ryu, dashmap, bumpalo)
- **Python**: Compatible with Python 3.8+, uses Maturin for build system
- **Core Dependencies**: blinker (events), datastar-py (reactive components), pydantic (validation)
- **Build System**: Maturin with aggressive release optimizations

## Key Components

### Rust Implementation (`src/lib.rs`)
- **Core Classes**:
  - `HtmlString`: Optimized HTML content container with encoding support
  - `TagBuilder`: Callable syntax support for FastHTML-style chaining
  - `DatastarProcessor`: Advanced attribute processing with intelligent JavaScript expression detection
- **Performance Features**:
  - Thread-local string pools and memory arenas for efficient allocation
  - Lock-free caching system with DashMap and thread-local fallbacks
  - String interning for common HTML/attribute names
  - Memory-optimized attribute processing with comprehensive caching
- **HTML Generation**:
  - Complete HTML5 and SVG tag set with macro-generated functions
  - Automatic mapping expansion (dictionaries in positional args become attributes)
  - Smart type conversion with `__html__`, `_repr_html_`, and `render()` method support
  - Intelligent Datastar expression detection for reactive components

### Python Integration Layer (`rusty_tags/`)

#### Core Module (`__init__.py`)
- Comprehensive tag imports (HTML, SVG, and all specialized tags)
- Core utilities (Page, create_template, show, AttrDict)
- Event system and client management exports
- Datastar integration utilities

#### Datastar Integration (`datastar.py`)
- **DS Class**: Action generators for common Datastar patterns (get, post, put, delete, patch, set, toggle)
- **Signal Management**: Utility functions for signal manipulation and state management
- **Method Chaining**: Support for chaining multiple Datastar actions
- **Framework Integration**: Full datastar-py compatibility with SSE and ElementPatchMode support

#### Utilities (`utils.py`)
- **Page Templates**: `Page()` function for complete HTML document structure
- **Template Decorators**: `create_template()` and `page_template()` for view function wrapping
- **Development Tools**: `show()` for Jupyter/IPython integration, `AttrDict` for flexible attribute access
- **Header Management**: Pre-configured CDN URLs for common libraries (highlight.js, etc.)

#### Event System (`events.py`)
- **Enhanced Blinker Integration**: Custom Event class with async/sync handler support
- **Async Bridge**: Thread-safe bridging between sync generators and async consumers
- **Namespace Management**: Default namespace with protocol typing for IDE support
- **Decorators**: `@on()` decorator for signal handlers, `emit()` and `emit_async()` functions

#### Client Management (`client.py`)
- **Client Class**: WebSocket/SSE client lifecycle management with automatic cleanup
- **Topic Subscription**: Flexible topic/sender filtering with queue-based message delivery
- **Connection Handling**: Context manager support with connect/disconnect lifecycle events

#### UI Components (`xtras/`)
- **Accordion**: Collapsible content components
- **Dialog**: Modal dialog implementations
- **Icons**: Icon management utilities
- **Tabs**: Tabbed interface components
- **Input Components**: Enhanced form input elements
- **Code Blocks**: Syntax-highlighted code display
- **Sheets**: Side panel/sheet components
- **Sidebar**: Navigation sidebar components

### Example Applications (`lab/`)
- **FastAPI Integration**: Complete FastAPI applications demonstrating real-world usage
- **Basic Examples**: Simple integration patterns
- **Advanced Examples**: Complex reactive applications with SSE
- **Static Assets**: Supporting CSS and JavaScript files

## Development Commands

### Building
```bash
# Development build with fast compilation
maturin develop

# Release build with maximum optimizations
maturin build --release

# Install in development mode
pip install -e .
```

### Dependencies
```bash
# Install runtime dependencies
pip install blinker>=1.9.0 datastar-py>=0.6.5 pydantic>=2.11.7

# For development examples
pip install fastapi uvicorn
```

## Performance Characteristics

The Rust implementation uses advanced optimization strategies:

### Memory Management
- **Thread-Local Pools**: String and arena pooling to minimize allocations
- **Smart Capacity Calculation**: Pre-calculated string sizes to avoid reallocations
- **String Interning**: Common HTML strings are interned for memory efficiency
- **Arena Allocation**: Bumpalo allocators for batch operations

### Caching Systems
- **Lock-Free Global Cache**: DashMap-based caching for attribute transformations
- **Thread-Local Cache**: Fast access with fallback to global cache
- **Datastar Attribute Cache**: Specialized caching for reactive attribute processing
- **Expression Detection**: Intelligent caching of JavaScript expression analysis

### Type System Integration
- **Smart Type Detection**: Automatic conversion of Python types to appropriate HTML representations
- **Framework Method Support**: Native support for `__html__()`, `_repr_html_()`, and `render()` methods
- **Boolean Attribute Handling**: HTML5-compliant boolean attribute processing

## Modern Web Development Features

### Automatic Mapping Expansion
```python
# Dictionary arguments automatically become attributes
Div("Content", {"id": "main", "class": "container", "hidden": False})
# Renders: <div id="main" class="container">Content</div>
```

### Datastar Shorthand Attributes
```python
# Clean shorthand syntax for reactive components
Div(
    signals={"count": 0},
    show="$visible",
    on_click="$increment()",
    cls={"active": "$isActive"}
)
# Automatically converts to proper data-* attributes
```

### FastHTML-Style Callable Syntax
```python
# Chainable syntax support
content = Div(cls="container")(P("Hello"), Button("Click"))
# Supports both traditional and callable patterns
```

### Intelligent Expression Detection
The Rust core automatically detects JavaScript expressions in Datastar attributes:
- `$signal` references
- `@action` calls
- Function calls with `()`
- Logical operators (`&&`, `||`, `===`, `!==`)
- Object property access (`.length`, `.push()`)
- Browser globals (`window.`, `document.`)

## Package Configuration

### Current Version
- **Package Version**: 0.5.26
- **Python Compatibility**: 3.8+ (broad compatibility across Python versions)
- **Build Backend**: Maturin with PyO3 extension module features

### Key Dependencies
- **Runtime**: blinker ≥1.9.0, datastar-py ≥0.6.5, pydantic ≥2.11.7
- **Build**: maturin ≥1.9,<2.0
- **Development**: mypy, pyright configuration included

## File Structure Notes

- **Core Implementation**: Single-file Rust implementation (`src/lib.rs`) with comprehensive macro system
- **Python Modules**: Modular Python layer with clear separation of concerns
- **Example Applications**: Real-world FastAPI applications in `lab/` directory
- **UI Components**: Extensible component library in `rusty_tags/xtras/`
- **Extension Module**: Pre-compiled Rust extension at `rusty_tags/rusty_tags.cpython-312-x86_64-linux-gnu.so`

## Known Issues

### Import System
- **Current Issue**: Circular import dependencies prevent full package import
- **Workaround**: Import directly from `rusty_tags.rusty_tags` for core functionality
- **Status**: Needs refactoring of Python module imports

### Development Infrastructure
- **Missing**: Comprehensive test suite and benchmarking infrastructure
- **Priority**: High priority for production readiness

## Framework Integration

- **FastAPI**: Native async/await support with SSE streaming (examples in `lab/`)
- **Jupyter/IPython**: Built-in `show()` function for rich notebook display
- **Datastar**: Full reactive component support with shorthand attribute processing
- **CSS Frameworks**: Ready-to-use integrations through `xtras/` components

## Performance Notes

The Rust implementation provides significant performance improvements over pure Python HTML generation through:
- Memory pooling and arena allocation
- Lock-free concurrent data structures
- Intelligent caching systems
- SIMD-ready optimizations
- String interning and capacity pre-calculation

Performance testing requires setting up proper benchmarking infrastructure.