import os
from datetime import datetime, timezone

from telegram import Update
from telegram.ext import ContextTypes

from database.models import User, Feed, get_session
import feedparser


def __check_auth(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        with get_session() as session:
            user = session.query(User).filter_by(chat_id=update.message.chat_id).first()
        if not user:
            await update.message.reply_text("Yetkiniz Yok!")
            return
        else:
            await func(update, context)

    return wrapper


@__check_auth
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Merhaba {update.effective_user.first_name} \n\n" +
        "add rss feed: /addfeed \n" +
        "delete rss feed: /deletefeed \n" +
        "list rss feeds: /listfeed \n")


@__check_auth
async def add_feed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 2:
        with get_session() as session:
            user = session.query(User).filter_by(chat_id=update.message.chat_id).first()
            feed = session.query(Feed).filter_by(name=context.args[0]).first()

        if feed:
            await update.message.reply_text("Bu isimde bir kayıt zaten var.")
            return

        try:
            feed = feedparser.parse(context.args[1])
            if "bozo_exception" in feed:
                await update.message.reply_text("Rss url geçerli değil.")
                return

            with get_session() as session:
                new_feed = Feed(
                    name=context.args[0],
                    url=context.args[1],
                    last_read=str(datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %z")),
                    user=user
                )

                session.add(new_feed)
                session.commit()

            await update.message.reply_text("Rss feed eklendi.")

        except Exception as e:
            print(e)
            await update.message.reply_text(f"Rss feed eklenemedi bir hata oluştu.\n {e}")
    else:
        await update.message.reply_text("Geçerli parametre gönderilmedi.")


@__check_auth
async def delete_feed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 1:
        with get_session() as session:
            feed = session.query(Feed).filter_by(name=context.args[0]).first()
            if feed:
                session.delete(feed)
                session.commit()
                await update.message.reply_text(f"{feed.name} silindi.")
            else:
                await update.message.reply_text(f"{context.args[0]} isimli bir kayıt yok.")
    else:
        await update.message.reply_text("Geçerli parametre gönderilmedi.")


@__check_auth
async def list_feed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with get_session() as session:
        user = session.query(User).filter_by(chat_id=update.message.chat_id).first()
        feeds = user.feeds
    if not feeds:
        await update.message.reply_text("Hiç rss feed eklememişsiniz.")
    else:
        reformatted_feed_str = ""
        for feed in feeds:
            reformatted_feed_str = reformatted_feed_str + f"name: {feed.name}  ||  last_read: {feed.last_read}\n"
        await update.message.reply_text(reformatted_feed_str)


async def auth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 1 and context.args[0] == os.getenv("AUTH_KEY"):
        with get_session() as session:
            user = session.query(User).filter_by(chat_id=update.message.chat_id).first()
            if not user:
                new_user = User(chat_id=str(update.message.chat_id))
                session.add(new_user)
                session.commit()
                await update.message.reply_text("Yetki Verildi.")
            else:
                await update.message.reply_text("Zaten Yetkilisiniz.")
                return
    else:
        await update.message.reply_text("Yetki Verilmedi.")
