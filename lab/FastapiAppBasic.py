from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from rusty_tags import *
from rusty_tags import Section as HTMLSection
from rusty_tags.utils import create_template
from rusty_tags.datastar import Signals, DS
from rusty_tags.events import event, emit_async, on, ANY
from rusty_tags.client import Client
from rusty_tags.starlette import *
from rusty_tags.components import Button, Icon

from rusty_tags.components.utils import cn
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

hdrs = (
    # Link(rel='stylesheet', href='https://cdn.jsdelivr.net/npm/franken-ui@2.1.0-next.18/dist/css/core.min.css'),
    # Link(rel='stylesheet', href='https://cdn.jsdelivr.net/npm/franken-ui@2.1.0-next.18/dist/css/utilities.min.css'),
    # Script(src='https://cdn.jsdelivr.net/npm/franken-ui@2.1.0-next.18/dist/js/core.iife.js', type='module'),
    # Script(src='https://cdn.jsdelivr.net/npm/franken-ui@2.1.0-next.18/dist/js/icon.iife.js', type='module'),

    Link(rel='stylesheet', href='https://unpkg.com/open-props'),
    # Link(rel='stylesheet', href='https://unpkg.com/open-props/normalize.min.css'),
    Style("""

        html {
            background: light-dark(var(--gradient-5), var(--gradient-16));
            min-height: 100vh;
            color: light-dark(var(--gray-9), var(--gray-1));
            font-family: var(--font-geometric-humanist);
            font-size: var(--font-size-1);
        }
        main {
            width: min(100% - 2rem, 50rem);
            margin-inline: auto;
        }
    """),
)
htmlkws = dict(lang="en")
bodykws = dict(signals=Signals(message="", conn=""))
page = create_template(hdrs=hdrs, htmlkw=htmlkws, bodykw=bodykws, highlightjs=True)
ftrs=(
    Script("hljs.highlightAll();"),
    Script("lucide.createIcons();"),
)
app = FastAPI()

def Section(title, *content):
    return HTMLSection(
        H2(title),
        *content,
        cls="fluid-flex"
    )
def CodeBlock(*c: str, # Contents of Code tag (often text)
              cls: Enum | str | tuple = (), # Classes for the outer container
              code_cls: Enum | str | tuple = (), # Classes for the code tag
              **kwargs # Additional args for Code tag
              ) -> HtmlString: # Div(Pre(Code(..., cls='uk-codeblock), cls='multiple tailwind styles'), cls='uk-block')
    "CodeBlock with Styling"
    return Div(
        Pre(Code(*c, cls=cn(code_cls), **kwargs),
            # cls=cn((f'bg-gray-100 dark:bg-gray-800 {TextT.gray} p-0.4 rounded text-sm font-mono'))
            ),
#             cls=('bg-gray-100 dark:bg-gray-800 dark:text-gray-200 p-0.4 rounded text-sm font-mono')),
        cls=cn(cls))

@app.get("/")
@page(title="FastAPI App", wrap_in=HTMLResponse)
def index():
    return Main(
            H1("Rusty Tags"),
            P("A high-performance HTML generation library that combines Rust-powered performance with modern Python web development."),
            Section("What Rusty Tags Does",
                P("Rusty Tags generates HTML and SVG content programmatically with:"),
                Ul(
                    Li("⚡ Rust Performance: 3-10x faster than pure Python with memory optimization, caching, and thread-local pools"),
                    Li("🆕 Automatic Mapping Expansion: Dictionaries automatically expand as tag attributes - `Div(\"text\", {\"id\": \"main\"})`"),
                    Li("🏗️ FastHTML-Style Syntax: Callable chaining support - `Div(cls=\"container\")(P(\"Hello\"), Button(\"Click\"))`"),
                    Li("⚡ Datastar Integration: Complete reactive web development with shorthand attributes (`signals`, `show`, `on_click`)"),
                    Li("🎨 Full-Stack Utilities: Page templates, decorators, and framework integrations (FastAPI, Flask, Django)"),
                    Li("🔧 Smart Type System: Native support for `__html__()`, `_repr_html_()`, `render()` methods and automatic type conversion"),
                    Li("📦 Complete HTML5/SVG: All standard tags plus custom tag creation with dynamic names"),
                ),
            ),
            
            Section("Component Demos",
                P("Test the RustyTags components:"),
                Ul(
                    Li(A("Button Component Demo", href="/components/button", cls="color-blue-6 text-decoration-underline")),
                ),
            ),
            
            signals=Signals(message=""),
        )

