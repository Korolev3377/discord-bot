import os
import discord
import discord.ext.commands as commands
    
TOKEN = os.environ.get("BOT_TOKEN")

class quit_view(discord.ui.View):
    def __init__(self, user):
        super().__init__()
        self.user = user

    @discord.ui.button(style=discord.ButtonStyle.red, label="Yes")
    async def confirm(self, interaction: discord.Interaction,
                      button: discord.ui.Button):
        if interaction.user == self.user:
            self.stop()
            await interaction.guild.leave()

    @discord.ui.button(style=discord.ButtonStyle.grey, label="No")
    async def cancel(self, interaction: discord.Interaction,
                     button: discord.ui.Button):
        if interaction.user == self.user:
            self.stop()

intents = discord.Intents.default()

class Bot(commands.Bot):
    def __init__(self, *, intents=intents):
        super().__init__(command_prefix=commands.when_mentioned_or("!"),
                         intents=intents)

    async def setup_hook(self):
        await bot.tree.sync()

bot = Bot()

@bot.event
async def on_ready():
    print(f"Name#tag: {bot.user}\nID: {bot.user.id}")

@bot.check
def is_guild(ctx):
	return ctx.guild is not None

def is_owner_or_admin(ctx):
	if ctx.author.id in bot.owner_ids or ctx.author.guild_permissions.administrator

@bot.tree.command(name="quit", description="Kick bot")
@commands.check(is_owner_or_admin)
async def quit(interaction: discord.Interaction):
	await interaction.response.send_message(
		"Are you sure want to kick me?",
		ephemeral=True,
		view=quit_view(interaction.user)
	)

@quit.error
async def check_errors(ctx, error):
	if isinstance(error, commands.errors.MissingPermissions):
		await ctx.send("Permission Error", ephemeral=True)
	
@bot.tree.context_menu(name="Delete your interaction")
async def del_int(interaction: discord.Interaction, message: discord.Message):
    await interaction.response.defer(ephemeral=True, thinking=True)
    if message.interaction:
        if message.interaction.user == interaction.user:
            await message.delete()
            await interaction.delete_original_response()
        else:
            await interaction.followup.send(
                "You can delete only the Interactions you have created",
                ephemeral=True)
    else:
        await interaction.followup.send(
            "You can delete only the Interactions you have created",
            ephemeral=True)


bot.run(TOKEN)
