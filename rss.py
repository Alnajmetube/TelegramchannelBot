import feedparser
import random

RSS_FEEDS = [
    "https://feeds.feedburner.com/TheHackersNews",
    "https://www.bleepingcomputer.com/feed/",
    "https://krebsonsecurity.com/feed/"
]

KEYWORDS = {
    "termux": 10,
    "kali": 9,
    "nmap": 9,
    "metasploit": 9,
    "burp": 8,
    "sqlmap": 8,
    "wireshark": 8,
    "linux": 7,
    "python": 6,
    "bash": 6,
    "github": 5,
    "cybersecurity": 5,
    "security": 5,
    "exploit": 5,
    "cve": 5,
    "vulnerability": 5,
    "malware": 4,
    "ransomware": 4,
    "tool": 3,
}


def get_news():

    articles = []

    for url in RSS_FEEDS:

        feed = feedparser.parse(url)

        for item in feed.entries[:15]:

            text = (
                item.title + " " +
                item.get("summary", "")
            ).lower()

            score = 0

            for keyword, weight in KEYWORDS.items():
                if keyword in text:
                    score += weight

            if score == 0:
                continue

            articles.append({
                "title": item.title,
                "summary": item.get("summary", ""),
                "link": item.link,
                "score": score
            })

    if not articles:
        return None

    articles.sort(key=lambda x: x["score"], reverse=True)

    top = articles[:5]

    return random.choice(top)