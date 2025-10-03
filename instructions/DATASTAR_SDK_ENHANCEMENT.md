# RustyTags Datastar SDK Enhancement Specification

## Overview

This document specifies the enhancement of RustyTags' Datastar integration by adopting StarHTML's pythonic expression system while maintaining explicit signal definition and preparing for future Rust optimization.

## Current State Analysis

### RustyTags Datastar SDK (389 lines)
**Architecture**: Static method-based string generation via `DS` class
- ✅ Simple, explicit, easy to understand
- ✅ Integration with `datastar_py` (SSE, attribute_generator)
- ✅ Explicit target/data parameters in HTTP methods
- ❌ No type safety or validation
- ❌ Limited composability and expression building
- ❌ String-based signal references prone to typos
- ❌ Repetitive code across HTTP methods

### StarHTML Datastar SDK (827 lines)
**Architecture**: Expression-based system with operator overloading
- ✅ Type-safe `Signal` class with validation
- ✅ Pythonic operators for natural expression building
- ✅ Rich methods: string/math/array operations
- ✅ Pattern matching: `match()`, `switch()`, `collect()`
- ✅ Template literals and composable expressions
- ✅ Automatic signal tracking via `process_datastar_kwargs()`
- ❌ No SSE integration
- ❌ Steeper learning curve

## Design Goals

### 1. Explicit Signal Definition
**Decision**: Keep explicit signal declaration, avoid inline walrus operator pattern

```python
# We want this (explicit)
signals = Signals(counter=0, user={"name": ""})
Div(
    data_signals=signals,
    P("Count: ", data_text=signals.counter),
    Button("+", data_on_click=signals.counter.add(1))
)

# Not this (implicit with walrus)
Div(
    (counter := Signal("counter", 0)),  # ❌ Too magical
    P("Count: ", data_text=counter)
)
```

### 2. Hybrid Signals/Signal Architecture
**Design**: `Signals(AttrDict)` enhanced to create `Signal` objects internally

```python
class Signals(AttrDict):
    """Enhanced signal container with dual access patterns."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._signal_objects = {}
        for key, value in kwargs.items():
            # Create Signal object for each entry
            self._signal_objects[key] = Signal(key, value)
    
    def __getattr__(self, key):
        """Dot notation returns Signal objects for expressions."""
        return self._signal_objects.get(key)
    
    def __getitem__(self, key):
        """Dict access returns raw values."""
        return super().__getitem__(key)
    
    def to_dict(self):
        """Return plain dict for data-signals attribute."""
        return dict(self)
```

**Usage patterns**:
```python
signals = Signals(counter=0, items=[])

# Signal object for expressions
signals.counter.add(1)           # → "$counter++"
signals.counter == 5             # → "$counter === 5"
signals.items.append("new")      # → "$items.push('new')"

# Raw value access
signals['counter']               # → 0
signals.to_dict()               # → {"counter": 0, "items": []}
```

### 3. Maintain Backward Compatibility
- Keep existing `DS` class methods
- Preserve `datastar_py` integrations (SSE, attribute_generator)
- Add new features alongside, not replacing

## Implementation Plan

### Phase 1: Core Expression System (Python)
**Goal**: Implement foundational classes for expression building

#### 1.1 Base Classes
```python
# Abstract base for all expressions
class Expr(ABC):
    @abstractmethod
    def to_js(self) -> str:
        """Compile to JavaScript string."""
        pass
    
    def __str__(self) -> str:
        return self.to_js()
```

#### 1.2 Expression Types
- `_JSLiteral`: Safe Python value → JS literal
- `_JSRaw`: Raw JavaScript code passthrough
- `BinaryOp`: Binary operations (a + b, x > y)
- `UnaryOp`: Unary operations (!x)
- `Conditional`: Ternary expressions (a ? b : c)
- `Assignment`: Assignment expressions (x = y)
- `MethodCall`: Method invocations (obj.method(args))
- `PropertyAccess`: Property access (obj.prop)
- `IndexAccess`: Array/object indexing (obj[index])
- `TemplateLiteral`: Template string interpolation

