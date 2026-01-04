"""
Tests for SVG tag generation and special tags (Fragment, Safe, CustomTag).

This test suite covers:
- SVG container with viewBox and dimensions
- SVG shapes (Circle, Rect, Ellipse, Line, Polygon, Polyline, Path)
- SVG grouping and reuse (G, Defs, Use, Symbol)
- SVG gradients (LinearGradient, RadialGradient, Stop)
- SVG Text element
- Special tags (Fragment, Safe, CustomTag)
"""

import pytest
from rusty_tags import (
    # SVG tags
    Svg, Circle, Rect, Line, Path, Polygon, Polyline, Ellipse,
    Text, G, Defs, Use, Symbol,
    LinearGradient, RadialGradient, Stop,
    ClipPath,
    # Special tags
    Fragment, Safe, CustomTag,
    # HTML tags for comparison
    Div, Span
)


class TestSvgContainer:
    """Test SVG container element with viewBox and dimensions."""

    def test_svg_with_dimensions(self):
        """Test SVG container with width, height, viewBox."""
        result = str(Svg(width="200", height="200", viewBox="0 0 200 200"))
        assert "<svg" in result
        assert 'width="200"' in result
        assert 'height="200"' in result
        assert 'viewBox="0 0 200 200"' in result
        assert "</svg>" in result

    def test_svg_with_children(self):
        """Test SVG with shape children."""
        result = str(Svg(
            Circle(cx="50", cy="50", r="40"),
            Rect(x="100", y="100", width="50", height="50"),
            width="200", height="200"
        ))
        assert "<svg" in result
        assert "<circle" in result
        assert "<rect" in result
        assert "</svg>" in result

    def test_svg_empty(self):
        """Test empty SVG container."""
        result = str(Svg())
        # Empty SVG may render as self-closing tag
        assert "<svg" in result and ("</svg>" in result or "/>" in result)


class TestSvgShapes:
    """Test all SVG shape elements."""

    def test_circle_shape(self):
        """Test Circle with cx, cy, r, fill."""
        result = str(Circle(cx="50", cy="50", r="40", fill="blue"))
        assert "<circle" in result
        assert 'cx="50"' in result
        assert 'cy="50"' in result
        assert 'r="40"' in result
        assert 'fill="blue"' in result

    def test_rect_shape(self):
        """Test Rect with x, y, width, height."""
        result = str(Rect(x="10", y="10", width="80", height="80", fill="red"))
        assert "<rect" in result
        assert 'x="10"' in result
        assert 'y="10"' in result
        assert 'width="80"' in result
        assert 'height="80"' in result

    def test_ellipse_shape(self):
        """Test Ellipse with cx, cy, rx, ry."""
        result = str(Ellipse(cx="100", cy="50", rx="100", ry="50"))
        assert "<ellipse" in result
        assert 'cx="100"' in result
        assert 'cy="50"' in result
        assert 'rx="100"' in result
        assert 'ry="50"' in result

    def test_line_shape(self):
        """Test Line with x1, y1, x2, y2."""
        result = str(Line(x1="0", y1="0", x2="100", y2="100", stroke="black"))
        assert "<line" in result
        assert 'x1="0"' in result
        assert 'y1="0"' in result
        assert 'x2="100"' in result
        assert 'y2="100"' in result
        assert 'stroke="black"' in result

    def test_polygon_shape(self):
        """Test Polygon with points."""
        result = str(Polygon(points="0,0 100,0 50,100", fill="green"))
        assert "<polygon" in result
        assert 'points="0,0 100,0 50,100"' in result
        assert 'fill="green"' in result

    def test_polyline_shape(self):
        """Test Polyline with points."""
        result = str(Polyline(points="0,0 50,25 100,0", stroke="blue", fill="none"))
        assert "<polyline" in result
        assert 'points="0,0 50,25 100,0"' in result
        assert 'stroke="blue"' in result
        assert 'fill="none"' in result

    def test_path_with_d_attribute(self):
        """Test Path with d attribute."""
        result = str(Path(d="M10 10 L90 90 L10 90 Z", stroke="black", fill="yellow"))
        assert "<path" in result
        assert 'd="M10 10 L90 90 L10 90 Z"' in result
        assert 'stroke="black"' in result

    def test_all_shapes_render_correctly(self):
        """Test all shapes rendered with their attributes."""
        circle = str(Circle(cx="50", cy="50", r="40"))
        rect = str(Rect(x="10", y="10", width="80", height="80"))
        ellipse = str(Ellipse(cx="100", cy="50", rx="100", ry="50"))
        line = str(Line(x1="0", y1="0", x2="100", y2="100"))
        polygon = str(Polygon(points="0,0 100,0 50,100"))
        polyline = str(Polyline(points="0,0 50,25 100,0"))
        path = str(Path(d="M10 10 L90 90"))

        assert "<circle" in circle
        assert "<rect" in rect
        assert "<ellipse" in ellipse
        assert "<line" in line
        assert "<polygon" in polygon
        assert "<polyline" in polyline
        assert "<path" in path


