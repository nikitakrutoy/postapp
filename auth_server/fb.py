import requests
import pymongo
from flask import request, Response
from .utils import Config

db = pymongo.MongoClient().users

def auth():
    if "code" in request.args:
        code = request.args["code"]
        tg_id = request.args["state"]
        resp = requests.get(
            "https://graph.facebook.com/v6.0/oauth/access_token",
            params=dict(
                client_id=Config.options["facebook"]["client_id"],
                client_secret=Config.options["facebook"]["client_secret"],
                redirect_uri=Config.options["facebook"]["redirect_uri"],
                code=code
            )
        )
        access_token = resp.json()["access_token"]

        resp = requests.get(
            "https://graph.facebook.com/me/accounts",
            params=dict(
                fields="name,access_token",
                access_token=access_token
            )
        )
        pages = resp.json()["data"]

        resp = requests.get(
            "https://graph.facebook.com/me/",
            params=dict(
                fields="name, id",
                access_token=access_token
            )
        )
        me = resp.json()
        print(tg_id, me, pages, access_token)
        db_insert(tg_id, me, pages, access_token)
        return Response("You successfully logged into Facebook. You can go back now.", status=200)
    else:
        return Response("What are you doing here little snitch, hah?", status=400)


def db_insert(tg_id, me, pages, access_token):
    query = {
        "tgId": tg_id,
        "fb.id": {
            "$eq": me["id"]
        }
    }

    res = db.data.update_one(
        query,
        {
            "$set": {
                "fb.$.access_token": access_token,
                "fb.$.pages": pages
            }
        }
    )

    if res.modified_count == 0:
        res = db.data.update_one(
            {"tgId": tg_id,},
            {
                "$push": {
                    "fb": {
                        "id": me["id"],
                        "name": me["name"],
                        "access_token": access_token,
                        "pages": pages
                    }

                }
            },
            upsert=True
        )