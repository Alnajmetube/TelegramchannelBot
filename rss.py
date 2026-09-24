from __future__ import annotations

import calendar
import hashlib
import json
import os
import random
import re
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher
from urllib.parse import (
    parse_qsl,
    urlencode,
    urlsplit,
    urlunsplit,
)

import feedparser


# ============================================================
# CONFIGURATION
# ============================================================

# How many entries to read from each RSS feed.
ENTRIES_PER_FEED = 30

# Ignore articles older than this number of days.
MAX_AGE_DAYS = 10

# Number of best articles used for final random selection.
TOP_POOL_SIZE = 10

# Do not select the same story again during this period.
SEEN_COOLDOWN_DAYS = 5

# Maximum number of records stored in history.
MAX_HISTORY_ITEMS = 500

# Set True to see RSS errors in terminal.
VERBOSE = True


# ============================================================
# RSS SOURCES
# ============================================================
#
# IMPORTANT:
# RSS_FEEDS remains a normal list so other files can continue
# importing/using it exactly as before.
#
# Add or remove feeds here without changing the rest of the code.
#

RSS_FEEDS = [
    # --------------------------------------------------------
    # General Cybersecurity News
    # --------------------------------------------------------
    "https://feeds.feedburner.com/TheHackersNews",
    "https://www.bleepingcomputer.com/feed/",
    "https://krebsonsecurity.com/feed/",
    "https://www.securityweek.com/feed/",
    "https://www.darkreading.com/rss.xml",

    # --------------------------------------------------------
    # Security Research / Hacking
    # --------------------------------------------------------
    "https://hackread.com/feed/",
    "https://grahamcluley.com/feed/",
    "https://www.tripwire.com/blog/feed",
    "https://risky.biz/feeds/latest/",

    # --------------------------------------------------------
    # OSINT / Investigations
    # --------------------------------------------------------
    "https://www.bellingcat.com/feed/",
    "https://osintcurio.us/feed/",

    # --------------------------------------------------------
    # Linux / Kali / Practical Security
    # --------------------------------------------------------
    "https://www.kali.org/feed/",
    "https://termux.dev/feed.xml",

    # --------------------------------------------------------
    # Hack The Box
    # --------------------------------------------------------
    "https://www.hackthebox.com/rss/blog/red-teaming",
    "https://www.hackthebox.com/rss/blog/write-ups",
    "https://www.hackthebox.com/rss/blog/threat-intelligence",
    "https://www.hackthebox.com/rss/blog/security-101",

    # --------------------------------------------------------
    # Web Security / Burp Suite
    # --------------------------------------------------------
    "https://portswigger.net/blog/rss",
    "https://portswigger.net/research/rss",

    # --------------------------------------------------------
    # Security Tooling / Vulnerability Research
    # --------------------------------------------------------
    "https://projectdiscovery.io/rss.xml",
    "https://blog.trailofbits.com/feed/",

    # --------------------------------------------------------
    # Official Security Advisories
    # --------------------------------------------------------
    "https://www.cisa.gov/cybersecurity-advisories/all.xml",
    "https://www.cisa.gov/news.xml",

    # --------------------------------------------------------
    # General Security / Technology
    # --------------------------------------------------------
    "https://arstechnica.com/security/feed/",
]


# ============================================================
# SOURCE METADATA
# ============================================================
#
# These settings affect source priority.
# Unknown/new sources automatically get default values.
#
# You can add a source here if you want custom priority:
#
# "https://example.com/feed":
# {
#     "name": "Example",
#     "weight": 1.20,
# }
#

