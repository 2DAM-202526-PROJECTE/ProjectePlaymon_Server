from flask import Blueprint, Response, stream_with_context
from .sse_broker import subscribe, unsubscribe, subscribe_notifications, unsubscribe_notifications

sse_bp = Blueprint("sse", __name__)


def _generate(q):
    yield "data: connected\n\n"
    while True:
        try:
            event_type, data = q.get(timeout=25)
            yield f"event: {event_type}\ndata: {data}\n\n"
        except Exception:
            yield ": ping\n\n"


@sse_bp.get("/api/stream/users")
def stream_users():
    q = subscribe()

    def generate():
        try:
            yield from _generate(q)
        finally:
            unsubscribe(q)

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@sse_bp.get("/api/stream/notifications")
def stream_notifications():
    q = subscribe_notifications()

    def generate():
        try:
            yield from _generate(q)
        finally:
            unsubscribe_notifications(q)

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
