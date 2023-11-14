import asyncio
import os
from typing import List
from dateutil import parser
import feedparser
from dotenv import load_dotenv
from telegram import Bot

from bot.database.models import User, Feed, get_session
from schedule.celery import app

load_dotenv()

bot = Bot(os.getenv("TOKEN"))


async def __send_tg_message_to_user(chat_id: int, message: str):
    await bot.sendMessage(chat_id=chat_id, text=message, parse_mode="HTML")


def __get_users() -> List[User]:
    with get_session() as session:
        users = session.query(User).all()
        for user in users:
            user.feeds = user.feeds
    return users


def __parse_feeds(feeds: List[Feed]) -> []:
    entries = []
    for feed in feeds:
        feed_content = feedparser.parse(feed.url)
        latest_entries = []
        for entry in feed_content.entries:
            published_parsed = parser.parse(entry.published)
            last_read = parser.parse(feed.last_read)

            if published_parsed > last_read:
                latest_entries.append(entry)

        last_sorted_entries = sorted(latest_entries, key=lambda entry: entry.published)
        if len(last_sorted_entries) > 0:
            with get_session() as session:
                session.query(Feed).filter_by(id=feed.id).update(
                    {"last_read": parser.parse(last_sorted_entries[-1].published)})
                session.commit()

            entries.extend(last_sorted_entries)
    sorted_entries = sorted(entries, key=lambda entry: entry.published)
    return sorted_entries


@app.task
def check_and_process_rss_feed_every_minutes():
    users = __get_users()
    for user in users:
        entries = __parse_feeds(user.feeds)
        if entries:
            for entry in entries:
                title = "<b>" + entry.title + "</b>\n"
                link = "<a href='" + entry.link + "'>Görüntüle</a>\n\n"
                text = title + "\n" + link
                asyncio.run(__send_tg_message_to_user(int(user.chat_id), text))


check_and_process_rss_feed_every_minutes()
