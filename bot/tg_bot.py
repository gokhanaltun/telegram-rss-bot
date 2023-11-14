import os
from telegram.ext import CommandHandler, ApplicationBuilder
import tg_commands as commands
from dotenv import load_dotenv

load_dotenv()


app = ApplicationBuilder().token(os.getenv("TOKEN")).build()

app.add_handler(CommandHandler("start", commands.start))
app.add_handler(CommandHandler("addfeed", commands.add_feed, has_args=True))
app.add_handler(CommandHandler("deletefeed", commands.delete_feed, has_args=True))
app.add_handler(CommandHandler("listfeed", commands.list_feed))
app.add_handler(CommandHandler("auth", commands.auth))

app.run_polling()
