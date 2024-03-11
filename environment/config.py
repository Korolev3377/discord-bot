from discord.ext.commands import when_mentioned_or
from discord import Intents


def CONFIG(): return


CONFIG.CMD_PREFIX = when_mentioned_or(">_", "!")
CONFIG.INTENTS = Intents.all()

CONFIG.DEFAULT_CFG = {
  "wealth_name": {
    "en": "coins",
    "ru": "монета"
  }
}
