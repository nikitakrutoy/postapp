import requests
import pymongo
import hashlib
import odnoklassniki
from flask import request, Response
from .utils import Config

db = pymongo.MongoClient().users
 
def auth():
    if "code" in request.args:
        code = request.args["code"]
        tg_id = request.args["state"]
        resp = requests.post(
            "https://api.ok.ru/oauth/token.do",
            params=dict(
                client_id=Config.options["odnoklassniki"]["client_id"],
                client_secret=Config.options["odnoklassniki"]["client_secret"],
                redirect_uri=Config.options["odnoklassniki"]["redirect_uri"],
                code=code,
                grant_type="authorization_code"
            )
        )
        resp = resp.json()
        access_token = resp["access_token"]
        client_key = Config.options["odnoklassniki"]["client_key"]
        client_secret = Config.options["odnoklassniki"]["client_secret"]
        ok = odnoklassniki.Odnoklassniki(client_key, client_secret, access_token)
        me = ok.users.getCurrentUser()
        groups = ok.group.getUserGroupsV2()
        user_groups_ids = list()
        for group in groups["groups"]:
            members = ok.group.getMembers(uid=group["groupId"], statuses="ADMIN", count=10)
            admins = list(map(
                lambda x: x["userId"],
                members.get("members", []) 
            ))
            if me["uid"] in admins:
                user_groups_ids.append(group["groupId"])

        user_groups_names = list(map(
            lambda x: x["name"],
            ok.group.getInfo(uids=','.join(user_groups_ids), fields="name")
        ))
        user_groups = [dict(id=uid, name=name) for uid, name in zip(user_groups_ids, user_groups_names)]
        db_insert(tg_id, me, user_groups, access_token)
        return Response("You successfully logged into OK.ru. You can go back now.", status=200)
    else:
        return Response("What are you doing here little snitch, hah?", status=400)


def db_insert(tg_id, me, pages, access_token):
    query = {
        "tgId": tg_id,
        "ok.id": {
            "$eq": me["uid"]
        }
    }

    res = db.data.update_one(
        query,
        {
            "$set": {
                "ok.$.access_token": access_token,
            }
        }
    )

    if res.modified_count == 0:
        res = db.data.update_one(
            {"tgId": tg_id,},
            {
                "$push": {
                    "ok": {
                        "id": me["uid"],
                        "name": me["name"],
                        "pages": pages,
                        "access_token": access_token,
                    }

                }
            },
            upsert=True
        )