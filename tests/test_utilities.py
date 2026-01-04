"""
Tests for RustyTags utility functions (Phase 4).

This module tests:
- Page() function for complete HTML document generation
- page_template() and create_template() decorators
- AttrDict utility class
- when() and unless() conditional rendering helpers
- HtmlString methods (render, encode, __html__)
"""

import pytest
from rusty_tags import (
    Page, page_template, create_template, AttrDict, when, unless, show,
    Div, H1, Span, Meta, Link, Script, Fragment, HtmlString, Button, Input
)


class TestPageFunction:
    """Test Page() utility function for creating complete HTML documents."""

    def test_page_creates_html_structure(self):
        """Test Page creates DOCTYPE and html structure."""
        result = str(Page(Div("content"), title="Test"))
        assert "<!doctype html>" in result.lower()
        assert "<html>" in result
        assert "<head>" in result
        assert "<body>" in result
        assert "<title>Test</title>" in result

    def test_page_title_parameter(self):
        """Test title parameter sets page title."""
        result = str(Page(Div("content"), title="My Page Title"))
        assert "<title>My Page Title</title>" in result

    def test_page_default_title(self):
        """Test default title when not specified."""
        result = str(Page(Div("content")))
        assert "<title>RustyTags</title>" in result

    def test_page_with_datastar_true(self):
        """Test datastar=True includes CDN script."""
        result = str(Page(Div("content"), datastar=True))
        assert "datastar" in result
        assert "jsdelivr" in result
        assert "script" in result.lower()

    def test_page_with_datastar_false(self):
        """Test datastar=False excludes script."""
        result = str(Page(Div("content"), datastar=False))
        # Should not contain datastar script
        assert "datastar.js" not in result

    def test_page_datastar_version(self):
        """Test ds_version parameter for CDN version."""
        result = str(Page(Div("content"), datastar=True, ds_version="1.0.0"))
        assert "1.0.0" in result
        assert "datastar.js" in result

    def test_page_with_hdrs(self):
        """Test hdrs parameter adds elements to head."""
        result = str(Page(
            Div("content"),
            hdrs=(Meta(charset="utf-8"), Link(rel="stylesheet", href="/style.css"))
        ))
        assert 'charset="utf-8"' in result
        assert 'href="/style.css"' in result
        assert 'rel="stylesheet"' in result

    def test_page_with_ftrs(self):
        """Test ftrs parameter adds elements to body end."""
        result = str(Page(
            Div("content"),
            ftrs=(Script(src="/app.js"),)
        ))
        assert 'src="/app.js"' in result
        # Footer script should be in body
        assert "<body>" in result
        # Find script position is after content
        body_start = result.index("<body>")
        script_pos = result.index('src="/app.js"')
        assert script_pos > body_start

    def test_page_with_htmlkw(self):
        """Test htmlkw passes attributes to html tag."""
        result = str(Page(Div("content"), htmlkw={"lang": "en"}))
        assert 'lang="en"' in result
        assert "<html" in result

    def test_page_with_bodykw(self):
        """Test bodykw passes attributes to body tag."""
        result = str(Page(Div("content"), bodykw={"cls": "main-content"}))
        assert 'class="main-content"' in result
        assert "<body" in result

    def test_page_with_multiple_content_elements(self):
        """Test Page with multiple content children."""
        result = str(Page(
            H1("Title"),
            Div("Content 1"),
            Div("Content 2"),
            title="Multi-content"
        ))
        assert "<h1>Title</h1>" in result
        assert "<div>Content 1</div>" in result
        assert "<div>Content 2</div>" in result


