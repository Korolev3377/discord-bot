import discord
import pickle as pik
import json

from discord import app_commands
from discord import ui
from discord.app_commands import locale_str as _ls

import commands
import environment
from commands.database import DB

from translator.__init__ import T
from environment.variable import *

_locale: dict = {  # TODO добавить перевод на embed конфигуратор
  ADMIN_GRP_NAME: {EN: "opa",
                   RU: "опа"},
  ADMIN_GRP_DESC: {EN: "Admins thing",
                   RU: "Штуки для админов"},
  BOTSAY_CMD_NAME: {EN: "speak-for-bot",
                    RU: "говорить-за-бота"},
  BOTSAY_CMD_DESC: {EN: "Sends a message on behalf of the bot",
                    RU: "Отправляет сообщение от имени бота"},
  MSG: {EN: "message",
        RU: "сообщение"},
  CHNL: {EN: "channel",
         RU: "канал"},
  EDIT: {EN: "Edit",
         RU: "Редактировать"},
  DELETE: {EN: "Delete",
           RU: "Удалить"},
  MODAL_TITLE: {EN: "Message editor",
                RU: "Редактирования сообщения"},
  MODAL_TEXT_LABEL: {EN: "Message content",
                     RU: "Содержание сообщения"},
  SHOPADDROLE_CMD_NAME: {EN: "add-role-to-shop",
                         RU: "добавить-роль-в-магазин"},
  SHOPADDROLE_CMD_DESC: {EN: "Add role to shop",
                         RU: "Добавить роль в магазин"},
  ROLE: {EN: ROLE,
         RU: "роль"},
  COST: {EN: COST,
         RU: "стоимость"},
  STOCK: {EN: STOCK,
          RU: "количество"},
  VISIBLE: {EN: VISIBLE,
            RU: "видимость"},
  BOT_TERM_NAME: {EN: "shutdown-bot",
                  RU: "выключить-бота"},
  BOT_TERM_DESC: {EN: "Shutdwon bot",
                  RU: "Запустить процедуру отключения бота"},
  SHUTING_DOWN: {EN: "Shuting down...",
                 RU: "Прощай, жестокий мир..."},
  CFG_GET_CMD_NAME: {EN: "get-config-data",
                     RU: "получить-конфиг"},
  CFG_GET_CMD_DESC: {EN: "Returns configuration file.",
                     RU: "Просмотреть конфиг-фаил."},
  CFG_FOR_SERVER: {EN: "Here {new?}config file for server \"{serv_name}\":\n",
                   RU: "Вот {new?}конфигурация сервера \"{serv_name}\":\n"},
  CFG_LOAD_CMD_NAME: {EN: "load-config",
                      RU: "загрузить-конфиг"},
  CFG_LOAD_CMD_DESC: {EN: "Returns config load message in PM.",
                      RU: "Запускает загрузку нового конфига."},
  DETALS_IN_PM: {EN: "Details sent to PM.\n{msg_link}",
                 RU: "Детали отправлены в личку.\n{msg_link}"},
  GIMME_CONFIG: {
    EN: "Send the following message with the configuration file to change the server settings \"{serv_name}\".",
    RU: "Отправьте следующее сообщение с файлом конфигурации, чтобы изменить настройки сервера \"{serv_name}\"."},
  NEW: {EN: "**new** ",
        RU: "**новая** "},
  NO_FILE_DETECTED: {EN: "No file was detected in your message. Action canceled.",
                     RU: "В вашем сообщении не обнаружен файл. Действие отменено."},
  ASYNCIO_TIMEOUT_ERROR: {EN: "The waiting time has expired.",
                          RU: "Время ожидания истекло."},
  DEFAULT_CFG_GET_CMD_NAME: {EN: "default-config-data",
                             RU: "стандартный-конфиг"},
  DEFAULT_CFG_GET_CMD_DESC: {EN: "Returns default configuration file.",
                             RU: "Просмотреть стандартный конфиг-фаил."},
  DEFAULT_CFG_FOR_SERVER: {EN: "Here default config file:\n",
                           RU: "Вот стандартная конфигурация для серверов:\n"},
}

