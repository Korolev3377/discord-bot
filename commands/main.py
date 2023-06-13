from .regular.main import facts, cults, rolldice
from .enjoy.main import enjoy_grp
from .database.main import wealthgrp

commands_to_declare = [facts, cults, rolldice, enjoy_grp, wealthgrp]
# commands_to_declare = [cults]


def declare_cmds(bot):
    for i in commands_to_declare:
        bot.tree.add_command(i)
