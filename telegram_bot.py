from telegram import Bot
from config import BOT_TOKEN, CHANNEL_ID


async def publish(text):

    bot = Bot(BOT_TOKEN)


    await bot.send_message(
        chat_id=CHANNEL_ID,
        text=text,
        parse_mode="Markdown"
    )