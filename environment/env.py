import os

path = os.environ.get("BOT_TOKEN")
with open(path, 'r') as file:
    TOKEN = file.read()

path = os.environ.get("TG_BOT_TOKEN")
with open(path, 'r') as file:
    TG_TOKEN = file.read()