#### 1.3 Signal Class
```python
class Signal(Expr):
    """Type-safe signal with validation and methods."""
    
    def __init__(self, name: str, initial: Any = None, 
                 type_: type | None = None,
                 namespace: str | None = None):
        self._name = name
        self._initial = initial
        self._namespace = namespace
        self._is_computed = isinstance(initial, Expr)
        self.type_ = type_ or self._infer_type(initial)
        self._validate_name()
    
    @property
    def value(self):
        """Public access to initial value."""
        return self._initial
    
    def to_js(self) -> str:
        return f"${self.full_name}"
    
    def to_dict(self) -> dict[str, Any]:
        if self._is_computed:
            return {}
        return {self.full_name: self._initial}
```

#### 1.4 Operator Overloading
Add to `Expr` base class:
- Logical: `__and__`, `__or__`, `__invert__` (&&, ||, !)
- Comparison: `__eq__`, `__ne__`, `__lt__`, `__le__`, `__gt__`, `__ge__`
- Arithmetic: `__add__`, `__sub__`, `__mul__`, `__truediv__`, `__mod__`
- Property/Index: `__getattr__`, `__getitem__`

### Phase 2: Rich Methods & Helpers
**Goal**: Add convenience methods and helper functions

#### 2.1 Signal Methods
```python
# Mutation methods
.set(value)              # Assignment
.add(amount)             # Increment (++ for 1)
.sub(amount)             # Decrement (-- for 1)
.toggle(*values)         # Toggle or cycle values

# String methods
.lower()                 # toLowerCase()
.upper()                 # toUpperCase()
.strip()                 # trim()
.contains(text)          # includes()

# Math methods
.round(digits=0)         # Math.round()
.abs()                   # Math.abs()
.min(limit)              # Math.min()
.max(limit)              # Math.max()
.clamp(min_val, max_val) # Bounded value

# Array methods
.append(*items)          # push()
.prepend(*items)         # unshift()
.pop()                   # pop()
.remove(index)           # splice()
.join(separator)         # join()
.slice(start, end)       # slice()

# Control flow
.if_(true_val, false_val) # Ternary
.then(action)            # if (condition) { action }
```

#### 2.2 Helper Functions
```python
# Pattern matching
match(subject, **patterns)    # Match/case style
switch(cases, default)        # If/elif/else chain
collect(cases, join_with)     # Combine conditional values

# Logical aggregation
all(*signals)                 # All truthy
any(*signals)                 # Any truthy

# Template & raw JS
js(code)                      # Raw JavaScript
f(template_str, **kwargs)     # Template literal
value(v)                      # Safe literal
regex(pattern)                # Regex literal

# JavaScript globals
console, Math, JSON, Object, Array, Date, Number, String, Boolean
```

#### 2.3 Enhanced DS Class
Keep existing methods, add expression support:
```python
class DS:
    # Keep existing static methods
    @staticmethod
    def get(url: str, **params) -> str:
        """Existing implementation."""
        ...
    
    # Add expression-aware variants
    @staticmethod
    def get_expr(url: str | Expr, **params) -> _JSRaw:
        """Expression-aware variant."""
        url_js = url.to_js() if isinstance(url, Expr) else f"'{url}'"
        # ... build expression
```

### Phase 3: Event Modifiers & Advanced Features
**Goal**: Complete feature parity with StarHTML

#### 3.1 Event Modifiers
```python
# Add .with_() method to Expr
expr.with_(debounce=300, prevent=True)
# Returns: (expr, {"debounce": 300, "prevent": True})

# Modifier suffix builder
def _build_modifier_suffix(modifiers: dict) -> str:
    """data-on-click__debounce__300ms"""
    ...
```

#### 3.2 Keyword Processing
```python
def process_datastar_kwargs(kwargs: dict) -> tuple[dict, set[Signal]]:
    """
    Convert Pythonic kwargs to Datastar attributes.
    - Normalizes keys (data_on_click → data-on-click)
    - Processes expressions and collects Signal references
    - Handles modifiers
    - Returns processed attrs and found signals
    """
    ...
```

### Phase 4: Integration & Documentation
**Goal**: Seamless integration with existing RustyTags

#### 4.1 Module Structure
```
rusty_tags/
├── __init__.py           # Core exports
├── datastar.py           # Enhanced SDK
│   ├── DS class          # Existing + enhanced
│   ├── Signals class     # Enhanced AttrDict
│   ├── Signal class      # New
│   ├── Expr classes      # New
│   └── Helpers           # New
└── utils.py              # AttrDict, Page, show
```

