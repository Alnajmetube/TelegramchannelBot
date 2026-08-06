import feedparser
import random


RSS_FEEDS = [
    "https://feeds.feedburner.com/TheHackersNews",
    "https://www.bleepingcomputer.com/feed/",
    "https://krebsonsecurity.com/feed/"
]


KEYWORDS = [
    "hack",
    "security",
    "malware",
    "vulnerability",
    "exploit",
    "tool",
    "linux",
    "termux"
]


def get_news():

    articles = []

    for url in RSS_FEEDS:

        feed = feedparser.parse(url)

        for item in feed.entries[:10]:

            title = item.title.lower()

            if any(word in title for word in KEYWORDS):

                articles.append({
                    "title": item.title,
                    "summary": item.get("summary", ""),
                    "link": item.link
                })


    if not articles:
        return None

    return random.choice(articles)