"""
Tests for Datastar SDK Python API (Phase 3).

This module tests the Python API for building Datastar expressions:
- Signal class and Signals collection
- Expression operators (arithmetic, comparison, logical)
- Signal methods (set, add, sub, toggle)
- String methods (upper, lower, strip, contains, length)
- Array methods (append, pop, remove, join, slice)
- Math methods (round, abs, min, max, clamp)
- Conditional helpers (if_, match, switch)
- Aggregation helpers (all_, any_)
- Class helpers (collect, classes)
- HTTP action helpers (post, get, put, patch, delete)
- Template helpers (f, js)
- Property access (nested properties and indexing)
- DS class for action generation
"""

import pytest
from rusty_tags.datastar import (
    Signal, Signals, Expr,
    js, f, value, expr,
    if_, match, switch,
    all_, any_,
    collect, classes,
    post, get, put, patch, delete,
    DS,
    to_js_value,
)


# ============================================================================
# Signal Class Tests
# ============================================================================

class TestSignalClass:
    """Test Signal creation and basic functionality."""

    def test_signal_creation(self):
        """Test Signal creation with name and initial value."""
        sig = Signal("count", 0)
        assert sig.to_js() == "$count"
        assert str(sig) == "$count"

    def test_signal_to_dict(self):
        """Test to_dict() returns signal name/value pair."""
        sig = Signal("name", "test")
        assert sig.to_dict() == {"name": "test"}

    def test_signal_with_namespace(self):
        """Test Signal with namespace prefix."""
        sig = Signal("count", 0, namespace="app")
        assert sig.to_js() == "$app.count"

    def test_signal_str_conversion(self):
        """Test str() returns JavaScript reference."""
        sig = Signal("value", 42)
        assert str(sig) == "$value"

    def test_signal_type_inference_int(self):
        """Test type inference for integer values."""
        sig = Signal("num", 42)
        assert sig.type_ == int

    def test_signal_type_inference_str(self):
        """Test type inference for string values."""
        sig = Signal("text", "hello")
        assert sig.type_ == str

    def test_signal_type_inference_bool(self):
        """Test type inference for boolean values."""
        sig = Signal("flag", True)
        assert sig.type_ == bool

    def test_signal_type_inference_list(self):
        """Test type inference for list values."""
        sig = Signal("items", [1, 2, 3])
        assert sig.type_ == list

    def test_signal_type_inference_dict(self):
        """Test type inference for dict values."""
        sig = Signal("data", {"key": "value"})
        assert sig.type_ == dict

    def test_signal_hashing(self):
        """Test Signal can be hashed for use in sets/dicts."""
        sig1 = Signal("count", 0)
        sig2 = Signal("count", 0)
        sig3 = Signal("other", 0)

        # Same name signals should hash the same
        assert hash(sig1) == hash(sig2)
        # Different names should (usually) hash differently
        assert hash(sig1) != hash(sig3)


# ============================================================================
# Signals Class Tests
# ============================================================================

class TestSignalsClass:
    """Test Signals collection for managing multiple signals."""

    def test_signals_creation(self):
        """Test Signals creation with multiple values."""
        sigs = Signals(counter=0, name="test")
        assert "counter" in sigs
        assert "name" in sigs

    def test_signals_attribute_access(self):
        """Test accessing signals via attribute returns Signal objects."""
        sigs = Signals(counter=0, name="test")
        assert isinstance(sigs.counter, Signal)
        assert isinstance(sigs.name, Signal)

    def test_signals_to_dict(self):
        """Test to_dict() returns original values."""
        sigs = Signals(counter=0, name="test")
        result = sigs.to_dict()
        assert result == {"counter": 0, "name": "test"}

    def test_signals_with_namespace(self):
        """Test Signals with namespace applies to all signals."""
        sigs = Signals(count=0, namespace="form")
        assert sigs.count.to_js() == "$form.count"

    def test_signals_dict_access(self):
        """Test accessing raw values via dict notation."""
        sigs = Signals(counter=0, name="test")
        assert sigs["counter"] == 0
        assert sigs["name"] == "test"


# ============================================================================
# Expression Arithmetic Operators Tests
# ============================================================================

