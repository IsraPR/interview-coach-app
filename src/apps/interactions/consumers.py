import asyncio
import json
import time


from channels.generic.websocket import AsyncWebsocketConsumer
from typing import Dict, Any
from apps.ai_engine.s2s.session_manger import S2sSessionManager
from core.settings.base import logger
from core.settings.base import DEFAULT_REGION, SPEECH_TO_SPEECH_MODEL_ID


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
        self.session_tasks = set()
        self.transcription = []
        self.start_time = None
        self.write_transcript = False
        self.role = "Unknown"
        self.session_started = False
        self.input_queue = asyncio.Queue()
        await self.accept()
        await self.safe_send({"event": {"message": "Connected!"}})

    async def disconnect(self, code: int):
        """
        A robust disconnect method with a delay to prevent SDK race conditions.
        """
        try:
            logger.info(
                "Disconnect initiated. Closing stream manager first..."
            )

            if self.stream_manager:
                await self.stream_manager.close()
            await asyncio.sleep(0.2)
            logger.info(
                f"Cancelling {len(self.session_tasks)} background tasks..."
            )
            for task in self.session_tasks:
                task.cancel()
            if self.session_tasks:
                await asyncio.gather(
                    *self.session_tasks, return_exceptions=True
                )

            logger.info("Graceful disconnect complete.")

        except Exception as e:
            logger.error(f"Error during graceful disconnect: {e}")

    async def receive(self, text_data: str = None):
        try:
            data = json.loads(text_data)
            if "body" in data:
                data = json.loads(data["body"])
            if "event" not in data:
                return

            event_type = list(data["event"].keys())[0]
            if not self.session_started:
                self.session_started = True
                self.stream_manager = S2sSessionManager(
                    model_id=SPEECH_TO_SPEECH_MODEL_ID,
                    region=DEFAULT_REGION,
                    mcp_client=None,
                    strands_agent=None,
                )
                await self.stream_manager.initialize_stream()

                forward_task = asyncio.create_task(self.forward_responses())

                self.session_tasks.add(forward_task)
                forward_task.add_done_callback(self.session_tasks.discard)
                self.session_tasks.add(self.stream_manager.response_task)
                self.stream_manager.response_task.add_done_callback(
                    self.session_tasks.discard
                )

                self.session_tasks.add(self.stream_manager.response_audio_task)
                self.stream_manager.response_audio_task.add_done_callback(
                    self.session_tasks.discard
                )

            if event_type == "promptStart":
                prompt_name = data["event"]["promptStart"]["promptName"]
                self.stream_manager.prompt_name = prompt_name
                self.start_time = time.perf_counter()

            elif event_type == "contentStart":
                content_name = data["event"]["contentStart"]["contentName"]
                if data["event"]["contentStart"].get("type") == "AUDIO":
                    self.stream_manager.audio_content_name = content_name

            if event_type == "audioInput":
                prompt_name = data["event"]["audioInput"]["promptName"]
                content_name = data["event"]["audioInput"]["contentName"]
                audio_base64 = data["event"]["audioInput"]["content"]
                self.stream_manager.add_audio_chunk(
                    prompt_name, content_name, audio_base64
                )
            else:
                # Forward to Bedrock
                await self.stream_manager.send_raw_event(data)
        except Exception as e:
            logger.error(f"Receive error: {e}")
            await self.send(
                text_data=json.dumps(
                    {"error": f"Unexpected server error: {str(e)}"}
                )
            )

    async def create_transcription(self, response: Dict[str, Any]):
        if "contentStart" in response["event"]:
            content_start = response["event"]["contentStart"]
            self.role = content_start["role"]
            if "additionalModelFields" in content_start:
                try:
                    additional_fields = json.loads(
                        content_start["additionalModelFields"]
                    )
                    if (
                        additional_fields.get("generationStage")
                        == "SPECULATIVE"
                    ):
                        logger.trace("SPECULATIVE content detected:")
                        self.write_transcript = True
                    else:
                        self.write_transcript = False
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing additionalModelFields: {e}")
                    raise e

        if "textOutput" in response["event"]:
            text_content = response["event"]["textOutput"]["content"]
            # Check if there is a barge-in
            if '{ "interrupted" : true }' in text_content:
                logger.trace(
                    "Barge-in detected. Front should cancel audio output."
                )  # TODO: Add logic to handle barge-in in transcripts
            if self.role == "ASSISTANT" and self.write_transcript:
                transcript = {
                    "role": "coach",
                    "content": text_content,
                    "timestamp": round(
                        time.perf_counter() - self.start_time, 2
                    ),
                }
                self.transcription.append(transcript)
            elif self.role == "USER":
                transcript = {
                    "role": "user",
                    "content": text_content,
                    "timestamp": round(
                        time.perf_counter() - self.start_time, 2
                    ),
                }
                self.transcription.append(transcript)

    async def forward_responses(self):
        try:
            while True:
                response = await self.stream_manager.output_queue.get()

                if not isinstance(response, dict):
                    logger.warning(f"Non-dict response received: {response}")
                    continue

                await self.create_transcription(response)

                await self.safe_send(response)

        except asyncio.CancelledError:
            # This is the expected, clean way for this task to exit.
            logger.info("Forwarding task has been gracefully cancelled.")
        except Exception as e:
            logger.error(f"Forwarding task failed unexpectedly: {e}")
        finally:
            # If this task ends for ANY reason (crash or cancellation),
            # we should trigger the disconnect process for the whole consumer.
            await self.close()