_T = T(locale_dict=_locale)

admingrp = create_group(ADMIN_GRP_NAME, ADMIN_GRP_DESC, _locale)
admingrp.default_permissions = discord.Permissions.none()


@admingrp.command(
  name=namedesc(BOTSAY_CMD_NAME, _locale),
  description=namedesc(BOTSAY_CMD_DESC, _locale),
  extras={IS_OWNER_ONLY: True}
)
@app_commands.rename(msg=namedesc(MSG, _locale),
                     chnl=namedesc(CHNL, _locale))
async def botsay(interaction: discord.Interaction, msg: str, chnl: str = None):
  await interaction.response.defer(ephemeral=True, thinking=True)
  _T.set_language(interaction.locale)
  if not chnl:
    chnl = interaction.channel
  else:
    chnl = interaction.client.get_channel(int(chnl))

  message = await chnl.send(msg)

  view = BotsayView(interaction.locale)

  control_message = await interaction.user.send(content=message.jump_url, view=view)

  data = {
    "message_id": message.id,
    "channel_id": message.channel.id,
    "content": message.content,
    "language": interaction.locale.value
  }


@admingrp.command(
  name=namedesc(BOT_TERM_NAME, _locale),
  description=namedesc(BOT_TERM_DESC, _locale)
)
async def bottermcmd(interaction: discord.Interaction):
  await interaction.response.defer(ephemeral=True, thinking=True)
  _T.set_language(language=interaction.locale)
  _T.set_string(string=_ls(SHUTING_DOWN))
  await interaction.followup.send(_T.stranslate())
  interaction.client.logger.critical(
    f"Пользователь {interaction.user.name} ({interaction.user.id}) запустил команду отключения бота!")
  await interaction.client.close()


class BotsayView(discord.ui.View):
  def __init__(self, locale=None):
    super().__init__(timeout=None)
    self.add_item(self.EditMessageButton(locale))
    self.add_item(self.DeleteMessageButton(locale))

  class EditMessageButton(discord.ui.Button):
    def __init__(self, locale=None):
      super().__init__(label=_T.stranslate(_ls(EDIT), locale), style=discord.ButtonStyle.blurple,
                       custom_id="editmessage")

    async def callback(self, interaction: discord.Interaction):
      i = await DB.select_message_data(interaction.message.id)
      if i:
        data = pik.loads(i[0])
        modal = self.EditModal(data.get("content"), data.get("language"))
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

    class EditModal(discord.ui.Modal):
      data = None

      def __init__(self, data, locale):
        _T.set_language(locale)
        super().__init__(title=_T.stranslate(_ls(MODAL_TITLE), locale))
        self.add_item(ui.TextInput(label=_T.stranslate(_ls(MODAL_TEXT_LABEL), locale), default=data,
                                   style=discord.TextStyle.paragraph))

      async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        self.data = self.children[0].value

  class DeleteMessageButton(discord.ui.Button):
    def __init__(self, locale=None):
      _T.set_language(locale)
      super().__init__(label=_T.stranslate(_ls(DELETE), locale), style=discord.ButtonStyle.red,
                       custom_id="deletemessage")

    async def callback(self, interaction: discord.Interaction):
      i = await DB.select_message_data(interaction.message.id)
      if i:
        data = pik.loads(i[0])
        await DB.delete_message_data(interaction.message.id)
        channel = await interaction.client.fetch_channel(data.get("channel_id"))
        message = await channel.fetch_message(data.get("message_id"))
        await message.delete()
      await interaction.message.delete()


@botsay.autocomplete(CHNL)
async def channel_autocomplite(interaction: discord.Interaction, current: str):
  return [app_commands.Choice(name=str(channel.name), value=str(channel.id))
          for channel in interaction.guild.channels
          if current in channel.name and channel.type.value in (0,)][:25]

