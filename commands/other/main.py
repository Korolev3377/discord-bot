import discord
import re
import random
import collections as coll

# from environment import Facts
from discord import app_commands
from translator.main import T
from discord.app_commands import locale_str as _ls
from environment.variable import *


def capitalize_words(string):
    return str.join(' ', [word.capitalize() for word in string.split(' ')])


FACT_NAME = "fact_name"
FACT_DESC = "facts_desc"
NO_FACTS = "no_facts"

CULTS_NAME = "cults_name"
CULTS_DESC = "cults_desc"
TOP_CULT = "top_cults"
MEMBERS_COUNT = "members_count"
NO_CULTS = "no_cults"

ROLLDICE_NAME = "rd_name"
ROLLDICE_DESC = "rd_desc"
TOO_MANY_DICES = "tmd"
ZERO_OUTPUT = "zo"

_locale = {
    FACT_NAME: {EN: "fun-fact",
                RU: "забавный-факт"},
    FACT_DESC: {EN: "Let me gave u funny fackt.",
                RU: "Дай мне дать тебе забавный факт."},
    NO_FACTS: {EN: "Top {_} cults",
               RU: "Топ {_} культов"},

    CULTS_NAME: {EN: "top-cults",
                 RU: "топ-культов"},
    CULTS_DESC: {EN: "Check most popular cults on this server.",
                 RU: "Проверить наиболее популярные культы на этом сервере."},
    TOP_CULT: {EN: "Top {_} cults",
               RU: "Топ {_} культов"},
    MEMBERS_COUNT: {EN: "Members: {_}.",
                    RU: "Участников: {_}."},
    NO_CULTS: {EN: "Sorry, no cults on this server.",
               RU: "Извините, на этом сервере нет культов."},

    ROLLDICE_NAME: {EN: "roll-dice",
                    RU: "кинуть-кубики"},
    ROLLDICE_DESC: {EN: "Trhow some dises.",
                    RU: "Книуть немного кубеков."},
    TOO_MANY_DICES: {EN: "Too many dices. Maxium == 10.",
                     RU: "Слишком много кубиков. Максимум - 10."},
    ZERO_OUTPUT: {EN: "No info for output. Check input.",
                  RU: "Нет информации для вывода. Проверте ввод."}
}

_T = T(locale_dict=_locale)


# _F = Facts()


@app_commands.command(
    name=namedesc(FACT_NAME, _locale),
    description=namedesc(FACT_DESC, _locale),
    extras={IS_BROKEN: True}
)
async def facts(interaction: discord.Interaction):
    await interaction.response.defer()
    _T.set_locale(interaction.locale)
    if fact := await _F.read_facts(guild=interaction.guild, lang=lang):
        await interaction.followup.send(fact)
    else:
        await interaction.followup.send(_T.stranslate(_ls(NO_FACTS)))


@app_commands.command(
    name=namedesc(CULTS_NAME, _locale),
    description=namedesc(CULTS_DESC, _locale)
)
async def cults(interaction: discord.Interaction):
    await interaction.response.defer()
    _T.set_locale(interaction.locale)
    clist = []
    for member in interaction.guild.members:
        if member.nick:
            s = str.find(member.nick, '[') + 1
            e = str.find(member.nick, ']')
            if s != -1 and e != -1:
                clist.append(str.lower(member.nick[s:e]))
        else:
            s = str.find(member.name, '[') + 1
            e = str.find(member.name, ']')
            if s != -1 and e != -1:
                clist.append(str.lower(member.name[s:e]))
    cults_tuple = list(dict(coll.Counter(clist).most_common(10)).items())
    if len(cults_tuple) > 0:
        embed = discord.Embed(
            title=_T.stranslate(
                _ls(
                    TOP_CULT,
                    extras={
                        FORMAT: {"_": len(cults_tuple)}
                    }
                )
            )
        )
        for i, cult in enumerate(cults_tuple):
            cult_name, members_count = cult
            if members_count > 1:
                embed.add_field(
                    name=f"{i + 1}) {capitalize_words(cult_name)}",
                    value=_T.stranslate(
                        _ls(
                            MEMBERS_COUNT,
                            extras={
                                FORMAT: {"_": members_count}
                            }
                        )
                    ),
                    inline=False)
        if len(embed.fields) > 1:
            await interaction.followup.send(embed=embed)
            return
    await interaction.followup.send(_T.stranslate(_ls(NO_CULTS)))


@app_commands.command(
    name=namedesc(ROLLDICE_NAME, _locale),
    description=namedesc(ROLLDICE_DESC, _locale)
)
async def rolldice(interaction: discord.Interaction, *, dice_args: str):
    await interaction.response.defer()
    _T.set_locale(interaction.locale)
    results = {}
    dices = re.findall(r'\d*[dк-]\d+', dice_args)
    if len(dices) > 10:
        await interaction.followup.send(_T.stranslate(_ls(TOO_MANY_DICES)))
        return
    for dice in dices:
        count, value = re.split(r'[dк-]', dice)
        result = []
        if count != '':
            if not (0 < int(count) < 11) or not (1 < int(value) < 101):
                continue
            for i in range(1, int(count) + 1):
                result.append(random.randint(1, int(value)))
        else:
            if not (1 < int(value) < 101):
                continue
            result.append(random.randint(1, int(value)))
        results[f'{dice}'] = result
    tosay = ''
    gsum = 0
    for r in results.items():
        if len(r[1]) > 1:
            tosay += f'''{r[0]}: {' + '.join(map(str, r[1]))} = {sum(r[1])}
'''
            gsum += sum(r[1])
        else:
            tosay += f'''{r[0]}: {sum(r[1])}
'''
            gsum += sum(r[1])
    if len(results.items()) > 1:
        tosay += f'{gsum}'
    if tosay == '':
        await interaction.followup.send(_T.stranslate(_ls(ZERO_OUTPUT)))
        return
    await interaction.followup.send(tosay)
