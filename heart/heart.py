import time
import http.client as httplib
import urllib
import json

from discord.ext import tasks
from environment import TG_TOKEN

loop_seconds = 1.0
cooling_rate = 1 / 1.2


class Heart:
  cycle = 0
  step_cycle = 1
  end_cycle = 0
  tg_offset = -1

  def __init__(self, bot):
    self.BOT = bot

  def time_to_cooldown(self, overload):
    return (overload / cooling_rate) * loop_seconds

  @tasks.loop(seconds=loop_seconds, reconnect=False)
  async def beat(self):
    host = 'api.telegram.org'
    url = '/bot' + TG_TOKEN + '/getUpdates'
    url = url.replace("\n", "")

    values = {"offset": self.tg_offset}

    headers = {
      'User-Agent': 'python',
      'Content-Type': 'application/x-www-form-urlencoded',
    }

    values = urllib.parse.urlencode(values)

    conn = httplib.HTTPSConnection(host)
    conn.request("GET", url, values, headers)
    response = conn.getresponse()
    res = json.loads(response.read())
    if res.get("ok"):
      try:
        for upd in res.get("result"):
          self.tg_offset = upd.get("update_id")+1
          if upd.get("message").get("text") == "/allo@MFBK_bot":
            url = '/bot' + TG_TOKEN + '/sendMessage'
            url = url.replace("\n", "")

            values = {"chat_id": upd.get("message").get("chat").get("id"),
                      "text": f"\"chat.id\" = {upd.get('message').get('chat').get('id')}\n\"message_thread_id\" = {upd.get('message').get('message_thread_id')}",
                      "reply_parameters": f'{{"message_id": {upd.get("message").get("message_id")}, "chat_id": {upd.get("message").get("chat").get("id")}}}',
                      "message_thread_id": upd.get("message").get("message_thread_id")}

            headers = {
              'User-Agent': 'python',
              'Content-Type': 'application/x-www-form-urlencoded',
            }

            values = urllib.parse.urlencode(values)
            conn = httplib.HTTPSConnection(host)
            conn.request("POST", url, values, headers)
          self.BOT.logger.info(["len(guilds)", len(self.BOT.guilds)])
          for g in self.BOT.guilds:
            self.BOT.logger.info(["g", g.id])
            status_d2t_0, _ = check_config(self.BOT.guilds_data, [str(g.id), "discord2tg_bridge", "enable_d2t"])
            status_d2t_1, _ = check_config(self.BOT.guilds_data, [str(g.id), "discord2tg_bridge", "enable_from_tg"])
            status_d2t_2, _ = check_config(self.BOT.guilds_data, [str(g.id), "discord2tg_bridge", "from_tg"])
            if status_d2t_0 and status_d2t_1 and status_d2t_2:
              if self.BOT.guilds_data.get(str(g.id)).get("discord2tg_bridge", "enable_d2t"):
                if self.BOT.guilds_data.get(str(g.id)).get("discord2tg_bridge", "enable_from_tg"):
                  mfilter = self.BOT.guilds_data.get(str(g.id)).get("discord2tg_bridge").get("from_tg").split(" ")
                  # mfilter == ["1090104010005050103:-1000202090908+2060", "1090104010005050103:-1000202090908+2060"]
                  if str(upd.get("message").get("chat").get("id")) == mf.split(":")[1].split("+")[0] and str(upd.get("message").get("message_thread_id")) == mf.split(":")[1].split("+")[1]:  # ["-1000202090908", "2060"]
                    discord_channel_id = mf.split(":")[0]  # "1090104010005050103"
                    self.BOT.logger.info(["discord_channel_id", discord_channel_id])
                    await self.BOT.get_channel(int(discord_channel_id)).send(f"{upd.get('message').get('from').get('username')}:\n{upd.get('message').get('text')}")
      except:
        pass

    for _id, _user in dict(self.BOT.antispam).items():
      if _user.get('overload') > 0:  # Пассивное охлаждение
        _user['overload'] -= cooling_rate
      if _user.get('overload') < 0:
        _user['overload'] = 0
      if _user.get('overload') > 100:
        _user['overloaded'] = True
        _user['overload'] = 100
      if _user.get('overload') == 0:
        self.BOT.antispam.pop(_id)
    self.cycle += cooling_rate / 10000
    if self.cycle >= self.end_cycle:
      self.end_cycle += self.step_cycle
      self.BOT.logger.info(f'Цикл: {round(self.cycle)}')

  @beat.before_loop
  async def before_loop(self):
    self.BOT.logger.info('Сердце запущено!')

  @beat.after_loop
  async def after_loop(self):
    self.BOT.logger.critical("Сердце остановлено!")
