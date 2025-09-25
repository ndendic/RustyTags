# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RustyTags Core is a minimal, high-performance HTML generation library focused on blazing-fast HTML and SVG creation. This core package provides only essential HTML generation capabilities with zero framework dependencies. For advanced web framework features, see the separate "Nitro" package.

**Architecture:**
- **Rust Core** (`src/lib.rs`): High-performance HTML/SVG generation using PyO3 bindings with advanced memory optimizations
- **Python Integration Layer** (`rusty_tags/`): Minimal Python API with core tag functions and essential utilities

## Core Technologies

- **Rust**: PyO3 0.25.0 bindings with performance dependencies (ahash, smallvec, itoa, ryu, dashmap, bumpalo)
- **Python**: Compatible with Python 3.8+, uses Maturin for build system
- **Core Dependencies**: None (zero runtime dependencies for maximum compatibility)
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
- Core utilities (Page, show, AttrDict)
- Essential functionality only - no framework dependencies

#### Utilities (`utils.py`)
- **Page Function**: Simple `Page()` function for basic HTML document structure
- **Development Tools**: `show()` for Jupyter/IPython integration, `AttrDict` for flexible attribute access
- **Minimal Dependencies**: No external dependencies beyond Python standard library

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
# No runtime dependencies required - core library only
# For development, optionally install IPython for show() function
pip install ipython  # Optional, only for Jupyter integration
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

## Core HTML Generation Features

### Automatic Mapping Expansion
```python
# Dictionary arguments automatically become attributes
Div("Content", {"id": "main", "class": "container", "hidden": False})
# Renders: <div id="main" class="container">Content</div>
```

### FastHTML-Style Callable Syntax
```python
# Chainable syntax support
content = Div(cls="container")(P("Hello"), Button("Click"))
# Supports both traditional and callable patterns
```

### Smart Type Conversion
The Rust core automatically handles Python types:
- Numbers, booleans, None, lists
- Objects with `__html__()`, `_repr_html_()`, or `render()` methods
- Dictionary expansion to attributes
- Safe HTML escaping by default

## Package Configuration

### Current Version
- **Package Version**: 0.6.0 (core-only release)
- **Python Compatibility**: 3.8+ (broad compatibility across Python versions)
- **Build Backend**: Maturin with PyO3 extension module features

### Key Dependencies
- **Runtime**: None (zero dependencies for maximum compatibility)
- **Build**: maturin ≥1.9,<2.0
- **Development**: mypy, pyright configuration included
- **Optional**: IPython for `show()` function in Jupyter notebooks

## File Structure Notes

- **Core Implementation**: Single-file Rust implementation (`src/lib.rs`) with comprehensive macro system
- **Python Modules**: Minimal Python layer with essential utilities only
- **Extension Module**: Pre-compiled Rust extension provides all HTML/SVG tag functions
- **Clean Structure**: Only essential files remain for maximum simplicity

## Framework Integration

- **Framework Agnostic**: Works with FastAPI, Flask, Django, or any Python web framework
- **Jupyter/IPython**: Built-in `show()` function for rich notebook display
- **Drop-in Replacement**: Can replace any HTML generation library
- **Zero Dependencies**: No runtime dependencies ensure maximum compatibility

## Performance Notes

The Rust implementation provides significant performance improvements over pure Python HTML generation through:
- Memory pooling and arena allocation
- Lock-free concurrent data structures
- Intelligent caching systems
- SIMD-ready optimizations
- String interning and capacity pre-calculation

Performance testing requires setting up proper benchmarking infrastructure.