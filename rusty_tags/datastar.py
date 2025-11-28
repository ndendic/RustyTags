"""
Pythonic API for Datastar attributes and signals in StarHTML.

This module provides a powerful expression system to generate Datastar-compatible
JavaScript from Python code, enabling a type-safe and intuitive developer experience.

Key Concepts:
- Signal: A typed reference to a reactive piece of state (e.g., Signal("count", 0)).
- Expr: An abstract base class for objects that can be compiled to a JavaScript expression.
- Operators: Python operators like `+`, `-`, `==`, `&`, `|`, `~` are overloaded on
  Signal and Expr objects to build complex reactive expressions pythonically.
- Helpers: Functions like `match()`, `switch()`, `js()`, and `f()` provide
  higher-level constructs for common UI patterns.
"""

import builtins
import json
import re
from abc import ABC, abstractmethod
from typing import Any, Callable, Union, Iterable, Generator

# ============================================================================
# NotStr: String wrapper to prevent HTML escaping
# ============================================================================
def is_array(x):
    "`True` if `x` supports `__array__` or `iloc`"
    return hasattr(x,'__array__') or hasattr(x,'iloc')

def is_iter(o):
    "Test whether `o` can be used in a `for` loop"
    #Rank 0 tensors in PyTorch are not really iterable
    return isinstance(o, (Iterable,Generator)) and getattr(o,'ndim',1)

def is_coll(o):
    "Test whether `o` is a collection (i.e. has a usable `len`)"
    #Rank 0 tensors in PyTorch do not have working `len`
    return hasattr(o, '__len__') and getattr(o,'ndim',1)

def listify(o=None, *rest, use_list=False, match=None):
    "Convert `o` to a `list`"
    if rest: o = (o,)+rest
    if use_list: res = list(o)
    elif o is None: res = []
    elif isinstance(o, list): res = o
    elif isinstance(o, str) or isinstance(o, bytes) or is_array(o): res = [o]
    elif is_iter(o): res = list(o)
    else: res = [o]
    if match is not None:
        if is_coll(match): match = len(match)
        if len(res)==1: res = res*match
        else: assert len(res)==match, 'Match length mismatch'
    return res

def custom_dir(c, add):
    "Implement custom `__dir__`, adding `add` to `cls`"
    return object.__dir__(c) + listify(add)

class GetAttr:
    "Inherit from this to have all attr accesses in `self._xtra` passed down to `self.default`"
    _default='default'
    def _component_attr_filter(self,k):
        if k.startswith('__') or k in ('_xtra',self._default): return False
        xtra = getattr(self,'_xtra',None)
        return xtra is None or k in xtra
    def _dir(self): return [k for k in dir(getattr(self,self._default)) if self._component_attr_filter(k)]
    def __getattr__(self,k):
        if self._component_attr_filter(k):
            attr = getattr(self,self._default,None)
            if attr is not None: return getattr(attr,k)
        raise AttributeError(k)
    def __dir__(self): return custom_dir(self,self._dir())
#     def __getstate__(self): return self.__dict__
    def __setstate__(self,data): self.__dict__.update(data)

class NotStr(GetAttr):
    "Behaves like a `str`, but isn't an instance of one"
    _default = 's'
    def __init__(self, s): self.s = s.s if isinstance(s, NotStr) else s
    def __repr__(self): return repr(self.s)
    def __str__(self): return self.s
    def __add__(self, b): return NotStr(self.s+str(b))
    def __mul__(self, b): return NotStr(self.s*b)
    def __len__(self): return len(self.s)
    def __eq__(self, b): return self.s==b.s if isinstance(b, NotStr) else b
    def __lt__(self, b): return self.s<b
    def __hash__(self): return hash(self.s)
    def __bool__(self): return bool(self.s)
    def __contains__(self, b): return b in self.s
    def __iter__(self): return iter(self.s)

# ============================================================================
# JavaScript Value Encoding (with single quotes for Datastar compatibility)
# ============================================================================

def _to_single_quoted_js(value: Any) -> str:
    """
    Convert Python value to JavaScript with single quotes.
    
    Uses json.dumps() but converts to single-quoted strings for better
    Datastar/HTML attribute compatibility.
    """
    json_str = json.dumps(value, separators=(",", ":"))
    
    # Replace double quotes with single quotes
    # Handle escaped quotes: \" becomes ' and we need to escape any actual single quotes
    result = json_str.replace(r'\"', "ESCAPED_QUOTE_PLACEHOLDER")
    result = result.replace('"', "'")
    result = result.replace("ESCAPED_QUOTE_PLACEHOLDER", r"\'")
    
    return result


# ============================================================================
# 1. Core Expression System (The Foundation)
# ============================================================================


