import queue
import threading
import json

_lock = threading.Lock()
_subscribers: list[queue.Queue] = []


def subscribe() -> queue.Queue:
    q: queue.Queue = queue.Queue(maxsize=50)
    with _lock:
        _subscribers.append(q)
    return q


def unsubscribe(q: queue.Queue) -> None:
    with _lock:
        try:
            _subscribers.remove(q)
        except ValueError:
            pass


def broadcast_user_updated(user_id: int) -> None:
    data = json.dumps({"user_id": user_id})
    with _lock:
        dead = []
        for q in _subscribers:
            try:
                q.put_nowait(("user_updated", data))
            except queue.Full:
                dead.append(q)
        for q in dead:
            _subscribers.remove(q)
