"""CodeBlock component documentation page"""

from .base import *

def example_1():
    return CodeBlock("print('Hello, World!')")

def example_2():
    return CodeBlock(
        "const greeting = 'Hello, World!';\nconsole.log(greeting);", 
        cls="border-1 border-radius-2 p-3 surface-2",
        code_cls="language-javascript"
    )



def get_routes(app: FastAPI):
    """Register routes for CodeBlock documentation"""
    
    @app.get("/xtras/codeblock")
    @page(title="CodeBlock Component Documentation", wrap_in=HTMLResponse)
    def codeblock_docs():
        return Main(
            H1("CodeBlock Component"),
            P("The CodeBlock component provides a semantic structure for displaying code with proper HTML markup and styling hooks."),
            
            Section("Component Purpose",
                P("CodeBlock is an anatomical pattern that solves:"),
                Ul(
                    Li("🏗️ Consistent semantic HTML structure (Div > Pre > Code)"),
                    Li("🎨 Flexible styling with separate classes for container and code"),
                    Li("⚡ Simple API for common code display patterns"),
                    Li("🔧 Integration with syntax highlighting libraries"),
                ),
            ),
            
            Section("Basic Usage",
                P("Simple code block without styling:"),
                ComponentShowcase(example_1),
            ),
            
            Section("With Styling",
                P("CodeBlock with Open Props styling:"),
                ComponentShowcase(example_2),
            ),
            
            Section("API Reference",
                P("CodeBlock component parameters:"),
                CodeBlock("""
def CodeBlock(
    *content: str,      # Text content for the code block
    cls: str = "",      # CSS classes for outer container
    code_cls: str = "", # CSS classes for code element  
    **kwargs: Any       # Additional HTML attributes for code element
) -> rt.HtmlString""", code_cls="language-python"),
            ),
            
            BackLink(),
            
            signals=Signals(message=""),
        )