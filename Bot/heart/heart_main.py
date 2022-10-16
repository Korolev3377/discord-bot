from discord.ext import tasks


class Heart:
    def __init__(self, BOT):
        self.BOT = BOT
        self.loop_seconds = 1.0
        self.cooling_rate = 0.1

    def time_to_cooldown(self):
        return (self.BOT.overload / self.cooling_rate) * self.loop_seconds

    @tasks.loop(seconds=self.loop_seconds)
    async def heartbeat(self):
        if self.BOT.overload > 0:  # Пассивное охлаждение
            self.BOT.overload -= self.cooling_rate

    @heartbeat.before_loop
    async def before_loop(self):
        print('Сердце запущено')
        print('\nКонец инициализации')
