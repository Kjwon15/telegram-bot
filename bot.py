from __future__ import unicode_literals

import os

from telegram import Bot
from util import extract_token


class TelegramBot(object):

    def __init__(self, token=None):
        self.offset = None
        self.commands = {}
        if token:
            self.bot = Bot(token)

    def set_token(self, token):
        self.bot = Bot(token)

    def loop(self):
        while 1:
            updates = self.bot.getUpdates(offset=self.offset, timeout=10)
            for update in updates:
                self.run_command(update)

            if updates:
                self.offset = updates[-1].update_id + 1

    def run_command(self, update):
        tokens = extract_token(update.message.text)
        cmd = tokens[0]
        args = tokens[1:]

        if cmd in self.commands:
            reply = self.commands[cmd](*args)
            self.bot.sendMessage(update.message.chat_id, reply)
        else:
            pass

    def command(self, funcname):
        """
        This function is a decorator to bind command.
        """
        def real_decorator(func):
            self.commands[funcname] = func
            return func

        return real_decorator
