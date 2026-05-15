import queue
import threading
import json

_lock = threading.Lock()
_subscribers: list[queue.Queue] = []
_notification_subscribers: list[queue.Queue] = []


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


def subscribe_notifications() -> queue.Queue:
    q: queue.Queue = queue.Queue(maxsize=50)
    with _lock:
        _notification_subscribers.append(q)
    return q


def unsubscribe_notifications(q: queue.Queue) -> None:
    with _lock:
        try:
            _notification_subscribers.remove(q)
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


def broadcast_notification(notification_id: int, notif_type: str, target_user_id=None) -> None:
    data = json.dumps({
        "notification_id": notification_id,
        "type": notif_type,
        "target_user_id": target_user_id,
    })
    with _lock:
        dead = []
        for q in _notification_subscribers:
            try:
                q.put_nowait(("notification", data))
            except queue.Full:
                dead.append(q)
        for q in dead:
            _notification_subscribers.remove(q)
