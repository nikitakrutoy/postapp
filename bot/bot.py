import logging
import telegram
import json
from .auth import auth
from .post import post
from .list import list
from .utils import Config as botConfig
from telegram.ext import Dispatcher, MessageHandler, CommandHandler, Filters
from flask import Blueprint, request, Response

TOKEN = botConfig.options["token"]

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

bot = telegram.Bot(token=TOKEN)
dispatcher = Dispatcher(bot, None, workers=0, use_context=True)

def dice(update, context):
    context.bot.send_dice(chat_id=update.effective_chat.id)

dispatcher.add_handler(CommandHandler("dice", dice))

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hello, my little friend")

dispatcher.add_handler(CommandHandler("start", start))

def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


dispatcher.add_handler(CommandHandler("auth", auth, pass_args=True))
dispatcher.add_handler(CommandHandler("list", list, pass_args=True))
dispatcher.add_handler(MessageHandler(
    (Filters.text | Filters.photo) & \
    ~(Filters.update.channel_post | Filters.group | Filters.update.edited_message | Filters.update.edited_channel_post), 
    post
))
dispatcher.add_handler(MessageHandler(Filters.command, unknown))

blueprint = Blueprint("bot", __name__)

@blueprint.route(f"/")
def home():
    return "Hello, Wolrd!"

@blueprint.route(f"/{TOKEN}", methods=["GET", "POST"])
def webhook():
    update = telegram.Update.de_json(json.loads(request.get_data(as_text=True)), bot)
    dispatcher.process_update(update)
    return Response(status=200)

