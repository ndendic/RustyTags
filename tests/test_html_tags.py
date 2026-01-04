"""
Comprehensive tests for HTML tag generation in RustyTags.

Tests cover:
- Basic HTML tags (Div, Span, P, etc.)
- Heading tags (H1-H6)
- Form elements (Form, Input, Button, Label, Select, Textarea)
- Table elements (Table, Thead, Tbody, Tfoot, Tr, Th, Td)
- List elements (Ul, Ol, Li)
- Semantic HTML5 tags (Header, Footer, Nav, Main, Article, Section, Aside)
- Media tags (Img, Audio, Video, Source, Track)
- Document structure (Html, Head, Body, Title, Meta, Link, Script)
- Special tags (Fragment, Safe, CustomTag)
- Attribute mappings and transformations
"""

import pytest
from rusty_tags import (
    # Basic tags
    Div, Span, P, A, B, I, Em, Strong, Code,
    # Heading tags
    H1, H2, H3, H4, H5, H6,
    # Form tags
    Form, Input, Button, Label, Select, OptionEl, Textarea,
    # Table tags
    Table, Thead, Tbody, Tfoot, Tr, Th, Td, Caption,
    # List tags
    Ul, Ol, Li,
    # Semantic tags
    Header, Footer, Nav, Main, Article, Section, Aside,
    # Media tags
    Img, Audio, Video, Source, Track,
    # Document tags
    Html, Head, Body, Title, Meta, Link, Script,
    # Other tags
    Br, Hr, Iframe, Details, Summary, Figure, Figcaption,
    Address, Pre, Blockquote,
    # Special tags
    Fragment, Safe, CustomTag
)


class TestBasicTags:
    """Test basic HTML tag generation with text content."""

    def test_div_with_text_content(self):
        """Test Div renders with simple text content."""
        result = str(Div("Hello World"))
        assert result == "<div>Hello World</div>"

    def test_span_with_text_content(self):
        """Test Span renders with simple text content."""
        result = str(Span("test"))
        assert result == "<span>test</span>"

    def test_p_with_text_content(self):
        """Test P (paragraph) renders with text content."""
        result = str(P("This is a paragraph."))
        assert result == "<p>This is a paragraph.</p>"


class TestAttributeBasics:
    """Test HTML tags with single and multiple attributes."""

    def test_div_with_id_attribute(self):
        """Test Div with id attribute."""
        result = str(Div("Content", id="main"))
        assert 'id="main"' in result
        assert "<div" in result
        assert ">Content</div>" in result

    def test_div_with_cls_attribute(self):
        """Test Div with cls (class) attribute."""
        result = str(Div("Content", cls="container"))
        assert 'class="container"' in result

    def test_input_with_multiple_attributes(self):
        """Test Input with multiple attributes."""
        result = str(Input(type="text", name="username", value="test", placeholder="Enter username"))
        assert 'type="text"' in result
        assert 'name="username"' in result
        assert 'value="test"' in result
        assert 'placeholder="Enter username"' in result


class TestBooleanAttributes:
    """Test boolean attributes (required, disabled, checked)."""

    def test_input_required_true(self):
        """Test Input with required=True renders valueless attribute."""
        result = str(Input(type="text", required=True))
        assert "required" in result
        # Boolean should not have ="value"
        assert 'required=""' not in result

    def test_input_disabled_true(self):
        """Test Input with disabled=True renders valueless attribute."""
        result = str(Input(type="text", disabled=True))
        assert "disabled" in result

    def test_input_checked_true(self):
        """Test Input checkbox with checked=True renders valueless attribute."""
        result = str(Input(type="checkbox", checked=True))
        assert "checked" in result

    def test_input_required_false(self):
        """Test Input with required=False omits the attribute."""
        result = str(Input(type="text", required=False))
        assert "required" not in result


