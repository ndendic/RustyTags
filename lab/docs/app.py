from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from rusty_tags import *
from rusty_tags import Section as HTMLSection
from rusty_tags.utils import create_template
from rusty_tags.datastar import Signals, DS
from rusty_tags.events import event, emit_async, on, ANY
from rusty_tags.client import Client
from rusty_tags.starlette import *
from rusty_tags.xtras import Icon, CodeBlock, Tabs, TabsList, TabsTrigger, TabsContent, Accordion, AccordionItem

from rusty_tags.xtras.utils import cn
from datastar_py.fastapi import  ReadSignals
from datastar_py.consts import ElementPatchMode
from uuid import uuid4
from typing import Any
from enum import Enum

HEADER_URLS = {
        'franken_css': "https://cdn.jsdelivr.net/npm/franken-ui@2.0.0/dist/css/core.min.css",
        'franken_js_core': "https://cdn.jsdelivr.net/npm/franken-ui@2.0.0/dist/js/core.iife.js",
        'franken_icons': "https://cdn.jsdelivr.net/npm/franken-ui@2.0.0/dist/js/icon.iife.js",
        'tailwind': "https://cdn.tailwindcss.com/3.4.16",
        'daisyui': "https://cdn.jsdelivr.net/npm/daisyui@4.12.24/dist/full.min.css",
        'apex_charts': "https://cdn.jsdelivr.net/npm/franken-ui@2.0.0/dist/js/chart.iife.js"
}

# Read the xtras CSS content
import os
xtras_css_path = os.path.join(os.path.dirname(__file__), '../../rusty_tags/xtras/xtras.css')
with open(xtras_css_path, 'r') as f:
    xtras_css = f.read()

hdrs = (
    Link(rel='stylesheet', href='https://unpkg.com/open-props'),
    # Link(rel='stylesheet', href='https://unpkg.com/open-props/normalize.min.css'),
    Style(f"""
        html {{
            background: light-dark(var(--gradient-5), var(--gradient-16));
            min-height: 100vh;
            color: light-dark(var(--gray-9), var(--gray-1));
            font-family: var(--font-geometric-humanist);
            font-size: var(--font-size-1);
        }}
        main {{
            width: min(100% - 2rem, 40rem);
            margin-inline: auto;
        }}
        
        /* RustyTags Xtras CSS */
        {xtras_css}
    """),
)
htmlkws = dict(lang="en")
bodykws = dict(signals=Signals(message="", conn=""))
page = create_template(hdrs=hdrs, htmlkw=htmlkws, bodykw=bodykws, highlightjs=True)

app = FastAPI()

def Section(title, *content):
    return HTMLSection(
        H2(title),
        *content,
        cls="fluid-flex"
    )

