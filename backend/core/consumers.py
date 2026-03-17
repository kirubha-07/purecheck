import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from core.models import LiveAlert


class AlertConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time alert feed."""
    
    async def connect(self):
        """Handle WebSocket connection."""
        self.city = self.scope['url_route']['kwargs']['city'].lower()
        self.room_group_name = f'alerts_{self.city}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        print(f"[WebSocket] Client connected to alerts for {self.city}")
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"[WebSocket] Client disconnected from alerts for {self.city}")
    
    async def receive(self, text_data):
        """Handle incoming WebSocket message."""
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON'
            }))
            return
    
    async def alert_message(self, event):
        """
        Receive alert message from channel layer and send to WebSocket.
        Called by group_send from other parts of the app.
        """
        message = event['message']
        
        await self.send(text_data=json.dumps(message))
