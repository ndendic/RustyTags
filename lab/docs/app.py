"""RustyTags Documentation App - Modular Structure"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from starlette.staticfiles import StaticFiles
from rusty_tags import *
from rusty_tags.events import event, emit_async, on
from rusty_tags.client import Client
from rusty_tags.starlette import *
from datastar_py.fastapi import ReadSignals
from datastar_py.consts import ElementPatchMode

# Import modular page system
from pages.base import page, Section, Signals
from pages import register_all_routes

app = FastAPI()
app.mount("/static", StaticFiles(directory="lab/docs/static"), name="static")
# Register all component documentation routes
register_all_routes(app)

@app.get("/")
@page(title="RustyTags Documentation", wrap_in=HTMLResponse)
def index():
    return Main(
        H1("RustyTags Documentation"),
        P("A high-performance HTML generation library that combines Rust-powered performance with modern Python web development."),
        
        Section("Component Documentation",
            P("Explore the RustyTags Xtras components:"),
            Ul(
                Li(A("CodeBlock Component", href="/xtras/codeblock", cls="color-blue-6 text-decoration-underline")),
                Li(A("Tabs Component", href="/xtras/tabs", cls="color-blue-6 text-decoration-underline")),
                Li(A("Accordion Component (Simplified)", href="/xtras/accordion", cls="color-blue-6 text-decoration-underline")),
                Li(A("Dialog Component", href="/xtras/dialog", cls="color-blue-6 text-decoration-underline")),
            ),
        ),
        
        Section("Architecture Principles",
            P("RustyTags components follow key principles:"),
            Ul(
                Li("🏗️ Native HTML First - Use browser-native features when available"),
                Li("⚡ Focus on Anatomical Patterns - Solve complex DOM coordination problems"),
                Li("♿️ Accessibility by Default - Built-in WCAG compliance"),
                Li("🎨 Open Props Integration - Semantic design tokens"),
                Li("📊 Datastar Reactivity - Modern reactive web development"),
            ),
        ),
        
        signals=Signals(message=""),
    )


@app.get("/playground")
@page(title="RustyTags Playground", wrap_in=HTMLResponse)
def playground():
    popover_style="background: var(--gray-2); padding: var(--size-1); border-radius: var(--radius-1); border: solid var(--border-size-1);"
    return Main(
        H1("RustyTags Playground"),
        P("This is a playground for RustyTags."),
        Div(Button("Click me",id="myButton", on_click="$anchorOpen = !$anchorOpen", style="width: 300px; height: 100px;"), cls="anchor-container"),

        Div("default", data_anchor="'#myButton'", show="$anchorOpen", style=popover_style),
        Div("bottom-start", data_anchor="'#myButton, bottom-start'", show="$anchorOpen", style=popover_style),
        Div("bottom-end", data_anchor="'#myButton, bottom-end'", show="$anchorOpen", style=popover_style),

        Div("top", data_anchor="'#myButton, top'", show="$anchorOpen", style=popover_style),
        Div("top-start", data_anchor="'#myButton, top-start'", show="$anchorOpen", style=popover_style),
        Div("top-end", data_anchor="'#myButton, top-end'", show="$anchorOpen", style=popover_style),

        Div("left", data_anchor="'#myButton, left'", show="$anchorOpen", style=popover_style),
        Div("left-start", data_anchor="'#myButton, left-start'", show="$anchorOpen", style=popover_style),
        Div("left-end", data_anchor="'#myButton, left-end'", show="$anchorOpen", style=popover_style),

        Div("right", data_anchor="'#myButton, right'", show="$anchorOpen", style=popover_style),
        Div("right-start", data_anchor="'#myButton, right-start'", show="$anchorOpen", style=popover_style),
        Div("right-end", data_anchor="'#myButton, right-end'", show="$anchorOpen", style=popover_style),
        
        
        signals=Signals(anchorOpen=False),
    )

# Event handlers and utility routes below this line
# Component documentation routes are now handled in separate page files

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




