import os
import json
import discord
import discord.ext.commands as commands
import discord.ext.tasks as tasks

TOKEN_PATH = os.environ.get("BOT_TOKEN")
TOKEN = None
MY_ID = 400989403482423296

with open(TOKEN_PATH, 'r') as file:
	TOKEN = file.read()

class quit_view(discord.ui.View):

	def __init__(self, user):
		super().__init__()
		self.user = user

	async def interaction_check(self, interaction):
		if interaction.type is discord.InteractionType.component:
			return interaction.user == self.user
		else:
			return False

	@discord.ui.button(style=discord.ButtonStyle.red, label="Confirm")
	async def confirm(self, ctx,  button):
		for child in self.children:
			child.disabled = True
		button.label = '> '+button.label+' <'
		await ctx.edit(content="Nanobuttons, son\nThey disables response on clicked by user\nYou can't kick me, Jack", view=self)
		self.stop()
		# await interaction.guild.leave()

	@discord.ui.button(style=discord.ButtonStyle.grey, label="Cancel")
	async def cancel(self, ctx, button):
		for child in self.children:
			child.disabled = True
		button.label = '> '+button.label+' <'
		await ctx.edit(content="Command cancelled", view=self)
		self.stop()

intents = discord.Intents.all()

class TicTacToeButton(discord.ui.Button['TicTacToe']):
    def __init__(self, x: int, y: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=' ', row=y)
        self.x = x
        self.y = y

    async def callback(self, interaction):
        global DEBUGUS
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

        if view.current_player == view.X and interaction.user == view.player_one and state not in (
                view.X, view.O):
            self.style = discord.ButtonStyle.red
            view.board[self.y][self.x] = view.X
            view.current_player = view.O
            if view.player_two:
                content = f"Tic Tac Toe: Waiting for {view.player_two.mention} :green_circle:"
            else:
                content = "Tic Tac Toe: Waiting for P2 :green_circle:"
        elif view.current_player == view.O and interaction.user == view.player_two and state not in (
                view.X, view.O):
            self.style = discord.ButtonStyle.green
            view.board[self.y][self.x] = view.O
            view.current_player = view.X
            if self.view.player_two:
                content = f"Tic Tac Toe: Waiting for {self.view.player_one.mention} :red_circle:"
            else:
                content = "Tic Tac Toe: Waiting for P1 :red_circle:"

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
                    content = f'Tic Tac Toe: Game over\nDraw between {self.view.player_one.mention} :red_circle: and {self.view.player_two.mention} :green_circle:!'

            for child in view.children:
                child.disabled = True

            view.stop()

        view.busy = False
        await interaction.edit_original_response(content=content, view=view)

class TicTacToe(discord.ui.View):
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
                self.add_item(TicTacToeButton(x, y))

    def check_board_winner(self):

        # Check vertical
        for across in self.board:
            value = sum(across)
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        for line in range(3):
            value = self.board[0][line] + self.board[1][line] + self.board[2][
                line]
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




class Bot(commands.Bot):
	def __init__(self, *, intents=intents):

		super().__init__(command_prefix=commands.when_mentioned_or(">_"), strip_after_prefix=True, intents=intents)

	async def on_command_error(self, ctx, exception):
		await ctx.send(exception)

	async def setup_hook(self):
		await bot.tree.sync()

bot = Bot()

def is_guild(ctx):
	if ctx.guild is None:
		raise commands.CommandError("Error: Guild only command")
	else:
		return True
bot.add_check(is_guild)

@tasks.loop(minutes=5.0)
async def check_battery():
	try:
		battery = json.loads(os.popen("termux-battery-status").read())
		details = f"Battery {battery.get('status').lower()}: {battery.get('percentage')}% {round(battery.get('temperature'))}°C"

		activity = discord.Game(name=details)

	except:
		check_battery.cancel()
		details = f"Battery: Not detected"
		activity = discord.Game(name=details)

	await bot.change_presence(activity=activity)

@bot.event
async def on_ready():
	print(f"Name: {bot.user}\nID: {bot.user.id}")
	await check_battery.start()



def is_battery_or_owner(bot, user):
	print(bot.owner_ids)
	if user.id != MY_ID:
		raise commands.CommandError("Error: User permission")
	elif os.system("termux-battery-status") != 0:
		raise commands.CommandError("Error: Battery not detected")
	return True

@bot.hybrid_command(name="check_battery", description="Return current battery status")
async def chk_btr(ctx):
	await ctx.defer()
	is_battery_or_owner(bot, ctx.author)
	battery = json.loads(os.popen("termux-battery-status").read())
	details = f"""Battery status: {battery.get('status').lower().capitalize()}
Charge: {battery.get('percentage')}%
Temperature: {round(battery.get('temperature'))}°C"""
	await ctx.send(details)

@bot.hybrid_command(name="stop_checking_battery", description="Cancel check_battery task")
async def stop_chk_btr(ctx):
	await ctx.defer()
	is_battery_or_owner(bot, ctx.author)
	if check_battery.is_running() is True:
		check_battery.cancel()
		await bot.change_presence(activity=None)
		await ctx.send("Checking battery stopped")
	else:
		await ctx.send("Already stopped")

@bot.hybrid_command(name="start_checking_battery", description="Starts check_battery task")
async def start_chk_btr(ctx):
	await ctx.defer()
	is_battery_or_owner(bot, ctx.author)
	if check_battery.is_running() is False:
		check_battery.start()
		await ctx.send("Checking battery started")
	else:
		await ctx.send("Already started")



@bot.hybrid_command(name='ttt', description='Play Tic Tac Toe')
async def ttt(ctx):
    await ctx.send(f'Tic Tac Toe: Waiting for P1 :red_circle:', view=TicTacToe())

@bot.hybrid_command(name="quit", description="Kick bot from this guild")
async def quit(ctx):
	if ctx.permissions.administrator:
		await ctx.send("Are you sure want to kick me?", view=quit_view(ctx.author))
	else:
		raise commands.CommandError("Error: User permissions")

@bot.tree.context_menu(name="Delete your interaction")
async def del_int(interaction, message: discord.Message):
    await interaction.response.defer(ephemeral=True, thinking=True)
    if message.interaction:
        if message.interaction.user == interaction.user:
            await message.delete()
            await interaction.followup.send("Deleted successfully", ephemeral=True)
        else:
            await interaction.followup.send("You can delete only the Interactions you have created", ephemeral=True)
    else:
        await interaction.followup.send("You can delete only the Interactions you have created", ephemeral=True)

bot.run(TOKEN)
