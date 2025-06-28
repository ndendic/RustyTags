# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RustyTags is a high-performance HTML generation library that provides a Rust-based Python extension for building HTML/SVG tags. It's designed as a performance-optimized alternative to pure Python HTML generation libraries like Air.

**Architecture:**
- **Rust Core** (`src/lib.rs`): High-performance HTML generation using PyO3 bindings with aggressive optimizations
- **Python Compatibility Layer** (`air/`): Python-compatible interface for backward compatibility with Air library
- **Benchmarking Suite**: Performance comparison tools between Rust and Python implementations

## Core Technologies

- **Rust**: PyO3 for Python bindings, optimized for maximum performance
- **Python**: Compatible with Python 3.8+, uses Maturin for build system
- **Dependencies**: Jinja2, Mako (Python), ahash, smallvec, itoa, ryu (Rust)

## Key Components

### Rust Implementation (`src/lib.rs`)
- `HtmlString`: Core HTML content container with optimized memory layout
- `Tag`: Backward-compatible class for existing Air code
- HTML tag functions: Optimized functions for all standard HTML tags (A, Div, P, etc.)
- `Html`: Special tag with automatic DOCTYPE and head/body separation
- Performance optimizations: String arenas, SmallVec for stack allocation, fast attribute mapping

### Python Layer (`air/`)
- `tags.py`: Pure Python implementation with Air-compatible API
- `svg.py`: SVG-specific tags using CaseTag for proper casing
- Backward compatibility with existing Air-based codebases

## Development Commands

### Building
```bash
# Build the Rust extension
maturin develop

# Build for release with optimizations
maturin build --release
```

### Testing
```bash
# Run benchmarks comparing Rust vs Python performance
python benchmark_comparison.py

# Run stress tests
python stress_test.py
python stress_test_fixed.py

# Run complex functionality tests
python test_complex.py

# Template performance testing
python template_benchmark.py
```

### Development Environment
```bash
# Install in development mode
pip install -e .

# Install with UV package manager (if available)
uv pip install -e .
```

## Performance Characteristics

The Rust implementation uses several optimization strategies:
- Pre-calculated string capacities to avoid reallocations
- Fast attribute key mapping with common case optimization
- Stack allocation for small collections using SmallVec
- Specialized integer/float to string conversion (itoa/ryu)
- String arenas for efficient concatenation
- Aggressive compiler optimizations in release builds

## API Compatibility

The library maintains backward compatibility with Air's API:
- Same tag names and attribute handling
- Support for `cls`, `_class`, `_for` attribute mapping
- Compatible `Html` tag with automatic head/body separation
- SVG tags with proper case sensitivity

## File Structure Notes

- Notebook files (`*.ipynb`) contain development experiments and benchmarking
- Test files demonstrate both performance characteristics and functionality
- Configuration uses aggressive optimization settings for maximum performance
- Build system uses Maturin for seamless Rust-Python integration