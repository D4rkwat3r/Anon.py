# Botanon
Library for creating chatbots and automating account actions in the Anon social network

### Simple chat bot
```python3
from botanon import AnonClient
from botanon import ChatMessage
from botanon import MESSAGE_TYPE_USER_KICKED
import asyncio


client = botanon.AnonClient(prefix="/")


@client.on_command("ping")
async def handle_ping(c: AnonClient, message: ChatMessage):
    await c.send_message(message.room_id, "Pong!")


@client.on_command("photo")
async def handle_photo(c: AnonClient, message: ChatMessage):
    info = await c.get_user(message.sender.anon_fields.anonym_id)
    photo_text = info.photo.data.original.url if info.photo is not None else "У тебя нет профильного фото"
    await c.send_message(message.room_id, photo_text)


@client.on_command("fake-kick")
async def handle_fake_kick(c: AnonClient, message: ChatMessage):
    try: text = message.text.split(maxsplit=1)[1]
    except IndexError: return await c.send_message(message.room_id, "Формат: /fake-kick [никнейм]")
    await c.send_message(message.room_id, text, MESSAGE_TYPE_USER_KICKED)


async def main():
    account = await client.login("your login", "your password")
    print(f"Successfully logged in to account with ID {account.id}")


asyncio.get_event_loop().run_until_complete(main())
```

## Installation: soon
