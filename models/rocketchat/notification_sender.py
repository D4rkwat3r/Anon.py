from dataclasses import dataclass
from dataclasses import field
from dataclasses_json import dataclass_json
from dataclasses_json import config


@dataclass_json
@dataclass
class NotificationSender:
    id: str = field(metadata=config(field_name="_id"))
    username: str
    name: str
