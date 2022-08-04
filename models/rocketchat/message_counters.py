from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import Optional


@dataclass_json
@dataclass
class MessageCounters:
    views: int
    members: Optional[int] = None
    deliveries: Optional[int] = None
