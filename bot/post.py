import pymongo
import requests
import logging
import json

from .tasks.app import FacebookPost, TelegramPost, OdnoklassnikiPost, reply_message
from .utils import Config as botConfig, \
    parse_message, extract_photo, ParseMessageException

db = pymongo.MongoClient().users


def post(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Posting")
    if update.effective_message.photo:
        photo = extract_photo(update.effective_message.photo)
        text = update.message.caption
    else:
        photo = None
        text = update.effective_message.text

    try:
        text, eta, queries = parse_message(text)
    except ParseMessageException as error:
        context.bot.send_message(update.effective_chat.id, text=str(error))

    bot_token = botConfig.options["token"]
    user_id = update.effective_user.id
    if queries:
        for query in queries:
            _eta = eta
            args = [text, photo, user_id, bot_token, query.to_json()]
            if query.sid == "fb":
                FacebookPost.apply_async(args=args, countdown=_eta, link=reply_message.s(bot_token, user_id, f"posted {query.sid}:{query.uid}:{query.pid}"))
            elif query.sid == "tg":
                TelegramPost.apply_async(args=args, countdown=_eta, link=reply_message.s(bot_token, user_id, f"posted {query.sid}:{query.uid}:{query.pid}"))
            elif query.sid == "ok": 
                OdnoklassnikiPost.apply_async(args=args, countdown=_eta, link=reply_message.s(bot_token, user_id, f"posted {query.sid}:{query.uid}:{query.pid}"))
            else:
                context.bot.send_message(update.effective_chat.id, text=f"Unknown site: {query.sid}")
    else:
        args = [text, photo, user_id, bot_token]
        FacebookPost.apply_async(args=args, countdown=eta, link=reply_message.s(bot_token, user_id, "posted fb"))
        TelegramPost.apply_async(args=args, countdown=eta, link=reply_message.s(bot_token, user_id, "posted tg"))
        OdnoklassnikiPost.apply_async(args=args, countdown=eta, link=reply_message.s(bot_token, user_id, "posted ok"))
        