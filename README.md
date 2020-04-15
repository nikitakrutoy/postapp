# postapp
Telegram bot for posting to Facebook, Odnoklassniki and Telegram Channels. Bot can send post with one image or text or both to all or specified list of authorized pages.
Working copy of of bot should be [here](https://t.me/postapp_bot) but i do not guarantee that because i have not finished with docker images of the bot and it may fall and do not restart.


# Backstory (aka Проектирование сервиса)
I decided to make telegram bot beacause i was limitied in time and havent tourch Vue.js for a long time. 
Therefore i decided it will be much more prodcutive if i concentrate mainly on backend part of app. This was a mistake. 
The first api that is started with was VK, and it took me a lot of time to found out that it is actually really hard to 
create posts from server side with server side authorization, only client side. One of the tricks to do it is to imitate client side authorization 
on server side, but that would require user to trust server his login and password, and this is not a solution. That is how i ended
with a strange combination of Facebook and OK.ru. I added Telegram Channels because I was afraid that ok.ru api team would not give 
my app permisions or give them after deadline.

![alt text](https://wompampsupport.azureedge.net/fetchimage?siteId=7575&v=2&jpgQuality=100&width=700&url=https%3A%2F%2Fi.kym-cdn.com%2Fentries%2Ficons%2Ffacebook%2F000%2F028%2F021%2Fwork.jpg)

## Stack (aka Какой язык программирования и технологии использовать для реализации данного сервиса?)
The app stack is Python3.6.9 + python-telegram-bot + Flask + Celery. I this is a great combination because with python and flask
development of small apps an fast and ease. Using python-telegram-bot you do not need to care a lot about frontend. And Celery just 
naturally fits this, because t can be used to distribute posting task among many nodes.

## Interface (aka Какой будет пользовательский интерфейс and Опишите формат ответа)
I tried to keep user interface as simple as it can be. There is only to commands for bot /auth and /list, which are used for 
authenfication and for listing user accounts, respectively. To post you just need to send a message to bot. The result will
en error message or success message.

# Video
[click](https://yadi.sk/d/QjncgO0coqi_5Q)

# Service (aka Распишите по шагам весь процесс работы программы)

First you authorized with one of sites. For fb and ok.ru there is a callback which stores user tokens by there telegram id to mongodb.
For telegram auth, bot only checks that current user is admin in the channel and that bot is admin of channel.

Second you post. Bot creates celery task (one for each site in general case). Each task retrieve user tokens and group and then posts message.

If picture is send, bot fetches file id and url of image from telegram servers. To post iamge to facebook it send image url to api.
To post image to tg it sends image file id with message back to tg server. To post image to ok.ru it downloads image and sends it to ok.ru servers.

Finally, after eash task there is a callback task which sends success message to user.

# Usage (aka Как запустить вашу программу)

First you will need to obtain a domain and ssl certificates for it. Put them in ssl folder in app root. Self-signed certificates probably would not work. I signed mine with certbot.

After that you need to change credentials for fb and ok.ru apps in bot/config.json and auth_server/config.json to your credentials.

Obtain a telegram token via @BotFather and put in bot/config.json

Start redis:
```
docker run -p 6379:6379 redis
```

Start mongodb:

```
docker run -p 6379:6379 mongo
```

Set webhook to you bot:
```
python webhook.py
```

Start app
```
python start.py
```

Probably I will finish with docker-compose.yaml soon and it should starts with docker-compose up

