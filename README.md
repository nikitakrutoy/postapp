# postapp
Telegram bot for posting to Facebook, Odnoklassniki and Telegram Channels. Bot can send posts with one image or text or both to all or specified list of authorized pages.
Working copy of of bot should be [here](https://t.me/postapp_bot) but i do not guarantee that because i have not finished with docker images of the bot and it may fall and do not restart.

If you are interested please checkout [version](https://github.com/nikitakrutoy/postapp-latest) of the app with changes that i made after deadline. This version of the app can be started with *docker-compose up* сommand.

# Backstory (aka Проектирование сервиса)
I decided to make telegram bot beacause i was limitied in time and havent touched Vue.js for a long time. 
Therefore i decided it will be much more productive if i concentrate mainly on backend part of the app. This was a mistake. 
The first api that I started with was VK, and it took me a lot of time to found out that it is actually really hard to 
create posts from server side with server side authorization, only client side is possible. One of the tricks to do it is to imitate client side authorization 
on server side, but that would require user to trust server his login and password, and this is not a solution. That is how i ended
with a strange combination of Facebook and OK.ru. I added Telegram Channels because I was afraid that ok.ru api team would not give my app permisions or give them after deadline. 

To sum up i think the decision to develop app without web frontend was wrong, because turns out that it is much easier to work with authorization and APIs from client side then from server side.

![alt text](https://wompampsupport.azureedge.net/fetchimage?siteId=7575&v=2&jpgQuality=100&width=700&url=https%3A%2F%2Fi.kym-cdn.com%2Fentries%2Ficons%2Ffacebook%2F000%2F028%2F021%2Fwork.jpg)

Also I want to notice that it did not took 4 hours to code this app. I guess it could take 4 hours only if you previously done identical app and you are only rewriting it.

## Stack (aka Какой язык программирования и технологии использовать для реализации данного сервиса?)
The app stack is Python3.6.9 + python-telegram-bot + Flask + Celery. I think this is a great combination: 
- With python and flask development of small apps is fast and easy
- Using python-telegram-bot you do not need to care a lot about frontend
- And Celery just naturally fits this app, because it can be used to distribute posting task among many nodes.

## Interface (aka Какой будет пользовательский интерфейс and Опишите формат ответа)
I tried to keep user interface as simple as it can be. There is only two commands, which can be used with bot: `/auth` and `/list`, which are used for 
authenfication and for listing user accounts, respectively. To post you just need to send a message to bot. The result will
be en error message or success message.

User can use special commands at the end of the message:
- `&pages* list of <site:user_id:page_id> separated by space`. Posts to specified pages. If page_id is missing, message will be posted to all user pages. If only site is passed, message will be posted to all pages of all authorized users for this site. For tg there is no users, so the syntax is different: `tg:@channel_id`.
- `*&eta* number`. To post message after eta seconds.

Example:
```
Hello world!
&pages fb:1234:777 ok:420 tg
```

The message will be posted to facebook page 777 of 1234 user, to all ok.ru pages of 420 user, and to all tg channels.

To see ids of your authorized pages and users `/list` command can be used.

# Video
[click](https://yadi.sk/d/QjncgO0coqi_5Q)

# Service (aka Распишите по шагам весь процесс работы программы)

First you authorize into one of the sites. For fb and ok.ru there is a callback which stores user tokens by there telegram id to mongodb.
For telegram auth, user passes channel id and bot only checks that current user is admin in that channel and that bot is admin of it.

Second you post. Bot creates celery task (one for each site in general case and one for each page if you use *&pages* syntax). Each task retrieves user and page tokens and then posts message.

If picture is send, bot fetches file id and url of image from telegram servers. To post image to facebook it sends image url to api.
To post image to tg it sends image file id with message text back to tg server. To post image to ok.ru it downloads image and sends it to ok.ru servers.

Finally, after ecsh task there is a callback task which sends success message to user.

# Usage (aka Как запустить вашу программу)

First you will need to obtain a domain, ssl certificate and key for the domain. Put them in ssl folder in app root name them fullchain.pem and key.pem. Self-signed certificates probably would not work. I signed mine with certbot.

After that you need to change credentials for fb and ok.ru apps in bot/config.json and auth_server/config.json to your credentials.

Obtain a telegram token via @BotFather and put in bot/config.json

Start redis:
```
docker run -p 6379:6379 redis
```

Start mongodb:

```
docker run -p 27017:27017 mongo
```
Install dependencies:
```
pip install -r requeirements.txt
```

Set webhook to your bot:
```
python webhook.py
```

Start celery
```
celery -A bot.tasks.app worker
```

Start app
```
python start.py
```

Probably I will finish with docker-compose.yaml soon and it should starts with docker-compose up



