from .text_contents import TextContents
from .image_contents import ImageContents
from .tags_contents import TagsContents
from .audio_contents import AudioContents
from .poll_contents import PollContents


def decode_text_contents(contents: list) -> list[TextContents]:
    return [
        TextContents.from_dict(content)
        for content in contents
        if content["type"] == "TEXT"
    ]


def decode_image_contents(contents: list) -> list[ImageContents]:
    return [
        ImageContents.from_dict(content)
        for content in contents
        if content["type"] == "IMAGE"
    ]


def decode_tags_contents(contents: list) -> list[TagsContents]:
    return [
        TagsContents.from_dict(content)
        for content in contents
        if content["type"] == "TAGS"
    ]


def decode_audio_contents(contents: list) -> list[AudioContents]:
    return [
        AudioContents.from_dict(content)
        for content in contents
        if content["type"] == "AUDIO"
    ]


def decode_poll_contents(contents: list) -> list[PollContents]:
    return [
        PollContents.from_dict(content)
        for content in contents
        if content["type"] == "POLL"
    ]
