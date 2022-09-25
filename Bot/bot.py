import discord
from discord import Intents
from discord.ext import commands
from discord.app_commands import locale_str as _ls

from Bot.misc import Env, Config
from Bot.cmds import register_all_commands
from Bot.translator import Translator

def start_bot():
    class Bot(commands.Bot):
        def __init__(self):
            super().__init__(command_prefix=Config.CMD_PREFIX,
                             help_command=None,
                             strip_after_prefix=True,
                             intents=Config.INTENTS)

        async def setup_hook(self):
            self.tree.interaction_check = itr_check
            await self.tree.set_translator(Translator())
            await self.tree.sync()

    BOT = Bot()

    async def itr_check(interaction: discord.Interaction):
        if interaction.command.extras.get("disabled"):
            await interaction.response.send_message(BOT.tree.translator.soft_translate(_ls("cmd_disabled"), locale=interaction.locale), ephemeral=True)
            return False

        if not interaction.permissions.administrator and interaction.command.extras.get("admin_only"):
            if not await BOT.is_owner(interaction.user):
                await interaction.response.send_message(BOT.tree.translator.soft_translate(_ls("cmd_adminonly"), locale=interaction.locale), ephemeral=True)
                return False

        if not await BOT.is_owner(interaction.user) and interaction.command.extras.get("owner_only"):
            await interaction.response.send_message(BOT.tree.translator.soft_translate(_ls("cmd_owneronly"), locale=interaction.locale), ephemeral=True)
            return False
        return True

    @BOT.event
    async def on_ready():
        print(f"Name: {BOT.user}\nID: {BOT.user.id}")
        if translate_not_found := BOT.tree.translator.translate_not_found:
            print(f"Translate not found for {translate_not_found}")

    """@BOT.event
    async def on_member_join(member: discord.Member):
        await member.guild.system_channel.send("{user} joined this Guild".format(user=member.mention))

    @BOT.event
    async def on_member_remove(member: discord.Member):
        await member.guild.system_channel.send("{user} left this Guild".format(user=member.mention))"""

    register_all_commands(BOT)
    BOT.run(Env.TOKEN)
