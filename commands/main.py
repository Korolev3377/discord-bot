from .other.main import facts, cults, rolldice


def declare_cmds(bot):
    for i in [facts, cults, rolldice]:
        bot.tree.add_command(i)
