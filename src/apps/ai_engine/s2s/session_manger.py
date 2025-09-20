import asyncio
import json
import warnings
import uuid
import time
import os

from typing import Dict, Any

from aws_sdk_bedrock_runtime.client import (
    BedrockRuntimeClient,
    InvokeModelWithBidirectionalStreamOperationInput,
)
from aws_sdk_bedrock_runtime.models import (
    InvokeModelWithBidirectionalStreamInputChunk,
    BidirectionalInputPayloadPart,
)
from aws_sdk_bedrock_runtime.config import (
    Config,
    HTTPAuthSchemeResolver,
    SigV4AuthScheme,
)
from smithy_aws_core.credentials_resolvers.environment import (
    EnvironmentCredentialsResolver,
)

from smithy_http.aio.aiohttp import AIOHTTPClient
from smithy_aws_core.credentials_resolvers.container import (
    ContainerCredentialsResolver,
)
from .events import S2sEvent
from .integration import inline_agent, kb

from core.settings.base import logger

# Suppress warnings
warnings.filterwarnings("ignore")


class S2sSessionManager:
    """Manages bidirectional streaming with AWS Bedrock using asyncio"""

    def __init__(
        self,
        region: str,
        model_id: str = "amazon.nova-sonic-v1:0",
        mcp_client=None,
        strands_agent=None,
    ):
        """Initialize the stream manager."""
        self.model_id = model_id
        self.region = region

        # Audio and output queues
        self.audio_input_queue = asyncio.Queue()
        self.output_queue = asyncio.Queue()

        self.response_task = None
        self.response_audio_task = None
        self.stream = None
        self.is_active = False
        self.bedrock_client = None

        # Session information
        self.prompt_name = None  # Will be set from frontend
        self.content_name = None  # Will be set from frontend
        self.audio_content_name = None  # Will be set from frontend
        self.toolUseContent = ""
        self.toolUseId = ""
        self.toolName = ""
        self.mcp_loc_client = mcp_client
        self.strands_agent = strands_agent
        self.stream_healthy = asyncio.Event()  # NEW: The health signal
        self.initialization_error = None  # NEW: To store any startup error

    def _initialize_client(self):
        """Initialize the Bedrock client."""
        if os.environ.get("STAGE") == "dev":
            logger.debug(
                f"{os.environ.get('STAGE')} config, using local resolver"
            )
            resolver = EnvironmentCredentialsResolver()
        else:
            logger.debug(
                f"{os.environ.get('STAGE')} config, using container resolver"
            )
            http_client = AIOHTTPClient()
            resolver = ContainerCredentialsResolver(http_client=http_client)

        config = Config(
            endpoint_uri=f"https://bedrock-runtime.{self.region}.amazonaws.com",
            region=self.region,
            aws_credentials_identity_resolver=resolver,
            http_auth_scheme_resolver=HTTPAuthSchemeResolver(),
            http_auth_schemes={"aws.auth#sigv4": SigV4AuthScheme()},
        )
        self.bedrock_client = BedrockRuntimeClient(config=config)

    async def initialize_stream(self):
        """Initialize the bidirectional stream with Bedrock."""
        try:
            if not self.bedrock_client:
                self._initialize_client()
        except Exception as ex:
            self.is_active = False
            print(f"Failed to initialize Bedrock client: {str(ex)}")
            raise ex

        try:
            # Initialize the stream
            self.stream = (
                await (
                    self.bedrock_client.invoke_model_with_bidirectional_stream(
                        InvokeModelWithBidirectionalStreamOperationInput(
                            model_id=self.model_id
                        )
                    )
                )
            )
            self.is_active = True

            # Start listening for responses
            self.response_task = asyncio.create_task(self._process_responses())

            # Start processing audio input
            self.response_audio_task = asyncio.create_task(
                self._process_audio_input()
            )

            # Wait a bit to ensure everything is set up
            await asyncio.sleep(0.2)

            print("Stream initialized successfully")
            return self
        except Exception as e:
            self.is_active = False
            print(f"Failed to initialize stream: {str(e)}")
            raise

    async def send_raw_event(self, event_data: Dict[str, Any]):
        try:
            """Send a raw event to the Bedrock stream."""
            if not self.stream or not self.is_active:
                logger.warning("Stream not initialized or closed")
                return

            event_json = json.dumps(event_data)
            # if "audioInput" not in event_data["event"]:
            #    print(event_json)
            event = InvokeModelWithBidirectionalStreamInputChunk(
                value=BidirectionalInputPayloadPart(
                    bytes_=event_json.encode("utf-8")
                )
            )
            await self.stream.input_stream.send(event)

            # Close session
            if "sessionEnd" in event_data["event"]:
                await self.close()

        except Exception as e:
            logger.error(f"Error sending event: {str(e)}")
            raise e

    async def _process_audio_input(self):
        """Process audio input from the queue and send to Bedrock."""
        while self.is_active:
            try:
                # Get audio data from the queue
                data = await self.audio_input_queue.get()

                # Extract data from the queue item
                prompt_name = data.get("prompt_name")
                content_name = data.get("content_name")
                audio_bytes = data.get("audio_bytes")

                if not audio_bytes or not prompt_name or not content_name:
                    logger.warning("Missing required audio data properties")
                    continue

                # Create the audio input event
                audio_event = S2sEvent.audio_input(
                    prompt_name,
                    content_name,
                    (
                        audio_bytes.decode("utf-8")
                        if isinstance(audio_bytes, bytes)
                        else audio_bytes
                    ),
                )

                # Send the event
                await self.send_raw_event(audio_event)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing audio: {e}")
                raise e

    def add_audio_chunk(self, prompt_name, content_name, audio_data):
        """Add an audio chunk to the queue."""
        # The audio_data is already a base64 string from the frontend
        self.audio_input_queue.put_nowait(
            {
                "prompt_name": prompt_name,
                "content_name": content_name,
                "audio_bytes": audio_data,
            }
        )

    async def _process_responses(self):
        """
        Main task to process incoming responses from the Bedrock stream.
        Handles the health check and runs the main message loop.
        """
        try:
            output = await self.stream.await_output()
            # self.stream_healthy.set()  # Signal that the connection is established and healthy.

            # Enter the main loop to process messages one by one.
            while self.is_active:
                await self._handle_next_message(output)

        except Exception as e:
            logger.error(f"Fatal error in Bedrock response task: {e}")
            self.initialization_error = e
        finally:
            logger.debug(
                "Response processing loop ended. Setting health signal and cleaning up."
            )
            self.stream_healthy.set()  # GUARANTEES the connect method will unblock.
            self.is_active = False

    async def _handle_next_message(self, output_stream):
        """Receives, decodes, and dispatches a single message from the stream."""
        try:
            result = await output_stream[1].receive()
            if not (result.value and result.value.bytes_):
                return  # Skip empty messages

            response_data = result.value.bytes_.decode("utf-8")
            json_data = json.loads(response_data)

            await self._dispatch_message(json_data)

        except StopAsyncIteration:
            logger.info("Bedrock stream has ended.")
            self.is_active = False  # Signal the main loop to exit.
        except json.JSONDecodeError:
            logger.warning(
                f"Received non-JSON response from Bedrock: {response_data}"
            )
            await self.output_queue.put({"raw_data": response_data})
        except Exception as e:
            logger.error(f"Error receiving or decoding message: {e}")
            # Depending on severity, you might want to stop the session.
            # For now, we log and continue, but for validation errors, stopping is better.
            if "ValidationException" in str(e):
                self.is_active = False

    async def _dispatch_message(self, json_data: Dict[str, Any]):
        """Inspects a message and routes it to the correct handler (e.g., tool use)."""
        json_data["timestamp"] = int(time.time() * 1000)

        if "event" in json_data:
            event_name = list(json_data["event"].keys())[0]
            event_data = json_data["event"][event_name]

            if event_name == "toolUse":
                self._handle_tool_use_start(event_data)
            elif (
                event_name == "contentEnd" and event_data.get("type") == "TOOL"
            ):
                await self._handle_tool_use_end(event_data)

        # Always forward the original message to the client.
        await self.output_queue.put(json_data)

    def _handle_tool_use_start(self, tool_use_data: Dict[str, Any]):
        """Stores the state of a tool use request when it begins."""
        self.tool_use_content = tool_use_data
        self.tool_name = tool_use_data.get("toolName", "")
        self.tool_use_id = tool_use_data.get("toolUseId", "")
        logger.info(
            f"Tool use detected: {self.tool_name}, ID: {self.tool_use_id}"
        )

    async def _handle_tool_use_end(self, content_end_data: Dict[str, Any]):
        """
        Executes the tool and sends the results back to Bedrock when a
        tool use content block ends.
        """
        prompt_name = content_end_data.get("promptName")
        if not all([prompt_name, self.tool_name, self.tool_use_id]):
            logger.warning("Missing context to handle tool use end. Aborting.")
            return

        logger.info(f"Processing result for tool '{self.tool_name}'")
        tool_result = await self.processToolUse(
            self.tool_name, self.tool_use_content
        )

        # The response sequence must be: start, input, end.
        tool_content_name = f"tool-content-{uuid.uuid4()}"

        # 1. Send tool start event
        start_event = S2sEvent.content_start_tool(
            prompt_name, tool_content_name, self.tool_use_id
        )
        await self.send_raw_event(start_event)

        # 2. Send tool result event
        result_str = (
            json.dumps(tool_result)
            if isinstance(tool_result, dict)
            else str(tool_result)
        )
        result_event = S2sEvent.text_input_tool(
            prompt_name, tool_content_name, result_str
        )
        await self.send_raw_event(result_event)

        # 3. Send tool content end event
        end_event = S2sEvent.content_end(prompt_name, tool_content_name)
        await self.send_raw_event(end_event)

    async def processToolUse(self, toolName, toolUseContent):
        """Return the tool result"""
        logger.debug(f"Tool Use Content: {toolUseContent}")
        toolName = toolName.lower()
        content = None
        result = None
        try:
            if toolUseContent.get("content"):
                # The content is a JSON *string*, so we must parse it first.
                content_json = json.loads(toolUseContent.get("content"))
                # Now `content_json` is a Python dict.
                # We might need the original string or the dict depending on the tool.
                content = toolUseContent.get("content")

            # Simple toolUse to get system time in UTC
            if toolName == "getdatetool":
                from datetime import datetime, timezone

                result = datetime.now(timezone.utc).strftime(
                    "%A, %Y-%m-%d %H-%M-%S"
                )

            # Bedrock Knowledge Bases (RAG)
            if toolName == "getkbtool":
                result = kb.retrieve_kb(content)

            # MCP integration - location search
            if toolName == "getlocationtool":
                if self.mcp_loc_client:
                    result = await self.mcp_loc_client.call_tool(content)

            # Strands Agent integration - weather questions
            if toolName == "externalagent":
                if self.strands_agent:
                    result = self.strands_agent.query(content)

            # Bedrock Agents integration - Bookings
            if toolName == "getbookingdetails":
                try:
                    # Pass the tool use content (JSON string) directly to the agent
                    result = await inline_agent.invoke_agent(content)
                    # Try to parse and format if needed
                    try:
                        booking_json = json.loads(result)
                        if "bookings" in booking_json:
                            result = await inline_agent.invoke_agent(
                                f"Format this booking information for the user: {result}"
                            )
                    except Exception:
                        pass  # Not JSON, just return as is

                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {str(e)}")
                    return {
                        "result": f"Invalid JSON format for booking details: {str(e)}"
                    }
                except Exception as e:
                    print(f"Error processing booking details: {str(e)}")
                    return {
                        "result": f"Error processing booking details: {str(e)}"
                    }

            if not result:
                result = "no result found"

            return {"result": result}
        except Exception as ex:
            print(ex)
            return {
                "result": "An error occurred while attempting to retrieve information related to the toolUse event."
            }

    async def close(self):
        """Close the stream properly. Assumes tasks are cancelled by the owner."""
        if not self.is_active:
            return

        logger.info("Closing S2sSessionManager stream...")
        self.is_active = False

        # The consumer now handles cancelling the tasks.
        # This method's only job is to close the underlying AWS stream.
        if self.stream:
            try:
                await self.stream.input_stream.close()
                logger.info("Bedrock input stream closed.")
            except Exception as e:
                # This is not a critical error, as the stream might already be closed.
                logger.warning(
                    f"Ignoring error while closing Bedrock stream: {e}"
                )
