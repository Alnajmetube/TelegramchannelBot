import feedparser
import random
import re


RSS_FEEDS = [
    "https://feeds.feedburner.com/TheHackersNews",
    "https://www.bleepingcomputer.com/feed/",
    "https://krebsonsecurity.com/feed/",
    "https://termux.com/feed.xml",

    # General Cybersecurity News
    "https://feeds.feedburner.com/TheHackersNews",
    "https://www.bleepingcomputer.com/feed/",
    "https://krebsonsecurity.com/feed/",
    "https://www.securityweek.com/feed/",
    "https://www.darkreading.com/rss.xml",

    # Hacking / Security Research
    "https://hackread.com/feed/",
    "https://grahamcluley.com/feed/",
    "https://www.tripwire.com/blog/feed",
    "https://risky.biz/feeds/latest/",

    # OSINT / Investigations
    "https://www.bellingcat.com/feed/",

    # Linux / Kali / Practical Security
    "https://www.kali.org/feed/",

    # Termux
    "https://termux.dev/feed.xml",

    # Hack The Box - practical/security content
    "https://www.hackthebox.com/rss/blog/red-teaming",
    "https://www.hackthebox.com/rss/blog/write-ups",
    "https://www.hackthebox.com/rss/blog/threat-intelligence",
    "https://www.hackthebox.com/rss/blog/security-101",
]


# High-value topics for cybersecurity enthusiasts
KEYWORDS = {
    # Termux
    "termux": 20,
    "termux tool": 25,
    "termux hacking": 25,
    "termux osint": 25,

    # Security tools
    "nmap": 18,
    "metasploit": 18,
    "burp suite": 17,
    "burpsuite": 17,
    "sqlmap": 17,
    "wireshark": 15,
    "nikto": 15,
    "hydra": 15,
    "john the ripper": 15,
    "hashcat": 15,
    "aircrack": 15,
    "bettercap": 15,
    "ffuf": 15,
    "gobuster": 15,
    "subfinder": 15,
    "amass": 15,
    "nuclei": 17,
    "shodan": 16,
    "maltego": 15,
    "recon-ng": 15,

    # OSINT
    "osint": 20,
    "open source intelligence": 20,
    "reconnaissance": 14,
    "digital footprint": 15,
    "username": 12,
    "username search": 15,
    "reverse search": 13,
    "metadata": 12,
    "geolocation": 12,

    # Telegram
    "telegram": 17,
    "telegram bot": 20,
    "telegram bots": 20,
    "telegram security": 22,
    "telegram vulnerability": 22,

    # Hacking / security
    "hacking": 14,
    "hacker": 12,
    "cyber attack": 12,
    "cyberattack": 12,
    "breach": 13,
    "data breach": 15,
    "account takeover": 16,
    "credential theft": 15,
    "phishing": 12,
    "malware": 10,
    "ransomware": 10,
    "spyware": 12,
    "backdoor": 13,
    "botnet": 12,

    # Vulnerabilities
    "exploit": 12,
    "exploit code": 20,
    "proof of concept": 18,
    "poc": 17,
    "zero-day": 20,
    "zero day": 20,
    "vulnerability": 8,
    "cve-": 8,

    # Linux / programming
    "kali linux": 18,
    "kali": 14,
    "linux": 8,
    "python": 8,
    "bash": 8,
    "shell": 7,
    "github": 6,

    # Tutorials / practical content
    "how to": 14,
    "tutorial": 14,
    "guide": 12,
    "install": 14,
    "installation": 14,
    "setup": 12,
    "command": 10,
    "commands": 10,
    "configuration": 8,
    "release": 8,
    "new tool": 20,
    "new security tool": 25,
    "open source tool": 18,
}


# Topics that usually produce boring corporate/security-news content.
NEGATIVE_KEYWORDS = {
    "quarterly earnings": -15,
    "financial results": -15,
    "revenue": -10,
    "acquisition": -8,
    "appointed": -10,
    "appoints": -10,
    "partnership": -7,
    "conference": -6,
    "webinar": -8,
    "survey": -5,
    "report released": -5,
    "market report": -12,
    "enterprise": -4,
    "corporate": -4,
    "compliance": -8,
    "policy": -6,
}


