import json
import logging
from urllib.parse import unquote
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from core.models import LiveAlert


logger = logging.getLogger(__name__)


class AlertConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time alert feed."""
    
    async def connect(self):
        """Handle WebSocket connection."""
        self.city = unquote(self.scope['url_route']['kwargs']['city']).strip().lower()
        self.room_group_name = f'alerts_{self.city}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        recent_alerts = await self.get_recent_alerts()
        for alert in recent_alerts:
            await self.send(text_data=json.dumps(alert))

        logger.info("[WebSocket] Client connected to alerts for %s", self.city)
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info("[WebSocket] Client disconnected from alerts for %s", self.city)
    
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

    @database_sync_to_async
    def get_recent_alerts(self):
        alerts = LiveAlert.objects.filter(
            city__iexact=self.city
        ).order_by('-created_at')[:5]

        return [
            {
                'id': a.id,
                'city': a.city,
                'food_item': a.food_item,
                'risk_level': a.risk_level,
                'message': a.message,
                'created_at': a.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
            for a in alerts
        ]