class TestExprArithmeticOperators:
    """Test arithmetic operators on Signal and Expr objects."""

    def test_addition(self):
        """Test addition operator (+)."""
        sigs = Signals(x=10, y=5)
        result = (sigs.x + sigs.y).to_js()
        assert result == "($x + $y)"

    def test_subtraction(self):
        """Test subtraction operator (-)."""
        sigs = Signals(x=10, y=5)
        result = (sigs.x - sigs.y).to_js()
        assert result == "($x - $y)"

    def test_multiplication(self):
        """Test multiplication operator (*)."""
        sigs = Signals(x=10, y=5)
        result = (sigs.x * sigs.y).to_js()
        assert result == "($x * $y)"

    def test_division(self):
        """Test division operator (/)."""
        sigs = Signals(x=10, y=5)
        result = (sigs.x / sigs.y).to_js()
        assert result == "($x / $y)"

    def test_modulo(self):
        """Test modulo operator (%)."""
        sigs = Signals(x=10, y=3)
        result = (sigs.x % sigs.y).to_js()
        assert result == "($x % $y)"

    def test_arithmetic_with_literal(self):
        """Test arithmetic with Python literals."""
        sig = Signal("count", 0)
        result = (sig + 5).to_js()
        assert result == "($count + 5)"

    def test_reverse_addition(self):
        """Test reverse addition (literal + signal)."""
        sig = Signal("value", 10)
        # String concatenation creates template literal
        result = (10 + sig).to_js()
        assert "$value" in result


# ============================================================================
# Expression Comparison Operators Tests
# ============================================================================

class TestExprComparisonOperators:
    """Test comparison operators on Signal and Expr objects."""

    def test_equality(self):
        """Test equality operator (==) converts to ===."""
        sig = Signal("count", 0)
        result = (sig == 0).to_js()
        assert result == "($count === 0)"

    def test_inequality(self):
        """Test inequality operator (!=) converts to !==."""
        sig = Signal("count", 0)
        result = (sig != 0).to_js()
        assert result == "($count !== 0)"

    def test_less_than(self):
        """Test less than operator (<)."""
        sig = Signal("age", 25)
        result = (sig < 18).to_js()
        assert result == "($age < 18)"

    def test_less_than_or_equal(self):
        """Test less than or equal operator (<=)."""
        sig = Signal("age", 25)
        result = (sig <= 18).to_js()
        assert result == "($age <= 18)"

    def test_greater_than(self):
        """Test greater than operator (>)."""
        sig = Signal("age", 25)
        result = (sig > 18).to_js()
        assert result == "($age > 18)"

    def test_greater_than_or_equal(self):
        """Test greater than or equal operator (>=)."""
        sig = Signal("age", 25)
        result = (sig >= 18).to_js()
        assert result == "($age >= 18)"

    def test_comparison_between_signals(self):
        """Test comparison between two signals."""
        sigs = Signals(x=10, y=5)
        result = (sigs.x > sigs.y).to_js()
        assert result == "($x > $y)"


# ============================================================================
# Expression Logical Operators Tests
# ============================================================================

class TestExprLogicalOperators:
    """Test logical operators on Signal and Expr objects."""

    def test_logical_and(self):
        """Test logical AND (&) converts to &&."""
        s1 = Signal("a", True)
        s2 = Signal("b", True)
        result = (s1 & s2).to_js()
        assert result == "($a && $b)"

    def test_logical_or(self):
        """Test logical OR (|) converts to ||."""
        s1 = Signal("a", True)
        s2 = Signal("b", True)
        result = (s1 | s2).to_js()
        assert result == "($a || $b)"

    def test_logical_not(self):
        """Test logical NOT (~) converts to !."""
        sig = Signal("flag", True)
        result = (~sig).to_js()
        assert result == "!($flag)"

    def test_complex_logical_expression(self):
        """Test complex logical expression with multiple operators."""
        sigs = Signals(age=25, licensed=True)
        result = ((sigs.age >= 18) & sigs.licensed).to_js()
        assert "$age" in result
        assert ">=" in result
        assert "&&" in result
        assert "$licensed" in result


# ============================================================================
# Signal Methods Tests
# ============================================================================

