from flask import Blueprint
from .fb import auth as auth_fb
from .ok import auth as auth_ok

blueprint = Blueprint('auth', __name__)

@blueprint.route(f"/")
def home():
    return "Hello, Wolrd!"

blueprint.add_url_rule("/fb", "fb", auth_fb, methods=["GET", "POST"])
blueprint.add_url_rule("/ok", "ok", auth_ok, methods=["GET", "POST"])