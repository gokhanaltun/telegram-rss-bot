from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler

from .commands import *

load_dotenv()
app = ApplicationBuilder().token(os.getenv("TOKEN")).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("addfeed", add_feed, has_args=True))
app.add_handler(CommandHandler("listfeed", list_feed))
app.add_handler(CommandHandler("deletefeed", delete_feed, has_args=True))
app.add_handler(CommandHandler("auth", auth, has_args=True))


def run():
    print("tg bot called...")
    app.run_polling()