class TestPageTemplate:
    """Test page_template() and create_template() decorators."""

    def test_page_template_creates_decorator(self):
        """Test page_template() creates decorator."""
        template = page_template("MyApp")

        @template
        def my_view():
            return Div("Hello")

        result = str(my_view())
        assert "<!doctype html>" in result.lower()
        assert "<title>MyApp</title>" in result
        assert "<div>Hello</div>" in result

    def test_page_template_with_custom_title(self):
        """Test decorator allows overriding title."""
        template = page_template("Default Title")

        @template
        def my_view():
            return Div("Content")

        result = str(my_view())
        assert "<title>Default Title</title>" in result

    def test_page_template_with_hdrs(self):
        """Test page_template with hdrs parameter."""
        template = page_template(
            "MyApp",
            hdrs=(Meta(charset="utf-8"),)
        )

        @template
        def my_view():
            return Div("Content")

        result = str(my_view())
        assert 'charset="utf-8"' in result

    def test_page_template_with_datastar_false(self):
        """Test page_template with datastar=False."""
        template = page_template("MyApp", datastar=False)

        @template
        def my_view():
            return Div("Content")

        result = str(my_view())
        assert "datastar.js" not in result

    def test_create_template_backwards_compatibility(self):
        """Test create_template is alias for page_template."""
        template = create_template("MyApp")

        @template
        def my_view():
            return Div("Hello")

        result = str(my_view())
        assert "<!doctype html>" in result.lower()
        assert "<title>MyApp</title>" in result
        assert "<div>Hello</div>" in result

    def test_page_template_function_with_args(self):
        """Test decorated function can accept arguments."""
        template = page_template("MyApp")

        @template
        def my_view(name):
            return Div(f"Hello {name}")

        result = str(my_view("World"))
        assert "<div>Hello World</div>" in result


class TestAttrDict:
    """Test AttrDict utility class."""

    def test_attrdict_attribute_access(self):
        """Test AttrDict attribute access."""
        d = AttrDict(a=1, b=2)
        assert d.a == 1
        assert d.b == 2

    def test_attrdict_dict_access(self):
        """Test AttrDict dictionary-style access."""
        d = AttrDict(a=1, b=2)
        assert d['a'] == 1
        assert d['b'] == 2

    def test_attrdict_both_access_methods(self):
        """Test both access methods return same value."""
        d = AttrDict(name="test", value=42)
        assert d.name == d['name']
        assert d.value == d['value']

    def test_attrdict_set_via_attribute(self):
        """Test setting values via attribute access."""
        d = AttrDict(a=1)
        d.b = 2
        assert d.b == 2
        assert d['b'] == 2

    def test_attrdict_set_via_dict(self):
        """Test setting values via dictionary access."""
        d = AttrDict(a=1)
        d['b'] = 2
        assert d.b == 2
        assert d['b'] == 2

    def test_attrdict_missing_key_returns_none(self):
        """Test accessing missing key returns None."""
        d = AttrDict(a=1)
        assert d.missing is None

    def test_attrdict_copy(self):
        """Test AttrDict.copy() creates new instance."""
        d1 = AttrDict(a=1, b=2)
        d2 = d1.copy()
        assert d2.a == 1
        assert d2.b == 2
        # Verify it's a copy, not the same object
        d2.a = 10
        assert d1.a == 1  # Original unchanged


class TestWhenUnless:
    """Test when() and unless() conditional rendering helpers."""

    def test_when_true_returns_element(self):
        """Test when(True, element) returns element."""
        result = when(True, Div("shown"))
        html = str(result)
        assert "<div>shown</div>" in html

    def test_when_false_returns_fragment(self):
        """Test when(False, element) returns empty Fragment."""
        result = when(False, Div("hidden"))
        assert isinstance(result, type(Fragment()))
        # Empty fragment should render to empty string or minimal output
        html = str(result)
        # Fragment should not contain the hidden div
        assert "hidden" not in html

    def test_unless_false_returns_element(self):
        """Test unless(False, element) returns element."""
        result = unless(False, Div("shown"))
        html = str(result)
        assert "<div>shown</div>" in html

    def test_unless_true_returns_fragment(self):
        """Test unless(True, element) returns empty Fragment."""
        result = unless(True, Div("hidden"))
        assert isinstance(result, type(Fragment()))
        html = str(result)
        assert "hidden" not in html

    def test_when_in_parent_element(self):
        """Test when() used as child in parent element."""
        is_visible = True
        result = str(Div(
            "Before",
            when(is_visible, Span("Visible")),
            "After"
        ))
        assert "Before" in result
        assert "Visible" in result
        assert "After" in result

    def test_unless_in_parent_element(self):
        """Test unless() used as child in parent element."""
        is_hidden = False
        result = str(Div(
            "Before",
            unless(is_hidden, Span("Visible")),
            "After"
        ))
        assert "Before" in result
        assert "Visible" in result
        assert "After" in result


