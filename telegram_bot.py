from telegram import Bot
from config import BOT_TOKEN, CHANNEL_ID, CHAT_ID


async def publish(text: str, image_bytes: bytes | None = None):
    bot = Bot(BOT_TOKEN)

    if not image_bytes:
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=text,
            parse_mode="Markdown"
        )
        return

    if len(text) <= 1024:
        await bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=image_bytes,
            caption=text,
            parse_mode="Markdown"
        )
    else:
        await bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=image_bytes
        )
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=text,
            parse_mode="Markdown"
        )


async def publish_ideas(text: str):
    bot = Bot(BOT_TOKEN)
    await bot.send_message(
        chat_id=CHAT_ID,
        text=text,
        parse_mode="Markdown"


async def publish_ideas(text):

    bot = Bot(BOT_TOKEN)


    await bot.send_message(
        chat_id=CHAT_ID,
        text=text,
        parse_mode="Markdown"
    )
