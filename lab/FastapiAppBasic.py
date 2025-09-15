from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from rusty_tags import *
from rusty_tags import Section as HTMLSection
from rusty_tags.utils import create_template
from rusty_tags.datastar import Signals, DS
from rusty_tags.events import event, emit_async, on, ANY
from rusty_tags.client import Client
from rusty_tags.starlette import *

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




