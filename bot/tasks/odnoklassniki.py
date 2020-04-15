import celery
import pymongo
import requests
import logging
import odnoklassniki
import telegram
import json
import io
from ..utils import DataStorage, Query, Config

class OdnoklassnikiPostException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__()
    
    def __str__(self):
        return f"Odnoklassniki: {self.message}"


class OdnoklassnikiPost(celery.Task):
    def setup(self, tg_id, token, query):
        self.tg_id = tg_id
        self.query = query
        db = pymongo.MongoClient().users
        self.data = DataStorage(db.data.find_one(dict(tgId=str(tg_id))).get("ok"), exception_class=OdnoklassnikiPostException)
        self.bot = telegram.Bot(token=token)
        return self

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        self.bot.send_message(chat_id=int(self.tg_id), text=str(exc))
        self.bot.send_message(chat_id=int(self.tg_id), 
            text="If you do not understand error, please, notice @nikitakrutoy")

    def download_photo(self, photo):
        bytes = io.BytesIO()
        photo.download(out=bytes)
        return bytes

    def upload_photo(self, bytes, upload_info):
        photo_id = upload_info["photo_ids"][0]
        upload_url = upload_info["upload_url"]
        action = {"file": bytes.getvalue()}
        resp = requests.post(upload_url, files=action)
        data = resp.json()
        return resp.json()['photos'][photo_id]['token']

    def post_page(self, uid, pid, message, photo=None):
        CLIENT_KEY = Config.options["odnoklassniki"]["client_key"]
        CLIENT_SECRET = Config.options["odnoklassniki"]["client_secret"]
        page = self.data.get_page(uid, pid)
        token = self.data.get_profile(uid).get("access_token")
        ok = odnoklassniki.Odnoklassniki(CLIENT_KEY, CLIENT_SECRET, token)
        media = [dict(type="text", text=message,)] if message is not None else []
        if photo is not None:            
            bytes = self.download_photo(photo)
            upload_info = ok.photosV2.getUploadUrl(gid=pid, count=1)
            photo_token = self.upload_photo(bytes, upload_info)
            media.append({
                "type": "photo",
                "list": [{ "id": photo_token }]
            })

        res = ok.mediatopic.post(
            gid=pid,
            type="GROUP_THEME",
            attachment=json.dumps(dict(
                media=media
            ))
        )

    def post_user(self, uid, message, photo):
        pages = self.data.get_pages(uid)
        for pid in pages:
            self.post_page(uid, pid, message, photo)

    def post(self, message, photo):
        for uid in self.data.profiles.keys():
            self.post_user(uid, message, photo)

    def run(self, message, photo, tg_id, token, query=None):
        self.setup(tg_id, token, query)
        query = Query.from_json(query) if query is not None else None
        photo = telegram.File(**photo, bot=self.bot) if photo is not None else None
        if query is not None:
            if query["pid"] is not None:
                self.post_page(query.uid, query.pid, message, photo)
            elif query.uid is not None:
                self.post_user(query.uid, query.pid, message, photo)
        else:
            self.post(message, photo)