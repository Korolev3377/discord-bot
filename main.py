import os, json
import discord
from discord.ext import commands, tasks

import cmds

TOKEN_PATH = os.environ.get("BOT_TOKEN")
TOKEN = None

with open(TOKEN_PATH, 'r') as file:
	TOKEN = file.read()

class Bot(commands.Bot):
	def __init__(self):
		super().__init__(command_prefix=commands.when_mentioned_or(">_"), strip_after_prefix=True, intents=discord.Intents.all())
		
		@tasks.loop(minutes=1.0)
		async def CHK_BTR():
			if os.popen("uname -o").read() == "Android\n":
				battery = json.loads(os.popen("termux-battery-status").read())
				
				details = f"Battery {battery.get('status').lower()}: {battery.get('percentage')}% {round(battery.get('temperature'))}°C"
				
				activity = discord.Game(name=details)
				await self.change_presence(activity=activity)
			else:
				CHK_BTR.cancel()
		
		self.task = CHK_BTR
		self.admin = cmds.Admin(self)
		self.games = cmds.Games(self)
		self.battery = cmds.Battery(self)
		
	async def on_command_error(self, ctx, exception):
		await ctx.send(exception, ephemeral=True)

BOT = Bot()

@BOT.check
def is_guild(ctx):
	if ctx.guild is None:
		raise commands.CommandError("Error: Guild only command")
	else:
		return True

@BOT.event
async def on_ready():
	print(f"Name: {BOT.user}\nID: {BOT.user.id}")
	await BOT.tree.sync()
	await BOT.task.start()
	
@BOT.event
async def on_member_join(member: discord.Member):
	await member.guild.system_channel.send("{user} joined this Guild".format(user=member.mention))
	
@BOT.event
async def on_member_remove(member: discord.Member):
	await member.guild.system_channel.send("{user} left this Guild".format(user=member.mention))

BOT.run(TOKEN)