@admingrp.command(
  name=namedesc("config_embed_cmd_name", _locale),
  description=namedesc("config_embed_cmd_desc", _locale)
)
async def configembedcmd(interaction: discord.Interaction):
  await interaction.response.defer(thinking=True, ephemeral=True)
  _T.set_language(language=interaction.locale)
  # _T.set_string(string=ls(EXAMPLE_CMD_ANSWER, {"_": _T.stranslate(st=_ls(FORMAT_STRING))}))
  # await interaction.followup.send(_T.stranslate())
  configview = ConfigView(interaction.client.guilds_data[str(interaction.guild_id)], interaction)
  embed = discord.Embed(title=_T.stranslate(st=_ls("bot_settings")), description=configview.menu_dict.get("info"))
  embed = configview.update_embed(embed)
  await interaction.followup.send(
    "Нажимайте аккуратнее. Подтверждения  `Вы уверены что хотите сделать то-то то-то?`  НЕ будет!",
    embed=embed,
    view=configview)


class ConfigView(discord.ui.View):
  def __init__(self, original_config_dict, interaction):
    super().__init__()
    self.page = 0
    self.selected = 0
    self.embed = None
    self.path_to_menu = []
    self.menu_dict = dict(original_config_dict)  # TODO сделать разделение на страницы тут
    self.interaction = interaction

    self.add_item(ConfigViraButton())
    self.add_item(ConfigMainaButton())
    self.add_item(ConfigEnterButton())
    self.add_item(ConfigBackButton())
    # self.add_item(ConfigPrevButton())
    # self.add_item(ConfigNextButton())
    self.add_item(ConfigCancelButton())
    self.add_item(ConfigSaveButton())
    self.add_item(ConfigRestoreButton())

  async def on_timeout(self):
    for child in self.children:
      child.disabled = True
    await self.interaction.edit_original_response(embed=self.update_embed(self.embed), view=self)
    self.stop()

  def update_embed(self, original_embed):
    embed = original_embed.copy()

    _T.set_language(language=self.interaction.locale)

    embed.clear_fields()
    if len(self.path_to_menu) == 0:
      embed.description = _T.stranslate(_ls("main_menu"))
    else:
      embed.description = self.path_to_menu[-1]

    i = 0

    selected_menu = dict(self.menu_dict)
    for path in self.path_to_menu:
      selected_menu = selected_menu.get(path)

    for k, v in selected_menu.items():
      embed_field_name = []
      if i == self.selected:
        embed_field_name.append("---> ")
      embed_field_name.append(_T.stranslate(st=_ls(k)))

      embed_field_value = []
      if type(v) is dict:
        embed_field_value.append("= " + _T.stranslate(st=_ls("menu")))
      elif type(v) is bool:
        embed_field_value.append("- " + [_T.stranslate(st=_ls(NO)), _T.stranslate(st=_ls(YES))][bool(v)])
      elif v is None or len(v) == 0:
        embed_field_value.append("- " + _T.stranslate(st=_ls("none")))
      else:
        embed_field_value.append("- `" + v + "`")
      embed.add_field(name="".join(embed_field_name), value="".join(embed_field_value), inline=False)
      i += 1
    self.embed = embed
    return embed


class ConfigViraButton(discord.ui.Button):
  def __init__(self):
    super().__init__(label="↑ Вира ↑", disabled=False, row=0, custom_id="vira")

  async def callback(self, interaction):
    if self.view.selected > 0:
      self.view.selected -= 1
    await interaction.response.edit_message(embed=self.view.update_embed(self.view.embed))


class ConfigMainaButton(discord.ui.Button):
  def __init__(self):
    super().__init__(label="↓ Майна ↓", disabled=False, row=0, custom_id="maina")

  async def callback(self, interaction):
    if self.view.selected < len(self.view.embed.fields) - 1:
      self.view.selected += 1
    await interaction.response.edit_message(embed=self.view.update_embed(self.view.embed))


