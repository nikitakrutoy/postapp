import requests
import utils
botConfig = utils.Config
botConfig.setup("./config.json")

utils.delete_webhook(botConfig.options["token"])
utils.set_webhook(botConfig.options["token"])

from app import app

ssl_context = (
    '/home/postapp/postapp/ssl/nikitakrutoy.ml/fullchain1.pem',
    '/home/postapp/postapp/ssl/nikitakrutoy.ml/privkey1.pem'
)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8443, ssl_context=ssl_context, debug=False)