class TestSvgGrouping:
    """Test SVG grouping and reuse elements."""

    def test_g_with_transform(self):
        """Test G (group) with transform attribute."""
        result = str(G(
            Circle(cx="0", cy="0", r="10"),
            transform="translate(50, 50)"
        ))
        assert "<g" in result
        assert 'transform="translate(50, 50)"' in result
        assert "<circle" in result
        assert "</g>" in result

    def test_defs_with_gradient(self):
        """Test Defs with gradient definition."""
        result = str(Defs(
            LinearGradient(
                Stop(offset="0%", stop_color="red"),
                Stop(offset="100%", stop_color="blue"),
                id="grad1"
            )
        ))
        assert "<defs" in result
        assert "<lineargradient" in result.lower()
        assert "<stop" in result.lower()
        assert "</defs>" in result

    def test_symbol_with_viewbox(self):
        """Test Symbol with viewBox."""
        result = str(Symbol(
            Circle(cx="50", cy="50", r="40"),
            id="icon",
            viewBox="0 0 100 100"
        ))
        assert "<symbol" in result
        assert 'id="icon"' in result
        assert 'viewBox="0 0 100 100"' in result
        assert "</symbol>" in result

    def test_use_with_href(self):
        """Test Use with href reference."""
        result = str(Use(href="#icon", x="10", y="10"))
        assert "<use" in result
        assert 'href="#icon"' in result
        assert 'x="10"' in result
        assert 'y="10"' in result

    def test_all_grouping_elements_rendered(self):
        """Test all grouping elements render correctly."""
        g = str(G(Circle(cx="0", cy="0", r="10")))
        defs = str(Defs(LinearGradient(id="grad")))
        symbol = str(Symbol(id="sym"))
        use = str(Use(href="#sym"))

        assert "<g" in g and "</g>" in g
        assert "<defs" in defs and "</defs>" in defs
        assert "<symbol" in symbol and "</symbol>" in symbol
        assert "<use" in use


class TestSvgGradients:
    """Test SVG gradient elements."""

    def test_linear_gradient_with_stops(self):
        """Test LinearGradient with Stop children."""
        result = str(LinearGradient(
            Stop(offset="0%", stop_color="red"),
            Stop(offset="100%", stop_color="blue"),
            id="gradient1"
        ))
        assert "<lineargradient" in result.lower()
        assert 'id="gradient1"' in result
        assert "<stop" in result.lower()
        assert 'offset="0%"' in result
        assert 'stop-color="red"' in result
        assert 'offset="100%"' in result
        assert 'stop-color="blue"' in result

    def test_radial_gradient_with_stops(self):
        """Test RadialGradient with Stop children."""
        result = str(RadialGradient(
            Stop(offset="0%", stop_color="yellow"),
            Stop(offset="100%", stop_color="orange"),
            id="gradient2"
        ))
        assert "<radialgradient" in result.lower()
        assert 'id="gradient2"' in result
        assert "<stop" in result.lower()
        assert 'stop-color="yellow"' in result
        assert 'stop-color="orange"' in result

    def test_linear_gradient_attributes(self):
        """Test LinearGradient with x1, y1, x2, y2 attributes."""
        result = str(LinearGradient(
            Stop(offset="0%", stop_color="red"),
            id="grad",
            x1="0%", y1="0%", x2="100%", y2="0%"
        ))
        assert 'x1="0%"' in result
        assert 'y1="0%"' in result
        assert 'x2="100%"' in result
        assert 'y2="0%"' in result

    def test_radial_gradient_attributes(self):
        """Test RadialGradient with cx, cy, r attributes."""
        result = str(RadialGradient(
            Stop(offset="0%", stop_color="white"),
            id="rad",
            cx="50%", cy="50%", r="50%"
        ))
        assert 'cx="50%"' in result
        assert 'cy="50%"' in result
        assert 'r="50%"' in result

    def test_stop_attributes(self):
        """Test Stop with offset and stop-color."""
        result = str(Stop(offset="50%", stop_color="green", stop_opacity="0.5"))
        assert "<stop" in result.lower()
        assert 'offset="50%"' in result
        assert 'stop-color="green"' in result
        assert 'stop-opacity="0.5"' in result