SOURCE_METADATA = {

    # High-priority general security
    "https://feeds.feedburner.com/TheHackersNews": {
        "name": "The Hacker News",
        "weight": 1.05,
    },

    "https://www.bleepingcomputer.com/feed/": {
        "name": "BleepingComputer",
        "weight": 1.10,
    },

    "https://krebsonsecurity.com/feed/": {
        "name": "KrebsOnSecurity",
        "weight": 1.05,
    },

    "https://www.securityweek.com/feed/": {
        "name": "SecurityWeek",
        "weight": 1.00,
    },

    "https://www.darkreading.com/rss.xml": {
        "name": "Dark Reading",
        "weight": 0.95,
    },

    # Security research
    "https://hackread.com/feed/": {
        "name": "HackRead",
        "weight": 1.05,
    },

    "https://grahamcluley.com/feed/": {
        "name": "Graham Cluley",
        "weight": 0.95,
    },

    "https://www.tripwire.com/blog/feed": {
        "name": "Tripwire",
        "weight": 0.90,
    },

    "https://risky.biz/feeds/latest/": {
        "name": "Risky Business",
        "weight": 1.05,
    },

    # OSINT
    "https://www.bellingcat.com/feed/": {
        "name": "Bellingcat",
        "weight": 1.10,
    },

    "https://osintcurio.us/feed/": {
        "name": "OSINT Curious",
        "weight": 1.05,
    },

    # Practical / tools
    "https://www.kali.org/feed/": {
        "name": "Kali Linux",
        "weight": 1.20,
    },

    "https://termux.dev/feed.xml": {
        "name": "Termux",
        "weight": 1.35,
    },

    # Hack The Box
    "https://www.hackthebox.com/rss/blog/red-teaming": {
        "name": "Hack The Box - Red Teaming",
        "weight": 1.10,
    },

    "https://www.hackthebox.com/rss/blog/write-ups": {
        "name": "Hack The Box - Writeups",
        "weight": 1.20,
    },

    "https://www.hackthebox.com/rss/blog/threat-intelligence": {
        "name": "Hack The Box - Threat Intelligence",
        "weight": 1.10,
    },

    "https://www.hackthebox.com/rss/blog/security-101": {
        "name": "Hack The Box - Security 101",
        "weight": 1.05,
    },

    # Web security
    "https://portswigger.net/blog/rss": {
        "name": "PortSwigger Blog",
        "weight": 1.20,
    },

    "https://portswigger.net/research/rss": {
        "name": "PortSwigger Research",
        "weight": 1.30,
    },

    # Tooling / research
    "https://projectdiscovery.io/rss.xml": {
        "name": "ProjectDiscovery",
        "weight": 1.30,
    },

    "https://blog.trailofbits.com/feed/": {
        "name": "Trail of Bits",
        "weight": 1.15,
    },

    # Advisories
    "https://www.cisa.gov/cybersecurity-advisories/all.xml": {
        "name": "CISA Advisories",
        "weight": 1.10,
    },

    "https://www.cisa.gov/news.xml": {
        "name": "CISA News",
        "weight": 0.95,
    },

    # General security
    "https://arstechnica.com/security/feed/": {
        "name": "Ars Technica Security",
        "weight": 0.90,
    },
}


# ============================================================
# KEYWORDS
# ============================================================

KEYWORDS = {

    # --------------------------------------------------------
    # Termux
    # --------------------------------------------------------
    "termux": 20,
    "termux tool": 25,
    "termux hacking": 25,
    "termux osint": 25,

    # --------------------------------------------------------
    # Security Tools
    # --------------------------------------------------------
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
    "httpx": 12,
    "katana": 12,
    "naabu": 12,
    "dnsx": 12,
    "uncover": 14,

    # --------------------------------------------------------
    # OSINT
    # --------------------------------------------------------
    "osint": 20,
    "open source intelligence": 20,
    "reconnaissance": 14,
    "digital footprint": 15,
    "username": 12,
    "username search": 15,
    "reverse search": 13,
    "metadata": 12,
    "geolocation": 12,
    "geoint": 14,

    # --------------------------------------------------------
    # Telegram
    # --------------------------------------------------------
    "telegram": 17,
    "telegram bot": 20,
    "telegram bots": 20,
    "telegram security": 22,
    "telegram vulnerability": 22,

    # --------------------------------------------------------
    # Hacking / Security
    # --------------------------------------------------------
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
    "infostealer": 15,
    "stealer": 12,

    # --------------------------------------------------------
    # Vulnerabilities
    # --------------------------------------------------------
    "exploit": 12,
    "exploit code": 20,
    "proof of concept": 18,
    "poc": 17,
    "zero-day": 20,
    "zero day": 20,
    "vulnerability": 8,
    "cve-": 8,
    "remote code execution": 18,
    "rce": 17,
    "sql injection": 18,
    "ssrf": 17,
    "xss": 16,
    "request smuggling": 17,
    "authentication bypass": 17,
    "privilege escalation": 15,

    # --------------------------------------------------------
    # Linux / Programming
    # --------------------------------------------------------
    "kali linux": 18,
    "kali": 14,
    "linux": 8,
    "python": 8,
    "bash": 8,
    "shell": 7,
    "github": 6,

    # --------------------------------------------------------
    # Tutorials / Practical Content
    # --------------------------------------------------------
    "how to": 14,
    "tutorial": 14,
    "guide": 12,
    "install": 14,
    "installation": 14,
    "setup": 12,
    "command": 10,
    "commands": 10,
    "configuration": 8,
    "configure": 8,
    "release": 8,
    "new tool": 20,
    "new security tool": 25,
    "open source tool": 18,
    "command line": 12,
    "cli": 10,
    "terminal": 10,
}


