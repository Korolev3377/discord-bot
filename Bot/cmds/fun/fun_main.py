from discord import app_commands
from .brainfuck import bf_cmd
from .tictactoe import tictactoe_cmd
from .gameoflife import gol_cmd

class FunGroup:
    def __init__(self, BOT):
        fun_group = app_commands.Group(name="fun_n", description="fun_d")
        fun_group.add_command(bf_cmd)
        fun_group.add_command(tictactoe_cmd)
        fun_group.add_command(gol_cmd)

        BOT.tree.add_command(fun_group)
