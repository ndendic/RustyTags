"""Accordion component documentation page"""

from .base import *

def example_1():
    return Accordion(
        AccordionItem(
            "What is RustyTags?",
            P("RustyTags is a high-performance HTML generation library that combines Rust-powered performance with modern Python web development."),
            P("It provides 3-10x faster rendering than pure Python solutions.")
        ),
        AccordionItem(
            "What are Xtras components?",
            P("Xtras components focus on complex anatomical patterns that are genuinely difficult to implement correctly."),
            P("We avoid wrapping simple HTML elements unnecessarily.")
        ),
        AccordionItem(
            "Why use native HTML?",
            P("Native HTML provides accessibility, performance, and simplicity out of the box."),
            P("We only add complexity when it solves real structural problems.")
        ),
        cls="border-1 border-gray-3 border-radius-2 overflow-hidden"
    )

def example_2():
    return Accordion(
        AccordionItem(
            "Performance Features",
            Ul(
                Li("Rust-powered HTML generation"),
                Li("Memory optimization and caching"),
                Li("Thread-local pools")
            ),
            name="single-group"
        ),
        AccordionItem(
            "Developer Experience",
            Ul(
                Li("FastHTML-style syntax"),
                Li("Automatic type conversion"),
                Li("Smart attribute handling")
            ),
            name="single-group"
        ),
        AccordionItem(
            "Framework Integration",
            Ul(
                Li("FastAPI support"),
                Li("Flask integration"),
                Li("Django compatibility")
            ),
            name="single-group"
        ),
        cls="border-1 border-gray-3 border-radius-2 overflow-hidden mt-4"
    )

def get_routes(app: FastAPI):
    """Register routes for Accordion documentation"""
    
    @app.get("/xtras/accordion")
    @page(title="Accordion Component Documentation", wrap_in=HTMLResponse)
    def accordion_docs():
        return Main(
            H1("Accordion Component"),
            P("The Accordion component uses native HTML details/summary elements with optional name-based grouping for accordion behavior."),
            
            Section("Design Philosophy",
                P("This component follows our 'less is more' principle:"),
                Ul(
                    Li("🏗️ Uses native HTML details/summary elements"),
                    Li("♿️ Built-in accessibility through semantic HTML"),
                    Li("🔗 Name attribute for native accordion grouping behavior"),
                    Li("🚀 No JavaScript required for basic functionality"),
                    Li("✨ Simple, clean API that's easy to understand"),
                ),
            ),
            
            Section("Key Insight",
                P(Strong("The name attribute on details elements automatically creates accordion behavior!"), " When multiple details elements share the same name, only one can be open at a time. This is native HTML functionality."),
            ),
            
            Section("Basic Usage Demo - Multiple Open",
                P("Multiple items can be open simultaneously (default behavior):"),
                ComponentShowcase(example_1),                
            ),
            
            Section("Single Open Demo - Name Grouping",
                P("Using the name attribute, only one item can be open at a time:"),
                ComponentShowcase(example_2),
                
            ),                        
            
            Section("API Reference",
                CodeBlock("""
# Simple accordion container
def Accordion(
    *children,                    # AccordionItem components or raw HTML
    name: Optional[str] = None,   # Shared name for single-open behavior
    cls: str = "",                # CSS classes for root container
    **attrs: Any                  # Additional HTML attributes
) -> rt.HtmlString

# Individual accordion item using HTML details/summary
def AccordionItem(
    trigger_content,              # Content for the accordion trigger
    *children,                    # Collapsible content
    open: bool = False,           # Whether item starts open
    name: Optional[str] = None,   # Name for grouping (single-open behavior)
    cls: str = "",                # CSS classes for the details element
    **attrs: Any                  # Additional HTML attributes
) -> rt.HtmlString""", code_cls="language-python")
            ),
                        
            
            BackLink(),
            
            signals=Signals(message=""),
        )