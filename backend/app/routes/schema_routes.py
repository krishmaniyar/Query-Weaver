import asyncio
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.db.schema_loader import load_database_schema
from app import sse_broadcaster

router = APIRouter(prefix="/schema", tags=["schema"])


@router.get("/")
def get_schema():
    try:
        schema_metadata = load_database_schema()
        return schema_metadata
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events")
async def schema_events():
    """SSE endpoint — pushes 'schema_changed' whenever the DB schema is modified."""

    async def event_stream():
        q = sse_broadcaster.subscribe()
        try:
            # Send an initial ping so the browser EventSource confirms connection
            yield "event: connected\ndata: ok\n\n"
            while True:
                try:
                    # Wait up to 30 s, then send a keepalive comment
                    msg = await asyncio.wait_for(q.get(), timeout=30)
                    yield f"event: {msg}\ndata: {{}}\n\n"
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            sse_broadcaster.unsubscribe(q)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
