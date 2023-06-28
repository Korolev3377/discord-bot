import discord

from discord import app_commands
from discord.app_commands import locale_str as _ls

from translator.main import T
from environment.variable import *

_ = ""
EXAMPLE_CMD_ANSWER = "1"
FORMAT_STRING = "2"
FUNNYTN = "ftn"
FUNNYTD = "ftd"
ADMINGN = "opn"
ADMINGD = "opd"

_locale = {
    _: {EN: "",
        RU: ""},

    EXAMPLE_CMD_ANSWER: {EN: "Clownfish. {_}",
                         RU: "Рыба-клоун. {_}"},
    FORMAT_STRING: {EN: "Smile!",
                    RU: "Улыбнись!"},
    FUNNYTN: {EN: "funny-thing",
              RU: "забавный-ништяг"},
    FUNNYTD: {EN: "Idk. This command only for admins!",
              RU: "Чзх. Эта комманда только для одменов!"},
    ADMINGN: {EN: "opa",
              RU: "опа"},
    ADMINGD: {EN: "Admins thing.",
              RU: "Шняги для одменов."},
    "msg": {EN: "message",
            RU: "сообщение"},
    "chnl": {EN: "channel",
             RU: "канал"}
}

_T = T(locale_dict=_locale)

admingrp = create_group(ADMINGN, ADMINGD, _locale)
admingrp.default_permissions = discord.Permissions.none()


@admingrp.command(
    name=namedesc(FUNNYTN, _locale),
    description=namedesc(FUNNYTD, _locale),
    extras={IS_OWNER_ONLY: True}
)
@app_commands.rename(msg=namedesc("msg", _locale),
                     chnl=namedesc('chnl', _locale))
async def botsay(interaction: discord.Interaction, msg: str, chnl: str = None):
    await interaction.response.defer(thinking=True, ephemeral=True)
    if chnl:
        chnl = await interaction.client.fetch_channel(int(chnl))
    else:
        chnl = interaction.channel
    await interaction.followup.send("Бэклог - сделать управление сообщением.")
    await chnl.send(msg)


@botsay.autocomplete("chnl")
async def channel_autocomplite(interaction: discord.Interaction, current: str):
    ac = []
    for _ in interaction.client.get_all_channels():
        if _.name.startswith(current) and _.type.value in (0,):
            ac.append(app_commands.Choice(name=str(_.name), value=str(_.id)))
    return ac[:25]
