import discord
from discord import app_commands


class Translator(app_commands.Translator):
    def __init__(self, locale_dict=None):
        super().__init__()
        self.translate_not_found = set()
        if locale_dict:
            self.locale_dict = locale_dict
        else:
            self.locale_dict = {
                "_": {"en": "_",
                      "ru": "_"},

                "test_n": {"en": "test",
                           "ru": "тест"},

                "test_d": {"en": "Experemental commands",
                           "ru": "Эксперементальные комманды"},

                "help_n": {"en": "help",
                           "ru": "помощь"},

                "help_d": {"en": "Command for output all commands",
                           "ru": "Команда для вывода всех комманд и их использования"},

                "st_n": {"en": "slap-tangakk",
                         "ru": "шлепнуть-тангакка"},

                "st_d": {"en": "Command for slap Tangakk",
                         "ru": "Команда для отшлепывания Тангакка. А так же для тестирования комманд."},

                "cmd_disabled": {"en": "Sorry. This command disabled! :(",
                                 "ru": "Простите. Эта комманда отключена! :("},

                "cmd_adminonly": {"en": "Sorry. This command only for admins! :(",
                                  "ru": "Простите. Эта комманда только для администраторов! :("},

                "cmd_owneronly": {"en": "Sorry. This command only for owners! :(",
                                  "ru": "Простите. Эта комманда только для создателя! :("},

                "fun_n": {"en": "games",
                          "ru": "игры"},

                "fun_d": {"en": "Funny commands",
                          "ru": "Комманды для развлечения"},

                "bf_n": {"en": "brainfuck",
                         "ru": "брэйнфак"},

                "bf_d": {"en": "Brainfuck code reader",
                         "ru": "Запустить брэйнфак код"},

                "gol_n": {"en": "game-of-life",
                          "ru": "игра-в-жизнь"},

                "gol_d": {"en": "Launch Game of life simulation",
                          "ru": "Запустить симуляцию игры в жизнь"},

                "ttt_n": {"en": "tic-tac-toe",
                          "ru": "крестики-нолики"},

                "ttt_d": {"en": "Create Tic Tac Toe field",
                          "ru": "Создать поле для крестиков ноликов"},

                "input": {"en": "input",
                          "ru": "ввод"},

                "code": {"en": "code",
                         "ru": "код"},

                "size": {"en": "field-size",
                         "ru": "размер-поля"},

                "command": {"en": "command",
                            "ru": "комманда"},

                "…": {"en": "...",
                      "ru": "..."}
            }

        self.inverted_locale_dict = {}
        for translate_name, translate_dict in self.locale_dict.items():
            for translate in translate_dict.values():
                self.inverted_locale_dict[translate] = translate_name

    def soft_translate(self, string, locale):
        if self.locale_dict:
            result = self.locale_dict.get(string.message)  # Наименование, которое нужно перевести
            if not result:  # Если не удалось найти наименование в словаре перевода
                self.translate_not_found.add(string.message)
                return string.message

            if locale.value in ("ru", "ukrainian"):  # Проверка на руссоподобную принадлежность локализации дискорда
                lang = "ru"
            else:  # Если перевода не предусмотренно
                lang = "en"  # Стандартный язык перевода (он всегда должен быть в словаре)

            result = result.get(lang)  # Получение перевода из locale_dict
            if not result:
                return string.message

            if string.extras:  # Проверка format (значение, которое нужно вставить в текст)
                if format_dict := string.extras["extras"].get("format"):
                    result = result.format(**format_dict)

            return result
        else:
            self.translate_not_found.add(string.message)
            return string.message

    async def translate(self,
                        string,
                        locale,
                        context=None) -> str:  # Язык клиента дискорда

        return self.soft_translate(string, locale)


# Как использовать:
"from discord.app_commands import locale_str as _T"  # Импорт locale_str as _T
"@app_commands.command(name=_T('bonk_usr', translate_dict))"  # Дискорд сам активирует translate()

""" Структура словаря:
{"bonk_usr": {"en": "{user} have been bonked",
              "ru": "{user} был стукнут"}
}
"""
