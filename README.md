# RustyTags

A high-performance HTML generation library with Rust-based Python extension.

## Quick Start

```bash
# Install dependencies and build
pip install rusty-tags
# Use in Python
from rusty_tags import Div, P, A
html = Div(P("Hello"), A("World", href="https://example.com"))
print(html)
```

## Features

- High-performance Rust core with Python bindings
- Optimized HTML/SVG tag generation

## Build

```bash
maturin build --release
```