import asyncio
import collections.abc as c
import inspect
import threading
import uuid
from typing import Any, Dict, TypeVar, Optional

from blinker import ANY, Signal
from blinker import signal as event

from pydantic import BaseModel, Field

SENTINEL = object()
client_signal = event("client_lifecycle")
active_clients: Dict[str, 'Client'] = {}

async def _aiter_sync_gen(gen):
    """Bridge a sync generator to async without blocking the event loop."""
    loop = asyncio.get_running_loop()
    q = asyncio.Queue()
    DONE = object()

    def pump():
        try:
            for item in gen:
                loop.call_soon_threadsafe(q.put_nowait, item)
        finally:
            loop.call_soon_threadsafe(q.put_nowait, DONE)

    threading.Thread(target=pump, daemon=True).start()

    while True:
        item = await q.get()
        if item is DONE:
            break
        yield item

async def _aiter_results(handler, *args, **kwargs):
    """
    Call handler(*args, **kwargs) and yield zero-or-more items:
      - async generator  -> yield each item
      - coroutine        -> yield awaited value once
      - sync generator   -> yield each item (via thread bridge)
      - plain sync value -> yield once
    """
    rv = handler(*args, **kwargs)

    if inspect.isasyncgen(rv):          # async generator
        async for x in rv:
            yield x
        return

    if inspect.isawaitable(rv):         # coroutine/awaitable
        yield await rv
        return

    if inspect.isgenerator(rv):         # sync generator
        async for x in _aiter_sync_gen(rv):
            yield x
        return

    # plain sync value
    yield rv

class Client:
    """Manages individual client connections with automatic lifecycle handling"""
    
    def __init__(self, client_id: str | None = None):
        self.client_id = client_id or str(uuid.uuid4())
        self.queue = asyncio.Queue()
        self.connected = False
        
    def connect(self):
        """Connect client and register with signal system"""
        if not self.connected:
            active_clients[self.client_id] = self
            self.connected = True
            # Send connection signal
            client_signal.send("system", action="connect", client=self)
            print(f"📡 Client {self.client_id} connected. Total: {len(active_clients)}")
        return self
    
    def disconnect(self):
        """Disconnect client and clean up resources"""
        if self.connected:
            active_clients.pop(self.client_id, None)
            self.connected = False
            # Send disconnection signal  
            client_signal.send("system", action="disconnect", client=self)
            print(f"📡 Client {self.client_id} disconnected. Total: {len(active_clients)}")
        return self
    
    async def stream(self, delay: float = 0.1):
        """Async generator for streaming updates to this client"""
        try:
            while self.connected:
                try:
                    event = await asyncio.wait_for(self.queue.get(), timeout=delay)
                    if event is None or event is SENTINEL or isinstance(event, Exception):
                        continue
                    yield event
                except asyncio.TimeoutError:
                    continue
        except Exception as e:
            print(f"Client {self.client_id} SSE stream error: {e}")
        finally:
            self.disconnect()
    
    def send(self, item):
        """Send item to this client's queue"""
        if self.connected:
            try:
                self.queue.put_nowait(item)
                return True
            except Exception:
                self.disconnect()
                return False
        return False
    
    def __enter__(self):
        return self.connect()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

# TODO: This is a hack to broadcast to all clients. It should be replaced with a more efficient way to broadcast to specific clients or all
def broadcast_to_clients(item):
    """Broadcast item to all active client queues"""
    for client_id, client in active_clients.items():
        client.send(item)

async def blinker_broadcast(sig, sender, *args, **kwargs):
    """Modified blinker sender that broadcasts to all clients"""
    async def worker(recv):
        try:
            async for item in _aiter_results(recv, sender, *args, **kwargs):
                if item is not None:
                    broadcast_to_clients(item)
        except Exception as e:
            broadcast_to_clients(e)

    # Run all receivers concurrently and broadcast results
    try:
        async with asyncio.TaskGroup() as tg:
            for recv in sig.receivers_for(sender):
                tg.create_task(worker(recv))
    finally:
        broadcast_to_clients(SENTINEL)

def broadcast(backend_signal, sender, *args, **kwargs):
    """Send to all connected clients using Blinker broadcasting"""
    asyncio.create_task(blinker_broadcast(backend_signal, sender, *args, **kwargs))


F = TypeVar("F", bound=c.Callable[..., Any])

def on_event(signal: str|Signal, sender: Any = ANY, weak: bool = True) -> c.Callable[[F], F]:
    if isinstance(signal, Signal):
        sig = signal
    else:
        sig = event(signal)
    def decorator(fn):
        sig.connect(fn, sender, weak)
        return fn
    return decorator

# Export all public components
__all__ = [
    'Client',
    'event', 
    'on_event',
    'broadcast',
    'client_signal',
    'SENTINEL'
]