@app.get("/")
@page(title="FastAPI App", wrap_in=HTMLResponse)
def index():
    return Main(
            H1("Rusty Tags"),
            P("A high-performance HTML generation library that combines Rust-powered performance with modern Python web development."),
            # Section("What Rusty Tags Does",
            #     P("Rusty Tags generates HTML and SVG content programmatically with:"),
            #     Ul(
            #         Li("⚡ Rust Performance: 3-10x faster than pure Python with memory optimization, caching, and thread-local pools"),
            #         Li("🆕 Automatic Mapping Expansion: Dictionaries automatically expand as tag attributes - `Div(\"text\", {\"id\": \"main\"})`"),
            #         Li("🏗️ FastHTML-Style Syntax: Callable chaining support - `Div(cls=\"container\")(P(\"Hello\"), Button(\"Click\"))`"),
            #         Li("⚡ Datastar Integration: Complete reactive web development with shorthand attributes (`signals`, `show`, `on_click`)"),
            #         Li("🎨 Full-Stack Utilities: Page templates, decorators, and framework integrations (FastAPI, Flask, Django)"),
            #         Li("🔧 Smart Type System: Native support for `__html__()`, `_repr_html_()`, `render()` methods and automatic type conversion"),
            #         Li("📦 Complete HTML5/SVG: All standard tags plus custom tag creation with dynamic names"),
            #     ),
            # ),
            
            Section("Component Demos",
                P("Test the RustyTags xtras components:"),
                Ul(
                    Li(A("CodeBlock Component", href="/xtras/codeblock", cls="color-blue-6 text-decoration-underline")),
                    Li(A("Tabs Component", href="/xtras/tabs", cls="color-blue-6 text-decoration-underline")),
                    Li(A("Accordion Component", href="/xtras/accordion", cls="color-blue-6 text-decoration-underline")),
                ),
            ),
            
            signals=Signals(message=""),
        )

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
            CodeBlock("print('Hello, World!')"),
            CodeBlock("""
CodeBlock("print('Hello, World!')")""", code_cls="language-python"),
        ),
        
        Section("With Styling",
            P("CodeBlock with Open Props styling:"),
            CodeBlock(
                "const greeting = 'Hello, World!';\nconsole.log(greeting);", 
                cls="border-1 border-radius-2 p-3 surface-2",
                code_cls="language-javascript"
            ),
            CodeBlock("""
CodeBlock(
    "const greeting = 'Hello, World!';\\nconsole.log(greeting);", 
    cls="border-1 border-radius-2 p-3 surface-2",
    code_cls="language-javascript"
)""", code_cls="language-python"),
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
        
        Section("HTML Output",
            P("The component generates this HTML structure:"),
            CodeBlock("""
<div class="{cls}">
    <pre>
        <code class="{code_cls}" {**kwargs}>
            {content}
        </code>
    </pre>
</div>""", code_cls="language-html"),
        ),
        
        Div(
            A("← Back to Home", href="/", cls="color-blue-6 text-decoration-underline"),
            cls="mt-8"
        ),
        
        signals=Signals(message=""),
    )


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
            
            # Use Tabs to showcase the component itself!
            Tabs(
                TabsList(
                    TabsTrigger("First Tab", id="tab1", cls="px-4 py-2 border-0 cursor-pointer bg-transparent"),
                    TabsTrigger("Second Tab", id="tab2", cls="px-4 py-2 border-0 cursor-pointer bg-transparent"),
                    TabsTrigger("Third Tab", id="tab3", cls="px-4 py-2 border-0 cursor-pointer bg-transparent"),
                    cls="flex border-bottom-1 mb-3"
                ),
                TabsContent(P("This is the content of the first tab. Click the other tabs to see the content change!"), id="tab1", cls="p-3"),
                TabsContent(P("This is the content of the second tab. Notice how the keyboard navigation works with arrow keys."), id="tab2", cls="p-3"),
                TabsContent(P("This is the content of the third tab. The component handles all ARIA attributes automatically."), id="tab3", cls="p-3"),
                default_tab="tab1",
                cls="border-1 border-radius-2 p-4 mt-4 surface-2"
            )
        ),
        
        Section("Code Example",
            P("Here's the code for the tabs above using the function closure API:"),
            CodeBlock("""
Tabs(
    TabsList(
        TabsTrigger("First Tab", id="tab1", cls="px-4 py-2 border-0 cursor-pointer"),
        TabsTrigger("Second Tab", id="tab2", cls="px-4 py-2 border-0 cursor-pointer"),
        TabsTrigger("Third Tab", id="tab3", cls="px-4 py-2 border-0 cursor-pointer"),
        cls="flex border-bottom-1 mb-3"
    ),
    TabsContent(P("Content of first tab..."), id="tab1", cls="p-3"),
    TabsContent(P("Content of second tab..."), id="tab2", cls="p-3"),
    TabsContent(P("Content of third tab..."), id="tab3", cls="p-3"),
    default_tab="tab1",
    cls="border-1 border-radius-2 p-4 surface-2"
)""", code_cls="language-python")
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
        
        Section("HTML Output Structure",
            P("The Tabs component generates this semantic HTML:"),
            CodeBlock(HtmlString("""
<div class="tabs-container {cls}" id="{component_id}">
    <div class="tabs-list {tab_list_cls}" role="tablist" aria-label="Tabs">
        <button role="tab" 
                aria-controls="{component_id}-panel-0"
                aria-selected="true"
                tabindex="0"
                class="tabs-tab {tab_cls}">
            Tab Label 1
        </button>
        <!-- More tab buttons... -->
    </div>
    
    <div class="tabs-panels">
        <div class="tabs-panel {panel_cls}" 
             role="tabpanel" 
             aria-labelledby="{component_id}-tab-0"
             tabindex="0">
            Tab 1 Content
        </div>
        <!-- More panels... -->
    </div>
</div>"""), code_cls="language-html")
        ),
        
        Div(
            A("← Back to Home", href="/", cls="color-blue-6 text-decoration-underline"),
            cls="mt-8"
        ),
        
        signals=Signals(message=""),
    )


