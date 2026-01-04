"""
Integration tests for HTML parsing feature

Tests the HtmlString.parse() method and HtmlElement manipulation
as specified in spec.md
"""

import pytest
from rusty_tags import Div, Input, Button, Form, Span, HtmlElement


def test_parse_and_modify():
    """Test parsing and modifying attributes"""
    html = Form(Input(name="email"), Button("Submit"))
    doc = html.parse()

    # Find and modify
    for child in doc.children:
        if hasattr(child, 'tag') and child.tag == "input":
            child.attributes["required"] = "true"

    result = doc.to_html()
    assert 'required="true"' in result.content


def test_nested_traversal():
    """Test deep traversal of nested elements"""
    html = Div(Form(Input(type="text")))
    doc = html.parse()

    # Deep traversal
    form = doc.children[0]
    assert hasattr(form, 'tag')
    assert form.tag == "form"

    inp = form.children[0]
    assert hasattr(inp, 'tag')
    assert inp.tag == "input"
    assert inp.attributes["type"] == "text"


def test_parse_simple_element():
    """Test parsing a simple single element"""
    html = Div("Hello World", id="test")
    doc = html.parse()

    assert doc.tag == "div"
    assert doc.attributes["id"] == "test"
    assert len(doc.children) == 1
    assert doc.children[0] == "Hello World"


def test_parse_nested_structure():
    """Test parsing nested structures with multiple children"""
    html = Div(
        Div("Child 1", cls="child"),
        Div("Child 2", cls="child"),
        Div("Child 3", cls="child")
    )
    doc = html.parse()

    assert doc.tag == "div"
    assert len(doc.children) == 3
    for i, child in enumerate(doc.children):
        assert hasattr(child, 'tag')
        assert child.tag == "div"
        assert child.attributes["class"] == "child"


def test_parse_mixed_children():
    """Test parsing mixed text and element children"""
    html = Div("Text before", Button("Click me"), "Text after")
    doc = html.parse()

    assert doc.tag == "div"
    assert len(doc.children) == 3
    assert doc.children[0] == "Text before"
    assert hasattr(doc.children[1], 'tag')
    assert doc.children[1].tag == "button"
    assert doc.children[2] == "Text after"


def test_preserve_attributes_roundtrip():
    """Test that all attributes are preserved during parse roundtrip"""
    html = Input(
        type="text",
        name="username",
        placeholder="Enter username",
        required=True,
        maxlength="50"
    )
    doc = html.parse()

    # Check attributes
    assert doc.attributes["type"] == "text"
    assert doc.attributes["name"] == "username"
    assert doc.attributes["placeholder"] == "Enter username"
    assert "required" in doc.attributes
    assert doc.attributes["maxlength"] == "50"

    # Roundtrip
    result = doc.to_html()
    assert "type=\"text\"" in result.content
    assert "name=\"username\"" in result.content
    assert "placeholder=\"Enter username\"" in result.content
    assert "required" in result.content
    assert "maxlength=\"50\"" in result.content


def test_html_element_type():
    """Test that parsed result is HtmlElement"""
    html = Div("Content")
    doc = html.parse()

    assert isinstance(doc, HtmlElement)
    assert hasattr(doc, 'tag')
    assert hasattr(doc, 'attributes')
    assert hasattr(doc, 'children')


def test_modify_and_serialize():
    """Test modifying element and serializing back"""
    html = Div("Original", id="test")
    doc = html.parse()

    # Modify attributes
    doc.attributes["id"] = "modified"
    doc.attributes["data-test"] = "value"

    # Serialize
    result = doc.to_html()
    assert 'id="modified"' in result.content
    assert 'data-test="value"' in result.content


def test_form_validation_use_case():
    """Test the use case from spec: adding validation to form inputs"""
    html = Form(
        Input(type="email", name="email"),
        Input(type="password", name="password"),
        Button("Submit")
    )
    doc = html.parse()

    # Add required attribute to all inputs
    input_count = 0
    for child in doc.children:
        if hasattr(child, 'tag') and child.tag == "input":
            child.attributes["required"] = "true"
            child.attributes["aria-required"] = "true"
            input_count += 1

    result = doc.to_html()

    # Check that modifications were applied (2 inputs were modified)
    assert input_count == 2
    assert 'required="true"' in result.content
    assert 'aria-required="true"' in result.content
    # Button should not have these attributes
    assert '<button>Submit</button>' in result.content


def test_empty_element():
    """Test parsing element with no children"""
    # Div with empty string to ensure it returns HtmlString
    html = Div("")
    doc = html.parse()

    assert doc.tag == "div"
    # Empty string might be preserved or filtered, so check length is 0 or 1
    assert len(doc.children) <= 1


def test_text_node_handling():
    """Test that text nodes are properly handled in children list"""
    html = Div("Plain text content")
    doc = html.parse()

    assert doc.tag == "div"
    assert len(doc.children) == 1
    assert isinstance(doc.children[0], str)
    assert doc.children[0] == "Plain text content"


