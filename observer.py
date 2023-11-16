import asyncio
import os
from typing import List

import feedparser
from dateutil import parser
from dotenv import load_dotenv
from telegram import Bot

from db.models import User, Feed, get_session

load_dotenv()


class Observer:

    def __init__(self):
        self.__bot = Bot(os.getenv("TOKEN"))

    async def __get_users(self) -> List[User]:
        with get_session() as session:
            users = session.query(User).all()
            for user in users:
                user.feeds = user.feeds
        return users

    async def __parse_feeds(self, feeds: List[Feed]) -> []:
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

    async def __send_message(self, chat_id, message):
        await self.__bot.send_message(chat_id=chat_id, text=message, parse_mode="HTML")

    async def __start(self):
        while True:
            users = await self.__get_users()
            for user in users:
                entries = await self.__parse_feeds(user.feeds)
                if entries:
                    for entry in entries:
                        title = "<b>" + entry.title + "</b>\n"
                        link = "<a href='" + entry.link + "'>Görüntüle</a>\n\n"
                        text = title + "\n" + link
                        await self.__send_message(chat_id=user.chat_id, message=text)
            await asyncio.sleep(60)

    def run(self):
        print("observer called...")
        asyncio.run(self.__start())