class TestSignalMethods:
    """Test Signal mutation methods."""

    def test_set_method(self):
        """Test set() method generates assignment."""
        sig = Signal("count", 0)
        result = sig.set(10).to_js()
        assert result == "$count = 10"

    def test_add_method_increment(self):
        """Test add(1) generates increment (++)."""
        sig = Signal("count", 0)
        result = sig.add(1).to_js()
        assert result == "$count++"

    def test_add_method_with_value(self):
        """Test add(n) generates addition assignment."""
        sig = Signal("count", 0)
        result = sig.add(5).to_js()
        assert result == "$count = ($count + 5)"

    def test_sub_method_decrement(self):
        """Test sub(1) generates decrement (--)."""
        sig = Signal("count", 10)
        result = sig.sub(1).to_js()
        assert result == "$count--"

    def test_sub_method_with_value(self):
        """Test sub(n) generates subtraction assignment."""
        sig = Signal("count", 10)
        result = sig.sub(3).to_js()
        assert result == "$count = ($count - 3)"

    def test_toggle_method(self):
        """Test toggle() method generates negation."""
        sig = Signal("isOpen", False)
        result = sig.toggle().to_js()
        assert "!" in result
        assert "$isOpen" in result

    def test_mul_method(self):
        """Test mul() method generates multiplication assignment."""
        sig = Signal("value", 5)
        result = sig.mul(2).to_js()
        assert result == "$value = ($value * 2)"

    def test_div_method(self):
        """Test div() method generates division assignment."""
        sig = Signal("value", 10)
        result = sig.div(2).to_js()
        assert result == "$value = ($value / 2)"


# ============================================================================
# Signal String Methods Tests
# ============================================================================

class TestSignalStringMethods:
    """Test string manipulation methods on Signal."""

    def test_upper_method(self):
        """Test upper() converts to toUpperCase()."""
        sig = Signal("text", "hello")
        result = sig.upper().to_js()
        assert result == "$text.toUpperCase()"

    def test_lower_method(self):
        """Test lower() converts to toLowerCase()."""
        sig = Signal("text", "HELLO")
        result = sig.lower().to_js()
        assert result == "$text.toLowerCase()"

    def test_strip_method(self):
        """Test strip() converts to trim()."""
        sig = Signal("text", "  hello  ")
        result = sig.strip().to_js()
        assert result == "$text.trim()"

    def test_contains_method(self):
        """Test contains() converts to includes()."""
        sig = Signal("text", "hello world")
        result = sig.contains("world").to_js()
        assert result == "$text.includes('world')"

    def test_length_property(self):
        """Test .length property access."""
        sig = Signal("text", "hello")
        result = sig.length.to_js()
        assert result == "$text.length"


# ============================================================================
# Signal Array Methods Tests
# ============================================================================

class TestSignalArrayMethods:
    """Test array manipulation methods on Signal."""

    def test_append_method(self):
        """Test append() converts to push()."""
        sig = Signal("items", [])
        result = sig.append("item").to_js()
        assert result == "$items.push('item')"

    def test_append_multiple_items(self):
        """Test append() with multiple items."""
        sig = Signal("items", [])
        result = sig.append("a", "b").to_js()
        assert "push" in result
        assert "'a'" in result
        assert "'b'" in result

    def test_pop_method(self):
        """Test pop() method."""
        sig = Signal("items", [1, 2, 3])
        result = sig.pop().to_js()
        assert result == "$items.pop()"

    def test_remove_method(self):
        """Test remove() converts to splice()."""
        sig = Signal("items", [1, 2, 3])
        result = sig.remove(1).to_js()
        assert "splice" in result
        assert "1" in result

    def test_join_method(self):
        """Test join() method."""
        sig = Signal("items", ["a", "b", "c"])
        result = sig.join(", ").to_js()
        assert result == "$items.join(', ')"

    def test_join_default_separator(self):
        """Test join() with default separator."""
        sig = Signal("items", ["a", "b", "c"])
        result = sig.join().to_js()
        assert result == "$items.join(',')"

    def test_slice_method(self):
        """Test slice() method."""
        sig = Signal("items", [1, 2, 3, 4, 5])
        result = sig.slice(0, 3).to_js()
        assert "slice" in result
        assert "0" in result
        assert "3" in result

    def test_slice_start_only(self):
        """Test slice() with start only."""
        sig = Signal("items", [1, 2, 3, 4, 5])
        result = sig.slice(2).to_js()
        assert "slice" in result
        assert "2" in result

    def test_prepend_method(self):
        """Test prepend() converts to unshift()."""
        sig = Signal("items", [2, 3])
        result = sig.prepend(1).to_js()
        assert "unshift" in result
        assert "1" in result


# ============================================================================
# Signal Math Methods Tests
# ============================================================================

