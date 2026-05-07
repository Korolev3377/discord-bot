# ----- Python Standard Library ----- #
import logging

# ----- Discord Python Library ----- #
import discord

Log = logging.getLogger(__name__)

class DiscordClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tree = None

    async def setup_hook(self):
        self.tree = discord.app_commands.CommandTree(self)

    async def on_ready(self):
        Log.info(f"SatBot online\nName: {self.user.name}\nId: {self.user.id}")

    async def on_message(self, message):
        # ----- Игнорировать сообщения от себя и других ботов ----- #
        if message.author == self.user or message.author.bot:
            return