class TestNestedChildren:
    """Test HTML tags with nested children."""

    def test_nested_divs(self):
        """Test nested Div elements."""
        result = str(Div(Div(Div("content"))))
        assert "<div><div><div>content</div></div></div>" == result

    def test_div_with_multiple_children(self):
        """Test Div with multiple P children."""
        result = str(Div(P("First"), P("Second"), P("Third")))
        assert "<div>" in result
        assert "<p>First</p>" in result
        assert "<p>Second</p>" in result
        assert "<p>Third</p>" in result
        assert "</div>" in result

    def test_mixed_text_and_element_children(self):
        """Test Div with mixed text and element children."""
        result = str(Div("text", Span("inner"), "more text"))
        assert "<div>text<span>inner</span>more text</div>" == result


class TestSpecialChildren:
    """Test HTML tags with numeric, None, and empty children."""

    def test_div_with_integer_child(self):
        """Test Div with integer child converts to string."""
        result = str(Div(42))
        assert result == "<div>42</div>"

    def test_div_with_float_child(self):
        """Test Div with float child converts to string."""
        result = str(Div(3.14))
        assert result == "<div>3.14</div>"

    def test_div_with_none_children(self):
        """Test Div with None children ignores None values."""
        result = str(Div("before", None, "after"))
        assert result == "<div>beforeafter</div>"

    def test_empty_div(self):
        """Test empty Div renders proper empty element."""
        result = str(Div())
        assert result == "<div/>"


class TestHeadingTags:
    """Test all heading tags H1-H6."""

    def test_h1_heading(self):
        """Test H1 heading tag."""
        result = str(H1("Heading 1"))
        assert result == "<h1>Heading 1</h1>"

    def test_h2_heading(self):
        """Test H2 heading tag."""
        result = str(H2("Heading 2"))
        assert result == "<h2>Heading 2</h2>"

    def test_h3_heading(self):
        """Test H3 heading tag."""
        result = str(H3("Heading 3"))
        assert result == "<h3>Heading 3</h3>"

    def test_h4_heading(self):
        """Test H4 heading tag."""
        result = str(H4("Heading 4"))
        assert result == "<h4>Heading 4</h4>"

    def test_h5_heading(self):
        """Test H5 heading tag."""
        result = str(H5("Heading 5"))
        assert result == "<h5>Heading 5</h5>"

    def test_h6_heading(self):
        """Test H6 heading tag."""
        result = str(H6("Heading 6"))
        assert result == "<h6>Heading 6</h6>"


class TestFormTags:
    """Test form elements (Form, Input, Button, Label, Select, Textarea)."""

    def test_form_with_method_and_action(self):
        """Test Form with method and action attributes."""
        result = str(Form(Input(type="text"), Button("Submit"), method="post", action="/submit"))
        assert 'method="post"' in result
        assert 'action="/submit"' in result
        assert "<form" in result
        assert "<input" in result
        assert "<button>Submit</button>" in result
        assert "</form>" in result

    def test_input_type_text(self):
        """Test Input with type=text."""
        result = str(Input(type="text", name="username"))
        assert 'type="text"' in result
        assert 'name="username"' in result

    def test_input_type_email(self):
        """Test Input with type=email."""
        result = str(Input(type="email", name="email"))
        assert 'type="email"' in result

    def test_input_type_password(self):
        """Test Input with type=password."""
        result = str(Input(type="password", name="pass"))
        assert 'type="password"' in result

    def test_input_type_number(self):
        """Test Input with type=number."""
        result = str(Input(type="number", name="age"))
        assert 'type="number"' in result

    def test_input_type_checkbox(self):
        """Test Input with type=checkbox."""
        result = str(Input(type="checkbox", name="agree", value="yes"))
        assert 'type="checkbox"' in result
        assert 'value="yes"' in result

    def test_input_type_radio(self):
        """Test Input with type=radio."""
        result = str(Input(type="radio", name="choice", value="A"))
        assert 'type="radio"' in result
        assert 'value="A"' in result

    def test_select_and_option_elements(self):
        """Test Select with Option children."""
        result = str(Select(
            OptionEl("Option 1", value="1"),
            OptionEl("Option 2", value="2", selected=True),
            name="choice"
        ))
        assert "<select" in result
        assert 'name="choice"' in result
        assert "<option" in result
        assert 'value="1"' in result
        assert 'value="2"' in result
        assert "selected" in result
        assert "</select>" in result

    def test_textarea_with_content(self):
        """Test Textarea with rows, cols and content."""
        result = str(Textarea("Default text", rows="4", cols="50"))
        assert "<textarea" in result
        assert 'rows="4"' in result
        assert 'cols="50"' in result
        assert "Default text" in result
        assert "</textarea>" in result

    def test_label_with_for_attribute(self):
        """Test Label with _for attribute mapping."""
        result = str(Label("Username:", _for="username-input"))
        assert "<label" in result
        assert 'for="username-input"' in result
        assert "Username:" in result
        assert "</label>" in result

    def test_label_with_fr_attribute(self):
        """Test Label with fr attribute mapping to for."""
        result = str(Label("Email:", fr="email-input"))
        assert 'for="email-input"' in result


