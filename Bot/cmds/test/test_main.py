import discord
from discord import app_commands
from discord.ext import commands

from discord.app_commands import locale_str as _ls
from Bot.translator import Translator

locale = {"st?": {"en": "Slap Tangakk?",
                  "ru": "Дать пощечину тангакку?"},

          "st!": {"en": "*slapped Tangakk in the face*",
                  "ru": "*Дает пощечину Тангакку*"},

          "st_confirm": {"en": "{user} confirms the action",
                         "ru": "{user} подтверждает действие"},

          "st_cancel": {"en": "{user} cancels the action",
                        "ru": "{user} отменяет действие"},

          "st_idle": {"en": "No one has chosen anything... Well, that's okay...",
                      "ru": "Никто ничего не выбрал... Ну и ладно..."},

          "view_confirm": {"en": "Confirm",
                           "ru": "Подтвердить"},

          "view_cancel": {"en": "Cancel",
                          "ru": "Отменить"}
          }

T = Translator(locale_dict=locale)


class Test:
    def __init__(self, BOT):
        op_group = app_commands.Group(name="test_n", description="test_d")

        @op_group.command(name="st_n", description="st_d", extras={"disabled": True})
        async def slap_tangakk_cmd(interaction: discord.Interaction):
            await interaction.response.defer()

            lang = interaction.locale
            view = self.ConfirmView(lang=lang)

            await interaction.followup.send(T.soft_translate(string=_ls("st?"),
                                                             locale=lang),
                                            view=view)
            await view.wait()

            if view.status is True:
                await interaction.followup.send(T.soft_translate(
                    string=_ls("st_confirm", extras={"format": {"user": view.user}}),
                    locale=lang))
                await interaction.followup.send(T.soft_translate(string=_ls("st!"), locale=lang))
            elif view.status is False:
                await interaction.followup.send(T.soft_translate(
                    string=_ls("st_cancel", extras={"format": {"user": view.user}}),
                    locale=lang))
            else:
                await interaction.followup.send(T.soft_translate(string=_ls("st_idle"), locale=lang))

        BOT.tree.add_command(op_group)

    class ConfirmView(discord.ui.View):
        def __init__(self, lang):
            super().__init__()
            self.status = None
            self.user = None
            for child in self.children:
                child.label = T.soft_translate(string=_ls(child.label, extras={}), locale=lang)

        @discord.ui.button(style=discord.ButtonStyle.red, label="view_confirm")
        async def confirm(self, interaction, button):
            self.user = interaction.user
            for child in self.children:
                child.disabled = True
            button.label = '> ' + button.label + ' <'
            self.status = True
            await interaction.response.edit_message(view=self)
            self.stop()

        @discord.ui.button(style=discord.ButtonStyle.grey, label="view_cancel")
        async def cancel(self, interaction, button):
            self.user = interaction.user
            for child in self.children:
                child.disabled = True
            button.label = '> ' + button.label + ' <'
            self.status = False
            await interaction.response.edit_message(view=self)
            self.stop()
