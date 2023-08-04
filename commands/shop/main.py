import discord

from discord import app_commands
from discord.app_commands import locale_str as _ls

from translator.main import T
from environment.variable import *

_locale = {
    "shop_group_name": {EN: "inventory",
                        RU: "инвентарь"},
    "shop_group_desc": {EN: "inventory",
                        RU: "инвентарь"},
    "shop_cmd_name": {EN: "buy-roles",
                      RU: "купить-роли"},
    "shop_cmd_desc": {EN: "Check roles to buy",
                      RU: "Просмотреть покупаемые роли"},
    "inv_cmd_name": {EN: "yours-roles",
                     RU: "ваши-роли"},
    "inv_cmd_desc": {EN: "Personal roles control",
                     RU: "Управление персональными ролями"},
    "role": {EN: "role",
             RU: "роль"}
}

_T = T(locale_dict=_locale)

shopgrp = create_group("shop_group_name", "shop_group_desc", _locale)


@shopgrp.command(
    name=namedesc("shop_cmd_name", _locale),
    description=namedesc("shop_cmd_desc", _locale),
    extras={IS_OWNER_ONLY: True}
)
@app_commands.rename(role=namedesc("role", _locale))
async def shopcmd(interaction: discord.Interaction, role: str):
    await interaction.response.defer(thinking=True, ephemeral=True)
    # Разбивка на страницы
    # View с страницами
    # Проверка на приобретенные роли
    # Получить и убрать роли
    # Инвентарь с ролями.

    await interaction.followup.send(shop_data, ephemeral=True)


@shopcmd.autocomplete("role")
async def channel_autocomplite(interaction: discord.Interaction, current: str):
    if rts := interaction.client.guilds_data.get(interaction.guild.id)["roles_to_sale"]:
        les = []
        for val, itm in rts.items():
            if current in interaction.guild.get_role(int(val)).name:
                les.append(app_commands.Choice(name=interaction.guild.get_role(int(val)).name,
                                               value=str(interaction.guild.get_role(int(val)).id)))
        return les[:25]


class ShopView(discord.ui.View):
    roles = None

    def __init__(self, rts):
        super().__init__()
        self.roles_pages = [list(rts.keys())[r:r + 10] for r in range(0, len(list(rts.keys())), 10)]
