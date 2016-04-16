import datetime
import logging
import os

import mpd
import redis

from bot import TelegramBot

TOKEN = os.environ.get("TELEGRAM_TOKEN")
bot = TelegramBot(TOKEN)

MPD_PASSWORD = os.environ.get("MPD_PASSWORD")
MPD_HOST = os.environ.get("MPD_HOST", "localhost")
MPD_PORT = os.environ.get("MPD_POST", 6600)

redisconn = redis.Redis()


def time_format(timestamp):
    dt = datetime.datetime.fromtimestamp(timestamp)
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def get_mpd_client():
    mpd_client = mpd.MPDClient()
    mpd_client.connect(MPD_HOST, MPD_PORT)
    if MPD_PASSWORD:
        mpd_client.password(MPD_PASSWORD)

    return mpd_client


@bot.command(r'^echo (?P<msg>.+)')
def echo(msg):
    return msg


@bot.command('wifi status')
def send_wifi_info():
    clients = [
        {
            'name': key,
            'strength': redisconn.hget(key, 'strength'),
            'since': time_format(float(redisconn.hget(key, 'since'))),
            'lastseen': time_format(float(redisconn.hget(key, 'lastseen'))),
        }
        for key in redisconn.keys('*:*')
    ]
    reply = 'since, last seen, strength, name\n' +  '\n'.join(
        '{0[since]}, {0[lastseen]}, {0[strength]}, {0[name]}'.format(client)
        for client in clients
    )

    return reply


@bot.command(r'play ('
             'music by (?P<artist>.+)|'
             'some (?P<genre>.+)|'
             '(?P<playlist>.+)'
             ')')
def play_music(artist=None, playlist=None, genre=None):
    mpd_client = get_mpd_client()
    if playlist:
        mpd_client.clear()
        mpd_client.load(playlist)
        mpd_client.play()
    elif artist:
        mpd_client.clear()
        mpd_client.searchadd('artist', artist)
        mpd_client.play()
    elif genre:
        mpd_client.clear()
        mpd_client.searchadd('genre', genre)
        mpd_client.play()

    mpd_client.close()
    return 'OK'


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    bot.loop()