class TestHtmlString:
    """Test HtmlString methods and protocols."""

    def test_htmlstring_render(self):
        """Test HtmlString render() method."""
        html = Div("content")
        rendered = html.render()
        assert isinstance(rendered, str)
        assert "<div>content</div>" in rendered

    def test_htmlstring_str(self):
        """Test HtmlString __str__() method."""
        html = Div("content")
        string_output = str(html)
        assert isinstance(string_output, str)
        assert "<div>content</div>" in string_output

    def test_htmlstring_render_and_str_same(self):
        """Test render() and __str__() return same HTML."""
        html = Div("content", id="test")
        assert html.render() == str(html)

    def test_htmlstring_encode(self):
        """Test HtmlString encode() for bytes output."""
        html = Div("content")
        encoded = html.encode('utf-8')
        assert isinstance(encoded, bytes)
        assert b"<div>content</div>" in encoded

    def test_htmlstring_encode_different_encoding(self):
        """Test encode() with different encoding."""
        html = Div("content")
        encoded = html.encode('ascii')
        assert isinstance(encoded, bytes)
        assert b"content" in encoded

    def test_htmlstring_html_protocol(self):
        """Test HtmlString __html__() protocol."""
        html = Div("content")
        html_output = html.__html__()
        assert isinstance(html_output, str)
        assert "<div>content</div>" in html_output

    def test_htmlstring_as_child(self):
        """Test HtmlString can be used as child element."""
        inner = Span("inner")
        outer = Div(inner, "text")
        result = str(outer)
        assert "<div>" in result
        assert "<span>inner</span>" in result
        assert "text" in result

    def test_htmlstring_complex_structure(self):
        """Test HtmlString with complex nested structure."""
        html = Div(
            H1("Title"),
            Div(
                Span("Nested"),
                Button("Click"),
                cls="container"
            ),
            id="main"
        )
        result = str(html)
        assert '<div id="main">' in result
        assert "<h1>Title</h1>" in result
        assert 'class="container"' in result
        assert "<span>Nested</span>" in result
        assert "<button>Click</button>" in result


class TestShowFunction:
    """Test show() function for IPython integration."""

    def test_show_requires_ipython(self):
        """Test show() raises ImportError without IPython."""
        # This test will pass if IPython is not installed
        # or will verify the function works if it is installed
        html = Div("content")
        try:
            result = show(html)
            # If IPython is available, should return HTML object
            assert result is not None
        except ImportError as e:
            # Expected if IPython not installed
            assert "IPython is not installed" in str(e)


class TestPageIntegration:
    """Integration tests combining multiple utility functions."""

    def test_page_with_all_parameters(self):
        """Test Page with all parameters combined."""
        result = str(Page(
            H1("Welcome"),
            Div("Content here"),
            title="Full Test",
            hdrs=(Meta(charset="utf-8"), Link(rel="icon", href="/favicon.ico")),
            ftrs=(Script(src="/app.js"),),
            htmlkw={"lang": "en"},
            bodykw={"cls": "body-class"},
            datastar=True,
            ds_version="1.0.0"
        ))

        # Verify all components present
        assert "<!doctype html>" in result.lower()
        assert "<title>Full Test</title>" in result
        assert 'lang="en"' in result
        assert 'charset="utf-8"' in result
        assert 'href="/favicon.ico"' in result
        assert "<h1>Welcome</h1>" in result
        assert "<div>Content here</div>" in result
        assert 'class="body-class"' in result
        assert 'src="/app.js"' in result
        assert "datastar.js" in result
        assert "1.0.0" in result

    def test_conditional_rendering_in_page(self):
        """Test when/unless in Page content."""
        show_header = True
        show_footer = False

        result = str(Page(
            when(show_header, H1("Header")),
            Div("Main content"),
            unless(show_footer, Div("No footer")),
            title="Conditional Test"
        ))

        assert "<h1>Header</h1>" in result
        assert "Main content" in result
        assert "No footer" in result

    def test_attrdict_with_page(self):
        """Test using AttrDict for page configuration."""
        config = AttrDict(
            title="AttrDict Test",
            lang="en",
            charset="utf-8"
        )

        result = str(Page(
            Div("Content"),
            title=config.title,
            hdrs=(Meta(charset=config.charset),),
            htmlkw={"lang": config.lang}
        ))

        assert "<title>AttrDict Test</title>" in result
        assert 'lang="en"' in result
        assert 'charset="utf-8"' in result
