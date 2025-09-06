from .datastar import *
from .rusty_tags import HtmlString
from .utils import Page, create_template, page_template, show, AttrDict
from .client import Client
from .events import *
from .datastar import *
"""
RustyTags - High-performance HTML generation library

A Rust-based Python extension for building HTML/SVG tags with optimized performance.
"""

from .rusty_tags import (  # noqa: E402
    # Core classes
    TagBuilder,
    
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
    
    # All remaining HTML tags - comprehensive implementation
    Abbr, Area, Audio, Base, Bdi, Bdo, Blockquote, Canvas, Cite,
    Data, Datalist, Dd, Del, Dfn, Dialog, Dl, Dt, Embed, Fieldset,
    Hgroup, Ins, Kbd, Legend, Map, Mark, Menu, Meter, Noscript,
    Object, Optgroup, OptionEl, Picture, Pre, Progress, Q, Rp, Rt,
    Ruby, S, Samp, Small, Source, Style, Sub, Sup, Template, Time,
    Track, U, Var, Video, Wbr,
    
    # Custom tag function
    CustomTag,
)

# Create alias for proper HTML tag name  
Option = OptionEl

# Import Datastar utilities

__author__ = "Nikola Dendic"
__description__ = "High-performance HTML generation library with Rust-based Python extension"

__all__ = [
    # Core classes
    "HtmlString", "TagBuilder",
    
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
    
    # All remaining HTML tags - alphabetically
    "Abbr", "Area", "Audio", "Base", "Bdi", "Bdo", "Blockquote", "Canvas", "Cite",
    "Data", "Datalist", "Dd", "Del", "Dfn", "Dialog", "Dl", "Dt", "Embed", "Fieldset",
    "Hgroup", "Ins", "Kbd", "Legend", "Map", "Mark", "Menu", "Meter", "Noscript",
    "Object", "Optgroup", "OptionEl", "Option", "Picture", "Pre", "Progress", "Q", "Rp", "Rt",
    "Ruby", "S", "Samp", "Small", "Source", "Style", "Sub", "Sup", "Template", "Time",
    "Track", "U", "Var", "Video", "Wbr",
    
    # Custom tag function
    "CustomTag",

    # Utilities
    "Page", "create_template", "page_template", "show", "AttrDict",
    # Datastar utilities
    "signals", "reactive_class", "attribute_generator","DS",
    # Client
    "Client",
    # Events
    "Namespace",
    "ANY",
    "default_namespace",
    "event",
    "on",
    "emit",
    "emit_async",
    "Event",
    # Datastar
    'DS',
    'signals', 
    'Signals',
    'reactive_class',
    'attribute_generator',
    'SSE',
    'ElementPatchMode',
    'EventType'
]