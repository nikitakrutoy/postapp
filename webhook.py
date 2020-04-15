import bot.utils
botConfig = bot.utils.Config
botConfig.setup("./bot/config.json")
bot.utils.delete_webhook(botConfig.options["token"])
bot.utils.set_webhook(botConfig.options["token"])
