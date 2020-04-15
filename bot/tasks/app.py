import celery
import telegram
from .facebook import FacebookPost
from .telegram import TelegramPost
from .odnoklassniki import OdnoklassnikiPost
from ..utils import Config

Config.setup("./bot/config.json")

BROKER_URL = Config.options["celery"]["broker"]
BACKEND_URL = Config.options["celery"]["backend"]
app = celery.Celery('executor', broker=BROKER_URL, backend=BACKEND_URL)

FacebookPost = app.register_task(FacebookPost())
TelegramPost = app.register_task(TelegramPost())
OdnoklassnikiPost = app.register_task(OdnoklassnikiPost())


@app.task()
def reply_message(prev_result, token, chat_id, message):
    telegram.Bot(token).send_message(chat_id=int(chat_id), text=message)