class Expr(ABC):
    """Abstract base class for objects that can be compiled to JavaScript."""

    @abstractmethod
    def to_js(self) -> str:
        """Compile the expression to a JavaScript string."""
        pass

    def __str__(self) -> str:
        """Return the JavaScript representation of the expression."""
        return self.to_js()

    def __contains__(self, item: str) -> bool:
        """Check if string is contained in the JavaScript representation."""
        return item in self.to_js()

    # --- Property and Method Access ---
    def __getattr__(self, key: str) -> "PropertyAccess":
        """Access a property on the expression: `expr.key`."""
        return PropertyAccess(self, key)

    def __getitem__(self, index: Any) -> "IndexAccess":
        """Access an index or key on the expression: `expr[index]`."""
        return IndexAccess(self, index)

    @property
    def length(self) -> "PropertyAccess":
        return PropertyAccess(self, "length")

    # --- Logical & Comparison Operators ---
    def __and__(self, other: Any) -> "BinaryOp":
        return BinaryOp(self, "&&", other)

    def __or__(self, other: Any) -> "BinaryOp":
        return BinaryOp(self, "||", other)

    def __invert__(self) -> "UnaryOp":
        return UnaryOp("!", self)

    def __eq__(self, other: Any) -> "BinaryOp":
        return BinaryOp(self, "===", other)

    def __ne__(self, other: Any) -> "BinaryOp":
        return BinaryOp(self, "!==", other)

    def __lt__(self, other: Any) -> "BinaryOp":
        return BinaryOp(self, "<", other)

    def __le__(self, other: Any) -> "BinaryOp":
        return BinaryOp(self, "<=", other)

    def __gt__(self, other: Any) -> "BinaryOp":
        return BinaryOp(self, ">", other)

    def __ge__(self, other: Any) -> "BinaryOp":
        return BinaryOp(self, ">=", other)

    def eq(self, other: Any) -> "BinaryOp":
        return BinaryOp(self, "===", other)

    def neq(self, other: Any) -> "BinaryOp":
        return BinaryOp(self, "!==", other)

    def and_(self, other: Any) -> "BinaryOp":
        return BinaryOp(self, "&&", other)

    def or_(self, other: Any) -> "BinaryOp":
        return BinaryOp(self, "||", other)

    # --- Arithmetic Operators ---
    def __add__(self, other: Any) -> Union["BinaryOp", "TemplateLiteral"]:
        return TemplateLiteral([self, other]) if isinstance(other, str) else BinaryOp(self, "+", other)

    def __sub__(self, other: Any) -> "BinaryOp":
        return BinaryOp(self, "-", other)

    def __mul__(self, other: Any) -> "BinaryOp":
        return BinaryOp(self, "*", other)

    def __truediv__(self, other: Any) -> "BinaryOp":
        return BinaryOp(self, "/", other)

    def __mod__(self, other: Any) -> "BinaryOp":
        return BinaryOp(self, "%", other)

    def __radd__(self, other: Any) -> Union["BinaryOp", "TemplateLiteral"]:
        return TemplateLiteral([other, self]) if isinstance(other, str) else BinaryOp(other, "+", self)

    def __rsub__(self, other: Any) -> "BinaryOp":
        return BinaryOp(other, "-", self)

    def __rmul__(self, other: Any) -> "BinaryOp":
        return BinaryOp(other, "*", self)

    def __rtruediv__(self, other: Any) -> "BinaryOp":
        return BinaryOp(other, "/", self)

    def __rmod__(self, other: Any) -> "BinaryOp":
        return BinaryOp(other, "%", self)

    def set(self, value: Any) -> "Assignment":
        return Assignment(self, value)

    def add(self, amount: Any) -> Union["_JSRaw", "Assignment"]:
        return _JSRaw(f"{self.to_js()}++") if type(amount) is int and amount == 1 else Assignment(self, self + amount)

    def sub(self, amount: Any) -> Union["_JSRaw", "Assignment"]:
        return _JSRaw(f"{self.to_js()}--") if type(amount) is int and amount == 1 else Assignment(self, self - amount)

    def mul(self, factor: Any) -> "Assignment":
        return Assignment(self, self * factor)

    def div(self, divisor: Any) -> "Assignment":
        return Assignment(self, self / divisor)

    def mod(self, divisor: Any) -> "Assignment":
        return Assignment(self, self % divisor)

    # --- Control Flow ---
    def if_(self, true_val: Any, false_val: Any = "") -> "Conditional":
        """Ternary expression: `condition ? true_val : false_val`."""
        return Conditional(self, true_val, false_val)

    def then(self, action: Any) -> "_JSRaw":
        """Execute action when condition is true: `if (condition) { action }`."""
        action_js = action if isinstance(action, str) else action.to_js()
        return _JSRaw(f"if ({self.to_js()}) {{ {action_js} }}")

    def toggle(self, *values: Any) -> "Assignment":
        if not values:
            return self.set(~self)
        result = values[0]
        for i in range(len(values) - 1, 0, -1):
            result = (self == values[i - 1]).if_(values[i], result)
        return self.set(result)

    # --- String Methods ---
    def lower(self) -> "MethodCall":
        return MethodCall(self, "toLowerCase", [])

    def upper(self) -> "MethodCall":
        return MethodCall(self, "toUpperCase", [])

    def strip(self) -> "MethodCall":
        return MethodCall(self, "trim", [])

    def contains(self, text: Any) -> "MethodCall":
        return MethodCall(self, "includes", [text])

    # --- Math Methods ---
    def round(self, digits: int = 0) -> "MethodCall":
        return (
            MethodCall(_JSRaw("Math"), "round", [self])
            if digits == 0
            else MethodCall(_JSRaw("Math"), "round", [self * (10**digits)]) / (10**digits)
        )

    def abs(self) -> "MethodCall":
        return MethodCall(_JSRaw("Math"), "abs", [self])

    def min(self, limit: Any) -> "MethodCall":
        return MethodCall(_JSRaw("Math"), "min", [self, limit])

    def max(self, limit: Any) -> "MethodCall":
        return MethodCall(_JSRaw("Math"), "max", [self, limit])

    def clamp(self, min_val: Any, max_val: Any) -> "MethodCall":
        return self.max(min_val).min(max_val)

    # Array methods - simple operations without callbacks
    def append(self, *items: Any) -> "MethodCall":
        return MethodCall(self, "push", [_ensure_expr(item) for item in items])

    def prepend(self, *items: Any) -> "MethodCall":
        return MethodCall(self, "unshift", [_ensure_expr(item) for item in items])

    def pop(self) -> "MethodCall":
        return MethodCall(self, "pop", [])

    def remove(self, index: Any) -> "MethodCall":
        return MethodCall(self, "splice", [_ensure_expr(index), _ensure_expr(1)])

    def join(self, separator: str = ",") -> "MethodCall":
        return MethodCall(self, "join", [_ensure_expr(separator)])

    def slice(self, start: Any = None, end: Any = None) -> "MethodCall":
        args = []
        if start is not None:
            args.append(_ensure_expr(start))
        if end is not None:
            args.append(_ensure_expr(end))
        return MethodCall(self, "slice", args)


