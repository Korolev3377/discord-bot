import discord
import pickle as pik

from discord import app_commands
from discord import ui
from discord.app_commands import locale_str as _ls
from commands.database.dbcontrol import DB

from translator.main import T
from environment.variable import *

CHNL = "chnl"
MSG = "msg"
_ = ""
EXAMPLE_CMD_ANSWER = "1"
FORMAT_STRING = "2"
FUNNYTN = "ftn"
FUNNYTD = "ftd"
CRC = "crc"
ADMINGN = "opn"
ADMINGD = "opd"
CRCN = "crcn"
CRCD = "crcd"
ROLES = "roles"
CR = "cr"
CAPBUT = "t"
CBU = "cby"
CN = "cn"
CD = "cd"
CBY = "cby"

_locale: dict = {
    _: {EN: "",
        RU: ""},

    EXAMPLE_CMD_ANSWER: {EN: "Clownfish. {_}",
                         RU: "Рыба-клоун. {_}"},
    FORMAT_STRING: {EN: "Smile!",
                    RU: "Улыбнись!"},
    FUNNYTN: {EN: "funny-thing",
              RU: "забавный-ништяг"},
    FUNNYTD: {EN: "Idk. This command only for odmens!",
              RU: "Чзх. Эта комманда только для одменов!"},
    ADMINGN: {EN: "opa",
              RU: "опа"},
    ADMINGD: {EN: "Admins thing.",
              RU: "Шняги для одменов."},
    MSG: {EN: "message",
          RU: "сообщение"},
    CHNL: {EN: "channel",
           RU: "канал"},
    CN: {EN: "capsule",
         RU: "капсула"},
    CD: {EN: "This command only for admins!",
         RU: "Эта комманда только для админов!"},
    ROLES: {EN: "roles",
            RU: "роли"},
    CAPBUT: {EN: "CAPSULE",
             RU: "КАПСУЛА"},
    CBY: {EN: "{user}",
          RU: "{user}"}
}

_T = T(locale_dict=_locale)

admingrp = create_group(ADMINGN, ADMINGD, _locale)
admingrp.default_permissions = discord.Permissions.none()


@admingrp.command(
    name=namedesc(FUNNYTN, _locale),
    description=namedesc(FUNNYTD, _locale),
    extras={IS_OWNER_ONLY: True}
)
@app_commands.rename(msg=namedesc(MSG, _locale),
                     chnl=namedesc(CHNL, _locale))
async def botsay(interaction: discord.Interaction, msg: str, chnl: str = None):
    await interaction.response.defer(ephemeral=True, thinking=True)
    if not chnl:
        chnl = interaction.channel

    message = await chnl.send(msg)

    view = BotsayView()

    control_message = await interaction.user.send(content=message.jump_url, view=view)

    data = {
        "message_id": message.id,
        "content": message.content,
        "channel_id": message.channel.id
    }

    await DB.insert_message_data(message_id=control_message.id, message_data=pik.dumps(data))

    await interaction.delete_original_response()


class BotsayView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Edit", style=discord.ButtonStyle.blurple, custom_id="editmessage")
    async def editmessage(self, interaction: discord.Interaction, button: discord.ui.Button):
        i = await DB.select_message_data(interaction.message.id)
        if i:
            data = pik.loads(i[0])
            modal = self.EditModal(data.get("content"))
            await interaction.response.send_modal(modal)
            await modal.wait()
            data["content"] = modal.data
            await DB.update_message_data(interaction.message.id, pik.dumps(data))
            try:
                channel = await interaction.client.fetch_channel(data.get("channel_id"))
                message = await channel.fetch_message(data.get("message_id"))
                await message.edit(content=modal.data)
            except:
                await interaction.message.delete()
        else:
            await interaction.message.delete()

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.red, custom_id="deletemessage")
    async def deletemessage(self, interaction: discord.Interaction, button: discord.ui.Button):
        i = await DB.select_message_data(interaction.message.id)
        if i:
            data = pik.loads(i[0])
            await DB.delete_message_data(interaction.message.id)
            channel = await interaction.client.fetch_channel(data.get("channel_id"))
            message = await channel.fetch_message(data.get("message_id"))
            await message.delete()
        await interaction.message.delete()

    class EditModal(discord.ui.Modal):
        data = None

        def __init__(self, data):
            super().__init__(title="Message edit")
            self.add_item(ui.TextInput(label="Message content", default=data, style=discord.TextStyle.paragraph))

        async def on_submit(self, interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=True)
            self.data = self.children[0].value


@botsay.autocomplete(CHNL)
async def channel_autocomplite(interaction: discord.Interaction, current: str):
    return [app_commands.Choice(name=str(_.name), value=str(_.id))
            for _ in interaction.client.get_all_channels()
            if _.name.startswith(current) and _.type.value in (0,)][:25]


@admingrp.command(
    name=namedesc(CN, _locale),
    description=namedesc(CD, _locale),
    extras={IS_ADMIN_ONLY: False}
)
async def capsule(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True, ephemeral=False)
    view = CView(interaction.locale)
    message = await interaction.followup.send(view=view)
    message = await message.fetch()
    await DB.execute("INSERT INTO persistent (message_id, data) VALUES (?, ?);", (message.id, pik.dumps({})))


class CView(discord.ui.View):
    text = None
    user = None
    lang = None

    def __init__(self, lang=discord.Locale.american_english):
        super().__init__(timeout=None)
        self.add_item(self.Cbutton(lang))
        if lang:
            self.lang = lang

    class Cbutton(discord.ui.Button):
        text = None
        user = None

        def __init__(self, lang=None):
            super().__init__(label=_T.stranslate(_ls(CAPBUT), lang), style=discord.ButtonStyle.green, custom_id="crcb")

        async def callback(self, interaction: discord.Interaction):
            message = interaction.message
            data = pik.loads(await DB.execute("SELECT data FROM persistent WHERE message_id = ?;", (message.id,))[0])
            if data:
                self.text = data.get("text")
                self.user = data.get("user")

            _T.set_language(language=interaction.locale)

            modal = CapsuleModal(
                _T.stranslate(
                    _ls(CAPBUT)
                ),

                _T.stranslate(
                    _ls(
                        CBY,
                        extras={FORMAT: {"user": self.user}}
                    )
                ),

                self.text,

                _T.stranslate(
                    _ls("D0ne")
                )
            )

            await interaction.response.send_modal(modal)
            if not await modal.wait():
                await DB.execute("UPDATE persistent SET data = ? WHERE message_id = ?;",
                                 (pik.dumps({"text": modal.text, "user": interaction.user.name}), message.id))


class CapsuleModal(ui.Modal):
    lang = None
    text = None

    def __init__(self, title, label, oldtext, submit):
        super().__init__(title=title)
        self.add_item(ui.TextInput(label=label, default=oldtext, style=discord.TextStyle.paragraph))
        self.submit = submit

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        self.text = self.children[0].value