class TestTableTags:
    """Test table structure elements."""

    def test_complete_table_structure(self):
        """Test complete table with all parts."""
        result = str(
            Table(
                Thead(
                    Tr(Th("Header 1"), Th("Header 2"))
                ),
                Tbody(
                    Tr(Td("Cell 1"), Td("Cell 2")),
                    Tr(Td("Cell 3"), Td("Cell 4"))
                ),
                Tfoot(
                    Tr(Td("Footer 1"), Td("Footer 2"))
                )
            )
        )
        assert "<table>" in result
        assert "<thead>" in result
        assert "<tbody>" in result
        assert "<tfoot>" in result
        assert "<tr>" in result
        assert "<th>Header 1</th>" in result
        assert "<td>Cell 1</td>" in result
        assert "</table>" in result

    def test_td_with_colspan(self):
        """Test Td with colspan attribute."""
        result = str(Td("Wide cell", colspan="2"))
        assert 'colspan="2"' in result

    def test_td_with_rowspan(self):
        """Test Td with rowspan attribute."""
        result = str(Td("Tall cell", rowspan="3"))
        assert 'rowspan="3"' in result


class TestListTags:
    """Test list elements (Ul, Ol, Li)."""

    def test_unordered_list(self):
        """Test Ul with Li children."""
        result = str(Ul(Li("Item 1"), Li("Item 2"), Li("Item 3")))
        assert "<ul>" in result
        assert "<li>Item 1</li>" in result
        assert "<li>Item 2</li>" in result
        assert "<li>Item 3</li>" in result
        assert "</ul>" in result

    def test_ordered_list(self):
        """Test Ol with Li children."""
        result = str(Ol(Li("First"), Li("Second"), Li("Third")))
        assert "<ol>" in result
        assert "<li>First</li>" in result
        assert "<li>Second</li>" in result
        assert "<li>Third</li>" in result
        assert "</ol>" in result


class TestSemanticTags:
    """Test semantic HTML5 tags."""

    def test_header_tag(self):
        """Test Header semantic tag."""
        result = str(Header(H1("Site Title")))
        assert "<header>" in result
        assert "<h1>Site Title</h1>" in result
        assert "</header>" in result

    def test_footer_tag(self):
        """Test Footer semantic tag."""
        result = str(Footer(P("Copyright 2025")))
        assert "<footer>" in result
        assert "<p>Copyright 2025</p>" in result
        assert "</footer>" in result

    def test_nav_tag(self):
        """Test Nav semantic tag."""
        result = str(Nav(A("Home", href="/")))
        assert "<nav>" in result
        assert '<a href="/">Home</a>' in result
        assert "</nav>" in result

    def test_main_tag(self):
        """Test Main semantic tag."""
        result = str(Main(P("Main content")))
        assert "<main>" in result
        assert "<p>Main content</p>" in result
        assert "</main>" in result

    def test_article_tag(self):
        """Test Article semantic tag."""
        result = str(Article(H2("Article Title"), P("Article content")))
        assert "<article>" in result
        assert "<h2>Article Title</h2>" in result
        assert "</article>" in result

    def test_section_tag(self):
        """Test Section semantic tag."""
        result = str(Section(H3("Section Title")))
        assert "<section>" in result
        assert "<h3>Section Title</h3>" in result
        assert "</section>" in result

    def test_aside_tag(self):
        """Test Aside semantic tag."""
        result = str(Aside(P("Sidebar content")))
        assert "<aside>" in result
        assert "<p>Sidebar content</p>" in result
        assert "</aside>" in result