class _JSLiteral(Expr):
    """Internal: A Python value to be safely encoded as a JavaScript literal."""

    __slots__ = ("value",)

    def __init__(self, value: Any):
        self.value = value

    def to_js(self) -> str:
        return _to_single_quoted_js(self.value)


class TemplateLiteral(Expr):
    """JS template literal that efficiently combines parts."""

    __slots__ = ("parts",)

    def __init__(self, parts: list):
        self.parts = parts

    def to_js(self) -> str:
        if not self.parts:
            return '""'
        parts = []
        for part in self.parts:
            if isinstance(part, str):
                parts.append(part.replace("`", "\\`").replace("\\", "\\\\").replace("${", "\\${"))
            else:
                parts.append(f"${{{_ensure_expr(part).to_js()}}}")
        return f"`{''.join(parts)}`"

    def __add__(self, other: Any) -> "TemplateLiteral":
        return TemplateLiteral(self.parts + [other])

    def __radd__(self, other: Any) -> "TemplateLiteral":
        return TemplateLiteral([other] + self.parts)


class _JSRaw(Expr):
    """Internal: A raw string of JavaScript code to be passed through verbatim."""

    __slots__ = ("code",)

    def __init__(self, code: str):
        self.code = code

    def to_js(self) -> str:
        return self.code

    def __add__(self, other: Any) -> "TemplateLiteral":
        return TemplateLiteral([self, other])

    def __radd__(self, other: Any) -> "TemplateLiteral":
        return TemplateLiteral([other, self])

    def __call__(self, *args: Any) -> "_JSRaw":
        args_js = ", ".join(_ensure_expr(arg).to_js() for arg in args)
        return _JSRaw(f"{self.code}({args_js})")


class BinaryOp(Expr):
    """A binary operation like `a + b` or `x > y`."""

    __slots__ = ("left", "op", "right")

    def __init__(self, left: Any, op: str, right: Any):
        self.left = _ensure_expr(left)
        self.op = op
        self.right = _ensure_expr(right)

    def to_js(self) -> str:
        return f"({self.left.to_js()} {self.op} {self.right.to_js()})"


class UnaryOp(Expr):
    """A unary operation like `!x`."""

    __slots__ = ("op", "expr")

    def __init__(self, op: str, expr: Expr):
        self.op, self.expr = op, expr

    def to_js(self) -> str:
        return f"{self.op}({self.expr.to_js()})"


class Conditional(Expr):
    """A ternary expression: `condition ? true_val : false_val`."""

    __slots__ = ("condition", "true_val", "false_val")

    def __init__(self, condition: Expr, true_val: Any, false_val: Any):
        self.condition, self.true_val, self.false_val = condition, _ensure_expr(true_val), _ensure_expr(false_val)

    def to_js(self) -> str:
        return f"({self.condition.to_js()} ? {self.true_val.to_js()} : {self.false_val.to_js()})"


class Assignment(Expr):
    """An assignment: `target = value`."""

    __slots__ = ("target", "value")

    def __init__(self, target: Expr, value: Any):
        self.target, self.value = target, _ensure_expr(value)

    def to_js(self) -> str:
        return f"{self.target.to_js()} = {self.value.to_js()}"


class MethodCall(Expr):
    """A method call: `obj.method(arg1, arg2)`."""

    __slots__ = ("obj", "method", "args")

    def __init__(self, obj: Expr, method: str, args: list[Any]):
        self.obj, self.method, self.args = obj, method, [_ensure_expr(a) for a in args]

    def to_js(self) -> str:
        return f"{self.obj.to_js()}.{self.method}({', '.join(arg.to_js() for arg in self.args)})"


class PropertyAccess(Expr):
    """Property access: `obj.prop` that can be called like a method."""

    __slots__ = ("obj", "prop")

    def __init__(self, obj: Expr, prop: str):
        self.obj, self.prop = obj, prop

    def to_js(self) -> str:
        return f"{self.obj.to_js()}.{self.prop}"

    def __call__(self, *args: Any) -> "MethodCall":
        return MethodCall(self.obj, self.prop, args)


class IndexAccess(Expr):
    """Index access for arrays or objects: `obj[index]`."""

    __slots__ = ("obj", "index")

    def __init__(self, obj: Expr, index: Any):
        self.obj, self.index = obj, _ensure_expr(index)

    def to_js(self) -> str:
        return f"{self.obj.to_js()}[{self.index.to_js()}]"


def _ensure_expr(value: Any) -> Expr:
    """Idempotently convert a Python value into an Expr object."""
    return value if isinstance(value, Expr) else _JSLiteral(value)


