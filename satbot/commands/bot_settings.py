# ----- Python Standard Library ----- #
import logging

# ----- Discord Python Library ----- #
import discord

Log = logging.getLogger(__name__)

@discord.app_commands.command(
    name="bot_settings",
    description="Настройка бота"
)
@discord.app_commands.checks.has_permissions(administrator=True)
async def command(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True, ephemeral=True)
    await interaction.followup.send("WIP")

@command.error
async def error(interaction: discord.Interaction, e: discord.app_commands.AppCommandError):
    await interaction.response.defer(thinking=True, ephemeral=True)
    if isinstance(e, discord.app_commands.MissingPermissions):
        await interaction.followup.send(f"Clearance insufficient")
    else:
        await interaction.followup.send(f"Unhandled error: {str(e)}")
