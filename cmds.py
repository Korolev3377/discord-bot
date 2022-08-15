import os, sys, asyncio, json
import discord
from discord.ext import commands
from bf import Brainfuck
BF = Brainfuck()

class Admin:
	def __init__(self, BOT):
		@BOT.group(name="admin", description="Admin's commands", hidden=True)
		async def admin(ctx):
			pass
				
		@admin.command(name="quit", description="Kick bot from this guild", hidden=True)
		async def quit(ctx):
			if ctx.permissions.administrator:
				await ctx.send("Are you sure want to Kick me?", view=self.View(ctx.author, "QUIT"))
			else:
				raise commands.CommandError("Error: User permissions")
		
		@admin.command(name="exit", aliases=["stop"], description="Stop bot", hidden=True)
		async def exit(ctx):
			if await BOT.is_owner(ctx.author):
				await ctx.send("Are you sure want to Stop me?", view=self.View(ctx.author, "EXIT"))
			else:
				raise commands.CommandError("Error: User permissions")
		
		@BOT.hybrid_command(name="bf", aliases=["brainfuck"], description="Execute brainfuck code", usage="bf <code> <input>")
		async def help(ctx, code: str, *, input: str = None):
			await ctx.send("`"+BF.run(code, input)+"`")
		
		def signatures(cmd_list):
			to_return = []
			for cmd in cmd_list:
				to_return.append("%s - %s" % (cmd.name, cmd.description or "..."))
			return "\n".join(to_return)
		
		def get_commands(group, non_hidden=True):
			return [cmd for cmd in group.commands if not cmd.hidden] if non_hidden else group.commands
		
		def get_help(cmd):
			desc = cmd.description
			usage = cmd.usage
			doc = cmd.help
			if type(cmd) is commands.Group or type(cmd) is commands.HybridGroup:
				parents = "\n".join([cmd.name for cmd in cmd.commands])
			else: parents = None
			help_doc = []
			if desc:
				help_doc.append("Description: "+desc)
			if usage:
				help_doc.append("Usage: "+usage)
			if doc:
				help_doc.append(doc)
			if parents:
				help_doc.append("Subcommands:\n"+parents)
			return "\n".join(help_doc)
		
		@BOT.hybrid_command(name="help", description="Help command", usage="help <command>")
		async def help(ctx, *, command=None):
			embed = discord.Embed(title="Help")
			cmds = get_commands(BOT)
			if not command:
				embed.add_field(name="Available commands:",
					value=signatures(cmds),
					inline=False)
				await ctx.send(embed=embed)
			else:
				sub = BOT
				for arg in command.split():
					sub = sub.get_command(arg)
					if not sub:
						raise commands.CommandError("Error: Command \"{}\" not found".format(arg))
				embed.add_field(name="Command \"%s\":" % (sub.qualified_name),
					value=get_help(sub),
					inline=False)
				await ctx.send(embed=embed)

	class View(discord.ui.View):
		def __init__(self, user, type):
			super().__init__()
			self.user = user
			self.type = type
	
		async def interaction_check(self, interaction):
			if interaction.type is discord.InteractionType.component:
				return interaction.user == self.user
			else:
				return False
		
		@discord.ui.button(style=discord.ButtonStyle.red, label="Confirm")
		async def confirm(self, interaction,  button):
			for child in self.children:
				child.disabled = True
			button.label = '> '+button.label+' <'
			if self.type == "QUIT":
				await interaction.response.edit_message(content="Nanobuttons, son\nThey disables response on clicked by user\nYou can't kick me, Jack", view=self)
				self.stop()
				# await interaction.guild.leave()
			elif self.type == "EXIT":
				await interaction.response.edit_message(content="Shutting down...", view=self)
				self.stop()
				sys.exit()

		@discord.ui.button(style=discord.ButtonStyle.grey, label="Cancel")
		async def cancel(self, interaction, button):
			for child in self.children:
				child.disabled = True
			button.label = '> '+button.label+' <'
			await interaction.response.edit_message(content="Command cancelled", view=self)
			self.stop()
			