class ConfigEnterButton(discord.ui.Button):
  def __init__(self):
    super().__init__(label="Ввод", disabled=False, style=discord.ButtonStyle.blurple, row=0, custom_id="enter")

  async def callback(self, interaction):
    selected_menu = dict(self.view.menu_dict)
    for path in self.view.path_to_menu:
      selected_menu = selected_menu.get(path)
    if type(selected_menu.get(list(selected_menu.keys())[self.view.selected])) is dict:
      self.view.path_to_menu.append(list(selected_menu.keys())[self.view.selected])
      self.view.selected = 0
      await interaction.response.edit_message(embed=self.view.update_embed(self.view.embed))
    elif type(selected_menu.get(list(selected_menu.keys())[self.view.selected])) is bool:
      keys = list(self.view.path_to_menu)
      keys.append(list(selected_menu.keys())[self.view.selected])
      new_value = not selected_menu.get(list(selected_menu.keys())[self.view.selected])
      edited_menu_dict = self.view.menu_dict

      for key in keys[:-1]:
        edited_menu_dict = edited_menu_dict[key]

      edited_menu_dict[keys[-1]] = new_value
      await interaction.response.edit_message(embed=self.view.update_embed(self.view.embed))
    elif type(selected_menu.get(list(selected_menu.keys())[self.view.selected])) is str:
      keys = list(self.view.path_to_menu)
      keys.append(list(selected_menu.keys())[self.view.selected])

      class TextEditModal(discord.ui.Modal):
        def __init__(self, view):
          super().__init__(title=_T.stranslate(_ls("modal_field_editing")))
          self.view = view
          self.add_item(discord.ui.TextInput(label=list(selected_menu.keys())[self.view.selected],
                                             default=list(selected_menu.values())[self.view.selected], required=False))

        async def on_submit(self, interaction):
          new_value = str(self.children[0])
          edited_menu_dict = self.view.menu_dict
          for key in keys[:-1]:
            edited_menu_dict = edited_menu_dict[key]
          edited_menu_dict[keys[-1]] = new_value
          await interaction.response.edit_message(embed=self.view.update_embed(self.view.embed))

      await interaction.response.send_modal(TextEditModal(self.view))


class ConfigBackButton(discord.ui.Button):
  def __init__(self):
    super().__init__(label="Назад", disabled=False, row=0, custom_id="back")

  async def callback(self, interaction):
    if len(self.view.path_to_menu) > 0:
      self.view.path_to_menu.pop(-1)
    self.view.selected = 0
    await interaction.response.edit_message(embed=self.view.update_embed(self.view.embed))


class ConfigPrevButton(discord.ui.Button):  # TODO перелистывания страниц
  def __init__(self):
    super().__init__(label="<<< Пред. страница", disabled=True, row=1, custom_id="prev")


class ConfigNextButton(discord.ui.Button):  # TODO перелистывание страниц
  def __init__(self):
    super().__init__(label="След. страница >>>", disabled=True, row=1, custom_id="next")


class ConfigCancelButton(discord.ui.Button):
  def __init__(self):
    super().__init__(label="Галя, у нас отмена", disabled=False, style=discord.ButtonStyle.red, row=2,
                     custom_id="cancel")

  async def callback(self, interaction):
    for child in self.view.children:
      child.disabled = True
    await interaction.response.edit_message(embed=self.view.update_embed(self.view.embed), view=self.view)
    self.view.stop()


class ConfigSaveButton(discord.ui.Button):
  def __init__(self):
    super().__init__(label="Спаси и сохрани", disabled=False, style=discord.ButtonStyle.green, row=2, custom_id="save")

  async def callback(self, interaction):
    for child in self.view.children:
      child.disabled = True
    await interaction.response.edit_message(embed=self.view.update_embed(self.view.embed), view=self.view)
    interaction.client.guilds_data[str(interaction.guild_id)] = self.view.menu_dict
    await DB.execute("UPDATE servers_config SET cfg_data = ? WHERE server_id = ?;",
                     (pik.dumps(self.view.menu_dict), str(interaction.guild_id)))
    self.view.stop()
    await commands.declare_commands(interaction.client)


class ConfigRestoreButton(discord.ui.Button):
  def __init__(self):
    super().__init__(label="Сбросить к заводским", disabled=True, row=2, custom_id="restore")
