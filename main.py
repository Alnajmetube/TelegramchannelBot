import asyncio

from rss import get_news
from ai import build_news_post, generate_video_ideas
from telegram_bot import publish, publish_ideas


async def job():
    news = get_news()

    if not news:
        print("No news found")
        return

    print(f"Processing: {news['title']}")

    # 1. كتابة المنشور وتوليد البوستر الخاص به في خطوة واحدة
    post_data = await build_news_post(news)

    # 2. توليد أفكار الفيديو كما كان سابقاً
    idea = await generate_video_ideas(news)

    # 3. نشر المنشور مع البوستر في القناة
    await publish(
        text=post_data["text"],
        image_bytes=post_data["image"]
    )

    # 4. نشر أفكار الفيديو في المحادثة الخاصة بك
    await publish_ideas(idea)

    print("Published successfully!")


if __name__ == "__main__":
    asyncio.run(job())
