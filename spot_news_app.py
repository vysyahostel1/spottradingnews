import streamlit as st
import feedparser
import requests
from datetime import datetime

# 🔐 Telegram API
bot_token = "8376336695:AAEUqfYB2-nWXy4ozOaxeznEmvtRrTJ5AbI"
chat_id = "@spot_tradingnews"

# 🌐 RSS Feeds
feeds = [
    "https://www.moneycontrol.com/rss/news.xml",
    "https://economictimes.indiatimes.com/rssfeedsdefault.cms",
    "https://feeds.reuters.com/reuters/businessNews",
    "https://feeds.reuters.com/reuters/marketsNews",
    "https://www.business-standard.com/rss/home_page_top_stories.rss",
    "https://www.livemint.com/rss/news"
]

# 📊 Sentiment tagging
def detect_sentiment(text):
    text = text.lower()
    if any(word in text for word in ["surge", "gain", "rise", "up", "record high"]):
        return "Bullish 📈"
    elif any(word in text for word in ["fall", "drop", "decline", "down", "plunge"]):
        return "Bearish 📉"
    else:
        return "Neutral ⚖️"

# 🏷 Sector tagging
def tag_sector(text):
    text = text.lower()
    if any(word in text for word in ["bank", "loan", "insurance", "finance", "nifty"]):
        return "Finance 🏦"
    elif any(word in text for word in ["auto", "vehicle", "ev", "car", "bike"]):
        return "Auto 🚗"
    elif any(word in text for word in ["power", "energy", "solar", "electricity"]):
        return "Energy ⚡"
    elif any(word in text for word in ["gold", "silver", "commodity", "metal"]):
        return "Commodities 🪙"
    elif any(word in text for word in ["tech", "software", "ai", "it", "startup"]):
        return "Technology 💻"
    elif any(word in text for word in ["real estate", "property", "housing"]):
        return "Real Estate 🏘️"
    else:
        return "General 📰"

# 🌍 Country detection
def detect_country(text, source):
    text = text.lower()
    source = source.lower()
    if "india" in text or source in ["moneycontrol.com", "economictimes.indiatimes.com", "livemint.com", "business-standard.com"]:
        return "India 🇮🇳"
    else:
        return "Global 🌍"

# 🧠 Point-wise summarizer
def summarize_to_points(text):
    sentences = text.split(". ")
    return [s.strip() for s in sentences if len(s.strip()) > 30][:5]

# 📲 Telegram sector-wise batching
def push_sector_batches(sector_dict):
    for sector, items in sector_dict.items():
        if not items:
            continue
        message = f"📢 *{sector} News Update*\n\n"
        for h in items:
            message += f"*📰 {h['title']}*\n"
            message += f"🕒 {h['timestamp']} | 🌍 {h['country']}\n"
            for p in h['points']:
                message += f"• {p}\n"
            message += f"\n📊 {h['sentiment']} | 🔗 `{h['source']}`\n\n"
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
        )

# 🧩 Streamlit UI
st.set_page_config(page_title="Spot Trading – Auto News Pulse", layout="wide")
st.title("📈 Spot Trading – Daily Market Pulse")
st.write(f"🗓️ {datetime.now().strftime('%d %b %Y, %I:%M %p')}")

refresh_minutes = st.slider("🔁 Auto-refresh every X minutes", 1, 30, 5)

if "seen" not in st.session_state:
    st.session_state.seen = set()
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = datetime.now()

headlines = []
sector_batches = {}

# 🔄 Refresh logic
if datetime.now() - st.session_state.last_refresh > timedelta(minutes=refresh_minutes):
    st.session_state.last_refresh = datetime.now()
    st.experimental_rerun()

for url in feeds:
    try:
        feed = feedparser.parse(url)
    except Exception as e:
        st.warning(f"⚠️ Failed to load feed: {url}\nError: {e}")
        continue

    for entry in feed.entries[:3]:
        headline = entry.title
        link = entry.link
        source = link.split("/")[2]
        full_text = entry.get("summary", "")
        if headline not in st.session_state.seen:
            st.session_state.seen.add(headline)
            points = summarize_to_points(full_text)
            sentiment = detect_sentiment(full_text)
            sector = tag_sector(full_text)
            country = detect_country(full_text, source)
            timestamp = datetime.now().strftime("%d %b %Y, %I:%M %p")

            st.markdown(f"### 📰 {headline}")
            st.write(f"🕒 {timestamp} | 🌍 {country}")
            for p in points:
                st.write(f"• {p}")
            st.write(f"📊 Sentiment: {sentiment} | 🏷 Sector: {sector}")
            st.markdown(f"🔗 Source: `{source}`")
            st.markdown(f"[Read more]({link})")
            st.divider()

            item = {
                "title": headline,
                "points": points,
                "sentiment": sentiment,
                "source": source,
                "sector": sector,
                "timestamp": timestamp,
                "country": country
            }

            headlines.append(item)
            sector_batches.setdefault(sector, []).append(item)

# 🚀 Push to Telegram
if headlines:
    push_sector_batches(sector_batches)
    st.success("✅ Sector-wise news pushed to Telegram!")
else:
    st.info("No new headlines found.")