# ============================================================
# NEGATIVE KEYWORDS
# ============================================================

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
    "job opening": -8,
    "hiring": -5,
}


# ============================================================
# CONTENT TYPES
# ============================================================

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
        "scanner",
        "framework",
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
        "command",
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
        "campaign",
    ],

    "vulnerability": [
        "zero-day",
        "zero day",
        "exploit",
        "proof of concept",
        "poc",
        "cve-",
        "vulnerability",
        "remote code execution",
        "rce",
        "sql injection",
        "ssrf",
        "xss",
    ],

    "osint": [
        "osint",
        "open source intelligence",
        "digital footprint",
        "username",
        "geolocation",
        "geoint",
        "metadata",
        "reconnaissance",
    ],
}


# ============================================================
# HISTORY
# ============================================================

HISTORY_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    ".news_history.json"
)


# ============================================================
# TEXT HELPERS
# ============================================================

def normalize(text: str) -> str:
    """
    Normalize text for matching.
    """
    if not text:
        return ""

    text = str(text)

    # Remove HTML tags.
    text = re.sub(r"<[^>]+>", " ", text)

    # Decode HTML entities.
    text = re.sub(r"&[a-zA-Z0-9#]+;", " ", text)

    # Lowercase.
    text = text.lower()

    # Normalize common separators.
    text = text.replace("–", "-")
    text = text.replace("—", "-")
    text = text.replace("_", " ")

    # Remove punctuation but keep letters/numbers.
    text = re.sub(r"[^\w\s.-]", " ", text)

    # Collapse spaces.
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def normalize_title(title: str) -> str:
    """
    Stronger normalization specifically for duplicate detection.
    """
    text = normalize(title)

    # Remove common words that create false differences.
    stop_words = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "to",
        "of",
        "for",
        "in",
        "on",
        "with",
        "from",
        "this",
        "new",
        "latest",
        "update",
        "security",
    }

    words = [
        word
        for word in text.split()
        if word not in stop_words
    ]

    return " ".join(words)


def title_tokens(title: str) -> set[str]:
    """
    Extract meaningful title tokens.
    """
    text = normalize_title(title)

    return {
        word
        for word in text.split()
        if len(word) >= 3
    }


def keyword_matches(keyword: str, text: str) -> bool:
    """
    Match keywords safely.

    Handles special prefixes such as:
        cve-
    """
    keyword = keyword.lower().strip()

    if not keyword:
        return False

    if keyword.endswith("-"):
        return keyword in text

    return keyword in text


# ============================================================
# CONTENT DETECTION
# ============================================================

def detect_content_types(text: str) -> list[str]:
    """
    Detect what kind of content the article represents.
    """
    detected = []

    for content_type, keywords in CONTENT_TYPES.items():

        for keyword in keywords:

            if keyword_matches(keyword, text):
                detected.append(content_type)
                break

    return detected


# ============================================================
# SCORE
# ============================================================

