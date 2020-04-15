from flask import Flask
from .blueprint import blueprint
import bot.bot

app = Flask("postapp-auth-server")
app.register_blueprint(blueprint, url_prefix="/auth")