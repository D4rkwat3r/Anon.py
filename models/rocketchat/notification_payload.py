from dataclasses import dataclass
from dataclasses import field
from dataclasses_json import dataclass_json
from dataclasses_json import config
from .notification_sender import NotificationSender
from .notification_message import NotificationMessage


@dataclass_json
@dataclass
class NotificationPayload:
    id: str = field(metadata=config(field_name="_id"))
    room_id: str = field(metadata=config(field_name="rid"))
    sender: NotificationSender
    type: str
    message: NotificationMessage
