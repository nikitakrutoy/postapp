from flask import Flask

import bot.utils
import auth_server.utils

botConfig = bot.utils.Config
botConfig.setup("./bot/config.json")

authServerConfig = auth_server.utils.Config
authServerConfig.setup("./auth_server/config.json")



import auth_server.blueprint
import bot.bot

app = Flask("postapp")

app.register_blueprint(bot.bot.blueprint, url_prefix="/bot")
app.register_blueprint(auth_server.blueprint.blueprint, url_prefix="/auth")
