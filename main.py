import asyncio

from rss import get_news
from ai import rewrite_news, generate_video_ideas
from telegram_bot import publish, publish_ideas



async def job():

    news = get_news()


    if not news:
        print("No news found")
        return


    print(news["title"])


    content = await rewrite_news(news)
    idea = await generate_video_ideas(news)


    await publish(content)
    await publish_ideas(idea)



if __name__ == "__main__":

    asyncio.run(job())