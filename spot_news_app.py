import streamlit as st
import feedparser
from datetime import datetime
from telegram import Bot
from telegram.constants import ParseMode

# 🔐 Telegram credentials
bot_token = st.secrets["bot_token"]
chat_id = st.secrets["chat_id"]
bot = Bot(token=bot_token)

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
    if any(w in text for w in ["surge", "gain", "rise", "up", "record high"]): return "📈 Bullish"
    if any(w in text for w in ["fall", "drop", "decline", "down", "plunge"]): return "📉 Bearish"
    return "⚖️ Neutral"

# 🏷 Sector tagging
def tag_sector(text):
    text = text.lower()
    if any(w in text for w in ["bank", "loan", "insurance", "finance", "nifty"]): return "💰 Finance"
    if any(w in text for w in ["auto", "vehicle", "ev", "car", "bike"]): return "🚗 Auto"
    if any(w in text for w in ["power", "energy", "solar", "electricity"]): return "🔋 Energy"
    if any(w in text for w in ["gold", "silver", "commodity", "metal"]): return "🪙 Commodities"
    if any(w in text for w in ["tech", "software", "ai", "it", "startup"]): return "💻 Technology"
    if any(w in text for w in ["real estate", "property", "housing"]): return "🏠 Real Estate"
    return "🌐 General"

# 🧠 Summarizer
def summarize_to_points(text):
    return [s.strip() for s in text.split(". ") if len(s.strip()) > 30][:5]

# 📲 Telegram push
def send_text_to_telegram(headlines):
    message = "📈 Spot Trading – Daily Market Pulse\n\n"
    for h in headlines:
        message += f"*📰 {h['title']}*\n"
        for p in h['points']:
            message += f"• {p}\n"
        message += f"\n{h['sentiment']} | {h['sector']}\n"
        message += f"🔗 Source: {h['source']}\n\n"
    try:
        bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        st.error(f"Telegram error: {e}")

# 🧩 Streamlit UI
st.set_page_config(page_title="Spot Trading – Auto News Pulse", layout="wide")
st.title("📈 Spot Trading – Daily Market Pulse")
st.write(f"🗓️ {datetime.now().strftime('%d %b %Y, %I:%M %p')}")

if "seen" not in st.session_state:
    st.session_state.seen = set()

headlines = []

# 🔁 Fetch and display
for url in feeds:
    feed = feedparser.parse(url)
    for entry in feed.entries[:3]:
        headline = entry.title
        link = entry.link
        source = link.split("/")[2]
        full_text = entry.get("summary", entry.get("description", ""))

        if headline not in st.session_state.seen and full_text:
            st.session_state.seen.add(headline)
            points = summarize_to_points(full_text)
            sentiment = detect_sentiment(full_text)
            sector = tag_sector(full_text)

            st.markdown(f"### 📰 {headline}")
            for p in points:
                st.write(f"• {p}")
            st.write(f"{sentiment} | {sector}")
            st.markdown(f"🔗 Source: `{source}`")
            st.markdown(f"[Read more]({link})")
            st.divider()

            headlines.append({
                "title": headline,
                "points": points,
                "sentiment": sentiment,
                "source": source,
                "sector": sector
            })

if headlines:
    send_text_to_telegram(headlines)
    st.success("✅ News summary sent to Telegram!")
else:
    st.info("📭 No new headlines found.")