class TestSignalMathMethods:
    """Test math methods on Signal."""

    def test_round_method(self):
        """Test round() with no arguments."""
        sig = Signal("value", 3.7)
        result = sig.round().to_js()
        assert result == "Math.round($value)"

    def test_round_method_with_decimals(self):
        """Test round() with decimal places."""
        sig = Signal("value", 3.14159)
        result = sig.round(2).to_js()
        # Should multiply, round, then divide
        assert "Math.round" in result
        assert "100" in result  # 10^2

    def test_abs_method(self):
        """Test abs() converts to Math.abs()."""
        sig = Signal("value", -5)
        result = sig.abs().to_js()
        assert result == "Math.abs($value)"

    def test_min_method(self):
        """Test min() converts to Math.min()."""
        sig = Signal("value", 10)
        result = sig.min(5).to_js()
        assert result == "Math.min($value, 5)"

    def test_max_method(self):
        """Test max() converts to Math.max()."""
        sig = Signal("value", 3)
        result = sig.max(10).to_js()
        assert result == "Math.max($value, 10)"

    def test_clamp_method(self):
        """Test clamp() generates min/max chain."""
        sig = Signal("value", 50)
        result = sig.clamp(0, 100).to_js()
        # Should be Math.max(Math.min(value, max), min)
        assert "Math.max" in result
        assert "Math.min" in result
        assert "0" in result
        assert "100" in result


# ============================================================================
# Conditional Helpers Tests
# ============================================================================

class TestConditionalHelpers:
    """Test conditional expression helpers."""

    def test_if_helper(self):
        """Test if_() generates ternary expression."""
        sig = Signal("grade", 90)
        result = if_(sig >= 90, "A", "B")
        assert "?" in str(result)
        assert ":" in str(result)
        assert "$grade" in str(result)

    def test_if_helper_nested(self):
        """Test nested if_() calls."""
        sig = Signal("grade", 85)
        result = if_(sig >= 90, "A", if_(sig >= 80, "B", "C"))
        js_str = str(result)
        assert "?" in js_str
        assert ":" in js_str

    def test_match_helper(self):
        """Test match() pattern matching."""
        sig = Signal("status", "loading")
        result = match(sig, idle="Ready", loading="Loading...", default="Unknown")
        js_str = str(result)
        assert "$status" in js_str
        assert "?" in js_str
        assert ":" in js_str

    def test_match_helper_with_default(self):
        """Test match() uses default value."""
        sig = Signal("color", "red")
        result = match(sig, red="#f00", blue="#00f", default="#000")
        js_str = str(result)
        assert "'#000'" in js_str or '"#000"' in js_str

    def test_switch_helper(self):
        """Test switch() sequential conditions."""
        sig = Signal("count", 5)
        result = switch([(sig > 10, "High"), (sig > 5, "Medium")], default="Low")
        js_str = str(result)
        assert "?" in js_str
        assert ":" in js_str


# ============================================================================
# Aggregation Helpers Tests
# ============================================================================

class TestAggregationHelpers:
    """Test logical aggregation helpers."""

    def test_all_helper(self):
        """Test all_() generates && chain."""
        s1 = Signal("a", True)
        s2 = Signal("b", True)
        s3 = Signal("c", True)
        result = all_(s1, s2, s3).to_js()
        assert "&&" in result
        assert "!!$a" in result
        assert "!!$b" in result
        assert "!!$c" in result

    def test_any_helper(self):
        """Test any_() generates || chain."""
        s1 = Signal("a", False)
        s2 = Signal("b", False)
        s3 = Signal("c", True)
        result = any_(s1, s2, s3).to_js()
        assert "||" in result
        assert "!!$a" in result
        assert "!!$b" in result
        assert "!!$c" in result

    def test_all_with_list(self):
        """Test all_() accepts a list."""
        signals = [Signal(f"s{i}", True) for i in range(3)]
        result = all_(signals).to_js()
        assert "&&" in result

    def test_any_with_list(self):
        """Test any_() accepts a list."""
        signals = [Signal(f"s{i}", False) for i in range(3)]
        result = any_(signals).to_js()
        assert "||" in result


# ============================================================================
# Class Helpers Tests
# ============================================================================

