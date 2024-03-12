import discord.abc

from commands.admin import admingrp
from .regular import facts, cults, rolldice, facts_ignore, facts_count
from .fun import fungrp
from .wealth import wealthgrp, wealthopagrp
from .shop import shopgrp
from environment.variable import *

COMMANDS_DICT = {
    "facts": facts,
    "facts_ignore": facts_ignore,
    "facts_count": facts_count,
    "cults": cults,
    "rolldice": rolldice,
    "fungrp": fungrp,
    "wealthgrp": wealthgrp,
    "wealthopagrp": wealthopagrp
}


async def declare_commands(bot):
    commands_to_declare = []
    if bot.sys_var == 0:
        commands_to_declare = [admingrp, fungrp, facts, cults, rolldice, facts_ignore, facts_count, wealthgrp, wealthopagrp]
    elif bot.sys_var == 1:
        commands_to_declare = [cults, rolldice, facts_ignore, facts_count]
    for i in commands_to_declare:
        bot.tree.add_command(i)
    # Discord.py не поддерживает аргумент guilds, Так что код ниже пока закомменчен. Мда...
    """async for g in bot.fetch_guilds():  # Загрузка конфига комманд для каждого сервера.
        for k, v in COMMANDS_DICT.items():
            status, code = check_config(bot.guilds_data, [str(g.id), "commands_to_declare", k])
            codes = {
                0: f"Ошибка в конфигурации сервера \"{g.name}\": Нету конфигурации для сервера.",
                1: f"Ошибка в конфигурации сервера \"{g.name}\": Не найден \"commands_to_declare\" в конфигурации сервера.",
                2: f"Ошибка в конфигурации сервера \"{g.name}\": Отсутствует \"{k}\" в \"commands_to_declare\""
            }
            if status:
                if bot.guilds_data.get(str(g.id)).get("commands_to_declare").get(k) is not None:
                    bot.tree.add_command(v, guild=g)
            else:
                bot.logger.error(codes.get(code))"""
