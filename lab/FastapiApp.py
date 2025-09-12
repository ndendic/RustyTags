from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from rusty_tags import *
from rusty_tags.utils import create_template
from rusty_tags.datastar import Signals, DS
from rusty_tags.events import event, emit_async, on, ANY
from rusty_tags.client import Client
from rusty_tags.starlette import *
from datastar_py.fastapi import  ReadSignals
from datastar_py.consts import ElementPatchMode
from uuid import uuid4
from typing import Any
from rusty_tags.components.inputs import Input
from rusty_tags.components.sidebar import Sidebar, SidebarItem, SidebarToggle, create_nav_item
from fastapi.staticfiles import StaticFiles

hdrs = (Link(rel='stylesheet', href='/static/css/main.css'),)
htmlkws = dict(cls="")
bodykws = dict(cls="page", signals=Signals(message="", conn=""))
page = create_template(hdrs=hdrs, htmlkw=htmlkws, bodykw=bodykws)

app = FastAPI()
app.mount("/static", StaticFiles(directory="lab/static"), name="static")

def Section(title, *content):
    return Div(
        H2(title),
        Div(
            *content,
        ),  
    )

def Notification(message, topic: str | list[str] = "updates", sender: str | Any = ANY):
    element = Div(
        Span(
            CustomTag('uk-icon', icon='rocket'),
            cls='flex-none mr-2'
        ),
        message,
        cls='flex items-center text-primary'
    )
    return execute_script(f"UIkit.notification({{message: '{element}', pos: 'top-right'}})", 
                          topic=topic, sender=sender)

@app.get("/")
@page(title="FastAPI App", wrap_in=HTMLResponse)
def index():
    return Main(
        Section("Server event updates demo 🙂",
            Form(
                Input(label="Message", placeholder="Something...", 
                      supporting_text="Send server some message and press Enter", 
                      type="text", bind="message"),
                on_submit=DS.get(f"/cmds/message.send/{uuid4().hex}/")
                # on_submit="@post('/cmds/commands/user.global', {contentType: 'form'})"
            ),
            Div(id="updates")
        ),
        cls="container",
        signals=Signals(message=""),
        on_load=DS.get("/updates")
    )

@app.get("/playground")
@page(title="Playground 🎉", wrap_in=HTMLResponse)
def playground():
    # Create navigation items
    nav_items = [
        create_nav_item("Dashboard", href="/", icon="🏠"),
        create_nav_item("Components", icon="🧩", children=[
            {"label": "Forms", "href": "/forms"},
            {"label": "Navigation", "href": "/navigation"},
            {"label": "Layout", "href": "/layout"}
        ]),
        create_nav_item("Settings", href="/settings", icon="⚙️"),
        create_nav_item("Help", href="/help", icon="❓")
    ]
    
    return Div(
        # Sidebar component
        Sidebar(
            *nav_items,
            title="RustyTags UI",
            collapsed=False,
            width="280px"
        ),
        
        # Main content area with header
        Div(
            # Header with toggle button
            Header(
                SidebarToggle(button_class="sidebar-toggle-btn"),
                H1("Sidebar Demo"),
                cls="page-header"
            ),
            
            Main(
                P("This is a demo of the interactive sidebar component built with Open Props UI and Datastar."),
                
                Section("Features",
                    Ul(
                        Li("🎨 Open Props UI styling"),
                        Li("⚡ Datastar interactivity"), 
                        Li("📱 Responsive design"),
                        Li("🔧 Collapsible sections"),
                        Li("🖱️ Toggle collapse/expand")
                    )
                ),
                
                cls="main-content"
            ),
            
            cls="page-with-sidebar",
            **{
                "data-style": "margin-inline-start: $collapsed ? '60px' : '280px'"
            }
        ),
        
        cls="playground-layout"
    )

@app.get("/cmds/{command}/{sender}")
@datastar_response
async def commands(command: str, sender: str, request: Request, signals: ReadSignals):
    """Trigger events and broadcast to all connected clients"""
    signals = Signals(signals) if signals else {}
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




