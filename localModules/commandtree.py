# ----- Discord Python Library ----- #
import discord

# ----- Local Modules ----- #
import commands


class CommandTree(discord.app_commands.CommandTree):
    def __init__(self, commandlist, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for cmd in commandlist:
            self.add_command(commands.get(cmd))