class TestClassHelpers:
    """Test CSS class helper functions."""

    def test_collect_helper(self):
        """Test collect() for conditional class collection."""
        s1 = Signal("isActive", True)
        s2 = Signal("isDisabled", False)
        result = collect([(s1, "active"), (s2, "disabled")])
        js_str = str(result)
        assert "filter" in js_str
        assert "join" in js_str

    def test_collect_custom_separator(self):
        """Test collect() with custom separator."""
        s1 = Signal("a", True)
        result = collect([(s1, "class1")], join_with=",")
        js_str = str(result)
        assert "," in js_str or "','" in js_str

    def test_classes_helper(self):
        """Test classes() generates object literal."""
        s1 = Signal("isActive", True)
        s2 = Signal("isHidden", False)
        result = classes(active=s1, hidden=s2)
        js_str = str(result)
        assert "{" in js_str
        assert "}" in js_str
        assert "active" in js_str
        assert "hidden" in js_str
        assert "$isActive" in js_str
        assert "$isHidden" in js_str

    def test_classes_with_hyphens(self):
        """Test classes() with hyphenated class names."""
        sig = Signal("isBold", True)
        result = classes(**{"font-bold": sig})
        js_str = str(result)
        assert "font-bold" in js_str
        assert "$isBold" in js_str


# ============================================================================
# HTTP Action Helpers Tests
# ============================================================================

class TestHttpActionHelpers:
    """Test HTTP action helper functions."""

    def test_post_helper(self):
        """Test post() generates @post() action."""
        result = post("/api/data")
        assert str(result) == "@post('/api/data')"

    def test_post_with_data(self):
        """Test post() with data payload."""
        sig = Signal("name", "")
        result = post("/api/users", name=sig)
        js_str = str(result)
        assert "@post" in js_str
        assert "/api/users" in js_str
        assert "$name" in js_str

    def test_get_helper(self):
        """Test get() generates @get() action."""
        result = get("/api/data")
        assert str(result) == "@get('/api/data')"

    def test_get_with_params(self):
        """Test get() with query parameters."""
        result = get("/api/data", page=1)
        js_str = str(result)
        assert "@get" in js_str
        assert "/api/data" in js_str

    def test_put_helper(self):
        """Test put() generates @put() action."""
        result = put("/api/data")
        assert str(result) == "@put('/api/data')"

    def test_patch_helper(self):
        """Test patch() generates @patch() action."""
        result = patch("/api/data")
        assert str(result) == "@patch('/api/data')"

    def test_delete_helper(self):
        """Test delete() generates @delete() action."""
        result = delete("/api/data")
        assert str(result) == "@delete('/api/data')"

    def test_http_action_with_multiple_params(self):
        """Test HTTP action with multiple parameters."""
        sig1 = Signal("username", "")
        sig2 = Signal("email", "")
        result = post("/register", username=sig1, email=sig2)
        js_str = str(result)
        assert "$username" in js_str
        assert "$email" in js_str


# ============================================================================
# Template Helpers Tests
# ============================================================================

class TestTemplateHelpers:
    """Test template and JavaScript helper functions."""

    def test_f_helper(self):
        """Test f() template literal helper."""
        sig = Signal("name", "World")
        result = f("Hello {name}!", name=sig)
        js_str = str(result)
        assert "`" in js_str
        assert "Hello" in js_str
        assert "${$name}" in js_str

    def test_f_helper_multiple_placeholders(self):
        """Test f() with multiple placeholders."""
        s1 = Signal("first", "John")
        s2 = Signal("last", "Doe")
        result = f("Name: {first} {last}", first=s1, last=s2)
        js_str = str(result)
        assert "${$first}" in js_str
        assert "${$last}" in js_str

    def test_js_helper(self):
        """Test js() raw JavaScript helper."""
        result = js("console.log('test')")
        assert str(result) == "console.log('test')"

    def test_js_helper_preserves_code(self):
        """Test js() preserves raw code."""
        code = "if (x > 5) { doSomething(); }"
        result = js(code)
        assert str(result) == code


# ============================================================================
# Property Access Tests
# ============================================================================

class TestPropertyAccess:
    """Test nested property and index access."""

    def test_nested_property_access(self):
        """Test accessing nested properties."""
        sig = Signal("user", {"name": "John", "email": "john@example.com"})
        result = sig.user.name.to_js()
        assert result == "$user.user.name"

    def test_index_access(self):
        """Test array index access."""
        sig = Signal("items", [1, 2, 3])
        result = sig[0].to_js()
        assert result == "$items[0]"

    def test_index_access_with_signal(self):
        """Test index access with signal index."""
        items = Signal("items", [1, 2, 3])
        index = Signal("idx", 0)
        result = items[index].to_js()
        assert "$items" in result
        assert "$idx" in result
        assert "[" in result
        assert "]" in result

    def test_chained_property_access(self):
        """Test chaining multiple property accesses."""
        sig = Signal("data", {})
        result = sig.user.profile.avatar.to_js()
        assert "$data.user.profile.avatar" in result


