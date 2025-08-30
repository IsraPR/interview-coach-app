import asyncio
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from typing import Dict, Any
from loguru import logger


class SpeechToSpeechConsumer(AsyncWebsocketConsumer):
    async def safe_send(self, payload: Dict[str, Any] | str):
        try:
            if not isinstance(payload, str):
                payload = json.dumps(payload)
            await self.send(text_data=payload)
        except Exception as e:
            logger.error(f"Failed to send message to frontend: {e}")

    async def connect(self):
        self.stream_manager = None
        self.forward_task = None
        self.session = None
        self.transcription = []
        self.start_time = None
        self.write_transcript = False
        self.role = "Unknown"
        self.input_queue = asyncio.Queue()
        await self.accept()
        await self.safe_send({"event": {"message": "Connected!"}})

    async def disconnect(self, code: int):
        try:

            if self.forward_task:
                self.forward_task.cancel()
        except Exception as e:
            logger.error(f"Error on disconnect: {e}")

    async def receive(self, text_data: str = None):
        try:
            data = json.loads(text_data)
            logger.debug(f"This is the message received: {data}")
            await self.safe_send({"hello": "world xd 22"})
            await self.safe_send({"hello": "hermoso 🥹😭"})
        except Exception as e:
            logger.exception(e)
            await self.safe_send(
                text_data=json.dumps(
                    {"error": f"Unexpected server error: {str(e)}"}
                )
            )
