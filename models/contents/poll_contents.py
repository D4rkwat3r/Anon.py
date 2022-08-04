from dataclasses import dataclass
from dataclasses_json import dataclass_json
from .poll_contents_data import PollContentsData


@dataclass_json
@dataclass
class PollContents:
    data: PollContentsData