class Signal(Expr):
    """Typed reactive state reference that auto-generates JavaScript and data attributes."""

    def __init__(
        self,
        name: str,
        initial: Any = None,
        type_: type | None = None,
        namespace: str | None = None,
        _ref_only: bool = False,
    ):
        self._name = name
        self._initial = initial
        self._namespace = namespace
        self._ref_only = _ref_only
        self._is_computed = isinstance(initial, Expr)
        self.type_ = type_ or self._infer_type(initial)
        self.id = f"{namespace}.{name}" if namespace else name
        self._js = f"${self.id}"

    def _infer_type(self, initial: Any) -> type:
        if initial is None:
            return str
        if isinstance(initial, bool):
            return bool
        if isinstance(initial, int | float | str):
            return type(initial)
        if isinstance(initial, list | tuple):
            return list
        if isinstance(initial, dict):
            return dict
        return type(initial)

    def to_dict(self) -> dict[str, Any]:
        if self._is_computed:
            return {}
        return {self.id: self._initial}

    def get_computed_attr(self) -> tuple[str, Any] | None:
        if self._is_computed:
            return (f"data_computed_{self._name}", self._initial)
        return None

    def to_js(self) -> str:
        return self._js

    def __hash__(self):
        return hash((self._name, self._namespace))

    def __eq__(self, other) -> "BinaryOp":
        return BinaryOp(self, "===", _ensure_expr(other))

    def is_same_as(self, other: "Signal") -> bool:
        return isinstance(other, Signal) and self._name == other._name and self._namespace == other._namespace

    def __getattr__(self, key: str) -> PropertyAccess:
        return PropertyAccess(self, key)


_JS_EXPR_PREFIXES = ("$", "`", "!", "(", "'", "evt.")
_JS_EXPR_KEYWORDS = {"true", "false", "null", "undefined"}


def _to_js(value: Any, allow_expressions: bool = True, wrap_objects: bool = True) -> str:
    match value:
        case Expr() as expr:
            return expr.to_js()
        case None:
            return "null"
        case bool():
            return "true" if value else "false"
        case int() | float():
            return str(value)
        case str() as s:
            if allow_expressions and (s.startswith(_JS_EXPR_PREFIXES) or s in _JS_EXPR_KEYWORDS):
                return s
            return json.dumps(s)
        case dict() as d:
            try:
                return json.dumps(d)
            except (TypeError, ValueError):
                items = [
                    f"{_to_js(k.replace('_', '-') if isinstance(k, str) else k, allow_expressions)}: {_to_js(v, allow_expressions)}"
                    for k, v in d.items()
                ]
                obj = f"{{{', '.join(items)}}}"
                return f"({obj})" if wrap_objects else obj
        case list() | tuple() as l:
            try:
                return json.dumps(l)
            except (TypeError, ValueError):
                items = [_to_js(item, allow_expressions) for item in l]
                return f"[{', '.join(items)}]"
        case _:
            return json.dumps(str(value))


def to_js_value(value: Any) -> str:
    """Convert Python value to JavaScript expression."""
    return _to_js(value, allow_expressions=True)


# --- General Purpose Helpers ---


def js(code: str) -> _JSRaw:
    """Mark a string as raw JavaScript code."""
    return _JSRaw(code)


def value(v: Any) -> _JSLiteral:
    """Mark a Python value to be safely encoded as a JavaScript literal."""
    if isinstance(v, Expr):
        raise TypeError(
            f"value() should not be used with {type(v).__name__} objects. Use the object directly instead of wrapping it with value()."
        )
    return _JSLiteral(v)

def expr(v: Any) -> _JSLiteral:
    """Wrap Python value as JavaScript expression to enable method chaining."""
    if isinstance(v, Expr):
        raise TypeError(
            f"expr() expects a Python value, not {type(v).__name__}. Use the Expr object directly without wrapping."
        )
    return _JSLiteral(v)

def f(template_str: str, **kwargs: Any) -> _JSRaw:
    """Create reactive JavaScript template literal, like a Python f-string."""

    def replacer(match: re.Match) -> str:
        key = match.group(1)
        val = kwargs.get(key)
        if val is None:
            return match.group(0)
        return f"${{{to_js_value(val)}}}"

    js_template = re.sub(r"\{(\w+)\}", replacer, template_str)
    return _JSRaw(f"`{js_template}`")


def regex(pattern: str) -> _JSRaw:
    """Create JavaScript regex literal: regex("^todo_") → /^todo_/"""
    return _JSRaw(f"/{pattern}/")


# --- Conditional Logic Helpers ---


def match(subject: Any, /, **patterns: Any) -> _JSRaw:
    """Pattern matching for conditional values (like Python match/case)."""
    subject_expr = _ensure_expr(subject)
    default_val = patterns.pop("default", "")
    result = _ensure_expr(default_val)
    for pattern, val in reversed(patterns.items()):
        check_expr = subject_expr == _ensure_expr(pattern)
        result = check_expr.if_(val, result)
    return _JSRaw(result.to_js())


def switch(cases: list[tuple[Any, Any]], /, default: Any = "") -> _JSRaw:
    """Sequential condition evaluation (if/elif/else chain)."""
    result = _ensure_expr(default)
    for condition, val in reversed(cases):
        result = _ensure_expr(condition).if_(val, result)
    return _JSRaw(result.to_js())


def collect(cases: list[tuple[Any, Any]], /, join_with: str = " ") -> _JSRaw:
    """Collect values from true conditions: useful for CSS classes."""
    if not cases:
        return _JSRaw("''")
    parts = [_ensure_expr(condition).if_(val, "").to_js() for condition, val in cases]
    array_expr = "[" + ", ".join(parts) + "]"
    return _JSRaw(f"{array_expr}.filter(Boolean).join('{join_with}')")