# ============================================================================
# DS Class Tests
# ============================================================================

class TestDSClass:
    """Test DS class for action generation."""

    def test_ds_get(self):
        """Test DS.get() action generator."""
        result = DS.get("/api/data")
        assert result == "@get('/api/data')"

    def test_ds_get_with_params(self):
        """Test DS.get() with query parameters."""
        result = DS.get("/api/data", page=1, limit=10)
        assert "@get" in result
        assert "/api/data" in result
        assert "page=1" in result
        assert "limit=10" in result

    def test_ds_post(self):
        """Test DS.post() action generator."""
        result = DS.post("/api/users")
        assert "@post" in result
        assert "/api/users" in result

    def test_ds_post_with_data(self):
        """Test DS.post() with data."""
        result = DS.post("/api/users", data={"name": "test"})
        assert "@post" in result
        # Should include data in some form
        assert "name" in result or "@data" in result

    def test_ds_put(self):
        """Test DS.put() action generator."""
        result = DS.put("/api/users/1")
        assert "@put" in result

    def test_ds_patch(self):
        """Test DS.patch() action generator."""
        result = DS.patch("/api/users/1")
        assert "@patch" in result

    def test_ds_delete(self):
        """Test DS.delete() action generator."""
        result = DS.delete("/api/users/1")
        assert "@delete" in result

    def test_ds_set(self):
        """Test DS.set() signal setter."""
        result = DS.set("count", 10)
        assert result == "$count = 10"

    def test_ds_set_string(self):
        """Test DS.set() with string value."""
        result = DS.set("name", "John")
        assert "$name = 'John'" in result

    def test_ds_set_bool(self):
        """Test DS.set() with boolean value."""
        result = DS.set("flag", True)
        assert "$flag = true" in result

    def test_ds_toggle(self):
        """Test DS.toggle() for boolean signals."""
        result = DS.toggle("isOpen")
        assert "$isOpen = !$isOpen" in result

    def test_ds_increment(self):
        """Test DS.increment() for numeric signals."""
        result = DS.increment("count")
        assert "$count += 1" in result

    def test_ds_increment_with_amount(self):
        """Test DS.increment() with custom amount."""
        result = DS.increment("count", 5)
        assert "$count += 5" in result

    def test_ds_decrement(self):
        """Test DS.decrement() for numeric signals."""
        result = DS.decrement("count")
        assert "$count -= 1" in result

    def test_ds_decrement_with_amount(self):
        """Test DS.decrement() with custom amount."""
        result = DS.decrement("count", 3)
        assert "$count -= 3" in result


# ============================================================================
# Edge Cases and Integration Tests
# ============================================================================

class TestEdgeCases:
    """Test edge cases and complex scenarios."""

    def test_complex_expression_chain(self):
        """Test complex chained expression."""
        sigs = Signals(age=25, licensed=True, hasInsurance=True)
        result = ((sigs.age >= 18) & sigs.licensed & sigs.hasInsurance).to_js()
        assert "$age" in result
        assert "$licensed" in result
        assert "$hasInsurance" in result
        assert "&&" in result

    def test_signal_method_chaining(self):
        """Test method chaining on signals."""
        sig = Signal("text", "  HELLO  ")
        result = sig.strip().lower().to_js()
        assert "trim" in result
        assert "toLowerCase" in result

    def test_math_method_chaining(self):
        """Test chaining math methods."""
        sig = Signal("value", -7.8)
        result = sig.abs().round().to_js()
        assert "Math.abs" in result
        assert "Math.round" in result

    def test_expression_with_literals(self):
        """Test expressions mixing signals and literals."""
        sig = Signal("x", 10)
        result = ((sig * 2) + 5).to_js()
        assert "$x" in result
        assert "*" in result
        assert "2" in result
        assert "+" in result
        assert "5" in result

    def test_nested_conditionals(self):
        """Test deeply nested conditionals."""
        sig = Signal("score", 85)
        result = if_(
            sig >= 90, "A",
            if_(sig >= 80, "B",
                if_(sig >= 70, "C", "F")
            )
        )
        js_str = str(result)
        assert "$score" in js_str
        # Should have multiple ternaries
        assert js_str.count("?") >= 2
        assert js_str.count(":") >= 2
