import os
from dotenv import load_dotenv
from . import models as models
from datetime import datetime, timezone
import feedparser
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters
)


load_dotenv()


def check_auth(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = os.getenv("ID")
        if update.message.from_user.id != int(user_id):
            await update.message.reply_text("Yetkili Değilsiniz")
            return
        return await func(update, context)
    return wrapper


RSS_NAME, RSS_URL = range(2)


@check_auth
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(f"Merhaba {update.message.from_user.first_name} :)")


@check_auth
async def add_rss(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("RSS için isim girin. İptal etmek için /cancel komutunu kullanın.")
    return RSS_NAME


async def rss_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    with models.get_session() as session:
        feed = session.query(models.Feed).filter_by(
            name=update.message.text).first()

    if feed:
        await update.message.reply_text("Bu isimde bir kayıt zaten var. Başka bir isim girin.")
        return RSS_NAME

    context.user_data["rssName"] = update.message.text
    await update.message.reply_text("RSS url'ini girin.")
    return RSS_URL


async def rss_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    name_ = context.user_data["rssName"]
    url_ = update.message.text

    with models.get_session() as session:
        feed = session.query(models.Feed).filter_by(
            url=url_).first()

    if feed:
        await update.message.reply_text(f"Bu url daha önce {feed.name} olarak eklenmiş. Başka bir url girin.")
        return RSS_URL

    try:
        feed = feedparser.parse(url_)
        if "bozo_exception" in feed:
            await update.message.reply_text("Rss url geçerli değil.")
            return RSS_URL
    except Exception as e:
        await update.message.reply_text(f"URL parse edilmeye çalışılırken bir hata oldu. İşlem sonlandırıldı. \n {e}")
        return ConversationHandler.END

    with models.get_session() as session:
        new_feed = models.Feed(
            name=name_,
            url=url_,
            last_read=str(datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %z")))

        session.add(new_feed)
        session.commit()

    await update.message.reply_text("RSS eklendi.")
    return ConversationHandler.END


@check_auth
async def list_rss(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with models.get_session() as session:
        feeds = session.query(models.Feed).all()

    if len(feeds) == 0:
        await update.message.reply_text("Hiç RSS kaydı yok.")
        return

    for feed in feeds:
        await update.message.reply_text(f"name: {feed.name}\nurl: {feed.url}")


@check_auth
async def delete_rss(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []

    with models.get_session() as session:
        feeds = session.query(models.Feed).all()

    if len(feeds) == 0:
        await update.message.reply_text("Hiç RSS kaydı yok.")
        return

    for feed in feeds:
        button = InlineKeyboardButton(
            text=feed.name, callback_data=f"select:{feed.name}:{feed.id}")
        keyboard.append([button])

    keyboard.append([InlineKeyboardButton(
        text="İptal", callback_data=f"select:cancel")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Silmek istediğiniz kaydı seçin.", reply_markup=reply_markup)


async def select(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data.split(":")
    if data[1] == "cancel":
        await query.edit_message_text(text=f"İşlem iptal edildi.")
        return

    keyboard = [
        [InlineKeyboardButton(
            text="Evet", callback_data=f"confirm:{data[1]}:{data[2]}")],
        [InlineKeyboardButton(text="Hayır", callback_data=f"confirm:cancel")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=f"Bu kaydı silmek istiyor musunuz? '{data[1]}'", reply_markup=reply_markup)


async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data.split(":")

    if data[1] == "cancel":
        await query.edit_message_text(text=f"Silme işlemi iptal edildi")
        return
    else:
        with models.get_session() as session:
            feed = session.query(models.Feed).filter_by(
                id=int(data[2])).first()
            session.delete(feed)
            session.commit()

        await query.edit_message_text(text=f"'{data[1]}' isimli kayıt silindi.")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("iptal edildi")
    return ConversationHandler.END


rss_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("addRss", add_rss)],
    states={
        RSS_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, rss_name)],
        RSS_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, rss_url)],
    },
    fallbacks=[CommandHandler("cancel", cancel)]
)