class TestMediaTags:
    """Test media tags (Img, Audio, Video, Source, Track)."""

    def test_img_with_src_and_alt(self):
        """Test Img with src and alt attributes."""
        result = str(Img(src="/images/photo.jpg", alt="A photo"))
        assert "<img" in result
        assert 'src="/images/photo.jpg"' in result
        assert 'alt="A photo"' in result

    def test_video_with_source_children(self):
        """Test Video with Source children."""
        result = str(
            Video(
                Source(src="video.mp4", type="video/mp4"),
                Source(src="video.webm", type="video/webm")
            )
        )
        assert "<video>" in result
        assert "<source" in result
        assert 'src="video.mp4"' in result
        assert 'type="video/mp4"' in result
        assert 'src="video.webm"' in result
        assert "</video>" in result

    def test_audio_with_controls(self):
        """Test Audio with controls boolean attribute."""
        result = str(Audio(Source(src="audio.mp3"), controls=True))
        assert "<audio" in result
        assert "controls" in result
        assert "<source" in result
        assert "</audio>" in result


class TestDocumentTags:
    """Test document structure tags (Html, Head, Body, Title, Meta, Link, Script)."""

    def test_html_document_structure(self):
        """Test Html creates complete document with DOCTYPE."""
        result = str(Html(Head(Title("Test Page")), Body(Div("Content"))))
        assert "<!doctype html>" in result.lower()
        assert "<html>" in result
        assert "<head>" in result
        assert "<title>Test Page</title>" in result
        assert "</head>" in result
        assert "<body>" in result
        assert "<div>Content</div>" in result
        assert "</body>" in result
        assert "</html>" in result

    def test_meta_with_charset(self):
        """Test Meta with charset attribute."""
        result = str(Meta(charset="utf-8"))
        assert "<meta" in result
        assert 'charset="utf-8"' in result

    def test_meta_with_name_and_content(self):
        """Test Meta with name and content attributes."""
        result = str(Meta(name="viewport", content="width=device-width, initial-scale=1"))
        assert 'name="viewport"' in result
        assert 'content="width=device-width, initial-scale=1"' in result

    def test_link_with_rel_and_href(self):
        """Test Link tag with rel and href."""
        result = str(Link(rel="stylesheet", href="/css/style.css"))
        assert "<link" in result
        assert 'rel="stylesheet"' in result
        assert 'href="/css/style.css"' in result

    def test_script_with_src(self):
        """Test Script tag with src attribute."""
        result = str(Script(src="/js/app.js"))
        assert "<script" in result
        assert 'src="/js/app.js"' in result
        assert "</script>" in result

    def test_script_with_inline_content(self):
        """Test Script tag with inline JavaScript content."""
        result = str(Script("console.log('Hello');"))
        assert "<script>" in result
        assert "console.log('Hello');" in result
        assert "</script>" in result


