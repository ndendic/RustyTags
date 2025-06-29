# RustyTags

A high-performance HTML generation library with Rust-based Python extension.

## Quick Start

```bash
# Install dependencies and build
pip install
# Use in Python
from rusty_tags import Div, P, A
html = Div(P("Hello"), A("World", href="https://example.com"))
print(html)
```

## Features

- High-performance Rust core with Python bindings
- Compatible with existing Air library codebases
- Optimized HTML/SVG tag generation
- Backward compatibility layer included

## Build

```bash
maturin build --release
```