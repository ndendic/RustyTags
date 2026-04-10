"""
Parametrized test matrix for Datastar kwarg → attribute mapping.

Tests every keyed plugin × kwarg form combination to lock behavior and
prevent regressions during the colon-syntax migration.

Keyed plugins: on, bind, attr, class, signals, computed, style
Kwarg forms: shorthand (on_click), ds_* (ds_on_click), data_* (data_on_click), raw dict

See: https://data-star.dev/guide/getting-started (Datastar v1.0+ colon syntax)
"""

import pytest
from rusty_tags import Div, Input, Button, Span


# =============================================================================
# KEYED PLUGIN × KWARG FORM MATRIX
# =============================================================================
#
# Each tuple: (description, tag_kwargs, expected_substring)
#
# Forms tested per plugin:
#   1. shorthand    — on_click, attr_title, bind (bare)
#   2. ds_* prefix  — ds_on_click, ds_attr_title, ds_bind_username
#   3. data_* prefix — data_on_click, data_attr_title, data_bind_title
#   4. raw dict     — **{"data-on:click": "..."} (bypass all normalization)

KEYED_PLUGIN_CASES = [
    # =========================================================================
    # ON (event handler)
    # =========================================================================
    ("on / shorthand: on_click",
     {"on_click": "$count++"},
     'data-on:click="$count++"'),

    ("on / ds_* prefix: ds_on_click",
     {"ds_on_click": "$count++"},
     'data-on:click="$count++"'),

    ("on / data_* prefix: data_on_click",
     {"data_on_click": "$count++"},
     'data-on:click="$count++"'),

    ("on / raw dict: data-on:click",
     {"data-on:click": "$count++"},
     'data-on:click="$count++"'),

    ("on / shorthand with modifier: on_input__debounce_500ms",
     {"on_input__debounce_500ms": "search()"},
     'data-on:input__debounce.500ms="search()"'),

    ("on / data_* with underscore event: data_on_custom_event",
     {"data_on_custom_event": "handle()"},
     'data-on:custom-event="handle()"'),

    # =========================================================================
    # BIND (two-way binding)
    # =========================================================================
    ("bind / shorthand bare: bind",
     {"bind": "username"},
     'data-bind="username"'),

    ("bind / ds_* keyed: ds_bind_username",
     {"ds_bind_username": ""},
     'data-bind:username'),

    ("bind / data_* keyed: data_bind_title",
     {"data_bind_title": "True"},
     'data-bind:title'),

    ("bind / raw dict: data-bind:email",
     {"data-bind:email": ""},
     'data-bind:email'),

    # =========================================================================
    # ATTR (reactive attributes)
    # =========================================================================
    ("attr / shorthand: attr_title",
     {"attr_title": "$tooltip"},
     'data-attr:title="$tooltip"'),

    ("attr / ds_* prefix: ds_attr_disabled",
     {"ds_attr_disabled": "$isLoading"},
     'data-attr:disabled="$isLoading"'),

    ("attr / data_* prefix: data_attr_aria_hidden",
     {"data_attr_aria_hidden": "$isHidden"},
     'data-attr:aria-hidden="$isHidden"'),

    ("attr / raw dict: data-attr:title",
     {"data-attr:title": "$tooltip"},
     'data-attr:title="$tooltip"'),

    # =========================================================================
    # CLASS (reactive CSS classes)
    # =========================================================================
    ("class / ds_* prefix: ds_class_hidden",
     {"ds_class_hidden": "$isHidden"},
     'data-class:hidden="$isHidden"'),

    ("class / data_* prefix: data_class_hidden",
     {"data_class_hidden": "$isHidden"},
     'data-class:hidden="$isHidden"'),

    ("class / data_* prefix: data_class_active",
     {"data_class_active": "$isSelected"},
     'data-class:active="$isSelected"'),

    ("class / raw dict: data-class:hidden",
     {"data-class:hidden": "$isHidden"},
     'data-class:hidden="$isHidden"'),

    # =========================================================================
    # SIGNALS (reactive state)
    # =========================================================================
    ("signals / ds_* keyed: ds_signals_count",
     {"ds_signals_count": "0"},
     'data-signals:count="0"'),

    ("signals / data_* keyed: data_signals_count",
     {"data_signals_count": "0"},
     'data-signals:count="0"'),

    ("signals / raw dict: data-signals:count",
     {"data-signals:count": "0"},
     'data-signals:count="0"'),

    # =========================================================================
    # COMPUTED (derived signals)
    # =========================================================================
    ("computed / ds_* prefix: ds_computed_total",
     {"ds_computed_total": "$price * $qty"},
     'data-computed:total="$price * $qty"'),

    ("computed / data_* prefix: data_computed_total",
     {"data_computed_total": "$price * $qty"},
     'data-computed:total="$price * $qty"'),

    ("computed / raw dict: data-computed:total",
     {"data-computed:total": "$price * $qty"},
     'data-computed:total="$price * $qty"'),

    # =========================================================================
    # STYLE (reactive inline styles)
    # =========================================================================
    ("style / ds_* prefix: ds_style_color",
     {"ds_style_color": "$textColor"},
     'data-style:color="$textColor"'),

    ("style / data_* prefix: data_style_color",
     {"data_style_color": "$textColor"},
     'data-style:color="$textColor"'),

    ("style / data_* compound: data_style_background_color",
     {"data_style_background_color": "$bgColor"},
     'data-style:background-color="$bgColor"'),

    ("style / raw dict: data-style:color",
     {"data-style:color": "$textColor"},
     'data-style:color="$textColor"'),
]


