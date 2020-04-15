import pymongo
import telegram
import celery
from ..utils import Query

class TelegramPost(celery.Task):
    def setup(self, tg_id, token):
        self.tg_id = tg_id
        self.bot = telegram.Bot(token=token)
        db = pymongo.MongoClient().users
        data = db.data.find_one(dict(tgId=str(tg_id)))
        if data is None:
            data = {}
            self.bot.send_message(chat_id=int(tg_id), text="You do not have authorized tg channels")
        self.channels = data.get("channels", [])
        

    def post_channel(self, message, photo, channel):
        if photo is not None:
            self.bot.send_photo(chat_id=channel, photo=photo, caption=message)
        else:
            self.bot.send_message(chat_id=channel, text=message)
    

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        self.bot.send_message(chat_id=int(self.tg_id), text=str(exc))
        return super().on_failure(exc, task_id, args, kwargs, einfo)

    def post(self, message, photo):
        for channel in self.channels:
            self.post_channel(message, photo, channel)

    def run(self, message, photo, tg_id, token, query=None):
        self.setup(tg_id, token)
        photo = photo["file_id"] if photo is not None else None
        query = Query.from_json(query) if query is not None else None
        if query is not None:
            if query.uid is not None:
                self.post_channel(message, photo, query.uid)
            elif query.sid == "tg":
                self.post(message, photo)
        else:
            self.post(message, photo)