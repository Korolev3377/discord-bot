import os, sys, asyncio, json
import discord
from discord.ext import commands

class Admin:
	def __init__(self, BOT):
		@BOT.hybrid_command(name="quit", description="Kick bot from this guild")
		async def quit(ctx):
			if ctx.permissions.administrator:
				await ctx.send("Are you sure want to Kick me?", view=self.View(ctx.author, "QUIT"))
			else:
				raise commands.CommandError("Error: User permissions")
		
		@BOT.hybrid_command(name="exit", description="Stop bot")
		async def exit(ctx):
			if await BOT.is_owner(ctx.author):
				await ctx.send("Are you sure want to Stop me?", view=self.View(ctx.author, "EXIT"))
			else:
				raise commands.CommandError("Error: User permissions")
	
		@BOT.tree.context_menu(name="Is owner")
		async def chk_owner(interaction: discord.Interaction, user: discord.Member):
			await interaction.response.send_message("User {} is owner - {}".format(user, await BOT.is_owner(user)), ephemeral=True)

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
		@BOT.hybrid_command(name='ttt', description='Play Tic Tac Toe')
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
				asyncio.wait(1)
				view.busy = False
		
class Battery:
	def __init__(self, BOT):
		def is_battery_and_owner(ctx):
			check = BOT.is_owner(user).predicate
			async def extended_check(ctx):
				if await check(ctx.author):
					raise commands.CommandError("Error: User permission")
				elif not os.popen("uname -o").read() == "Android\n":
					raise commands.CommandError("Error: Battery not detected")
				return True
			return commands.check(extended_check)
			
		@BOT.hybrid_group(name="battery", invoke_without_command=True)
		@commands.check(is_battery_and_owner)
		async def battery(ctx):
			pass
		
		@battery.command(name="check")
		async def chk(ctx):
			await ctx.defer()
			battery = json.loads(os.popen("termux-battery-status").read())
			details = f"""Battery status: {battery.get('status').lower().capitalize()}
Charge: {battery.get('percentage')}%
Temperature: {round(battery.get('temperature'))}°C"""
			await ctx.send(details, ephemeral=True)

		@battery.command(name="stop", enabled=False)
		async def stop(ctx):
			await ctx.defer()
			if BOT.task.is_running() is True:
				BOT.task.cancel()
				await BOT.change_presence(activity=None)
				await ctx.send("Checking battery stopped", ephemeral=True)
			else:
				await ctx.send("Already stopped", ephemeral=True)

		@battery.command(name="start", enabled=False)
		async def start(ctx):
			await ctx.defer()
			if BOT.task.is_running() is False:
				BOT.task.start()
				await ctx.send("Checking battery started", ephemeral=True)
			else:
				await ctx.send("Already started", ephemeral=True)