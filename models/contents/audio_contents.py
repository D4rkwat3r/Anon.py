from dataclasses import dataclass
from dataclasses_json import dataclass_json
from .base_contents import BaseContents
from .audio_contents_data import AudioContentsData


@dataclass_json
@dataclass
class AudioContents(BaseContents):
    data: AudioContentsData