@app.get("/xtras/accordion")
@page(title="Accordion Component Documentation", wrap_in=HTMLResponse)
def accordion_docs():
    return Main(
        H1("Accordion Component"),
        P("The Accordion component handles complex expand/collapse coordination between multiple items with proper state management and accessibility."),
        
        Section("Component Purpose",
            P("Accordion is an anatomical pattern that solves:"),
            Ul(
                Li("🏗️ Complex coordination between multiple collapsible items"),
                Li("♿️ Proper ARIA attributes and keyboard navigation"),
                Li("📊 Single vs multiple open modes with state management"),
                Li("🎨 Smooth expand/collapse animations using CSS Grid"),
                Li("🔄 Automatic chevron rotation and visual feedback"),
            ),
        ),
        
        Section("Basic Usage Demo",
            P("Try the accordion below - click items to expand/collapse:"),
            
            Accordion(
                AccordionItem(
                    "What is RustyTags?",
                    P("RustyTags is a high-performance HTML generation library that combines Rust-powered performance with modern Python web development."),
                    P("It provides 3-10x faster rendering than pure Python solutions."),
                    id="what-is"
                ),
                AccordionItem(
                    "What are Xtras components?",
                    P("Xtras components are anatomical patterns that solve complex UI coordination problems."),
                    P("They focus on functionality and accessibility rather than styling."),
                    id="what-are-xtras"
                ),
                AccordionItem(
                    "How do animations work?",
                    P("Animations use CSS Grid transitions for smooth expand/collapse effects."),
                    P("The grid-template-rows property transitions from 0fr (collapsed) to 1fr (expanded)."),
                    id="how-animations"
                ),
                type="single",
                cls="border border-gray-200 rounded-lg overflow-hidden"
            )
        ),
        
        Section("Code Example",
            P("Here's the code for the accordion above:"),
            CodeBlock("""
Accordion(
    AccordionItem(
        "What is RustyTags?",
        P("RustyTags is a high-performance HTML generation library..."),
        P("It provides 3-10x faster rendering than pure Python."),
        id="what-is"
    ),
    AccordionItem(
        "What are Xtras components?",
        P("Xtras components are anatomical patterns..."),
        P("They focus on functionality and accessibility."),
        id="what-are-xtras"
    ),
    AccordionItem(
        "How do animations work?",
        P("Animations use CSS Grid transitions..."),
        P("The grid-template-rows property transitions..."),
        id="how-animations"
    ),
    type="single",
    cls="border border-gray-200 rounded-lg overflow-hidden"
)""", code_cls="language-python")
        ),
        
        Section("Multiple Mode Demo",
            P("Accordion with multiple items open simultaneously:"),
            
            Accordion(
                AccordionItem(
                    "Performance Features",
                    Ul(
                        Li("Rust-powered HTML generation"),
                        Li("Memory optimization and caching"),
                        Li("Thread-local pools")
                    ),
                    id="performance",
                    open=True
                ),
                AccordionItem(
                    "Developer Experience",
                    Ul(
                        Li("FastHTML-style syntax"),
                        Li("Automatic type conversion"),
                        Li("Smart attribute handling")
                    ),
                    id="dev-experience"
                ),
                AccordionItem(
                    "Framework Integration",
                    Ul(
                        Li("FastAPI support"),
                        Li("Flask integration"),
                        Li("Django compatibility")
                    ),
                    id="frameworks"
                ),
                type="multiple",
                cls="border border-gray-200 rounded-lg overflow-hidden mt-4"
            )
        ),
        
        Section("API Reference",
            CodeBlock("""
# Main Accordion container
def Accordion(
    *children,                               # AccordionItem components
    type: Literal["single", "multiple"] = "single", # Open mode
    signal: str = "",                        # Signal name (auto-generated)
    cls: str = "",                          # Root container classes
    **attrs: Any                            # Additional HTML attributes
) -> rt.HtmlString

# Individual accordion item
def AccordionItem(
    trigger_content,                        # Content for the trigger button
    *children,                              # Collapsible content
    id: str = "",                           # Unique item identifier
    open: bool = False,                     # Initial open state (multiple mode)
    cls: str = "",                          # Item classes
    **attrs: Any                            # Additional HTML attributes
)""", code_cls="language-python")
        ),
        
        Section("HTML Output Structure",
            P("The Accordion component generates this semantic HTML:"),
            CodeBlock("""
<section class="accordion-container" data-accordion-root>
    <details class="group border-b" data-accordion-item>
        <summary class="flex justify-between py-4 cursor-pointer">
            Item Title
            <svg class="accordion-chevron transition-transform">...</svg>
        </summary>
        
        <div class="grid transition-[grid-template-rows]">
            <div class="accordion-content-wrapper pb-4">
                Item Content
            </div>
        </div>
    </details>
    <!-- More accordion items... -->
</section>""", code_cls="language-html")
        ),
        
        Div(
            A("← Back to Home", href="/", cls="color-blue-6 text-decoration-underline"),
            cls="mt-8"
        ),
        
        signals=Signals(message=""),
    )


@app.get("/cmds/{command}/{sender}")
@datastar_response
async def commands(command: str, sender: str, request: Request, signals: ReadSignals):
    """Trigger events and broadcast to all connected clients"""
    signals = Signals(**signals) if signals else {}
    backend_signal = event(command)
    await emit_async(backend_signal, sender, signals=signals, request=request)

@app.get("/updates")
@datastar_response
async def event_stream(request: Request, signals: ReadSignals):
    """SSE endpoint with automatic client management"""
    with Client(topics=["updates"]) as client:
        async for update in client.stream():
            yield update
    
@on("message.send")
async def notify(sender, request: Request, signals: Signals):
    message = signals.message or "No message provided" 
    yield sse_elements(Div(f"Server processed message: {message}", cls="text-lg text-bold mt-4 mt-2"),
                             selector="#updates", mode=ElementPatchMode.APPEND, topic="updates")
    yield sse_signals({"message": ""}, topic="updates")
    # yield Notification(f"Server notification: {message}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("lab.docs.app:app", host="0.0.0.0", port=8800, reload=True)