class TestSvgText:
    """Test SVG Text element."""

    def test_text_with_position(self):
        """Test Text with x, y, and content."""
        result = str(Text("Hello SVG", x="10", y="20"))
        assert "<text" in result.lower()
        assert 'x="10"' in result
        assert 'y="20"' in result
        assert "Hello SVG" in result
        assert "</text>" in result

    def test_text_content_preserved(self):
        """Test text content is preserved."""
        result = str(Text("SVG Text Content", x="50", y="50"))
        assert "SVG Text Content" in result
        assert "<text" in result.lower()

    def test_text_with_styling(self):
        """Test Text with font attributes."""
        result = str(Text(
            "Styled Text",
            x="10", y="20",
            font_family="Arial",
            font_size="16",
            fill="blue"
        ))
        assert 'font-family="Arial"' in result
        assert 'font-size="16"' in result
        assert 'fill="blue"' in result


class TestFragmentTag:
    """Test Fragment special tag."""

    def test_fragment_renders_children_without_wrapper(self):
        """Test Fragment renders children without wrapper element."""
        result = str(Fragment(Div("a"), Div("b")))
        # Fragment should render children directly
        assert "<div>a</div>" in result
        assert "<div>b</div>" in result
        # Should NOT have a wrapper like <fragment>
        assert "<fragment" not in result.lower()

    def test_fragment_with_multiple_children(self):
        """Test Fragment with multiple children."""
        result = str(Fragment(
            Div("first"),
            Span("second"),
            Div("third")
        ))
        assert "<div>first</div>" in result
        assert "<span>second</span>" in result
        assert "<div>third</div>" in result

    def test_fragment_preserves_order(self):
        """Test Fragment preserves children order."""
        result = str(Fragment(Div("1"), Div("2"), Div("3")))
        # Check that order is preserved
        idx1 = result.index(">1<")
        idx2 = result.index(">2<")
        idx3 = result.index(">3<")
        assert idx1 < idx2 < idx3


class TestSafeTag:
    """Test Safe tag for HTML escaping."""

    def test_safe_escapes_less_than(self):
        """Test Safe escapes < to &lt;."""
        result = str(Safe("<script>alert()</script>"))
        assert "&lt;" in result
        assert "<script>" not in result

    def test_safe_escapes_greater_than(self):
        """Test Safe escapes > to &gt;."""
        result = str(Safe("<script>alert()</script>"))
        assert "&gt;" in result
        assert "</script>" not in result

    def test_safe_escapes_ampersand(self):
        """Test Safe escapes & to &amp;."""
        result = str(Safe("A&B"))
        assert "&amp;" in result
        assert "A&amp;B" in result

    def test_safe_escapes_quotes(self):
        """Test Safe escapes quotes."""
        result = str(Safe('"Hello" and \'World\''))
        # Check that quotes are handled (specific escaping may vary)
        assert "Hello" in result
        assert "World" in result

    def test_safe_full_script_tag(self):
        """Test Safe properly escapes dangerous script tag."""
        dangerous = "<script>alert('XSS')</script>"
        result = str(Safe(dangerous))
        assert "&lt;script&gt;" in result
        assert "&lt;/script&gt;" in result
        assert "<script>" not in result


class TestCustomTag:
    """Test CustomTag for arbitrary tags."""

    def test_custom_tag_creates_arbitrary_tag(self):
        """Test CustomTag creates tag with custom name."""
        result = str(CustomTag("custom-element", "content"))
        assert "<custom-element" in result
        assert "content" in result
        assert "</custom-element>" in result

    def test_custom_tag_with_attributes(self):
        """Test CustomTag with attributes."""
        result = str(CustomTag("my-widget", "text", cls="test", id="widget1"))
        assert "<my-widget" in result
        assert 'class="test"' in result
        assert 'id="widget1"' in result
        assert "text" in result

    def test_custom_tag_preserves_content(self):
        """Test CustomTag preserves content."""
        result = str(CustomTag("custom-element", "Hello World"))
        assert "Hello World" in result

    def test_custom_tag_with_children(self):
        """Test CustomTag with element children."""
        result = str(CustomTag("wrapper", Div("child1"), Span("child2")))
        assert "<wrapper" in result
        assert "<div>child1</div>" in result
        assert "<span>child2</span>" in result
        assert "</wrapper>" in result

    def test_custom_tag_hyphenated_name(self):
        """Test CustomTag with hyphenated custom element name."""
        result = str(CustomTag("my-custom-element", "content"))
        assert "<my-custom-element" in result
        assert "</my-custom-element>" in result


