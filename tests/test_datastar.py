"""
Tests for Datastar attribute transformation with colon syntax.

Datastar v1.0+ uses colon separator for keyed plugins:
- data-on:click (instead of data-on-click)
- data-attr:title (instead of data-attr-title)
- data-class:hidden (instead of data-class-hidden)
"""

import pytest
from rusty_tags import Div, Input, Button, Span


class TestDatastarEventSyntax:
    """Test data-on:event colon syntax for event handlers."""

    def test_on_click_colon_syntax(self):
        """Test simple click event uses colon syntax."""
        result = str(Div("Click me", on_click="$count++"))
        assert 'data-on:click="$count++"' in result

    def test_on_custom_event_colon_syntax(self):
        """Test custom event with underscores converts properly."""
        result = str(Div("Test", on_custom_event="handleEvent()"))
        assert 'data-on:custom-event="handleEvent()"' in result

    def test_on_event_with_debounce_modifier(self):
        """Test event with debounce modifier uses colon syntax."""
        result = str(Input(on_input__debounce_500ms="search()"))
        assert 'data-on:input__debounce.500ms="search()"' in result

    def test_on_event_with_throttle_modifier(self):
        """Test event with throttle modifier uses colon syntax."""
        result = str(Div("Test", on_click__throttle_1s="action()"))
        assert 'data-on:click__throttle.1s="action()"' in result

    def test_on_event_with_multiple_modifiers(self):
        """Test event with multiple modifiers."""
        result = str(Div("Test", on_click__window__throttle_1s="handleGlobal()"))
        assert 'data-on:click__window__throttle.1s="handleGlobal()"' in result


class TestDatastarKeyedPlugins:
    """Test colon syntax for keyed plugins (attr, bind, signals, computed, style)."""
    
    def test_attr_title_colon_syntax(self):
        """Test data-attr:title uses colon syntax."""
        result = str(Div("Hover", ds_attr_title="$tooltip"))
        assert 'data-attr:title="$tooltip"' in result
    
    def test_attr_disabled_colon_syntax(self):
        """Test data-attr:disabled uses colon syntax."""
        result = str(Button("Submit", ds_attr_disabled="$isLoading"))
        assert 'data-attr:disabled="$isLoading"' in result
    
    def test_computed_signal_colon_syntax(self):
        """Test data-computed uses colon syntax."""
        result = str(Div(ds_computed_total="$price * $quantity"))
        assert 'data-computed:total="$price * $quantity"' in result
    
    def test_style_color_colon_syntax(self):
        """Test data-style with property uses colon syntax."""
        result = str(Span("Colored", ds_style_color="$textColor"))
        assert 'data-style:color="$textColor"' in result
    
    def test_bind_with_key_colon_syntax(self):
        """Test data-bind with key uses colon syntax."""
        result = str(Input(ds_bind_username=""))
        assert 'data-bind:username' in result


class TestDatastarNonKeyedPlugins:
    """Test that non-keyed plugins still use hyphen syntax (no colon)."""

    def test_text_hyphen_syntax(self):
        """Test data-text uses hyphen syntax (no key)."""
        result = str(Span(ds_text="$message"))
        assert 'data-text="$message"' in result

    def test_text_shorthand(self):
        """Test text shorthand maps to data-text."""
        result = str(Span(text="$message"))
        assert 'data-text="$message"' in result

    def test_show_hyphen_syntax(self):
        """Test data-show uses hyphen syntax (no key)."""
        result = str(Div("Hidden", ds_show="$isVisible"))
        assert 'data-show="$isVisible"' in result

    def test_show_shorthand(self):
        """Test show shorthand maps to data-show."""
        result = str(Div("Content", show="$isVisible"))
        assert 'data-show="$isVisible"' in result

    def test_effect_hyphen_syntax(self):
        """Test data-effect uses hyphen syntax (no key)."""
        result = str(Div(ds_effect="console.log($count)"))
        assert 'data-effect="console.log($count)"' in result

    def test_effect_shorthand(self):
        """Test effect shorthand maps to data-effect."""
        result = str(Div(effect="console.log($count)"))
        assert 'data-effect="console.log($count)"' in result


class TestDatastarSignalsHandler:
    """Test signals handler (value-based, not keyed)."""
    
    def test_signals_with_dict_value(self):
        """Test data-signals with dict value stays as-is."""
        result = str(Div(signals={"count": 0, "name": "test"}))
        assert 'data-signals=' in result
        # Should contain the JSON object
        assert "'count'" in result or '"count"' in result


class TestDatastarClassHandler:
    """Test class handler with object value."""
    
    def test_class_with_dict_value(self):
        """Test data-class with dict value for reactive classes."""
        result = str(Div("Test", cls={"active": "$isActive"}))
        assert 'data-class=' in result


class TestDatastarBindHandler:
    """Test bind handler (value-based)."""

    def test_bind_value_based(self):
        """Test data-bind with value (signal name in value)."""
        result = str(Input(bind="username"))
        assert 'data-bind="username"' in result

    def test_bind_strips_dollar_sign(self):
        """Test data-bind strips $ from signal reference."""
        result = str(Input(bind="$username"))
        assert 'data-bind="username"' in result


