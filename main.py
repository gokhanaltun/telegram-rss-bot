from bot import tg_bot
import threading
from observer import Observer

obs = Observer()
threading.Thread(target=obs.run).start()
tg_bot.run()