#### 4.2 Exports
```python
__all__ = [
    # Existing
    'DS', 'signals', 'Signals', 'reactive_class',
    'attribute_generator', 'SSE', 'ElementPatchMode', 'EventType',
    
    # New
    'Signal', 'Expr',
    'js', 'value', 'f', 'regex',
    'match', 'switch', 'collect',
    'all', 'any',
    'console', 'Math', 'JSON', 'Object', 'Array', 'Date',
    'process_datastar_kwargs', 'to_js_value'
]
```

## Performance Strategy

### Benchmark First
Before Rust migration, establish Python baselines:

```python
# Benchmark targets
1. Signal.to_js() call overhead
2. Expression building (10-100 operations)
3. Template literal generation
4. process_datastar_kwargs() processing
5. Full component rendering with signals
```

### Rust Migration Candidates (Future)
**Priority order based on expected impact**:

1. **High ROI** (string-heavy, called frequently):
   - `to_js()` methods (all expression types)
   - `to_js_value()` / `_to_js()` conversion
   - Template literal building
   - `process_datastar_kwargs()` processing

2. **Medium ROI** (computational but less frequent):
   - Helper functions (`match`, `switch`, `collect`)
   - Signal validation and name checking
   - Modifier suffix building

3. **Low ROI** (keep in Python):
   - Operator overloading (requires Python objects)
   - Method chaining (returns Python objects)
   - High-level API surface

### Hybrid Architecture (Future)
```
Python Layer                 Rust Core
─────────────               ─────────────
Signal.__add__()     →      signal_binary_op(left, "&&", right)
signal.to_js()       →      expr_to_js_string(expr_id)
f("Hello {name}")    →      template_literal_build(template, vars)
```

## Dependencies

### Required
- None (stay dependency-free for core)

### Optional (for compatibility)
- `fastcore.xml.NotStr` replacement: Create our own `NotStr` class
- Type hints: Use standard library `typing` only

## Testing Strategy

### Unit Tests
```python
# Test each expression type
def test_signal_creation():
    sig = Signal("count", 0)
    assert sig.to_js() == "$count"
    assert sig.value == 0
    
def test_signal_operations():
    sig = Signal("count", 0)
    assert (sig + 1).to_js() == "($count + 1)"
    assert sig.add(1).to_js() == "$count++"
```

### Integration Tests
```python
def test_signals_integration():
    sigs = Signals(counter=0, items=[])
    assert sigs.counter.to_js() == "$counter"
    assert sigs['counter'] == 0
    assert sigs.to_dict() == {"counter": 0, "items": []}
```

### Benchmark Tests
```python
def test_performance_baseline():
    # Establish Python performance baseline
    # Compare against simple string concatenation
    # Track regression over time
```

## Migration Path

### Step 1: Add without Breaking
- Implement new classes alongside existing code
- Keep `DS` class methods unchanged
- Add tests for new functionality

### Step 2: Gradual Adoption
- Update examples to show both styles
- Document migration patterns
- Provide conversion utilities

### Step 3: Optimize Hot Paths
- Benchmark Python implementation
- Identify bottlenecks
- Migrate specific functions to Rust
- Maintain API compatibility

## Open Questions

1. **NotStr Alternative**: Should we create our own `NotStr` class or adopt a minimal dependency?
2. **Namespace Support**: Do we need signal namespacing for component isolation?
3. **Computed Signals**: Should we support reactive computed signals like StarHTML?
4. **Event Modifier Syntax**: Prefer tuple syntax `(expr, modifiers)` or method chaining?

## Success Criteria

- ✅ Pythonic expression building works naturally
- ✅ Type safety with Signal validation
- ✅ Backward compatibility with existing code
- ✅ Zero additional runtime dependencies
- ✅ Clear migration path from old to new API
- ✅ Performance baseline established for future Rust migration
- ✅ Comprehensive test coverage (>90%)
- ✅ Documentation with examples

## Timeline Estimate

- **Week 1**: Core expression system (Expr, Signal, basic operators)
- **Week 2**: Rich methods and helpers
- **Week 3**: Event modifiers and keyword processing
- **Week 4**: Integration, testing, documentation
- **Week 5+**: Performance benchmarking and optimization planning

---

*This specification should be reviewed and updated as implementation progresses. Track decisions and rationale for future reference.*