@pytest.mark.parametrize(
    "description, kwargs, expected",
    KEYED_PLUGIN_CASES,
    ids=[c[0] for c in KEYED_PLUGIN_CASES],
)
def test_keyed_plugin_kwarg_form(description, kwargs, expected):
    """Verify that every kwarg form for keyed plugins produces correct colon syntax."""
    result = str(Div("test", **kwargs))
    assert expected in result, (
        f"FAILED: {description}\n"
        f"  kwargs:   {kwargs}\n"
        f"  expected: {expected}\n"
        f"  got:      {result}"
    )


# =============================================================================
# NON-KEYED PLUGINS (should NOT use colon syntax)
# =============================================================================

NON_KEYED_PLUGIN_CASES = [
    ("text / shorthand", {"text": "$message"}, 'data-text="$message"'),
    ("text / ds_* prefix", {"ds_text": "$message"}, 'data-text="$message"'),
    ("show / shorthand", {"show": "$isVisible"}, 'data-show="$isVisible"'),
    ("show / ds_* prefix", {"ds_show": "$isVisible"}, 'data-show="$isVisible"'),
    ("effect / shorthand", {"effect": "console.log($x)"}, 'data-effect="console.log($x)"'),
    ("effect / ds_* prefix", {"ds_effect": "console.log($x)"}, 'data-effect="console.log($x)"'),
]


@pytest.mark.parametrize(
    "description, kwargs, expected",
    NON_KEYED_PLUGIN_CASES,
    ids=[c[0] for c in NON_KEYED_PLUGIN_CASES],
)
def test_non_keyed_plugin_kwarg_form(description, kwargs, expected):
    """Verify that non-keyed plugins use hyphen syntax (no colon)."""
    result = str(Div("test", **kwargs))
    assert expected in result, (
        f"FAILED: {description}\n"
        f"  kwargs:   {kwargs}\n"
        f"  expected: {expected}\n"
        f"  got:      {result}"
    )


# =============================================================================
# ON-KEYS PLUGIN (special colon syntax: data-on-keys:*)
# =============================================================================

ON_KEYS_CASES = [
    ("on_keys bare", {"on_keys": "logKey($event)"}, 'data-on-keys="logKey($event)"'),
    ("on_keys_escape", {"on_keys_escape": "close()"}, 'data-on-keys:escape="close()"'),
    ("on_keys_ctrl_k", {"on_keys_ctrl_k": "search()"}, 'data-on-keys:ctrl-k="search()"'),
    ("on_keys with modifier", {"on_keys_enter__el": "submit()"}, 'data-on-keys:enter__el="submit()"'),
]


@pytest.mark.parametrize(
    "description, kwargs, expected",
    ON_KEYS_CASES,
    ids=[c[0] for c in ON_KEYS_CASES],
)
def test_on_keys_plugin(description, kwargs, expected):
    """Verify on-keys plugin uses data-on-keys:* syntax."""
    result = str(Div("test", **kwargs))
    assert expected in result, (
        f"FAILED: {description}\n"
        f"  kwargs:   {kwargs}\n"
        f"  expected: {expected}\n"
        f"  got:      {result}"
    )
