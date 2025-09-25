# RustyTags Decoupling Migration Plan

## Overview
Split RustyTags into two distinct packages to separate concerns and improve maintainability:

1. **`rusty-tags` (Core)** - Pure HTML generation library (performance-focused)
2. **`nitro` (Web Framework)** - Full-stack web framework built on rusty-tags-core

## Current Architecture Analysis

### RustyTags Current Components

**Core Rust Layer** (`src/lib.rs`):
- High-performance HTML/SVG tag generation with PyO3 bindings (2,000+ lines)
- Memory optimization with pooling, caching, and string interning
- Datastar integration with intelligent JavaScript expression detection
- Complete HTML5/SVG tag system with macro-generated optimizations

**Python Integration Layer**:
- **Core utilities** (`utils.py`): Page templates, decorators, CDN management (140 lines)
- **Reactive components** (`datastar.py`): Datastar action generators, signal management (383 lines)
- **Event system** (`events.py`): Enhanced Blinker integration with async support (185 lines)
- **Client management** (`client.py`): WebSocket/SSE client lifecycle (125 lines)
- **UI components** (`rusty_tags/xtras/`): Pre-built components (accordion, dialog, tabs, etc.)
- **Framework integration** (`starlette.py`, examples in `lab/`)

**Examples/Applications** (`lab/`):
- FastAPI demo applications
- Component documentation apps
- Real-world usage examples

## Decoupling Strategy

### Phase 1: Refactor RustyTags (Core Package)
**Goal**: Create minimal, high-performance HTML generation library

#### Keep in RustyTags Core:
- [x] **Rust implementation** (`src/lib.rs`) - ALL performance-critical HTML generation
- [x] **Core Python bindings** - All HTML/SVG tag functions (H1, Div, Svg, Circle, etc.)
- [x] **Core types** (`HtmlString`, `TagBuilder`, `CustomTag`)
- [x] **Minimal utilities** (`utils.py` - stripped down version):
  - `AttrDict` class
  - `show()` function for Jupyter integration
  - Simple `Page()` function (only datastar CDN dependancy)
- [x] **Basic Datastar support** (keep in Rust core for performance):
  - Keep current rust implementation intact
  - JavaScript expression detection
  - Datastar attribute processing
  - Core reactive attribute handling

#### Remove from RustyTags Core:
- [ ] Advanced template system (`create_template()`, `page_template()`)
- [ ] CDN management and HEADER_URLS
- [ ] Enhanced Page() with highlightjs/lucide integration
- [ ] Event system (`events.py`) → Move to Nitro
- [ ] Client management (`client.py`) → Move to Nitro
- [ ] Datastar Python utilities (`datastar.py`) → Move to Nitro
- [ ] UI components (`xtras/`) → Move to Nitro
- [ ] Framework integrations → Move to Nitro
- [ ] Example applications (`lab/`) → Move to Nitro

### Phase 2: Create Nitro (Web Framework Package)
**Goal**: Full-featured web development framework built on RustyTags

#### Nitro Package Structure:
```
nitro/
├── src/                    # No Rust code - pure Python
├── nitro/
│   ├── __init__.py         # Re-export rusty-tags + framework features
│   ├── templates.py        # Advanced templating (create_template, page_template)
│   ├── datastar.py         # Moved from rusty-tags
│   ├── events.py           # Moved from rusty-tags
│   ├── client.py           # Moved from rusty-tags
│   ├── framework/          # Framework-specific integrations
│   │   ├── fastapi.py
│   │   ├── flask.py
│   │   └── django.py
│   └── components/         # UI component library (moved from xtras)
│       ├── __init__.py
│       ├── accordion.py
│       ├── dialog.py
│       ├── tabs.py
│       ├── inputs.py
│       └── ...
├── examples/               # Moved from lab/
├── docs/                   # Framework documentation
└── tests/
```

#### Nitro Dependencies:
```toml
[project]
dependencies = [
    "rusty-tags>=0.6.0",     # Core HTML generation
    "datastar-py>=0.6.5",   # Reactive components
    "blinker>=1.9.0",        # Event system
    "pydantic>=2.11.7",      # Validation
]
```

## Migration Tasks

### Phase 1: RustyTags Core Cleanup (Current Repo)

#### 1. Update `rusty_tags/__init__.py`:
- [ ] Remove imports: `datastar`, `events`, `client`
- [ ] Keep only: core tags, `HtmlString`, `TagBuilder`, `Page` (simple), `show`, `AttrDict`
- [ ] Update `__all__` to reflect core-only exports

#### 2. Simplify `rusty_tags/utils.py`:
- [ ] Remove `create_template()` and `page_template()` functions
- [ ] Remove `HEADER_URLS` and CDN management
- [ ] Simplify `Page()` function - remove `highlightjs`, `lucide`, `datastar` parameters
- [ ] Keep only: `AttrDict`, `show()`, basic `Page()`

#### 3. Remove files:
- [ ] Delete `rusty_tags/datastar.py`
- [ ] Delete `rusty_tags/events.py`
- [ ] Delete `rusty_tags/client.py`
- [ ] Delete `rusty_tags/starlette.py`
- [ ] Delete `rusty_tags/xtras/` directory
- [ ] Delete `lab/` directory

