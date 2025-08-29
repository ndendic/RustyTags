import asyncio
import uuid
from typing import Any, Dict

from .events import event, ANY

SENTINEL = object()
client_event = event("client_lifecycle")
active_clients: Dict[str, 'Client'] = {}    

class Client:
    """Manages individual client connections with automatic lifecycle handling"""
    
    def __init__(self, 
                 client_id: str | None = None, 
                 topics: list[str] | dict[str, list[str]] | Any = ["ANY"],
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
        else:
            self.subscribe(topics)
        

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
            client_event.emit("system", action="connect", client=self)
            print(f"📡 Client {self.client_id} connected. Total: {len(active_clients)}")
        return self
    
    def disconnect(self):
        """Disconnect client and clean up resources"""
        if self.connected:
            active_clients.pop(self.client_id, None)
            self.connected = False
            # Send disconnection signal  
            client_event.emit("system", action="disconnect", client=self)
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

