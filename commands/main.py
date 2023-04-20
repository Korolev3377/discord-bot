from .regular.main import facts, cults, rolldice
from .enjoy.main import enjoy_grp


def declare_cmds(bot):
    for i in [facts, cults, rolldice, enjoy_grp]:
        bot.tree.add_command(i)
