from ninja import Router
from .schemas import BasicChat
from apps.agents.services.workflow_service import invoke_multitask_agent

from django.http import StreamingHttpResponse

router = Router(tags=["agents"])


@router.post("/chat")
def workflow_1_ep(request, payload: BasicChat):
    async def generate_sse():
        try:
            async for event in invoke_multitask_agent(payload.prompt):
                if "data" in event:
                    chunk = event["data"].replace("\n", "\ndata: ")
                    # SSE requires "data: <payload>\n\n"
                    yield f"data: {chunk}\n\n"
        except Exception as e:
            yield f"data: Error: {str(e)}\n\n"

    return StreamingHttpResponse(
        generate_sse(),
        content_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
