# ----- Python Standard Library ----- #
import logging
from random import random

# ----- Discord Python Library ----- #
import discord

import sqlite3

Log = logging.getLogger(__name__)

@discord.app_commands.command(
    name="esteem",
    description="Повысь свою самооценку"
)
async def command(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    conn: sqlite3.Connection = interaction.client.db
    user_data = conn.execute("SELECT * FROM global_esteem WHERE user_id = ?;", [interaction.user.id]).fetchone()
    add_esteem = round(random()*10)
    if add_esteem > 0:
        new_esteem = None
        if not user_data:
            conn.execute("INSERT INTO global_esteem VALUES (?, ?);", [interaction.user.id, add_esteem])
        else:
            new_esteem = user_data[1]+add_esteem
            conn.execute("UPDATE global_esteem SET user_id = ?, esteem = ? WHERE user_id = ?;", [user_data[0], new_esteem, interaction.user.id])
        conn.commit()
        await interaction.followup.send(f"Ваша самооценка повысилась на {add_esteem} и теперь составляет {new_esteem or add_esteem}")
    else:
        await interaction.followup.send("Ваша самооценка никак не повысилась")