def calculate_score(title, summary):
    """
    Calculate article relevance.

    The function signature is intentionally unchanged so
    existing code can continue calling it.
    """

    text = normalize(
        f"{title} {summary}"
    )

    title_text = normalize(title)

    score = 0

    # --------------------------------------------------------
    # Main keywords
    # --------------------------------------------------------
    for keyword, weight in KEYWORDS.items():

        if keyword_matches(keyword, text):

            score += weight

            # Title bonus.
            if keyword_matches(keyword, title_text):
                score += int(weight * 0.6)

    # --------------------------------------------------------
    # Negative keywords
    # --------------------------------------------------------
    for keyword, weight in NEGATIVE_KEYWORDS.items():

        if keyword_matches(keyword, text):
            score += weight

    # --------------------------------------------------------
    # Content types
    # --------------------------------------------------------
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

    # --------------------------------------------------------
    # High priority subjects
    # --------------------------------------------------------
    if "termux" in text:
        score += 30

    if "telegram" in text:
        score += 20

    if "github" in text:
        score += 10

    # --------------------------------------------------------
    # Practical value
    # --------------------------------------------------------
    if any(
        x in text
        for x in [
            "command",
            "terminal",
            "cli",
            "install",
            "setup",
            "usage",
            "how to",
        ]
    ):
        score += 10

    return score, detected_types


# ============================================================
# URL NORMALIZATION
# ============================================================

def canonicalize_url(url: str) -> str:
    """
    Remove tracking parameters so the same article with
    different tracking URLs is treated as one article.
    """

    if not url:
        return ""

    try:
        parts = urlsplit(url)

        query = parse_qsl(
            parts.query,
            keep_blank_values=True
        )

        ignored_params = {
            "utm_source",
            "utm_medium",
            "utm_campaign",
            "utm_term",
            "utm_content",
            "fbclid",
            "gclid",
            "mc_cid",
            "mc_eid",
            "ref",
        }

        filtered_query = [
            (key, value)
            for key, value in query
            if key.lower() not in ignored_params
        ]

        filtered_query.sort()

        return urlunsplit(
            (
                parts.scheme.lower(),
                parts.netloc.lower(),
                parts.path.rstrip("/"),
                urlencode(filtered_query),
                "",
            )
        )

    except Exception:
        return url.strip().lower()


# ============================================================
# ARTICLE ID / FINGERPRINT
# ============================================================

def make_fingerprint(title: str) -> str:
    """
    Create a stable story fingerprint from the title.
    This helps detect the same news story across different sources.
    """

    normalized = normalize_title(title)

    return hashlib.sha1(
        normalized.encode("utf-8")
    ).hexdigest()


# ============================================================
# DUPLICATE DETECTION
# ============================================================

def title_similarity(title_a: str, title_b: str) -> float:
    """
    Calculate similarity between two article titles.

    Uses both character similarity and token similarity.
    """

    a = normalize_title(title_a)
    b = normalize_title(title_b)

    if not a or not b:
        return 0.0

    ratio = SequenceMatcher(
        None,
        a,
        b
    ).ratio()

    tokens_a = title_tokens(title_a)
    tokens_b = title_tokens(title_b)

    if not tokens_a or not tokens_b:
        return ratio

    intersection = len(
        tokens_a & tokens_b
    )

    union = len(
        tokens_a | tokens_b
    )

    jaccard = (
        intersection / union
        if union
        else 0
    )

    # Stronger when several meaningful words overlap.
    if intersection >= 4 and jaccard >= 0.60:
        return max(
            ratio,
            jaccard + 0.20
        )

    return max(
        ratio,
        jaccard
    )


def are_same_story(article_a, article_b) -> bool:
    """
    Determine whether two articles are probably the same story.
    """

    # Exact canonical URL.
    url_a = canonicalize_url(
        article_a.get("link", "")
    )

    url_b = canonicalize_url(
        article_b.get("link", "")
    )

    if url_a and url_b and url_a == url_b:
        return True

    # Exact fingerprint.
    fp_a = make_fingerprint(
        article_a.get("title", "")
    )

    fp_b = make_fingerprint(
        article_b.get("title", "")
    )

    if fp_a == fp_b:
        return True

    # Similar titles.
    similarity = title_similarity(
        article_a.get("title", ""),
        article_b.get("title", "")
    )

    return similarity >= 0.86


