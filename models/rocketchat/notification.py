from dataclasses import dataclass
from dataclasses_json import dataclass_json
from .notification_payload import NotificationPayload


@dataclass_json
@dataclass
class Notification:
    title: str
    text: str
    payload: NotificationPayload