class TestSpecialTags:
    """Test special tags (Fragment, Safe, CustomTag)."""

    def test_fragment_renders_children_without_wrapper(self):
        """Test Fragment renders children without wrapper element."""
        result = str(Fragment(Div("a"), Div("b")))
        assert result == "<div>a</div><div>b</div>"
        # No wrapper tag
        assert not result.startswith("<fragment>")

    def test_safe_escapes_html_characters(self):
        """Test Safe escapes HTML special characters."""
        result = str(Safe("<script>alert()</script>"))
        assert "&lt;" in result
        assert "&gt;" in result
        assert "<script>" not in result
        assert "alert()" in result

    def test_safe_escapes_ampersand(self):
        """Test Safe escapes ampersand."""
        result = str(Safe("Tom & Jerry"))
        assert "&amp;" in result

    def test_custom_tag_creates_arbitrary_tag(self):
        """Test CustomTag creates custom element."""
        result = str(CustomTag("custom-element", "content", cls="test"))
        assert "<custom-element" in result
        assert 'class="test"' in result
        assert "content" in result
        assert "</custom-element>" in result


class TestAttributeMapping:
    """Test attribute name mappings (cls, _for, _class, etc.)."""

    def test_cls_maps_to_class(self):
        """Test cls attribute maps to class."""
        result = str(Div("test", cls="container"))
        assert 'class="container"' in result

    def test_underscore_class_maps_to_class(self):
        """Test _class attribute maps to class."""
        result = str(Div("test", _class="box"))
        assert 'class="box"' in result

    def test_klass_maps_to_class(self):
        """Test klass attribute maps to class."""
        result = str(Div("test", klass="wrapper"))
        assert 'class="wrapper"' in result

    def test_underscore_for_maps_to_for(self):
        """Test _for attribute maps to for."""
        result = str(Label("Name:", _for="name-input"))
        assert 'for="name-input"' in result

    def test_fr_maps_to_for(self):
        """Test fr attribute maps to for."""
        result = str(Label("Email:", fr="email-input"))
        assert 'for="email-input"' in result

    def test_htmlFor_maps_to_for(self):
        """Test htmlFor attribute maps to for."""
        result = str(Label("Phone:", htmlFor="phone-input"))
        assert 'for="phone-input"' in result

    def test_underscore_to_hyphen_conversion(self):
        """Test underscore in attribute names converts to hyphen."""
        result = str(Div("test", data_test="value"))
        assert 'data-test="value"' in result

    def test_aria_attribute_underscore_to_hyphen(self):
        """Test aria attribute underscore conversion."""
        result = str(Div("test", aria_label="Important"))
        assert 'aria-label="Important"' in result

    def test_type_underscore_maps_to_type(self):
        """Test type_ attribute maps to type."""
        result = str(Input(type_="text"))
        assert 'type="text"' in result


class TestDictAsAttrs:
    """Test dictionary as positional argument expands to attributes."""

    def test_dict_expands_to_attributes(self):
        """Test dictionary positional argument expands to attributes."""
        result = str(Div("content", {"id": "test", "class": "demo"}))
        assert 'id="test"' in result
        assert 'class="demo"' in result
        assert "content" in result

    def test_nested_dict_attributes(self):
        """Test nested dictionary with data attributes."""
        result = str(Div("content", {"data-test": "value", "data-id": "123"}))
        assert 'data-test="value"' in result
        assert 'data-id="123"' in result


class TestHtmlProtocol:
    """Test __html__ protocol for custom objects."""

    def test_html_protocol(self):
        """Test object with __html__ method renders correctly."""
        class CustomWidget:
            def __html__(self):
                return "<div class='widget'>Custom</div>"

        result = str(Div(CustomWidget()))
        assert "<div class='widget'>Custom</div>" in result

    def test_repr_html_protocol(self):
        """Test object with _repr_html_ method renders correctly."""
        class JupyterWidget:
            def _repr_html_(self):
                return "<div class='jupyter'>Data</div>"

        result = str(Div(JupyterWidget()))
        assert "<div class='jupyter'>Data</div>" in result

    def test_render_protocol(self):
        """Test object with render method renders correctly."""
        class TemplateWidget:
            def render(self):
                return "<div class='template'>Rendered</div>"

        result = str(Div(TemplateWidget()))
        assert "<div class='template'>Rendered</div>" in result
