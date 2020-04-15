import pymongo
import yaml
db = pymongo.MongoClient().users

def list(update, context):
    data = db.data.find_one({"tgId": str(update.effective_user.id)})
    if not data:
        context.bot.send_message(update.effective_chat.id, text="You have not logged in any account")
        return
        
    del data["_id"]
    for fb in data.get("fb", []):
        del fb["access_token"]
        for page in fb["pages"]:
            del page["access_token"]
    for ok in data.get("ok", []):
        del ok["access_token"]

    data = yaml.dump(data, allow_unicode=True)
    context.bot.send_message(update.effective_chat.id, text=data)