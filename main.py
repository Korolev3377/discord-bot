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
		super().__init__(command_prefix=commands.when_mentioned_or(">_", "!"), help_command=None, strip_after_prefix=True, intents=discord.Intents.all())
		self.run_task = True
		
	@tasks.loop(minutes=1.0)
	async def CHK_BTR(self):
		if os.popen("uname -o").read() == "Android\n" and self.run_task:
			battery = json.loads(os.popen("termux-battery-status").read())
			
			details = f"Battery {battery.get('status').lower()}: {battery.get('percentage')}% {round(battery.get('temperature'))}°C"
			
			activity = discord.Game(name=details)
			await self.change_presence(activity=activity)
		else:
			self.run_task = False
			CHK_BTR.cancel()
				
	async def setup_hook(self):
		self.admin = cmds.Admin(self)
		self.games = cmds.Games(self)
		self.battery = cmds.Battery(self)
	
		await self.tree.sync()
		
	async def on_command_error(self, ctx, exception):
		await ctx.send(exception, ephemeral=True)

BOT = Bot()

@BOT.check
def is_guild(ctx):
	if ctx.guild is None:
		raise commands.CommandError("Error: Guild only command")
	return True
	
def check(msg):
	return msg == ctx.message

@BOT.event
async def on_ready():
	print(f"Name: {BOT.user}\nID: {BOT.user.id}")
	await BOT.CHK_BTR.start()
	
@BOT.event
async def on_member_join(member: discord.Member):
	await member.guild.system_channel.send("{user} joined this Guild".format(user=member.mention))
	
@BOT.event
async def on_member_remove(member: discord.Member):
	await member.guild.system_channel.send("{user} left this Guild".format(user=member.mention))

BOT.run(TOKEN)
