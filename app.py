import logging
import os

import redis

from bot import TelegramBot

TOKEN = os.environ.get("TELEGRAM_TOKEN")
bot = TelegramBot(TOKEN)

redisconn = redis.Redis()

@bot.command('/echo')
def echo(*args):
    msg = ' '.join(args)
    return msg

@bot.command('/wifi')
def send_wifi_info(*args):
    clients = [
        {
            'name': key,
            'strength': redisconn.hget(key, 'strength'),
            'since': redisconn.hget(key, 'since'),
            'ttl': redisconn.ttl(key),
        }
        for key in redisconn.keys('*:*')
    ]
    reply = '\n'.join(
        '{0[name]} {0[strength]} {0[ttl]} {0[since]}'.format(client)
        for client in clients
    )

    return reply


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    bot.loop()