class TestKeyedPluginShorthand:
    """Test shorthand attributes for keyed plugins (data_attr_*, attr_*, etc.)."""

    def test_data_attr_aria_hidden(self):
        """Test data_attr_aria_hidden -> data-attr:aria-hidden."""
        result = str(Div("Test", data_attr_aria_hidden="$isHidden"))
        assert 'data-attr:aria-hidden="$isHidden"' in result

    def test_data_attr_title(self):
        """Test data_attr_title -> data-attr:title."""
        result = str(Div("Hover", data_attr_title="$tooltip"))
        assert 'data-attr:title="$tooltip"' in result

    def test_data_attr_disabled(self):
        """Test data_attr_disabled -> data-attr:disabled."""
        result = str(Button("Submit", data_attr_disabled="$isLoading"))
        assert 'data-attr:disabled="$isLoading"' in result

    def test_attr_title_shorthand(self):
        """Test attr_title -> data-attr:title (shorter form)."""
        result = str(Div("Hover", attr_title="$tooltip"))
        assert 'data-attr:title="$tooltip"' in result

    def test_attr_disabled_shorthand(self):
        """Test attr_disabled -> data-attr:disabled (shorter form)."""
        result = str(Button("Submit", attr_disabled="$isLoading"))
        assert 'data-attr:disabled="$isLoading"' in result

    def test_data_class_hidden(self):
        """Test data_class_hidden -> data-class:hidden."""
        result = str(Div("Test", data_class_hidden="$isHidden"))
        assert 'data-class:hidden="$isHidden"' in result

    def test_data_class_active(self):
        """Test data_class_active -> data-class:active."""
        result = str(Button("Tab", data_class_active="$isSelected"))
        assert 'data-class:active="$isSelected"' in result

    def test_data_computed_total(self):
        """Test data_computed_total -> data-computed:total."""
        result = str(Span(data_computed_total="$price * $quantity"))
        assert 'data-computed:total="$price * $quantity"' in result

    def test_data_style_color(self):
        """Test data_style_color -> data-style:color."""
        result = str(Span("Colored", data_style_color="$textColor"))
        assert 'data-style:color="$textColor"' in result

    def test_data_style_background_color(self):
        """Test data_style_background_color -> data-style:background-color."""
        result = str(Div("Box", data_style_background_color="$bgColor"))
        assert 'data-style:background-color="$bgColor"' in result

    def test_data_signals_with_key(self):
        """Test data_signals_count -> data-signals:count."""
        result = str(Div(data_signals_count="0"))
        assert 'data-signals:count="0"' in result


class TestOnKeysPlugin:
    """Tests for the data-on-keys plugin support (keyboard shortcuts)."""

    def test_simple_key(self):
        """Test simple key binding."""
        result = str(Div("Test", on_keys_escape="closeModal()"))
        assert 'data-on-keys:escape="closeModal()"' in result

    def test_key_combination(self):
        """Test key combination with modifier."""
        result = str(Div("Test", on_keys_ctrl_k="openSearch()"))
        assert 'data-on-keys:ctrl-k="openSearch()"' in result

    def test_key_with_el_modifier(self):
        """Test key with element-scoped modifier."""
        result = str(Input(on_keys_enter__el="submitForm()"))
        assert 'data-on-keys:enter__el="submitForm()"' in result

    def test_key_with_timing_modifier(self):
        """Test key with timing modifier (throttle)."""
        result = str(Div("Test", on_keys_space__throttle_1s="$counter++"))
        assert 'data-on-keys:space__throttle.1s="$counter++"' in result

    def test_key_with_multiple_modifiers(self):
        """Test key with multiple modifiers."""
        result = str(Input(on_keys_enter__el__stop="handleEnter()"))
        assert 'data-on-keys:enter__el__stop="handleEnter()"' in result

    def test_bare_on_keys_captures_all(self):
        """Test bare on_keys captures all keys."""
        result = str(Div("Test", on_keys="logKey($event)"))
        assert 'data-on-keys="logKey($event)"' in result

    def test_alt_combination(self):
        """Test alt key combination."""
        result = str(Div("Test", on_keys_alt_enter="newLine()"))
        assert 'data-on-keys:alt-enter="newLine()"' in result

    def test_meta_combination(self):
        """Test meta/cmd key combination."""
        result = str(Div("Test", on_keys_meta_s="saveDocument()"))
        assert 'data-on-keys:meta-s="saveDocument()"' in result

    def test_function_key(self):
        """Test function key binding."""
        result = str(Div("Test", on_keys_f1="showHelp()"))
        assert 'data-on-keys:f1="showHelp()"' in result

    def test_debounce_modifier(self):
        """Test key with debounce modifier."""
        result = str(Div("Test", on_keys_ctrl_s__debounce_500ms="saveDocument()"))
        assert 'data-on-keys:ctrl-s__debounce.500ms="saveDocument()"' in result


class TestDatastarExpressionDetection:
    """Test expression detection for Datastar syntax."""

    def test_signal_reference_detection(self):
        """Test that $ signal references are preserved as expressions."""
        result = str(Div(text="$counter"))
        assert '$counter' in result
        # Verify the value is preserved without modification

    def test_action_reference_detection(self):
        """Test that @ action references are preserved as expressions."""
        result = str(Button("Load", on_click="@get('/api/data')"))
        assert "@get('/api/data')" in result

    def test_javascript_equality_operator(self):
        """Test that === operator is preserved."""
        result = str(Div(show="$status === 'active'"))
        assert "===" in result

    def test_javascript_logical_and_operator(self):
        """Test that && operator is preserved."""
        result = str(Div(show="$isActive && $isVisible"))
        assert "&&" in result

    def test_javascript_logical_or_operator(self):
        """Test that || operator is preserved."""
        result = str(Div(show="$isAdmin || $isModerator"))
        assert "||" in result

    def test_complex_expression(self):
        """Test complex expression with multiple operators."""
        result = str(Div(show="($count > 0) && ($status === 'ready')"))
        assert ">=" not in result or ">" in result
        assert "===" in result
        assert "&&" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