def test_parse_with_span_mixed_content():
    """Test parse() with mixed content including Span elements"""
    html = Div("text", Span("span content"), "more text")
    doc = html.parse()

    assert doc.tag == "div"
    assert len(doc.children) == 3
    assert doc.children[0] == "text"
    assert hasattr(doc.children[1], 'tag')
    assert doc.children[1].tag == "span"
    assert doc.children[2] == "more text"


def test_html_element_dot_notation_attribute_access():
    """Test HtmlElement attribute access via dot notation (if supported)"""
    html = Div("content", id="test", data_custom="value")
    doc = html.parse()

    # Test reading attributes via dict access
    assert doc.attributes["id"] == "test"
    assert doc.attributes.get("data-custom") == "value"

    # Test setting new attribute via dict
    doc.attributes["new_attr"] = "new_value"

    # Verify roundtrip (note: underscores become hyphens in attributes)
    result = doc.to_html()
    assert 'new-attr="new_value"' in result.content
    assert 'id="test"' in result.content


def test_html_element_as_child_protocol():
    """Test HtmlElement __html__ protocol works as child in new elements"""
    # Parse an element to HtmlElement
    inner_html = Span("Inner content", cls="inner")
    parsed_element = inner_html.parse()

    # Use HtmlElement as child in new Div
    outer_html = Div(parsed_element, cls="outer")

    # Verify serialization works
    result = str(outer_html)
    assert '<div class="outer">' in result
    assert '<span class="inner">Inner content</span>' in result

    # Verify nested content preserved
    assert "Inner content" in result


def test_html_element_repr():
    """Test HtmlElement __repr__ for debugging provides informative output"""
    html = Div("content", Span("nested"), id="test", cls="demo")
    doc = html.parse()

    # Get repr string
    repr_str = repr(doc)

    # Verify it's informative (should show tag, possibly attributes or children count)
    assert "HtmlElement" in repr_str or "div" in repr_str.lower()

    # For nested element
    nested_html = Form(Input(name="email"), Input(name="password"), Button("Submit"))
    nested_doc = nested_html.parse()
    nested_repr = repr(nested_doc)

    assert "HtmlElement" in nested_repr or "form" in nested_repr.lower()


def test_deeply_nested_structure_traversal():
    """Test parsing and traversing deeply nested structures"""
    html = Div(
        Div(
            Div(
                Span("Deep content", id="deep")
            )
        )
    )
    doc = html.parse()

    # Traverse to deepest element
    level1 = doc.children[0]
    assert hasattr(level1, 'tag')
    assert level1.tag == "div"

    level2 = level1.children[0]
    assert hasattr(level2, 'tag')
    assert level2.tag == "div"

    level3 = level2.children[0]
    assert hasattr(level3, 'tag')
    assert level3.tag == "span"
    assert level3.attributes["id"] == "deep"


def test_complex_roundtrip_preserves_structure():
    """Test parse/modify/serialize roundtrip preserves structure"""
    # Create complex HTML with multiple attributes
    html = Form(
        Div(
            Input(type="email", name="email", placeholder="Email", cls="input-field"),
            Input(type="password", name="password", placeholder="Password", cls="input-field")
        ),
        Button("Submit", type="submit", cls="btn-primary")
    )

    # Parse to HtmlElement
    doc = html.parse()

    # Modify some attributes
    doc.attributes["method"] = "post"
    doc.attributes["action"] = "/login"

    # Find and modify first div
    div_child = doc.children[0]
    if hasattr(div_child, 'tag') and div_child.tag == "div":
        div_child.attributes["class"] = "form-group"

    # Serialize with to_html()
    result = doc.to_html()

    # Verify structure preserved
    assert "<form" in result.content
    assert "<div" in result.content
    assert '<input' in result.content
    assert "<button" in result.content

    # Verify modifications applied
    assert 'method="post"' in result.content
    assert 'action="/login"' in result.content
    assert 'class="form-group"' in result.content

    # Verify unmodified parts unchanged
    assert 'type="email"' in result.content
    assert 'name="email"' in result.content
    assert 'placeholder="Email"' in result.content


def test_modify_specific_child_in_traversal():
    """Test finding and modifying specific children during traversal"""
    html = Div(
        Input(type="text", name="field1"),
        Span("Label"),
        Input(type="text", name="field2"),
        Button("Click")
    )
    doc = html.parse()

    # Iterate through children and modify inputs only
    modified_count = 0
    for child in doc.children:
        if hasattr(child, 'tag') and child.tag == "input":
            child.attributes["required"] = "true"
            child.attributes["class"] = "required-field"
            modified_count += 1

    # Serialize and verify
    result = doc.to_html()

    # Should have modified 2 inputs
    assert result.content.count('required="true"') == 2
    assert result.content.count('class="required-field"') == 2

    # Span and Button should be unmodified
    assert "<span>Label</span>" in result.content
    assert "<button>Click</button>" in result.content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
