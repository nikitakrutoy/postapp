import celery
import pymongo
import requests
import telegram
import logging
from ..utils import DataStorage, Query

class FacebookPostException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__()
    
    def __str__(self):
        return f"Facebook: {self.message}"

class FacebookPost(celery.Task):
    def setup(self, tg_id, token, query):
        self.tg_id = tg_id
        self.query = query
        self.bot = telegram.Bot(token=token)
        db = pymongo.MongoClient().users
        data = db.data.find_one(dict(tgId=str(tg_id)))
        if data is None:
            data = {}
            self.bot.send_message(chat_id=int(tg_id), text="You do not have authorized fb accounts")
        self.data = DataStorage(data.get("fb", {}), exception_class=FacebookPostException)
        return self

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        self.bot.send_message(chat_id=int(self.tg_id), text=str(exc))
        self.bot.send_message(chat_id=int(self.tg_id), 
            text="If you do not understand error, please, notice @nikitakrutoy")
        return super().on_failure(exc, task_id, args, kwargs, einfo)

    def upload_photo(self, pid, photo, token):
        url = f"https://graph.facebook.com/{pid}/photos"
        res = requests.post(
            url,
            params=dict(
                url=photo,
                access_token=token,
                published="False"
            )
        ).json()
        if "error" in res:
            raise FacebookPostError(f"{res['error']['message']} PageId: {pid}, UserId: {uid}")

        return res["id"]

    def post_page(self, uid, pid, message, photo=None):
        url = f"https://graph.facebook.com/{pid}/feed"
        page = self.data.get_page(uid, pid)

        token = page.get("access_token")

        params = dict(message=message, access_token=token,  )
        if photo is not None:
            photo_id = self.upload_photo(pid, photo, token)
            params["attached_media[0]"] = '{"media_fbid": ' + str(photo_id) + '}'

        res = requests.post(url, params=params).json()

        if "error" in res:
            raise FacebookPostException(f"{res['error']['message']} PageId: {pid}, UserId: {uid}")

    def post_user(self, uid, message, photo):
        pages = self.data.get_pages(uid)
        for pid in pages.keys():
            self.post_page(uid, pid, message, photo)

    def post(self, message, photo):
        for uid in self.data.profiles.keys():
            self.post_user(uid, message, photo)

    def run(self, message, photo, tg_id, token, query=None):
        photo = photo["file_path"] if photo is not None else None
        query = Query.from_json(query) if query is not None else None
        self.setup(tg_id, token, query)
        if query is not None:
            if query.pid is not None:
                self.post_page(query.uid, query.pid, message, photo)
            elif query.uid is not None:
                self.post_user(query.uid, message, photo)
            elif query.sid == "fb":
                self.post(message, photo)
        else:
            self.post(message, photo)