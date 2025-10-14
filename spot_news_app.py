import streamlit as st
import feedparser
import requests
from googletrans import Translator
from fpdf import FPDF
from datetime import datetime
import time


# 🔐 API Keys

bot_token = "8376336695:AAEUqfYB2-nWXy4ozOaxeznEmvtRrTJ5AbI"
chat_id = "@spot_tradingnews"

# 🌐 RSS Feeds
feeds = [
    "https://www.moneycontrol.com/rss/news.xml",
    "https://economictimes.indiatimes.com/rssfeedsdefault.cms",
    "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10001147",
    "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=158391",
    "https://feeds.reuters.com/reuters/businessNews",
    "https://feeds.reuters.com/reuters/marketsNews",
    "https://www.ft.com/rss/home",
    "https://www.investing.com/rss/news_25.rss",
    "https://finance.yahoo.com/news/rssindex",
    "https://www.marketwatch.com/rss/topstories",
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

# 🏷 Sector tagging with emojis
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
    elif "us" in text or "america" in text or "nasdaq" in text:
        return "USA 🇺🇸"
    elif "china" in text or "shanghai" in text:
        return "China 🇨🇳"
    elif "europe" in text or "germany" in text or "france" in text or "uk" in text:
        return "Europe 🇪🇺"
    elif "japan" in text or "tokyo" in text:
        return "Japan 🇯🇵"
    else:
        return "Global 🌍"

# 🧠 Point-wise summarizer
def summarize_to_points(text):
    sentences = text.split(". ")
    return [s.strip() for s in sentences if len(s.strip()) > 30][:5]

# 📲 Telegram Send (Formatted with Timestamp + Country)
def send_text_to_telegram(headlines):
    message = "📈 Spot Trading – Daily Market Pulse\n\n"
    for h in headlines:
        message += f"*📰 {h['title']}*\n"
        message += f"🕒 {h['timestamp']} | 🌍 {h['country']}\n"
        for p in h['points']:
            message += f"• {p}\n"
        message += f"\n📊 Sentiment: {h['sentiment']} | 🏷 Sector: {h['sector']}\n"
        message += f"🔗 Source: {h['source']}\n\n"

    requests.post(
        f"https://api.telegram.org/bot{bot_token}/sendMessage",
        data={
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
    )

# 🧩 Streamlit UI
st.set_page_config(page_title="Spot Trading – Auto News Pulse", layout="wide")
st.title("📈 Spot Trading – Daily Market Pulse")
st.write(f"🗓️ {datetime.now().strftime('%d %b %Y, %I:%M %p')}")

refresh_interval = st.slider("🔁 Auto-refresh every X seconds", 10, 600, 10)
if "seen" not in st.session_state:
    st.session_state.seen = set()

headlines = []

# 🔁 Auto-refresh loop
while True:
    new_found = False
    for url in feeds:
        feed = feedparser.parse(url)
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

                headlines.append({
                    "title": headline,
                    "points": points,
                    "sentiment": sentiment,
                    "source": source,
                    "sector": sector,
                    "timestamp": timestamp,
                    "country": country
                })
                new_found = True

    if new_found:
        send_text_to_telegram(headlines)
        st.success("✅ News summary sent to Telegram!")


    time.sleep(10)