def deduplicate_articles(articles):
    """
    Remove duplicate stories across all RSS feeds.

    The higher-scoring article survives.
    """

    result = []

    # First exact URL/fingerprint dedupe.
    seen_exact = {}

    for article in articles:

        url = canonicalize_url(
            article.get("link", "")
        )

        fingerprint = make_fingerprint(
            article.get("title", "")
        )

        key = url or fingerprint

        if key not in seen_exact:

            seen_exact[key] = article

        else:

            old_article = seen_exact[key]

            if article["score"] > old_article["score"]:
                seen_exact[key] = article

    candidates = list(
        seen_exact.values()
    )

    # Second stage: fuzzy title dedupe.
    #
    # This handles cases such as:
    #
    # Source A:
    # "Microsoft confirms critical vulnerability..."
    #
    # Source B:
    # "Critical Microsoft vulnerability exploited..."
    #
    for article in sorted(
        candidates,
        key=lambda x: x["score"],
        reverse=True
    ):

        duplicate = False

        for accepted in result:

            if are_same_story(
                article,
                accepted
            ):
                duplicate = True
                break

        if not duplicate:
            result.append(article)

    return result


# ============================================================
# DATE HANDLING
# ============================================================

def get_entry_datetime(entry) -> datetime | None:
    """
    Get publication/update datetime from RSS entry.
    """

    # feedparser normally provides *_parsed fields.
    for field in (
        "published_parsed",
        "updated_parsed",
        "created_parsed",
    ):

        parsed = entry.get(field)

        if parsed:

            try:
                timestamp = calendar.timegm(
                    parsed
                )

                return datetime.fromtimestamp(
                    timestamp,
                    tz=timezone.utc
                )

            except Exception:
                pass

    # Fallback to string dates.
    for field in (
        "published",
        "updated",
        "created",
        "date",
    ):

        value = entry.get(field)

        if not value:
            continue

        try:

            value = str(value)

            value = value.replace(
                "Z",
                "+00:00"
            )

            dt = datetime.fromisoformat(
                value
            )

            if dt.tzinfo is None:
                dt = dt.replace(
                    tzinfo=timezone.utc
                )

            return dt.astimezone(
                timezone.utc
            )

        except Exception:
            continue

    return None


def is_recent(entry) -> bool:
    """
    Determine whether an RSS entry is recent enough.

    Entries without a valid date are allowed because some
    RSS feeds omit publication timestamps.
    """

    published_at = get_entry_datetime(
        entry
    )

    if published_at is None:
        return True

    now = datetime.now(
        timezone.utc
    )

    age = now - published_at

    # Allow a slightly incorrect future timestamp.
    if age.total_seconds() < 0:
        return True

    return age <= timedelta(
        days=MAX_AGE_DAYS
    )


# ============================================================
# HISTORY
# ============================================================

