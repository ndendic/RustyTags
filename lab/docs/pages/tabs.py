"""Tabs component documentation page"""

from .base import *

def example_1():
    return Tabs(
        TabsList(
            TabsTrigger("First Tab", id="tab1"),
            TabsTrigger("Second Tab", id="tab2"),
            TabsTrigger("Third Tab", id="tab3"),
        ),
        TabsContent(P("This is the content of the first tab. Click the other tabs to see the content change!"), id="tab1", cls="p-3"),
        TabsContent(P("This is the content of the second tab. Notice how the keyboard navigation works with arrow keys."), id="tab2", cls="p-3"),
        TabsContent(P("This is the content of the third tab. The component handles all ARIA attributes automatically."), id="tab3", cls="p-3"),
        default_tab="tab1",
    )

def get_routes(app: FastAPI):
    """Register routes for Tabs documentation"""
    
    @app.get("/xtras/tabs")
    @page(title="Tabs Component Documentation", wrap_in=HTMLResponse)
    def tabs_docs():
        return Main(
            H1("Tabs Component"),
            P("The Tabs component is our first true anatomical pattern - it handles complex coordination between tab buttons, panels, ARIA relationships, and keyboard navigation."),
            
            Section("Component Purpose",
                P("Tabs is an anatomical pattern that solves:"),
                Ul(
                    Li("🏗️ Complex DOM coordination between buttons and panels"),
                    Li("♿️ Comprehensive ARIA relationships and accessibility"),
                    Li("⌨️ Full keyboard navigation (arrow keys, home, end)"),
                    Li("📊 State management with Datastar signals"),
                    Li("🎯 Focus management and proper tab order"),
                ),
            ),
            
            Section("Basic Usage Demo",
                P("Try the tabs below - they showcase the component itself using the new function closure API!"),
                ComponentShowcase(example_1),     
            ),
            
            
            Section("API Reference",
                CodeBlock("""
# Main Tabs container
def Tabs(
    *children,                     # TabsList and TabsContent components
    default_tab: str,              # ID of initially active tab
    signal: Optional[str] = None,  # Signal name (auto-generated)
    cls: str = "",                 # Root container classes
    **attrs: Any                   # Additional HTML attributes
) -> rt.HtmlString

# Tab list container (holds triggers)
def TabsList(
    *children,                     # TabsTrigger components
    cls: str = "",                 # Tab list classes
    **attrs: Any                   # Additional HTML attributes
)

# Individual tab trigger
def TabsTrigger(
    *children,                     # Button content
    id: str,                       # Unique tab identifier
    disabled: bool = False,        # Whether tab is disabled
    cls: str = "",                 # Trigger classes
    **attrs: Any                   # Additional HTML attributes
)

# Tab content panel
def TabsContent(
    *children,                     # Panel content
    id: str,                       # Tab identifier (matches trigger)
    cls: str = "",                 # Content panel classes
    **attrs: Any                   # Additional HTML attributes
)""", code_cls="language-python")
            ),
            
            
            BackLink(),
            
            signals=Signals(message=""),
        )