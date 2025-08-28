import asyncio
import collections.abc as c
import inspect
import threading
import uuid
from typing import Any, Dict, TypeVar, Optional

from blinker import ANY, Signal
from blinker import signal as event, default_namespace as all_topics

from pydantic import BaseModel, Field

SENTINEL = object()
client_signal = event("client_lifecycle")
active_clients: Dict[str, 'Client'] = {}

class Client:
    """Manages individual client connections with automatic lifecycle handling"""
    
    def __init__(self, 
                 client_id: str | None = None, 
                 topics: list[str] | dict[str, list[str]] | Any = ANY,
                 muted_topics: str | list[str] | Any = ANY):
        self.client_id = client_id or str(uuid.uuid4())
        self.queue = asyncio.Queue()
        self.connected = False
        self.topics = topics
        self.muted_topics = muted_topics
        self.subscriptions = {}
        self.process_topics(topics)
        self.process_muted_topics(muted_topics)
    
    def process_topics(self, topics: list[str] | dict[str, list[str]] | Any = ANY):
        if isinstance(topics, dict):
            for topic, senders in topics.items():
                self.subscribe(topic, senders) if senders is not ANY or [] else self.subscribe(topic)
        elif isinstance(topics, list):
            for topic in topics:
                self.subscribe(topic)
        elif isinstance(topics, str):
            self.subscribe(topics)
        else:
            for topic in all_topics:
                self.subscribe(topic)

    def process_muted_topics(self, muted_topics: str | list[str] | Any = ANY):
        if isinstance(muted_topics, list):
            for topic in muted_topics:
                self.unsubscribe(topic)
        elif isinstance(muted_topics, str):
            self.unsubscribe(muted_topics)        

    def subscribe(self, topic: str, senders: list[str] | Any = ANY):
        """Subscribe to a topic with optional sender filtering"""
        sig = event(topic)
        senders_set = set(senders) if senders is not ANY else ANY
        
        # Receiver function for this subscription
        # async def topic_receiver(sender, result: Any):
        async def topic_receiver(sender, result: Any):
            if senders_set is ANY or sender in senders_set:
                if result is not None:
                    self.queue.put_nowait(result)
        
        # Connect directly to the blinker signal
        sig.connect(topic_receiver, weak=False)
        self.subscriptions[topic] = {
            'senders': senders_set,
            'receiver': topic_receiver,
            'signal': sig
        }

    def unsubscribe(self, topic: str):
        """Unsubscribe from a topic"""
        if topic in self.subscriptions:
            sub = self.subscriptions[topic]
            sub['signal'].disconnect(sub['receiver'])
            del self.subscriptions[topic]

    def connect(self):
        """Connect client and register with signal system"""
        if not self.connected:
            active_clients[self.client_id] = self
            self.connected = True
            # Send connection signal
            client_signal.send("system", action="connect", client=self, _async_wrapper=sync_wrapper)
            print(f"📡 Client {self.client_id} connected. Total: {len(active_clients)}")
        return self
    
    def disconnect(self):
        """Disconnect client and clean up resources"""
        if self.connected:
            active_clients.pop(self.client_id, None)
            self.connected = False
            # Send disconnection signal  
            client_signal.send("system", action="disconnect", client=self, _async_wrapper=sync_wrapper)
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

# TODO: This is a hack to broadcast to all clients. It should be replaced with a more efficient way to broadcast to specific clients or all

async def blinker_broadcast(sig, sender, *args, **kwargs):
    """Modified blinker sender that broadcasts to all clients"""
    async def worker(recv):
        try:
            async for item in _aiter_results(recv, sender, *args, **kwargs):
                if item is not None:
                    print(f"Broadcasting to clients: {item}")
        except Exception as e:
            print(f"Error broadcasting to clients: {e}")

    # Run all receivers concurrently and broadcast results
    try:
        async with asyncio.TaskGroup() as tg:
            for recv in sig.receivers_for(sender):
                tg.create_task(worker(recv))
    finally:
        print(f"Completed broadcasting of {sig.name} from {sender}")

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

def sync_wrapper(func):
    async def inner(*args, **kwargs):
        func(*args, **kwargs)
    return inner

def async_wrapper(func):
    def inner(*args, **kwargs):
        loop = asyncio.get_running_loop()
        loop.create_task(func(*args, **kwargs))        
    return inner

def send(signal: str|Signal, sender: Any = ANY, *args, **kwargs):
    backend_signal = signal if isinstance(signal, Signal) else event(signal)
    backend_signal.send(sender, *args, **kwargs, _async_wrapper=async_wrapper)

async def send_async(signal: str|Signal, sender: Any = ANY, *args, **kwargs):
    backend_signal = signal if isinstance(signal, Signal) else event(signal)
    await backend_signal.send_async(sender, *args, **kwargs, _sync_wrapper=sync_wrapper)

# Export all public components
__all__ = [
    'Client',
    'event', 
    'on_event',
    'broadcast',
    'client_signal',
    'SENTINEL'
]