def classes(**class_conditions) -> _JSRaw:
    """
    Create a JavaScript object literal for Datastar's data-class attribute.
    
    Args:
        **class_conditions: CSS class name -> boolean condition pairs
        
    Returns:
        JavaScript object literal: {class1: condition1, class2: condition2}
        
    Example:
        classes(large=is_large, bold=is_bold)
        # → {large: $is_large, bold: $is_bold}
        
        classes(**{'font-bold': is_bold, hidden: is_hidden})
        # → {'font-bold': $is_bold, hidden: $is_hidden}
    """
    if not class_conditions:
        return _JSRaw("{}")
    
    pairs = []
    for class_name, condition in class_conditions.items():
        # Quote class names with hyphens or special chars
        if '-' in class_name or ' ' in class_name or not class_name.isidentifier():
            key = f"'{class_name}'"
        else:
            key = class_name
        
        value = _ensure_expr(condition).to_js()
        pairs.append(f"{key}: {value}")
    
    return _JSRaw("{" + ", ".join(pairs) + "}")

def seq(*exprs: Any) -> _JSRaw:
    """Comma operator sequence: seq(a, b, c) evaluates all, returns last."""
    if not exprs:
        return _JSRaw("undefined")
    expr_strs = [_ensure_expr(e).to_js() for e in exprs]
    return _JSRaw(f"({', '.join(expr_strs)})")

def if_(condition: Any, true_val: Any, false_val: Any = "") -> _JSRaw:
    """Conditional expression: `condition ? true_val : false_val`."""
    return _JSRaw(f"{_ensure_expr(condition).to_js()} ? {_ensure_expr(true_val).to_js()} : {_ensure_expr(false_val).to_js()}")

# --- Logical Aggregation Helpers ---


def _iterable_args(*args):
    """Support Python built-in style: if passed a single iterable, unpack it."""
    return (
        args[0]
        if builtins.len(args) == 1 and hasattr(args[0], "__iter__") and not isinstance(args[0], str | Signal | Expr)
        else args
    )


def all_(*signals) -> _JSRaw:
    """Check if all signals are truthy: all(a, b, c) → !!a && !!b && !!c"""
    if not signals:
        return _JSRaw("true")
    signals = _iterable_args(*signals)
    return _JSRaw(" && ".join(f"!!{_ensure_expr(s).to_js()}" for s in signals))


def any_(*signals) -> _JSRaw:
    """Check if any signal is truthy: any(a, b, c) → !!a || !!b || !!c"""
    if not signals:
        return _JSRaw("false")
    signals = _iterable_args(*signals)
    return _JSRaw(" || ".join(f"!!{_ensure_expr(s).to_js()}" for s in signals))


# --- Action Helpers ---


def post(url: str, data: dict[str, Any] | None = None, **kwargs) -> _JSRaw:
    return _action("post", url, data, **kwargs)


def get(url: str, data: dict[str, Any] | None = None, **kwargs) -> _JSRaw:
    return _action("get", url, data, **kwargs)


def put(url: str, data: dict[str, Any] | None = None, **kwargs) -> _JSRaw:
    return _action("put", url, data, **kwargs)


def patch(url: str, data: dict[str, Any] | None = None, **kwargs) -> _JSRaw:
    return _action("patch", url, data, **kwargs)


def delete(url: str, data: dict[str, Any] | None = None, **kwargs) -> _JSRaw:
    return _action("delete", url, data, **kwargs)


def clipboard(text: str|None = None, element: str|None = None, signal: str|None = None) -> _JSRaw:
    if not ((text is None) ^ (element is None)):
        raise ValueError("Must provide exactly one of: text or element")

    signal_suffix = f", {to_js_value(signal)}" if signal else ""

    if text is not None:
        return _JSRaw(f"@clipboard({to_js_value(text)}{signal_suffix})")

    # Element mode: generate appropriate DOM access
    if element == "el":
        js_expr = "el"
    elif element and element.startswith(("#", ".")):
        js_expr = f"document.querySelector({to_js_value(element)})"
    else:
        js_expr = f"document.getElementById({to_js_value(element)})"

    return _JSRaw(f"@clipboard({js_expr}.textContent{signal_suffix})")


def _timer_ref(timer: "Signal", window: bool = False) -> str:
    timer_id = timer.id if hasattr(timer, "id") else timer
    return f"window._{timer_id}" if window else f"${timer_id}"


def set_timeout(action: Any, ms: Any, *, store: Union["Signal", None] = None, window: bool = False) -> _JSRaw:
    """Schedule action(s) after delay.

    set_timeout(copied.set(False), 2000)
    set_timeout([step.set(2), progress.set(40)], 1000, store=timer)
    """
    action_js = (
        _ensure_expr(action).to_js()
        if not isinstance(action, list)
        else "; ".join(_ensure_expr(a).to_js() for a in action)
    )
    ms_js = _ensure_expr(ms).to_js()
    timeout_expr = f"setTimeout(() => {{ {action_js} }}, {ms_js})"

    if store:
        timer_ref = _timer_ref(store, window)
        return _JSRaw(f"{timer_ref} = {timeout_expr}")
    return _JSRaw(timeout_expr)


def clear_timeout(timer: "Signal", *actions: Any, window: bool = False) -> _JSRaw:
    """Cancel timeout, optionally run actions.

    clear_timeout(timer)
    clear_timeout(timer, open.set(False), loading.set(False))
    """
    timer_ref = _timer_ref(timer, window)
    clear = f"clearTimeout({timer_ref})"
    if not actions:
        return _JSRaw(clear)

    action_js = "; ".join(_ensure_expr(a).to_js() for a in actions)
    return _JSRaw(f"{clear}; {action_js}")


