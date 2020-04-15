import requests
from .utils import Config
from app import app

Config.setup("./config.json")

ssl_context = (
    '/home/postapp/postapp/ssl/nikitakrutoy.ml/fullchain1.pem',
    '/home/postapp/postapp/ssl/nikitakrutoy.ml/privkey1.pem'
)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8443, ssl_context=ssl_context, debug=False)

