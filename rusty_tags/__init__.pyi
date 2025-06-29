"""
Type stubs for RustyTags - High-performance HTML generation library
"""

from typing import Any, Union

# Type aliases for better type hints
AttributeValue = Union[str, int, float, bool]
Child = Union[str, int, float, bool, "HtmlString", "Tag", Any]

class HtmlString:
    """Core HTML content container with optimized memory layout"""
    content: str
    
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...
    def render(self) -> str: ...
    def _repr_html_(self) -> str: ...

class Tag:
    """Backward-compatible class for existing Air code"""
    _name: str
    _module: str
    
    def __init__(self, *children: Child, **kwargs: AttributeValue) -> None: ...
    
    @property
    def name(self) -> str: ...
    
    @property
    def attrs(self) -> str: ...
    
    def children(self) -> str: ...
    def render(self) -> str: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def _repr_html_(self) -> str: ...

# HTML Tag Functions
def A(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a hyperlink"""
    ...

def Aside(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines aside content"""
    ...

def B(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines bold text"""
    ...

def Body(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines the document body"""
    ...

def Br(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a line break"""
    ...

def Button(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a clickable button"""
    ...

def Code(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines computer code"""
    ...

def Div(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a division or section"""
    ...

def Em(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines emphasized text"""
    ...

def Form(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines an HTML form"""
    ...

def H1(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a level 1 heading"""
    ...

def H2(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a level 2 heading"""
    ...

def H3(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a level 3 heading"""
    ...

def H4(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a level 4 heading"""
    ...

def H5(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a level 5 heading"""
    ...

def H6(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a level 6 heading"""
    ...

def Head(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines the document head"""
    ...

def Header(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a page header"""
    ...

def Html(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines the HTML document with automatic DOCTYPE and head/body separation"""
    ...

def I(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines italic text"""
    ...

def Img(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines an image"""
    ...

def Input(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines an input field"""
    ...

def Label(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a label for a form element"""
    ...

def Li(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a list item"""
    ...

def Link(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a document link"""
    ...

def Main(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines the main content"""
    ...

def Nav(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines navigation links"""
    ...

def P(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a paragraph"""
    ...

def Script(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a client-side script"""
    ...

def Section(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a section"""
    ...

def Span(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines an inline section"""
    ...

def Strong(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines strong/important text"""
    ...

def Table(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a table"""
    ...

def Td(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a table cell"""
    ...

def Th(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a table header cell"""
    ...

def Title(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines the document title"""
    ...

def Tr(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a table row"""
    ...

def Ul(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines an unordered list"""
    ...

def Ol(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines an ordered list"""
    ...

def CustomTag(tag_name: str, *children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Creates a custom HTML tag with any tag name"""
    ...

# SVG Tag Functions
def Svg(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines an SVG graphics container"""
    ...

def Circle(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a circle in SVG"""
    ...

def Rect(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a rectangle in SVG"""
    ...

def Line(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a line in SVG"""
    ...

def Path(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a path in SVG"""
    ...

def Polygon(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a polygon in SVG"""
    ...

def Polyline(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a polyline in SVG"""
    ...

def Ellipse(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines an ellipse in SVG"""
    ...

def Text(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines text in SVG"""
    ...

def G(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a group in SVG"""
    ...

def Defs(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines reusable SVG elements"""
    ...

def Use(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a reusable SVG element instance"""
    ...

def Symbol(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a reusable SVG symbol"""
    ...

def Marker(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a marker for SVG shapes"""
    ...

def LinearGradient(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a linear gradient in SVG"""
    ...

def RadialGradient(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a radial gradient in SVG"""
    ...

def Stop(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a gradient stop in SVG"""
    ...

def Pattern(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a pattern in SVG"""
    ...

def ClipPath(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a clipping path in SVG"""
    ...

def Mask(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a mask in SVG"""
    ...

def Image(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines an image in SVG"""
    ...

def ForeignObject(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines foreign content in SVG"""
    ...

# Phase 1: Critical High Priority HTML Tags
def Meta(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines metadata about an HTML document"""
    ...

def Hr(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a thematic break/horizontal rule"""
    ...

def Iframe(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines an inline frame"""
    ...

def Textarea(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a multiline text input control"""
    ...

def Select(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a dropdown list"""
    ...

def Figure(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines self-contained content"""
    ...

def Figcaption(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a caption for a figure element"""
    ...

def Article(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines independent, self-contained content"""
    ...

def Footer(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a footer for a document or section"""
    ...

def Details(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines additional details that can be viewed or hidden"""
    ...

def Summary(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a visible heading for a details element"""
    ...

def Address(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines contact information for the author"""
    ...

# Phase 2: Table Enhancement Tags
def Tbody(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a table body"""
    ...

def Thead(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a table header"""
    ...

def Tfoot(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a table footer"""
    ...

def Caption(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a table caption"""
    ...

def Col(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a table column"""
    ...

def Colgroup(*children: Child, **kwargs: AttributeValue) -> HtmlString:
    """Defines a group of table columns"""
    ...

__version__: str
__author__: str 
__description__: str