from Bot.cmds.help import Help
from Bot.cmds.test import Test
from Bot.cmds.fun import FunGroup

def register_all_commands(BOT):
    Help(BOT)
    Test(BOT)
    FunGroup(BOT)
