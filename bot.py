from __future__ import unicode_literals

import collections
import functools
import os
import re

from telegram import Bot
from util import extract_token


class TelegramBot(object):

    def __init__(self, token=None):
        self.offset = None
        self.commands = {}
        self.authed_user = collections.defaultdict(set)

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
        not_matched = True
        if update.message.text == 'help':
            self.bot.sendMessage(update.message.chat_id, self.help())
            return

        for pattern, func in self.commands.items():
            text = update.message.text
            matched = pattern.match(text)

            if not matched:
                continue

            not_matched = False

            kwargs = matched.groupdict()
            reply = func(update=update, **kwargs)
            if reply:
                self.bot.sendMessage(update.message.chat_id, reply)

        if not_matched:
            self.bot.sendMessage(update.message.chat_id, 'Not matched')

    def command(self, pattern):
        """
        This function is a decorator to bind command.
        """
        def real_decorator(func):
            compiled_pattern = re.compile(pattern, re.U | re.I)
            self.commands[compiled_pattern] = func
            return func

        return real_decorator

    def restrict_user(self, category):
        def real_decorator(func):
            @functools.wraps(func)
            def wrapper(update, **kwargs):
                user_id = update.message.from_user.id
                if user_id in self.authed_user[category]:
                    return func(update, **kwargs)
                else:
                    return 'You are not authed.'

            return wrapper

        return real_decorator

    def help(self):
        return '\n'.join(map(lambda x: x.pattern, self.commands))
