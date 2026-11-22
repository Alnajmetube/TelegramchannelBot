"""Fetch one fresh channel item, create its post, and publish it."""

import asyncio

from ai import build_evergreen_post, build_news_post, illustrate_evergreen_post
from config import validate_config
from rss import get_news, get_recent_titles, remember_article, title_similarity
from telegram_bot import publish


async def job() -> bool:
    validate_config()
    news = get_news()
    if news:
        print(f"Preparing post from {news.get('source_name', 'selected source')}: {news['title']}")
        post_data = await build_news_post(news)
        history_record = news
    else:
        print("No fresh feed item found; creating a new evergreen channel post.")
        recent_titles = get_recent_titles()
        for _ in range(5):
            post_data = await build_evergreen_post(recent_titles)
            if not any(
                title_similarity(post_data["title"], title) >= 0.88
                for title in recent_titles
            ):
                break
            recent_titles.append(post_data["title"])
        else:
            raise RuntimeError("Workers AI repeatedly generated a recent title")
        post_data["image"] = await illustrate_evergreen_post(post_data)
        history_record = {"title": post_data["title"], "link": ""}

    await publish(text=post_data["text"], image_bytes=post_data["image"])

    # Record only after Telegram confirms publication, so failed runs can retry.
    remember_article(history_record)
    print("Published successfully.")
    return True


if __name__ == "__main__":
    asyncio.run(job())
