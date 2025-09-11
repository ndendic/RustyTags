# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RustyTags is a high-performance HTML generation library that provides a Rust-based Python extension for building HTML/SVG tags. It combines performance-critical Rust implementations with a comprehensive Python API for modern web development.

**Architecture:**
- **Rust Core** (`src/lib.rs`): High-performance HTML/SVG generation using PyO3 bindings with aggressive memory optimizations
- **Python Integration Layer** (`rusty_tags/`): Full-featured Python API with Datastar integration, utilities, and event system
- **Development Utilities** (`tests/`, `RustyMonsterUI/`): Comprehensive benchmarking suite and UI framework integrations

## Core Technologies

- **Rust**: PyO3 0.25.0 bindings with performance-critical dependencies (ahash, smallvec, itoa, ryu, dashmap, bumpalo)
- **Python**: Compatible with Python 3.12+, uses Maturin for build system
- **Core Dependencies**: blinker (events), datastar-py (reactive components), pydantic (validation)
- **Build System**: Maturin with aggressive release optimizations (LTO, single codegen unit, target-cpu=native)

## Key Components

### Rust Implementation (`src/lib.rs`)
- **Core Classes**:
  - `HtmlString`: Optimized HTML content container with encoding support and framework integration
  - `TagBuilder`: Callable syntax support for FastHTML-style chaining
  - `DatastarProcessor`: Advanced attribute processing with shorthand mapping and caching
- **Performance Features**:
  - Thread-local string pools and memory arenas for efficient allocation
  - Lock-free caching system with DashMap and thread-local fallbacks
  - String interning for common HTML/attribute names
  - SIMD-ready optimizations and aggressive compiler settings
- **HTML Generation**:
  - Complete HTML5 and SVG tag set with optimized macro-generated functions
  - Automatic mapping expansion (dicts in positional args become attributes)
  - Smart type conversion with `__html__`, `_repr_html_`, and `render()` method support
  - Custom tag creation with dynamic tag names

### Python Integration Layer (`rusty_tags/`)

#### Core Module (`__init__.py`)
- Comprehensive tag imports (HTML, SVG, and specialized tags)
- Core utilities (Page, create_template, show, AttrDict)
- Event system and client management exports

#### Datastar Integration (`datastar.py`)
- **DS Class**: Action generators for common Datastar patterns (get, post, put, delete, patch)
- **Signal Management**: Utility functions for signal manipulation (set, toggle, increment, append, remove)
- **Convenience Functions**: `signals()`, `reactive_class()`, conditional actions, and method chaining
- **Framework Integration**: Full datastar-py compatibility with SSE and ElementPatchMode support

#### Utilities (`utils.py`)
- **Page Templates**: `Page()` function for complete HTML document structure with Datastar integration
- **Template Decorators**: `create_template()` and `page_template()` for view function wrapping
- **Development Tools**: `show()` for Jupyter/IPython integration, `AttrDict` for flexible attribute access

#### Event System (`events.py`)
- **Enhanced Blinker Integration**: Custom Event class with async/sync handler support
- **Async Bridge**: Thread-safe bridging between sync generators and async consumers
- **Namespace Management**: Default namespace with protocol typing for better IDE support
- **Decorators**: `@on()` decorator for signal handlers, `emit()` and `emit_async()` functions

#### Client Management (`client.py`)
- **Client Class**: WebSocket/SSE client lifecycle management with automatic cleanup
- **Topic Subscription**: Flexible topic/sender filtering with queue-based message delivery
- **Connection Handling**: Context manager support with connect/disconnect lifecycle events

### Development Infrastructure

#### Testing (`tests/`)
- **Benchmarks**: Comprehensive performance testing suite comparing Rust vs Python implementations
- **Functionality Tests**: Validation of HTML generation, attribute processing, and Datastar integration
- **Stress Testing**: Memory usage and high-load scenarios

#### UI Frameworks (`RustyMonsterUI/`)
- Pre-built integrations with popular CSS frameworks (Daisy UI, Franken UI, Foundation)
- Component libraries and utility classes for rapid development

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

### Testing & Benchmarking
```bash
# Run comprehensive benchmark suite
python tests/benchmarks/run_all.py

# Memory usage analysis
python tests/benchmarks/memory_benchmark.py

# Realistic template performance
python tests/benchmarks/realistic_template_benchmark.py

# Stress testing
python tests/benchmarks/stress_test.py

# Specific functionality tests
python tests/test_datastar_basic.py
python tests/test_shorthand_attributes.py
python tests/test_boolean_attributes.py
```

## Performance Characteristics

The Rust implementation uses cutting-edge optimization strategies:

### Memory Management
- **Thread-Local Pools**: String and arena pooling to minimize allocations
- **Smart Capacity Calculation**: Pre-calculated string sizes to avoid reallocations
- **String Interning**: Common HTML strings are interned for memory efficiency
- **Stack Allocation**: SmallVec for small collections to avoid heap usage

### Caching Systems
- **Lock-Free Global Cache**: DashMap-based caching for attribute transformations
- **Thread-Local Cache**: Fast access with fallback to global cache
- **Datastar Attribute Cache**: Specialized caching for reactive attribute processing

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

### Full-Stack Integration
- **Page Templates**: Complete HTML document generation with head/body structure
- **Datastar Integration**: Built-in reactive component support with SSE
- **Event-Driven Architecture**: Blinker-based event system for scalable applications
- **Framework Compatibility**: Works with FastAPI, Flask, Django, and Starlette

## Package Configuration

### Current Version
- **Package Version**: 0.5.23
- **Python Compatibility**: 3.12+ (with broader compatibility in classifiers)
- **Build Backend**: Maturin with PyO3 extension module features

### Key Dependencies
- **Runtime**: blinker ≥1.9.0, datastar-py ≥0.6.5, pydantic ≥2.11.7
- **Build**: maturin ≥1.9,<2.0
- **Development**: Comprehensive tooling support (mypy, pyright configuration included)

## File Structure Notes

- **Core Implementation**: Single-file Rust implementation with comprehensive macro system
- **Python Modules**: Modular Python layer with clear separation of concerns
- **Development Tools**: Extensive benchmarking and testing infrastructure
- **UI Integrations**: Ready-to-use components for popular CSS frameworks
- **Documentation**: Inline documentation with type hints and comprehensive examples