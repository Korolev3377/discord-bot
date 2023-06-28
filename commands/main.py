from .regular.main import facts, cults, rolldice
from .enjoy.main import enjoy_grp
from .database.main import wealthgrp
from .admin.main import admingrp

commands_to_declare = [facts, cults, rolldice, enjoy_grp, wealthgrp, admingrp]


def declare_cmds(bot):
    for i in commands_to_declare:
        bot.tree.add_command(i, guilds=bot.servers)
