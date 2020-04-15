from flask import Flask
import bot

app = Flask("postapp-bot")

app.register_blueprint(bot.blueprint, url_prefix="/bot")