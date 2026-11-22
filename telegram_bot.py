"""Telegram publishing helpers with conservative message and caption limits."""

from telegram import Bot

from config import BOT_TOKEN, CHANNEL_ID

CAPTION_LIMIT = 1000  # Telegram permits 1024 characters; keep a safety margin.
MESSAGE_LIMIT = 3900  # Telegram permits 4096 characters; keep a safety margin.


def _chunks(text: str, limit: int) -> list[str]:
    remaining = text.strip()
    chunks: list[str] = []
    while remaining:
        if len(remaining) <= limit:
            chunks.append(remaining)
            break
        cut = remaining.rfind("\n", 0, limit + 1)
        if cut < limit // 2:
            cut = remaining.rfind(" ", 0, limit + 1)
        if cut < limit // 2:
            cut = limit
        chunks.append(remaining[:cut].rstrip())
        remaining = remaining[cut:].lstrip()
    return chunks


async def publish(text: str, image_bytes: bytes | None = None) -> None:
    """Publish a post, splitting it safely within Telegram's limits."""
    if not text or not text.strip():
        raise ValueError("Cannot publish an empty Telegram post")

    pieces = _chunks(text, MESSAGE_LIMIT)
    async with Bot(BOT_TOKEN) as bot:
        if image_bytes:
            caption = None
            if pieces and len(pieces[0]) <= CAPTION_LIMIT:
                caption = pieces.pop(0)
            await bot.send_photo(chat_id=CHANNEL_ID, photo=image_bytes, caption=caption)

        for piece in pieces:
            await bot.send_message(chat_id=CHANNEL_ID, text=piece)