def reset_timeout(timer: "Signal", ms: Any, *actions: Any, window: bool = False) -> _JSRaw:
    """Clear and reschedule timeout (debounce pattern).

    reset_timeout(timer, 700, open.set(True))
    reset_timeout(timer, 50, selected.set(0), window=True)
    """
    timer_ref = _timer_ref(timer, window)
    action_js = "; ".join(_ensure_expr(a).to_js() for a in actions)
    ms_js = _ensure_expr(ms).to_js()
    return _JSRaw(f"clearTimeout({timer_ref}); {timer_ref} = setTimeout(() => {{ {action_js} }}, {ms_js})")


def _action(verb: str, url: str, data: dict[str, Any] | None = None, **kwargs) -> _JSRaw:
    payload = {**(data or {}), **kwargs}
    if not payload:
        return _JSRaw(f"@{verb}('{url}')")
    parts = [f"{k}: {to_js_value(v)}" for k, v in payload.items()]
    return _JSRaw(f"@{verb}('{url}', {{{', '.join(parts)}}})")


# --- JavaScript Global Objects ---

console = js("console")
Math = js("Math")
JSON = js("JSON")
Object = js("Object")
Array = js("Array")
Date = js("Date")
Number = js("Number")
String = js("String")
Boolean = js("Boolean")


# --- Core Datastar Keyword Argument Processing Engine ---


def _normalize_data_key(key: str) -> str:
    """Normalizes a Pythonic key to its `data-*` attribute equivalent.
    
    Uses colon separator for keyed plugins (Datastar v1.0+ syntax):
    - data_computed_foo -> data-computed:foo
    - data_on_click -> data-on:click
    - data_attr_title -> data-attr:title
    """
    for prefix in ("data_computed_", "data_on_", "data_attr_", "data_"):
        if key.startswith(prefix):
            name = key.removeprefix(prefix)
            slug = name if prefix == "data_computed_" else name.replace("_", "-")
            return f"{prefix.removesuffix('_').replace('_', '-')}:{slug}"
    return key.replace("_", "-")


def _build_modifier_suffix(modifiers: dict[str, Any]) -> str:
    """Builds a modifier suffix (e.g., `__debounce__300ms`) from a dictionary."""
    if not modifiers:
        return ""
    parts = []
    for name, value in modifiers.items():
        match value:
            case True:
                parts.append(name)
            case False:
                parts.append(f"{name}.false")  # Preserve explicit false
            case int() | float():
                part = f"n{abs(value)}" if value < 0 else str(value)
                parts.append(f"{name}.{part}")
            case str():
                parts.append(f"{name}.{value}")
    return f"__{'__'.join(parts)}" if parts else ""


def _expr_list_to_js(items: list[Any], collect_signals: Callable) -> str:
    """Joins a list of expressions into a semicolon-separated JS string."""

    def process_item(item):
        if isinstance(item, Expr | Signal):
            collect_signals(item)
            return item.to_js()
        return str(item)

    return "; ".join(process_item(item) for item in items)


def _collect_signals(expr: Any, sink: set[Signal]) -> None:
    """Recursively traverses an expression to find all Signal references."""
    if isinstance(expr, Signal):
        sink.add(expr)
    elif isinstance(expr, Expr):
        attrs = (
            (getattr(expr, slot, None) for slot in expr.__slots__)
            if hasattr(expr, "__slots__")
            else expr.__dict__.values()
            if hasattr(expr, "__dict__")
            else ()
        )

        for attr in attrs:
            if isinstance(attr, Signal | Expr):
                _collect_signals(attr, sink)
            elif isinstance(attr, list | tuple):
                for item in attr:
                    _collect_signals(item, sink)


def build_data_signals(signals: dict[str, Any]) -> NotStr:
    """Builds a non-escaped JavaScript object literal for `data-signals`."""
    parts = [f"{key}: {_to_js(val, allow_expressions=False)}" for key, val in signals.items()]
    return NotStr("{" + ", ".join(parts) + "}")


def _handle_data_signals(value: Any) -> Any:
    """Processes the value for a `data_signals` keyword argument."""
    signal_dict = {}
    match value:
        case list() | tuple():
            for s in value:
                if isinstance(s, Signal) and not s._ref_only:
                    signal_dict.update(s.to_dict())
        case dict() as d:
            signal_dict = d
        case Signal() as s:
            signal_dict = s.to_dict()
    return build_data_signals(signal_dict) if signal_dict else value


def _apply_additive_class_behavior(processed: dict) -> None:
    """Combines cls and data_attr_cls for SSR + reactive classes.
    
    Uses colon separator for Datastar v1.0+ syntax: data-attr:class
    """
    if "cls" in processed and "data_attr_cls" in processed:
        base_classes = processed.pop("cls")
        reactive_classes = str(processed.pop("data_attr_cls"))
        if reactive_classes.startswith("(") and reactive_classes.endswith(")"):
            reactive_classes = reactive_classes[1:-1]
        processed["data-attr:class"] = NotStr(f"`{base_classes} ${{{reactive_classes}}}`")




# ============================================================================
# Original RustyTags Datastar Integration to be enhanced
# ============================================================================


"""
RustyTags Datastar Integration - Python API Layer

This module provides action generators and utilities for working with Datastar
in a pythonic way, similar to the official Datastar Python SDK.
"""

import json
from typing import Any, Dict, Union
from urllib.parse import urlencode
from datastar_py.attributes import attribute_generator
from datastar_py import ServerSentEventGenerator as SSE
from datastar_py.consts import ElementPatchMode, EventType
from .utils import AttrDict


