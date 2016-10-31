import datetime
import logging
import os

import mpd
import redis
import requests

from bot import TelegramBot

TOKEN = os.environ.get("TELEGRAM_TOKEN")
bot = TelegramBot(TOKEN)

MPD_PASSWORD = os.environ.get("MPD_PASSWORD")
MPD_HOST = os.environ.get("MPD_HOST", "localhost")
MPD_PORT = os.environ.get("MPD_POST", 6600)

YEELIGHT_BASE_URL=os.environ.get("YEELIGHT_BASE_URL")

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
def echo(update, msg):
    return msg


@bot.command('wifi status')
@bot.restrict_user('wifi')
def send_wifi_info(update):
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
@bot.restrict_user('music')
def play_music(update, artist=None, playlist=None, genre=None):
    mpd_client = get_mpd_client()
    try:
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
    except Exception as e:
        return str(e)
    else:
        mpd_client.close()
        return 'OK'


@bot.command(r'light (?P<switch>off|on)')
@bot.command(r'turn (?P<switch>on|off) (the )?light(?: in (?P<minutes>\d+) minutes?)?')
@bot.restrict_user('light')
def light_switch(update, switch=None, minutes=None):
    try:
        if switch == 'off' and minutes:
            resp = requests.post(
                '{}/sleep'.format(YEELIGHT_BASE_URL),
                {'minutes': minutes})
        else:
            resp = requests.post(
                '{}/switch'.format(YEELIGHT_BASE_URL),
                {'switch': switch})
        return resp.text
    except Exception as e:
        return str(e)


@bot.command(r'(?P<color>\w+) color light')
@bot.restrict_user('light')
def light_color(update, color=None):
    try:
        resp = requests.post(
            '{}/light'.format(YEELIGHT_BASE_URL),
            {'color': color})
        return resp.text
    except Exception as e:
        return str(e)


@bot.command(r'light brightness (?P<brightness>\d+)')
@bot.restrict_user('light')
def light_brightness(update, brightness=0):
    try:
        resp = requests.post(
            '{}/light'.format(YEELIGHT_BASE_URL),
            {'brightness': brightness})
        return resp.text
    except Exception as e:
        return str(e)


@bot.command(r'light warm (?P<warm>\d+)')
@bot.restrict_user('light')
def light_warm(update, warm=0):
    try:
        warm = float(warm) / 100
        resp = requests.post(
            '{}/light'.format(YEELIGHT_BASE_URL),
            {'warm': warm})
        return resp.text
    except Exception as e:
        return str(e)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    bot.loop()
