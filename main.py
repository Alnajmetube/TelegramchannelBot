import asyncio

from rss import get_news
from ai import rewrite_news
from telegram_bot import publish



async def job():

    news = get_news()


    if not news:
        print("No news found")
        return


    print(news["title"])


    content = await rewrite_news(news)


    await publish(content)



if __name__ == "__main__":

    asyncio.run(job())