
from urllib.parse import urlencode
import telegram
import pymongo
from .utils import Config

db = pymongo.MongoClient().users


def auth(update, context):
    site = None if not context.args else context.args[0]
    if site == "fb":
        auth_fb(update, context)
    elif site == "ok":
        auth_ok(update, context)
    elif site == "tg":
        auth_tg(update, context)
    else:
        context.bot.send_message(update.effective_chat.id, text="Usage: /auth {fb, ok, tg}")

def auth_fb(update, context):
    OAUTH="https://www.facebook.com/v6.0/dialog/oauth"
    params = dict(
        client_id=Config.options["facebook"]["client_id"],
        redirect_uri=Config.options["facebook"]["redirect_uri"],
        scope="publish_pages,manage_pages",
        state=update.effective_user.id
    )
    link = f"{OAUTH}?{urlencode(params)}" 
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Follow this [link]({link}) to login",
        parse_mode=telegram.ParseMode.MARKDOWN
    )

def auth_ok(update, context):
    oauth = "https://connect.ok.ru/oauth/authorize"
    params = dict(
        client_id=Config.options["odnoklassniki"]["client_id"],
        redirect_uri=Config.options["odnoklassniki"]["redirect_uri"],
        scope="VALUABLE_ACCESS;PHOTO_CONTENT;LONG_ACCESS_TOKEN;GROUP_CONTENT",
        response_type="code",
        state=update.effective_user.id
    )
    link = f"{oauth}?{urlencode(params)}" 
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Follow this [link]({link}) to login",
        parse_mode=telegram.ParseMode.MARKDOWN
    )

def auth_tg(update, context):
    if len(context.args) > 1:
        channel_id = context.args[1]
        try:
            admins = context.bot.get_chat_administrators(channel_id)
        except Exception:
            context.bot.send_message(update.effective_chat.id, text="Please, add this bot channel admins")
            return
        added = False
        for admin in admins:
            if admin.user.id == update.effective_user.id:
                res = db.data.update_one(
                    {"tgId": str(update.effective_user.id)},
                    {
                        "$addToSet": {"channels": channel_id}
                    }
                )
                context.bot.send_message(update.effective_chat.id, text="Added tg channel")
                return
        context.bot.send_message(update.effective_chat.id, text="You are not admin of this channel")
    else:
        context.bot.send_message(update.effective_chat.id, text="Usage: /auth tg <channel name/id>")