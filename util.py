import re

pattern = re.compile(r'"(.+?)"|(\S+)', re.U | re.S)

def extract_token(message):
    tokens = message.split(' ', 1)
    if len(tokens) > 1:
        return [tokens[0]] + filter(lambda x: x and x.strip(), pattern.split(tokens[1]))
    else:
        return tokens