def load_history():
    """
    Load previously selected stories.
    """

    if not os.path.exists(
        HISTORY_FILE
    ):
        return []

    try:

        with open(
            HISTORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            if isinstance(data, list):
                return data

    except Exception:
        pass

    return []


def save_history(history):
    """
    Save history safely.
    """

    try:

        history = history[
            -MAX_HISTORY_ITEMS:
        ]

        temp_file = HISTORY_FILE + ".tmp"

        with open(
            temp_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                history,
                file,
                ensure_ascii=False,
                indent=2
            )

        os.replace(
            temp_file,
            HISTORY_FILE
        )

    except Exception as e:

        if VERBOSE:
            print(
                f"History save error -> {e}"
            )


def cleanup_history(history):
    """
    Remove very old history records.
    """

    now = datetime.now(
        timezone.utc
    )

    cleaned = []

    # Keep a longer history than the cooldown
    # for better duplicate detection.
    retention_days = max(
        SEEN_COOLDOWN_DAYS * 3,
        15
    )

    for item in history:

        if not isinstance(
            item,
            dict
        ):
            continue

        timestamp = item.get(
            "selected_at"
        )

        if not timestamp:
            continue

        try:

            dt = datetime.fromisoformat(
                timestamp
            )

            if dt.tzinfo is None:
                dt = dt.replace(
                    tzinfo=timezone.utc
                )

            age = now - dt

            if age <= timedelta(
                days=retention_days
            ):
                cleaned.append(item)

        except Exception:
            continue

    return cleaned[
        -MAX_HISTORY_ITEMS:
    ]


def is_recently_seen(article, history):
    """
    Check if this story was recently selected.

    Exact fingerprints are checked first.
    Then fuzzy title comparison is used.
    """

    now = datetime.now(
        timezone.utc
    )

    fingerprint = make_fingerprint(
        article.get("title", "")
    )

    article_title = article.get(
        "title",
        ""
    )

    for item in history:

        if not isinstance(
            item,
            dict
        ):
            continue

        selected_at = item.get(
            "selected_at"
        )

        if not selected_at:
            continue

        try:

            dt = datetime.fromisoformat(
                selected_at
            )

            if dt.tzinfo is None:
                dt = dt.replace(
                    tzinfo=timezone.utc
                )

        except Exception:
            continue

        age = now - dt

        if age < timedelta(
            days=0
        ):
            age = timedelta(
                days=0
            )

        if age > timedelta(
            days=SEEN_COOLDOWN_DAYS
        ):
            continue

        # Exact story match.
        if item.get(
            "fingerprint"
        ) == fingerprint:
            return True

        # Fuzzy match.
        old_title = item.get(
            "title",
            ""
        )

        if old_title:

            similarity = title_similarity(
                article_title,
                old_title
            )

            if similarity >= 0.88:
                return True

    return False


def remember_article(article):
    """
    Add selected article to history.
    """

    history = load_history()
    history = cleanup_history(
        history
    )

    history.append(
        {
            "fingerprint": make_fingerprint(
                article.get("title", "")
            ),
            "title": article.get(
                "title",
                ""
            ),
            "link": canonicalize_url(
                article.get("link", "")
            ),
            "selected_at": datetime.now(
                timezone.utc
            ).isoformat(),
        }
    )

    save_history(
        history
    )


# ============================================================
# SOURCE HELPERS
# ============================================================

def unique_feed_urls():
    """
    Return unique RSS URLs while keeping original order.

    This also protects against accidentally adding the same
    source twice.
    """

    result = []
    seen = set()

    for url in RSS_FEEDS:

        canonical = canonicalize_url(
            url
        )

        if not canonical:
            continue

        if canonical in seen:
            continue

        seen.add(canonical)
        result.append(url)

    return result


def get_source_metadata(url):
    """
    Get source metadata.

    Unknown sources automatically work with defaults.
    """

    metadata = SOURCE_METADATA.get(
        url,
        {}
    )

    return {
        "name": metadata.get(
            "name",
            url
        ),
        "weight": float(
            metadata.get(
                "weight",
                1.0
            )
        ),
    }


# ============================================================
# ARTICLE CLEANING
# ============================================================

def clean_summary(summary: str) -> str:
    """
    Clean RSS summary while preserving useful content.
    """

    if not summary:
        return ""

    text = normalize(
        summary
    )

    # Prevent enormous RSS descriptions.
    return text[:3000]


# ============================================================
# MAIN NEWS FETCHER
# ============================================================

def get_news():
    """
    Fetch and select one relevant cybersecurity article.

    IMPORTANT:
    The return format remains compatible with the old code:

    {
        "title": ...,
        "summary": ...,
        "link": ...,
        "score": ...,
        "content_types": ...,
        "source": ...
    }

    Other files should not need modification.
    """

    articles = []

    # --------------------------------------------------------
    # Load history
    # --------------------------------------------------------
    history = cleanup_history(
        load_history()
    )

    save_history(
        history
    )

    # --------------------------------------------------------
    # Fetch feeds
    # --------------------------------------------------------
    for url in unique_feed_urls():

        try:

            feed = feedparser.parse(
                url
            )

            # Feed errors can sometimes be exposed through
            # feedparser's bozo flag.
            if getattr(
                feed,
                "bozo",
                False
            ):

                if VERBOSE:
                    print(
                        f"RSS warning: {url}"
                    )

            entries = getattr(
                feed,
                "entries",
                []
            )

            for item in entries[
                :ENTRIES_PER_FEED
            ]:

                title = item.get(
                    "title",
                    ""
                ).strip()

                if not title:
                    continue

                # ------------------------------------------------
                # Ignore old stories
                # ------------------------------------------------
                if not is_recent(item):
                    continue

                summary = clean_summary(
                    item.get(
                        "summary",
                        ""
                    )
                )

                # Some feeds expose content rather than summary.
                if not summary:

                    contents = item.get(
                        "content",
                        []
                    )

                    if contents:

                        parts = []

                        for content in contents:

                            if isinstance(
                                content,
                                dict
                            ):

                                value = content.get(
                                    "value",
                                    ""
                                )

                                if value:
                                    parts.append(
                                        value
                                    )

                        summary = clean_summary(
                            " ".join(parts)
                        )

                score, content_types = calculate_score(
                    title,
                    summary
                )

                # Ignore weak articles.
                if score < 15:
                    continue

                source_meta = get_source_metadata(
                    url
                )

                # ------------------------------------------------
                # Source weight
                # ------------------------------------------------
                weighted_score = (
                    score
                    * source_meta["weight"]
                )

                article = {
                    "title": title,
                    "summary": summary,
                    "link": item.get(
                        "link",
                        ""
                    ),
                    "score": score,
                    "weighted_score": weighted_score,
                    "content_types": content_types,
                    "source": url,
                    "source_name": source_meta[
                        "name"
                    ],
                }

                articles.append(
                    article
                )

        except Exception as e:

            if VERBOSE:
                print(
                    f"RSS error: {url} -> {e}"
                )

    # --------------------------------------------------------
    # Nothing found
    # --------------------------------------------------------
    if not articles:
        return None

    # --------------------------------------------------------
    # Remove duplicates
    # --------------------------------------------------------
    articles = deduplicate_articles(
        articles
    )

    if not articles:
        return None

    # --------------------------------------------------------
    # Remove stories selected recently
    # --------------------------------------------------------
    fresh_articles = [
        article
        for article in articles
        if not is_recently_seen(
            article,
            history
        )
    ]

    # If everything has already been seen,
    # don't completely fail. Use the full list.
    if fresh_articles:
        articles = fresh_articles

    # --------------------------------------------------------
    # Sort by weighted score
    # --------------------------------------------------------
    articles.sort(
        key=lambda x: x.get(
            "weighted_score",
            x["score"]
        ),
        reverse=True
    )

    # --------------------------------------------------------
    # Build selection pool
    # --------------------------------------------------------
    top = articles[
        :TOP_POOL_SIZE
    ]

    if not top:
        return None

    # --------------------------------------------------------
    # Weighted random selection
    # --------------------------------------------------------
    #
    # Higher score -> higher probability
    # but not 100% guaranteed.
    #

    min_score = min(
        article.get(
            "weighted_score",
            article["score"]
        )
        for article in top
    )

    weights = []

    for article in top:

        article_score = article.get(
            "weighted_score",
            article["score"]
        )

        relative_score = max(
            0.0,
            article_score - min_score
        )

        # Soft probability curve.
        weight = (
            1.0
            + relative_score * 0.12
        )

        weights.append(
            weight
        )

    selected = random.choices(
        top,
        weights=weights,
        k=1
    )[0]

    # --------------------------------------------------------
    # Remember selected story
    # --------------------------------------------------------
    remember_article(
        selected
    )

    # --------------------------------------------------------
    # Return only the old public structure
    # --------------------------------------------------------
    #
    # This is important for compatibility with the rest
    # of your project.
    #
    return {
        "title": selected["title"],
        "summary": selected["summary"],
        "link": selected["link"],
        "score": selected["score"],
        "content_types": selected["content_types"],
        "source": selected["source"],
    }


# ============================================================
# OPTIONAL DEBUG FUNCTION
# ============================================================
#
# This does NOT affect the existing get_news() API.
#
# You can use it during development to inspect the number
# of collected / filtered articles.
# ============================================================

def get_news_stats():
    """
    Lightweight diagnostic helper.

    Returns:
        {
            "feeds": int,
            "unique_feeds": int,
            "history_items": int,
        }
    """

    history = cleanup_history(
        load_history()
    )

    return {
        "feeds": len(RSS_FEEDS),
        "unique_feeds": len(
            unique_feed_urls()
        ),
        "history_items": len(
            history
        ),
    }