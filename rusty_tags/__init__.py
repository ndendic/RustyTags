"""
RustyTags - High-performance HTML generation library

A Rust-based Python extension for building HTML/SVG tags with optimized performance.
"""

from .rusty_tags import (
    # Core classes
    HtmlString,
    Tag,
    
    # HTML tags
    A, Aside, B, Body, Br, Button, Code, Div, Em, Form,
    H1, H2, H3, H4, H5, H6, Head, Header, Html, I, Img,
    Input, Label, Li, Link, Main, Nav, P, Script, Section,
    Span, Strong, Table, Td, Th, Title, Tr, Ul, Ol,
    
    # SVG tags
    Svg, Circle, Rect, Line, Path, Polygon, Polyline, Ellipse,
    Text, G, Defs, Use, Symbol, Marker, LinearGradient, RadialGradient,
    Stop, Pattern, ClipPath, Mask, Image, ForeignObject,
    
    # Phase 1: Critical High Priority HTML tags
    Meta, Hr, Iframe, Textarea, Select, Figure, Figcaption,
    Article, Footer, Details, Summary, Address,
    
    # Phase 2: Table Enhancement Tags
    Tbody, Thead, Tfoot, Caption, Col, Colgroup,
    
    # Custom tag function
    CustomTag,
)

__version__ = "0.2.3"
__author__ = "Nikola Dendic"
__description__ = "High-performance HTML generation library with Rust-based Python extension"

__all__ = [
    # Core classes
    "HtmlString",
    "Tag", 
    
    # HTML tags - organized alphabetically
    "A", "Aside", "B", "Body", "Br", "Button", "Code", "Div", "Em", "Form",
    "H1", "H2", "H3", "H4", "H5", "H6", "Head", "Header", "Html", "I", "Img",
    "Input", "Label", "Li", "Link", "Main", "Nav", "P", "Script", "Section",
    "Span", "Strong", "Table", "Td", "Th", "Title", "Tr", "Ul", "Ol",
    
    # SVG tags - organized alphabetically
    "Circle", "ClipPath", "Defs", "Ellipse", "ForeignObject", "G", "Image",
    "Line", "LinearGradient", "Marker", "Mask", "Path", "Pattern", "Polygon",
    "Polyline", "RadialGradient", "Rect", "Stop", "Svg", "Symbol", "Text", "Use",
    
    # Phase 1: Critical High Priority HTML tags - alphabetically
    "Address", "Article", "Details", "Figcaption", "Figure", "Footer", 
    "Hr", "Iframe", "Meta", "Select", "Summary", "Textarea",
    
    # Phase 2: Table Enhancement Tags - alphabetically
    "Caption", "Col", "Colgroup", "Tbody", "Tfoot", "Thead",
    
    # Custom tag function
    "CustomTag",
]