class DS:
    """
    Datastar action generators for common patterns.
    
    This class provides static methods that generate JavaScript expressions
    for common Datastar actions, making it easier to work with Datastar
    from Python without writing raw JavaScript.
    """
    
    @staticmethod
    def get(url: str, **params) -> str:
        """
        Generate a @get() action for fetching data.
        
        Args:
            url: The URL to fetch from
            **params: Query parameters to append to the URL. A special parameter
                  `_ds_options` can be passed as a dictionary to provide
                  options to the underlying Datastar action.
            
        Returns:
            JavaScript expression string for the @get action
            
        Example:
            DS.get("/api/data", page=1, _ds_options={'openWhenHidden': True})
            # Returns: "@get('/api/data?page=1', {'openWhenHidden':true})"
        """

        _ds_options = params.pop('_ds_options', {})
        if params:
            url = f"{url}?{urlencode(params)}"

        if _ds_options:
            action = f"@get('{url}', {_to_single_quoted_js(_ds_options)})"
        else:
            action = f"@get('{url}')"

        return action
    
    @staticmethod
    def post(url: str, target: str|None = None, data: Union[str, Dict]|None = None, **extra_data) -> str:
        """
        Generate a @post() action for sending data.
        
        Args:
            url: The URL to post to
            target: Optional target selector for where to place the response
            data: Data to send (can be a dict, signal reference, or raw string)
            **extra_data: Additional data fields to merge
            
        Returns:
            JavaScript expression string for the @post action
        """
        action = f"@post('{url}')"
        
        # Handle data parameter
        if data is not None or extra_data:
            combined_data = {}
            
            if isinstance(data, dict):
                combined_data.update(data)
            elif isinstance(data, str):
                # If data is a string, assume it's a signal reference or expression
                if data.startswith('$'):
                    action += f" @data({data})"
                else:
                    action += f" @data('{data}')"
            
            if extra_data:
                combined_data.update(extra_data)
            
            if combined_data and not isinstance(data, str):
                action += f" @data({_to_single_quoted_js(combined_data)})"
        
        if target:
            action += f" @target('{target}')"
        
        return action
    
    @staticmethod
    def put(url: str, target: str|None = None, data: Union[str, Dict]|None = None, **extra_data) -> str:
        """
        Generate a @put() action for updating data.
        
        Args:
            url: The URL to put to
            target: Optional target selector for where to place the response
            data: Data to send (can be a dict, signal reference, or raw string)
            **extra_data: Additional data fields to merge
            
        Returns:
            JavaScript expression string for the @put action
        """
        action = f"@put('{url}')"
        
        if data is not None or extra_data:
            combined_data = {}
            
            if isinstance(data, dict):
                combined_data.update(data)
            elif isinstance(data, str):
                if data.startswith('$'):
                    action += f" @data({data})"
                else:
                    action += f" @data('{data}')"
            
            if extra_data:
                combined_data.update(extra_data)
            
            if combined_data and not isinstance(data, str):
                action += f" @data({_to_single_quoted_js(combined_data)})"
        
        if target:
            action += f" @target('{target}')"
        
        return action
    
    @staticmethod
    def delete(url: str, target: str|None = None) -> str:
        """
        Generate a @delete() action.
        
        Args:
            url: The URL to delete
            target: Optional target selector for where to place the response
            
        Returns:
            JavaScript expression string for the @delete action
        """
        action = f"@delete('{url}')"
        if target:
            action += f" @target('{target}')"
        return action
    
    @staticmethod
    def patch(url: str, target: str|None = None, data: Union[str, Dict]|None = None, **extra_data) -> str:
        """
        Generate a @patch() action for partial updates.
        
        Args:
            url: The URL to patch
            target: Optional target selector for where to place the response
            data: Data to send (can be a dict, signal reference, or raw string)
            **extra_data: Additional data fields to merge
            
        Returns:
            JavaScript expression string for the @patch action
        """
        action = f"@patch('{url}')"
        
        if data is not None or extra_data:
            combined_data = {}
            
            if isinstance(data, dict):
                combined_data.update(data)
            elif isinstance(data, str):
                if data.startswith('$'):
                    action += f" @data({data})"
                else:
                    action += f" @data('{data}')"
            
            if extra_data:
                combined_data.update(extra_data)
            
            if combined_data and not isinstance(data, str):
                action += f" @data({_to_single_quoted_js(combined_data)})"
        
        if target:
            action += f" @target('{target}')"
        
        return action
    
    # Signal manipulation helpers
    @staticmethod
    def set(signal: str, value: Any) -> str:
        """
        Set a signal value.
        
        Args:
            signal: Signal name (without $)
            value: Value to set
            
        Returns:
            JavaScript expression to set the signal
        """
        if isinstance(value, str):
            # Check if it's already an expression or needs quoting
            # Use builtins.any to avoid any potential override
            import builtins
            is_dollar = value.startswith('$')
            is_at = value.startswith('@')
            has_operators = builtins.any(op in value for op in ['===', '!==', '&&', '||', '()'])
            is_expression = is_dollar or is_at or has_operators
            
            if is_expression:
                return f"${signal} = {value}"
            else:
                return f"${signal} = '{value}'"
        elif isinstance(value, bool):
            return f"${signal} = {'true' if value else 'false'}"
        elif isinstance(value, (int, float)):
            return f"${signal} = {value}"
        elif value is None:
            return f"${signal} = null"
        else:
            return f"${signal} = {_to_single_quoted_js(value)}"
    
    @staticmethod
    def toggle(signal: str) -> str:
        """
        Toggle a boolean signal.
        
        Args:
            signal: Signal name (without $)
            
        Returns:
            JavaScript expression to toggle the signal
        """
        return f"${signal} = !${signal}"
    
    @staticmethod
    def increment(signal: str, amount: Union[int, float] = 1) -> str:
        """
        Increment a numeric signal.
        
        Args:
            signal: Signal name (without $)
            amount: Amount to increment by (default: 1)
            
        Returns:
            JavaScript expression to increment the signal
        """
        return f"${signal} += {amount}"
    
    @staticmethod
    def decrement(signal: str, amount: Union[int, float] = 1) -> str:
        """
        Decrement a numeric signal.
        
        Args:
            signal: Signal name (without $)
            amount: Amount to decrement by (default: 1)
            
        Returns:
            JavaScript expression to decrement the signal
        """
        return f"${signal} -= {amount}"
    
    @staticmethod
    def append(signal: str, value: Any) -> str:
        """
        Append to an array signal.
        
        Args:
            signal: Signal name (without $)
            value: Value to append
            
        Returns:
            JavaScript expression to append to the signal array
        """
        if isinstance(value, str) and not (value.startswith('$') or value.startswith('@')):
            return f"${signal}.push('{value}')"
        else:
            return f"${signal}.push({_to_single_quoted_js(value) if not isinstance(value, str) else value})"
    
    @staticmethod
    def remove(signal: str, index: Union[int, str, None] = None, value: Any = None) -> str:
        """
        Remove from an array signal.
        
        Args:
            signal: Signal name (without $)
            index: Index to remove (if specified)
            value: Value to find and remove (if specified, used instead of index)
            
        Returns:
            JavaScript expression to remove from the signal array
        """
        if index is not None:
            return f"${signal}.splice({index}, 1)"
        elif value is not None:
            value_expr = _to_single_quoted_js(value) if not isinstance(value, str) or not value.startswith('$') else value
            return f"${signal}.splice(${signal}.indexOf({value_expr}), 1)"
        else:
            return f"${signal}.pop()"
    
    # Utility methods for complex actions
    @staticmethod
    def chain(*actions) -> str:
        """
        Chain multiple actions together.
        
        Args:
            *actions: Actions to chain
            
        Returns:
            JavaScript expression with chained actions
        """
        return '; '.join(str(action) for action in actions if action)
    
    @staticmethod
    def conditional(condition: str, true_action: str, false_action: str|None = None) -> str:
        """
        Create a conditional action.
        
        Args:
            condition: JavaScript condition
            true_action: Action to execute if condition is true
            false_action: Action to execute if condition is false (optional)
            
        Returns:
            JavaScript ternary expression
        """
        if false_action:
            return f"{condition} ? ({true_action}) : ({false_action})"
        else:
            return f"{condition} && ({true_action})"


