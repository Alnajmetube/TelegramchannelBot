from telegram import Bot
from config import BOT_TOKEN, CHANNEL_ID, CHAT_ID


async def publish(text):

    bot = Bot(BOT_TOKEN)


    await bot.send_message(
        chat_id=CHANNEL_ID,
        text=text,
        parse_mode="Markdown"
    )


async def publish_ideas(text):

    bot = Bot(BOT_TOKEN)


    await bot.send_message(
        chat_id=CHAT_ID,
        text=text,
        parse_mode="Markdown"
    )