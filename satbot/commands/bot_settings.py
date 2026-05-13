# ----- Python Standard Library ----- #
import logging

# ----- Discord Python Library ----- #
import discord

Log = logging.getLogger(__name__)

@discord.app_commands.command(
    name="bot_settings",
    description="Настройка бота"
)
async def configembedcmd(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True, ephemeral=True)
    await interaction.followup.send("WIP")