# Content formats that are especially useful for YouTube/Telegram content.
CONTENT_TYPES = {
    "tool": [
        "new tool",
        "security tool",
        "open source tool",
        "released",
        "release",
        "github",
        "command line",
        "cli",
        "utility",
    ],

    "tutorial": [
        "how to",
        "tutorial",
        "guide",
        "install",
        "installation",
        "setup",
        "configure",
        "commands",
    ],

    "story": [
        "hacker",
        "hack",
        "breach",
        "attack",
        "cyber attack",
        "ransomware",
        "stolen",
        "leaked",
        "arrested",
        "investigation",
    ],

    "vulnerability": [
        "zero-day",
        "zero day",
        "exploit",
        "proof of concept",
        "poc",
        "cve-",
        "vulnerability",
    ],

    "osint": [
        "osint",
        "open source intelligence",
        "digital footprint",
        "username",
        "geolocation",
        "metadata",
        "reconnaissance",
    ],
}


def normalize(text):
    """Normalize text for better matching."""
    text = text.lower()
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def detect_content_types(text):
    """
    Detect what kind of content the article represents.
    """
    detected = []

    for content_type, keywords in CONTENT_TYPES.items():
        for keyword in keywords:
            if keyword in text:
                detected.append(content_type)
                break

    return detected


def calculate_score(title, summary):
    """
    Calculate a relevance score based on:
    - Important cybersecurity topics
    - Practical value
    - Tools
    - Termux
    - OSINT
    - Telegram
    - Negative/broad corporate topics
    """

    text = normalize(f"{title} {summary}")
    title_text = normalize(title)

    score = 0

    # Main keyword scoring
    for keyword, weight in KEYWORDS.items():
        if keyword in text:
            score += weight

            # Extra bonus if keyword appears in the title.
            if keyword in title_text:
                score += int(weight * 0.6)

    # Negative scoring
    for keyword, weight in NEGATIVE_KEYWORDS.items():
        if keyword in text:
            score += weight

    # Strong bonuses for content that can easily become useful content.
    detected_types = detect_content_types(text)

    if "tool" in detected_types:
        score += 20

    if "tutorial" in detected_types:
        score += 18

    if "osint" in detected_types:
        score += 15

    if "story" in detected_types:
        score += 12

    if "vulnerability" in detected_types:
        score += 8

    # Termux should have very high priority.
    if "termux" in text:
        score += 30

    # Telegram is highly relevant to the target audience.
    if "telegram" in text:
        score += 20

    # GitHub projects/releases are usually more practical.
    if "github" in text:
        score += 10

    # Articles containing practical commands are more useful.
    if any(x in text for x in [
        "command",
        "terminal",
        "cli",
        "install",
        "setup",
    ]):
        score += 10

    return score, detected_types


def get_news():

    articles = []

    for url in RSS_FEEDS:

        try:
            feed = feedparser.parse(url)

            for item in feed.entries[:20]:

                title = item.get("title", "")
                summary = item.get("summary", "")

                if not title:
                    continue

                score, content_types = calculate_score(
                    title,
                    summary
                )

                # Ignore articles with almost no relevance.
                if score < 15:
                    continue

                articles.append({
                    "title": title,
                    "summary": summary,
                    "link": item.get("link", ""),
                    "score": score,
                    "content_types": content_types,
                    "source": url
                })

        except Exception as e:
            print(f"RSS error: {url} -> {e}")

    if not articles:
        return None

    # Remove duplicate articles.
    unique_articles = {}

    for article in articles:
        key = normalize(article["title"])

        if key not in unique_articles:
            unique_articles[key] = article
        else:
            # Keep the higher scoring version.
            if article["score"] > unique_articles[key]["score"]:
                unique_articles[key] = article

    articles = list(unique_articles.values())

    # Highest relevance first.
    articles.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    # Instead of always choosing the #1 article,
    # randomly choose from the best group.
    top = articles[:8]

    # Give higher probability to better articles.
    weights = []

    max_score = max(article["score"] for article in top)

    for article in top:
        # Prevent one article from dominating completely.
        weight = max(1, article["score"] / max_score)
        weights.append(weight)

    selected = random.choices(
        top,
        weights=weights,
        k=1
    )[0]

    return selected