# Convenience functions for common patterns
def signals(**kwargs) -> Dict[str, Any]:
    """
    Create a signals dictionary for ds_signals attribute.
    
    Args:
        **kwargs: Signal name/value pairs
        
    Returns:
        Dictionary suitable for ds_signals
        
    Example:
        signals(count=0, user={"name": "", "email": ""})
    """
    return kwargs


class Signals(AttrDict):
    """
    A dictionary of signals with reactive capabilities.
    
    Usage:
        signals = Signals(counter=0, items=[])
        signals.counter.add(1)    # → Signal object with methods
        signals['counter']        # → 0 (raw value)
        signals.to_dict()         # → {"counter": 0, "items": []}
    """
    def __init__(self, **kwargs: Any) -> None:
        # Always initialize _namespace first (even if None)
        self._namespace = kwargs.pop("namespace", None)
        
        super().__init__(**kwargs)
        
        # Create Signal objects for each entry
        self._signals = {}
        for k, v in kwargs.items():
            # Pass namespace to Signal if it exists
            self._signals[k] = Signal(k, v, namespace=self._namespace)
        
    def __getattribute__(self, key):
        """Intercept attribute access to return Signal objects for signal names"""
        # Always allow access to private attributes and special methods
        if key.startswith('_') or key in ('to_dict',):
            return object.__getattribute__(self, key)
        
        # Get _signals dict directly to avoid recursion
        try:
            signals_dict = object.__getattribute__(self, '_signals')
            if key in signals_dict:
                return signals_dict[key]
        except AttributeError:
            pass
        
        # Fall back to normal attribute access
        return object.__getattribute__(self, key)

    def __setattr__(self, k, v):
        """Handle attribute assignment - preserve underscore attributes"""
        if k.startswith('_'):
            # Internal attributes go to __dict__
            super().__setattr__(k, v)
        else:
            # Regular attributes go to dict storage
            self.__setitem__(k, v)

    def to_dict(self):
        """Return plain dict for data-signals attribute"""
        return dict(self)

    def __str__(self):
        """String representation with optional namespace"""
        if self._namespace:
            return f"{{{self._namespace}: {super().__str__()}}}"
        return super().__str__()

def reactive_class(**conditions) -> Dict[str, str]:
    """
    Create a reactive class dictionary for cls attribute.
    
    Args:
        **conditions: CSS class name -> condition pairs
        
    Returns:
        Dictionary suitable for reactive cls attribute
        
    Example:
        reactive_class(active="$isActive", disabled="$count === 0")
    """
    return conditions


# Export all public items
__all__ = [
    "DS",
    "signals",
    "Signals",
    "reactive_class",
    "attribute_generator",
    "SSE",
    "ElementPatchMode",
    "EventType",
    "Signal",
    "Expr",
    "js",
    "value",
    "f",
    "regex",
    "match",
    "switch",
    "collect",
    "classes",
    "all_",
    "any_",
    "post",
    "get",
    "put",
    "patch",
    "delete",
    "clipboard",
    "console",
    "Math",
    "JSON",
    "Object",
    "Array",
    "Date",
    "Number",
    "String",
    "Boolean",
    "if_",
    "to_js_value",
    "seq",
]