class Games:	
	def __init__(self, BOT):
		@BOT.hybrid_command(name='tictactoe', aliases=["ttt"], description='Play Tic Tac Toe game')
		async def ttt(ctx):
			await ctx.send(f'Tic Tac Toe: Waiting for Player one :red_circle:', view=self.View())
			
	class View(discord.ui.View):
		busy = False
		player_one = None
		player_two = None
		X = -1
		O = 1
		Tie = 2

		def __init__(self):
			super().__init__()
			self.current_player = self.X
			self.board = [
				[0, 0, 0],
				[0, 0, 0],
				[0, 0, 0],
			]

			for x in range(3):
				for y in range(3):
					self.add_item(self.Button(x, y))

		def check_board_winner(self):

			# Check horizontal
			for across in self.board:
				value = sum(across)
				if value == 3:
					return self.O
				elif value == -3:
					return self.X

			# Check vertical
			for line in range(3):
				value = self.board[0][line] + self.board[1][line] + self.board[2][line]
				if value == 3:
					return self.O
				elif value == -3:
					return self.X

			# Check diagonals
			diag = self.board[0][2] + self.board[1][1] + self.board[2][0]
			if diag == 3:
				return self.O
			elif diag == -3:
				return self.X

			diag = self.board[0][0] + self.board[1][1] + self.board[2][2]
			if diag == 3:
				return self.O
			elif diag == -3:
				return self.X

			# Check Tie
			if all(i != 0 for row in self.board for i in row):
				return self.Tie

			return None
		
		class Button(discord.ui.Button):
			def __init__(self, x: int, y: int):
				super().__init__(style=discord.ButtonStyle.secondary, label=' ', row=y)
				self.x = x
				self.y = y

			async def callback(self, interaction):
				await interaction.response.defer()
				view = self.view
				state = view.board[self.y][self.x]
				content = interaction.message.content

				if view.busy:
					return
				view.busy = True

				if view.player_one is None:
					view.player_one = interaction.user
				elif view.player_two is None:
					view.player_two = interaction.user

				if view.current_player == view.X and interaction.user == view.player_one and state not in (view.X, view.O):
					self.style = discord.ButtonStyle.red
					view.board[self.y][self.x] = view.X
					view.current_player = view.O
					if view.player_two:
						content = f"Tic Tac Toe: Waiting for {view.player_two.mention} :green_circle:"
					else:
						content = "Tic Tac Toe: Waiting for Player two :green_circle:"
				elif view.current_player == view.O and interaction.user == view.player_two and state not in (view.X, view.O):
					self.style = discord.ButtonStyle.green
					view.board[self.y][self.x] = view.O
					view.current_player = view.X
					if self.view.player_two:
						content = f"Tic Tac Toe: Waiting for {self.view.player_one.mention} :red_circle:"
					else:
						content = "Tic Tac Toe: Waiting for Player one :red_circle:"

				winner = view.check_board_winner()
				if winner is not None:
					if view.player_one == view.player_two:
						content = "Tic Tac Toe: Game over"
					else:
						if winner == view.X:
							content = f'Tic Tac Toe: Game over\n{view.player_one.mention} :red_circle: Won!\n{view.player_two.mention} :green_circle: Loses!'
						elif winner == view.O:
							content = f'Tic Tac Toe: Game over\n{view.player_two.mention} :green_circle: Won!\n{view.player_one.mention} :red_circle: Loses!'
						else:
							content = f'Tic Tac Toe: Game over\nDraw between {self.view.player_one.mention} :red_circle: and :green_circle: {self.view.player_two.mention}!'

					for child in view.children:
						child.disabled = True

					view.stop()

				await interaction.edit_original_response(content=content, view=view)
				await asyncio.sleep(1)
				view.busy = False
		
class Battery:
	def __init__(self, BOT):			
		@BOT.group(name="battery", description="Battery's commands", hidden=True, invoke_without_command=True)
		async def battery(ctx):
			await ctx.defer()
			if not await BOT.is_owner(ctx.author):
				raise commands.CommandError("Error: User permission")
			elif not os.popen("uname -o").read() == "Android\n":
				raise commands.CommandError("Error: Battery not detected")
			await ctx.send("Enter a subcommand:\n{}".format("\n".join([cmd.name for cmd in ctx.command.commands])))
		
		@battery.command(name="check", description='Check current battery status')
		async def chk(ctx):
			await ctx.defer()
			if not await BOT.is_owner(ctx.author):
				raise commands.CommandError("Error: User permission")
			elif not os.popen("uname -o").read() == "Android\n":
				raise commands.CommandError("Error: Battery not detected")
			battery = json.loads(os.popen("termux-battery-status").read())
			details = f"""Battery status: {battery.get('status').lower().capitalize()}
Charge: {battery.get('percentage')}%
Temperature: {round(battery.get('temperature'))}°C"""
			await ctx.send(details, ephemeral=True)

		@battery.command(name="stop", description='Stop check battery task')
		async def stop(ctx):
			await ctx.defer()
			if not await BOT.is_owner(ctx.author):
				raise commands.CommandError("Error: User permission")
			elif not os.popen("uname -o").read() == "Android\n":
				raise commands.CommandError("Error: Battery not detected")
			if BOT.CHK_BTR.is_running() is True:
				BOT.run_task = False
				BOT.CHK_BTR.cancel()
				await BOT.change_presence(activity=None)
				await ctx.send("Checking battery stopped")
			else:
				await ctx.send("Already stopped")

		@battery.command(name="start", description='Start check battery task')
		async def start(ctx):
			await ctx.defer()
			if not await BOT.is_owner(ctx.author):
				raise commands.CommandError("Error: User permission")
			elif not os.popen("uname -o").read() == "Android\n":
				raise commands.CommandError("Error: Battery not detected")
			if BOT.CHK_BTR.is_running() is False:
				BOT.run_task = True
				BOT.CHK_BTR.start()
				await ctx.send("Checking battery started")
			else:
				await ctx.send("Already started")