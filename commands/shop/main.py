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
             RU: "роль"},
    "cost": {EN: f" - Cost: {{val}}",
             RU: f" - Цена: {{val}}"},
    "free": {EN: "FREE",
             RU: "БЕСПЛАТНО"},
    "hex": {EN: f"{WEALTH_NAME.get('en')[1]}",
            RU: f"{WEALTH_NAME.get('kto_chto')[0]}(а/ов)"}
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
    uri = interaction.client.guilds_data.get(interaction.guild.id)["users_role_inv"]
    user_inv = uri.get(str(interaction.user.id))
    if not user_inv:
        uri[str(interaction.user.id)] = []
        user_inv = uri.get(str(interaction.user.id))
    user_inv.append(str(role))
    # Разбивка на страницы
    # View с страницами
    # Проверка на приобретенные роли
    # Получить и убрать роли
    # Инвентарь с ролями.

    await interaction.followup.send("D0ne", ephemeral=True)


@shopcmd.autocomplete("role")
async def channel_autocomplite(interaction: discord.Interaction, current: str):
    if rts := interaction.client.guilds_data.get(interaction.guild.id)["roles_to_sale"]:
        les = []
        for val, itm in sorted(rts.items()):
            if current in interaction.guild.get_role(int(val)).name:
                hexs = _T.stranslate(_ls("hex"), interaction.locale)
                if itm == 0:
                    itm = _T.stranslate(_ls("free"), interaction.locale)
                    hexs = ""
                les.append(app_commands.Choice(name="@" +
                                                    interaction.guild.get_role(int(val)).name +
                                                    _T.stranslate(
                                                        _ls(
                                                            'cost',
                                                            extras={FORMAT: {'val': itm}}), interaction.locale
                                                    ) + " " + hexs,
                                               value=str(interaction.guild.get_role(int(val)).id)))
        return les[:25]


class ShopView(discord.ui.View):
    roles = None

    def __init__(self, rts):
        super().__init__()
        self.roles_pages = [list(rts.keys())[r:r + 10] for r in range(0, len(list(rts.keys())), 10)]


@shopgrp.command(
    name=namedesc("inv_cmd_name", _locale),
    description=namedesc("inv_cmd_desc", _locale),
    extras={IS_OWNER_ONLY: True}
)
@app_commands.rename(role=namedesc("role", _locale))
async def invcmd(interaction: discord.Interaction, role: str):
    await interaction.response.defer(thinking=True, ephemeral=True)
    real_role = interaction.guild.get_role(int(role))
    if interaction.user.get_role(int(role)):
        await interaction.user.remove_roles(real_role)
    else:
        await interaction.user.add_roles(real_role)
    await interaction.followup.send("D0ne", ephemeral=True)


@invcmd.autocomplete("role")
async def channel_autocomplite(interaction: discord.Interaction, current: str):
    if rl := interaction.client.guilds_data.get(interaction.guild.id)["users_role_inv"].get(str(interaction.user.id)):
        les = []
        for val in sorted(rl):
            if current in interaction.guild.get_role(int(val)).name:
                les.append(app_commands.Choice(name="@" + interaction.guild.get_role(int(val)).name,
                                               value=val))
        return les[:25]