#### 4. Update `pyproject.toml`:
- [ ] Remove dependencies: `blinker`, `datastar-py`
- [ ] Keep only: `pydantic` (for minimal validation)
- [ ] Update description to focus on core HTML generation
- [ ] Version bump to 0.6.0 (breaking changes)

#### 5. Update documentation:
- [ ] Update README.md to focus on core HTML generation
- [ ] Remove framework integration examples
- [ ] Add note about Nitro for advanced features
- [ ] Update CLAUDE.md to reflect core-only scope

### Phase 2: Nitro Setup (Parallel Repo)

#### 1. Initial setup (in `/home/ndendic/WebDev/nitro/`):
- [x] Repository already created as duplicate
- [ ] Remove Rust components (keep only Python code)
- [ ] Update package name throughout codebase

#### 2. Create Nitro package structure:
- [ ] Rename `rusty_tags/` to `nitro/`
- [ ] Create `nitro/__init__.py` with full imports:
  ```python
  # Re-export everything from rusty-tags core
  from rusty_tags import *

  # Add framework-specific imports
  from .templates import create_template, page_template
  from .datastar import *
  from .events import *
  from .client import *
  from .components import *
  ```

#### 3. Move and refactor components:
- [ ] Move `rusty_tags/datastar.py` → `nitro/datastar.py`
- [ ] Move `rusty_tags/events.py` → `nitro/events.py`
- [ ] Move `rusty_tags/client.py` → `nitro/client.py`
- [ ] Move `rusty_tags/xtras/` → `nitro/components/`
- [ ] Move `lab/` → `examples/`

#### 4. Create `nitro/templates.py`:
- [ ] Move advanced templating from `utils.py`:
  - `create_template()`
  - `page_template()`
  - Enhanced `Page()` with CDN management
  - `HEADER_URLS` dictionary

#### 5. Update imports throughout:
- [ ] Update all internal imports to use `nitro.*`
- [ ] Update component imports to use `from rusty_tags import Div, H1, etc.`
- [ ] Fix circular import issues

#### 6. Update `pyproject.toml`:
- [ ] Change package name to `nitro`
- [ ] Add `rusty-tags>=0.6.0` as primary dependency
- [ ] Keep framework dependencies: `datastar-py`, `blinker`, `pydantic`
- [ ] Update description for web framework

### Phase 3: Documentation and Testing

#### 1. Update documentation:
- [ ] Create Nitro README.md focusing on web framework features
- [ ] Update examples to show both packages
- [ ] Create migration guide for existing users
- [ ] Update CLAUDE.md for Nitro-specific guidance

#### 2. Testing:
- [ ] Test RustyTags core independently
- [ ] Test Nitro framework with RustyTags dependency
- [ ] Verify all examples work with new structure
- [ ] Performance testing to ensure core performance maintained

#### 3. Migration guide for users:
```python
# Before (monolithic)
from rusty_tags import Div, create_template, DS, Client

# After (decoupled)
from rusty_tags import Div        # Core HTML generation
from nitro import create_template, DS, Client  # Framework features
```

## Benefits of This Approach

### For RustyTags Core:
- **Minimal dependencies**: Only essential Python packages
- **Faster installation**: No framework dependencies
- **Better performance**: No overhead from unused features
- **Framework agnostic**: Works with any Python web framework
- **Easier maintenance**: Focused scope

### For Nitro Framework:
- **Full feature set**: All advanced web development tools
- **Clear dependencies**: Built on proven core
- **Rapid development**: Rich component library and utilities
- **Modern patterns**: Reactive components, SSE, async support
- **Framework integration**: Ready-to-use with FastAPI, Flask, etc.

## Timeline Estimate

- **Phase 1** (RustyTags cleanup): 1-2 days
- **Phase 2** (Nitro setup): 2-3 days
- **Phase 3** (Documentation/testing): 1-2 days
- **Total**: 4-7 days for complete migration

## Version Strategy

- **RustyTags**: Bump to v0.6.0 (breaking changes, core-only)
- **Nitro**: Start at v0.1.0 (new package)
- **Compatibility**: Nitro v0.1.x requires RustyTags v0.6.x

## Risk Mitigation

1. **Breaking changes**: Clear migration guide and version communication
2. **Dependency management**: Semantic versioning and clear compatibility matrix
3. **Feature parity**: Ensure all current functionality available in combined packages
4. **Performance regression**: Comprehensive benchmarking before/after
5. **User confusion**: Clear documentation about which package to use when

## Success Criteria

- [x] RustyTags core package builds and installs independently
- [ ] Nitro package builds with RustyTags as dependency
- [ ] All existing functionality preserved across both packages
- [ ] Performance maintained or improved
- [ ] Clear documentation for both packages
- [ ] Successful migration of existing users
- [ ] Both packages published to PyPI

## Current Status

- [x] Analysis complete
- [x] Nitro repository created (duplicate)
- [ ] RustyTags core cleanup (Phase 1)
- [ ] Nitro package setup (Phase 2)
- [ ] Documentation and testing (Phase 3)