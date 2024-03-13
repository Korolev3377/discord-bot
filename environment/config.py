from discord.ext.commands import when_mentioned_or
from discord import Intents


def CONFIG(): return  # Костыль, но да пофиг.


CONFIG.CMD_PREFIX = when_mentioned_or(">_", "!")
CONFIG.INTENTS = Intents.all()

CONFIG.DEFAULT_CFG = {
  "wealth_name": {  # Имена для валюты.
    "en": "coins",
    "ru": "монета"
  },
  "commands_to_declare": {  # True - что бы комманда была добавлена на сервер. False - для обратного эффекта.
    # Regular Commands
    "facts": False,  # Команда для вывода забавного факта.
    "facts_ignore": False,  # Комманада для пользователей, что бы они могли отключать реакцию на слово факт в чате.
    "facts_count": False,  # Комманда для подсчета количества фактов в базе данных.
    "cults": False,  # Комманда для подсчета культов на сервере [Cult of _] & etc.
    "rolldice": False,  # Комманда для кидания DnD кубика.
    # Fun Commands Group
    "fungrp": False,  # Тут много игровых комманд.
    # Wealth Commands
    "wealthgrp": False,  # Тут коммадны для управления финансами пользователей.
    "wealthopagrp": False  # Тут для администрирования фанансов сервера.
  },
  "fact_word_react": False  # Отключает реагирование на слово "факт" в чате.
}
