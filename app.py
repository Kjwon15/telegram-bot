import logging
import os

import redis

from bot import TelegramBot

TOKEN = os.environ.get("TELEGRAM_TOKEN")
bot = TelegramBot(TOKEN)

redisconn = redis.Redis()

@bot.command(r'^echo (?P<msg>.+)')
def echo(msg):
    return msg

@bot.command('wifi status')
def send_wifi_info():
    clients = [
        {
            'name': key,
            'strength': redisconn.hget(key, 'strength'),
            'since': redisconn.hget(key, 'since'),
            'ttl': redisconn.ttl(key),
        }
        for key in redisconn.keys('*:*')
    ]
    reply = 'since, ttl, strength, name\n' +  '\n'.join(
        '{0[since]}, {0[ttl]}, {0[strength]}, {0[name]}'.format(client)
        for client in clients
    )

    return reply


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    bot.loop()