@app.get("/components/button")
@page(title="Button Component Demo", wrap_in=HTMLResponse)
def button_demo():
    return Main(
        H1("Button Component Demo"),
        P("Testing the Button component with different styles and interactions."),
        
        Section("Basic Buttons",
            P("Plain buttons without styling:"),
            Div(
                Button(Icon("home", lucide_width="24", lucide_height="24"), "Basic Button"),
                " ",
                Button("Disabled Button", disabled=True),
                " ",
                Button("Submit Button", type="submit"),
                cls="flex gap-2 flex-wrap"
            ),
            CodeBlock("""
Div(
    Button(Icon("home"), "Basic Button"),
    " ",
    Button("Disabled Button", disabled=True),
    " ",
    Button("Submit Button", type="submit"),
    cls="flex gap-2 flex-wrap"
)
            """, code_cls="language-python")
        ),
        
        Section("Open Props Styled Buttons",
            P("Using Open Props classes for styling:"),
            Div(
                Button("Primary", cls="surface-1 px-3 py-2 border-radius-2 font-weight-6 color-0 bg-blue-6 border-0 cursor-pointer transition"),
                " ",
                Button("Secondary", cls="surface-1 px-3 py-2 border-radius-2 font-weight-6 color-0 bg-gray-6 border-0 cursor-pointer transition"),
                " ",
                Button("Success", cls="surface-1 px-3 py-2 border-radius-2 font-weight-6 color-0 bg-green-6 border-0 cursor-pointer transition"),
                " ",
                Button("Danger", cls="surface-1 px-3 py-2 border-radius-2 font-weight-6 color-0 bg-red-6 border-0 cursor-pointer transition"),
                cls="flex gap-2 flex-wrap"
            ),
        ),
        
        Section("Interactive Buttons with Datastar",
            P("Buttons that interact with Datastar signals:"),
            Div(
                Button("Click Me!", 
                       on_click="$message = 'Button was clicked!'",
                       cls="surface-1 px-4 py-2 border-radius-2 font-weight-6 color-0 bg-blue-6 border-0 cursor-pointer transition"),
                " ",
                Button("Reset Message", 
                       on_click="$message = ''",
                       cls="surface-1 px-4 py-2 border-radius-2 font-weight-6 color-0 bg-gray-6 border-0 cursor-pointer transition"),
                cls="flex gap-2"
            ),
            Div(
                P("Message: ", Span("$message", cls="font-weight-6")),
                cls="mt-4 p-3 border-radius-2 surface-2"
            ),
        ),
        
        Section("Form Buttons",
            P("Different button types for forms:"),
            Form(
                Div(
                    Button("Submit Form", type="submit", cls="surface-1 px-4 py-2 border-radius-2 font-weight-6 color-0 bg-green-6 border-0 cursor-pointer"),
                    " ",
                    Button("Reset Form", type="reset", cls="surface-1 px-4 py-2 border-radius-2 font-weight-6 color-0 bg-orange-6 border-0 cursor-pointer"),
                    " ",
                    Button("Cancel", type="button", cls="surface-1 px-4 py-2 border-radius-2 font-weight-6 color-0 bg-gray-6 border-0 cursor-pointer"),
                    cls="flex gap-2"
                ),
                cls="mt-2"
            ),
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
    uvicorn.run("lab.FastapiAppBasic:app", host="0.0.0.0", port=8800, reload=True)



# @on(command, sender="user.global")
# def log(sender, request: Request, signals: dict | None):
#     message = (signals or {}).get("message", "No message provided")
#     print(f"Logging via 'log' handler: {message}")
#     return Notification(f"Logging via log handler: {message}")

# @on(command, sender="user.global")
# async def log_event(sender, request: Request, signals: dict | None):
#     message = (signals or {}).get("message", "No message provided")
#     print(f"Logging via 'log_event' handler: {message}")
#     return Notification(f"Logging via 'log_event' handler: {message}")




