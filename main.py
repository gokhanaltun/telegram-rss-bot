import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

from src import commands as commands

load_dotenv()


def main():
    application = Application.builder().token(os.getenv("TOKEN")).build()

    application.add_handler(commands.rss_conv_handler)
    application.add_handlers([
        CommandHandler("start", commands.start),
        CommandHandler("listRss", commands.list_rss),
        CommandHandler("deleteRss", commands.delete_rss),
        CallbackQueryHandler(commands.select, pattern="select"),
        CallbackQueryHandler(commands.confirm, pattern="^confirm"),
    ])

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
