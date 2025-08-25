from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from rusty_tags import *
from rusty_tags.datastar import DS, signals
from rusty_tags.utils import create_page_decorator, page_template
from rusty_tags.blinker import event
from datastar_py.fastapi import datastar_response, ReadSignals, ServerSentEventGenerator as SSE
from blinker import signal as blinker_signal
import asyncio

hdrs = (
    Script(src="https://cdn.jsdelivr.net/gh/starfederation/datastar@main/bundles/datastar.js", type="module"),
    Link(rel='stylesheet', href='https://cdn.jsdelivr.net/npm/franken-ui@2.1.0-next.18/dist/css/core.min.css'),
    Link(rel='stylesheet', href='https://cdn.jsdelivr.net/npm/franken-ui@2.1.0-next.18/dist/css/utilities.min.css'),
    Script(src='https://cdn.jsdelivr.net/npm/franken-ui@2.1.0-next.18/dist/js/core.iife.js', type='module'),
    Script(src='https://cdn.jsdelivr.net/npm/franken-ui@2.1.0-next.18/dist/js/icon.iife.js', type='module')
)
htmlkws = dict(cls="bg-background text-foreground font-sans antialiased")
bodykws = dict(cls="h-screen p-16 bg-white text-foreground font-sans antialiased")
page = create_page_decorator(hdrs=hdrs, htmlkw=htmlkws, bodykw=bodykws)
template = page_template(hdrs=hdrs, htmlkw=htmlkws, bodykw=bodykws)

app = FastAPI()

def Section(title, *content):
    return Div(
        H2(title, cls="uk-h2 mb-4"),
        Div(
            *content,
            cls=" border rounded-md p-4"
        ),  
        cls="my-4 max-w-md"
    )

@page(title="FastAPI App")
def index():
    partial = Main(
        H1("Hello, world!", cls="uk-h3 mb-2"),
        Span("Welcome to RustyTags! 🙂"),
        Section("Counter", P("Count: ", Span(text="$count"), cls="text-lg"),
            Button("Count++", on_click=DS.increment("count"), cls="uk-btn uk-btn-default"),
            Button("Count--", on_click=DS.decrement("count"), cls="uk-btn uk-btn-default"),
        ),
        Section("Updates", 
            Button("Get some updates", on_click=DS.get("/queries/user"), cls="uk-btn uk-btn-default"),    
            Input(type="text", id="message",bind="message", cls="uk-input"),
            Div(id="updates")
        ),
    
        signals=signals(count=0, message=""),
        on_load=DS.get("/updates")
    )
    return partial


@app.get("/")
def read_root():
    return HTMLResponse(index())

events_signal = blinker_signal("events")
results_queue = asyncio.Queue()

@app.get("/queries/{sender}")
@datastar_response
async def queries(sender: str, signals: ReadSignals):
    """Trigger events and return their results immediately"""
    events_results = events_signal.send(sender, signals=signals)
    await results_queue.put(events_results)


@event("events", sender="user")
def on_event(sender, signals: dict | None):
    message = (signals or {}).get("message", "No message provided")
    return SSE.execute_script(f"UIkit.notification({{message: '{message}'}})")

@event("events", sender="user")
def on_event_2(sender, signals: dict | None):
    message = (signals or {}).get("message", "No message provided")
    return SSE.patch_elements(Div(f"Server processed message: {message}",id="updates", cls="text-lg text-bold mt-4 mt-2"))

@app.get("/updates")
@datastar_response
async def event_stream(signals: ReadSignals):
    """SSE endpoint that processes queued events"""
    async def gen():
        try:
            while True:
                try:
                    # Check for queued events
                    events = results_queue.get_nowait()
                    for _, event in events:
                        if event is not None:
                            yield event
                except asyncio.QueueEmpty:
                    # No events, wait a bit
                    await asyncio.sleep(0.1)
                    # Send keep-alive ping
                    yield SSE.patch_signals({"_sse_ping": "ok"})
        except Exception as e:
            print(f"SSE stream error: {e}")

    return gen()
    