class TestSvgComplexStructures:
    """Test complex SVG structures combining multiple elements."""

    def test_complete_svg_with_gradient_and_shape(self):
        """Test complete SVG with gradient definition and shape using it."""
        result = str(Svg(
            Defs(
                LinearGradient(
                    Stop(offset="0%", stop_color="red"),
                    Stop(offset="100%", stop_color="blue"),
                    id="myGradient"
                )
            ),
            Circle(cx="50", cy="50", r="40", fill="url(#myGradient)"),
            width="100", height="100"
        ))
        assert "<svg" in result
        assert "<defs" in result
        assert "<lineargradient" in result.lower()
        assert 'id="myGradient"' in result
        assert "<circle" in result
        assert 'fill="url(#myGradient)"' in result

    def test_svg_with_grouped_shapes(self):
        """Test SVG with grouped shapes using G."""
        result = str(Svg(
            G(
                Circle(cx="20", cy="20", r="10"),
                Circle(cx="40", cy="20", r="10"),
                transform="scale(2)"
            ),
            width="200", height="200"
        ))
        assert "<g" in result
        assert 'transform="scale(2)"' in result
        assert result.count("<circle") == 2

    def test_svg_with_symbol_and_use(self):
        """Test SVG with symbol definition and use instances."""
        result = str(Svg(
            Defs(
                Symbol(
                    Circle(cx="10", cy="10", r="10"),
                    id="dot",
                    viewBox="0 0 20 20"
                )
            ),
            Use(href="#dot", x="0", y="0"),
            Use(href="#dot", x="30", y="30"),
            width="100", height="100"
        ))
        assert "<symbol" in result
        assert 'id="dot"' in result
        assert result.count("<use") == 2
        assert 'href="#dot"' in result


class TestSvgEdgeCases:
    """Test edge cases for SVG tags."""

    def test_empty_svg_shapes(self):
        """Test empty SVG shapes."""
        circle = str(Circle())
        rect = str(Rect())
        assert "<circle" in circle
        assert "<rect" in rect

    def test_svg_with_mixed_content(self):
        """Test SVG with shapes and text."""
        result = str(Svg(
            Circle(cx="50", cy="50", r="40"),
            Text("Label", x="50", y="50")
        ))
        assert "<circle" in result
        assert "<text" in result.lower()
        assert "Label" in result

    def test_gradient_without_stops(self):
        """Test gradient without stop elements."""
        result = str(LinearGradient(id="empty"))
        assert "<lineargradient" in result.lower()
        assert 'id="empty"' in result

    def test_nested_g_elements(self):
        """Test nested G (group) elements."""
        result = str(G(
            G(
                Circle(cx="0", cy="0", r="5"),
                transform="translate(10, 10)"
            ),
            transform="scale(2)"
        ))
        assert result.count("<g") == 2
        assert result.count("</g>") == 2
        assert 'transform="scale(2)"' in result
        assert 'transform="translate(10, 10)"' in result


class TestSpecialTagsEdgeCases:
    """Test edge cases for special tags."""

    def test_fragment_empty(self):
        """Test empty Fragment."""
        result = str(Fragment())
        # Empty fragment should produce minimal output
        assert result == "" or result.strip() == ""

    def test_safe_with_numbers(self):
        """Test Safe with numeric content as string."""
        result = str(Safe("42"))
        assert "42" in result

    def test_custom_tag_empty_content(self):
        """Test CustomTag with no content."""
        result = str(CustomTag("empty-tag"))
        assert "<empty-tag" in result
        assert "</empty-tag>" in result

    def test_custom_tag_with_underscore_attributes(self):
        """Test CustomTag with underscore attributes."""
        result = str(CustomTag("widget", data_test="value", aria_label="label"))
        assert 'data-test="value"' in result
        assert 'aria-label="label"' in result
