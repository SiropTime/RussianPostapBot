from emoji import emojize
import aiogram.utils.markdown as md


TOKEN = "5218155011:AAF0GYeUQtMswyMXHhsULlrLHlnQrphEpA8"
ADMIN = 390919747

START_MSG = """
Здравствуй!
Этот бот предназначен для помощи в отыгрыше Словесной РПГ.
Сейчас нам нужно создать твоего персонажа, введи своё имя!
P.S. Если у тебя уже есть персонаж, введи команду /return
"""

MAIN_SKILLS_MSG_0 = md.text(
    md.text("Теперь необходимо распределить основные навыки вашего персонажа."),
    md.text("Для большего понимания ролевой системой можете ознакомиться со страницой на"),
    md.text(md.hlink("Notion","https://lucky-nutmeg-f9f.notion.site/4-0-4263657f00e34e7fbb9de3859dae6bd3"))
)

_PHYSICS = '''
:muscle: ***Физподготовка*** отвечает за силу, выносливость и ловкость вашего персонажа.
Чем больше её уровень, тем лучше справляется персонаж в физнагрузками.
Точнее он сможет переносить больший вес, меньше уставать, лучше сражаться в ближнем бою.
'''

_INTELLIGENCE = """
:brain: ***Интеллект*** отвечает за разговорные и научные навыки.
Чем больше его уровень, тем легче даются персонажу изучение литературы, уговоры персонажей.
Также перонаж становится смекалистее, имеет базовые знания во многих областях и лучше продумывает тактику боёв.
"""

_PERCEPTION = """
:eyes: ***Восприятие*** отвечает за аудиальное, визуальное и тактильное восприятие.
Чем больше его уровень, тем лучше персонаж взаимодействует с окружающей средой.
Он лучше видит, слышит, чувствует. Из-за этого повышаются точность в боях и разные навыки выживания.
"""

_CHARISMA = """
:bust_in_silhouette: ***Харизма*** отвечает за ваше природное бояние.
Чем больше её уровень, тем легче вам удаётся убедить людей, выцыганить скидку и т.д.
Очень важный навык для мирного решения конфликтов.
"""

MAIN_SKILLS_MSG_1 = md.text("Если объяснять вкратце, то есть четыре основных навыка:",
                            md.bold(emojize(':muscle: Физподготовка', use_aliases=True)),
                            md.bold(emojize(':brain: Интеллект', use_aliases=True)),
                            md.bold(emojize(':eyes: Восприятие', use_aliases=True)),
                            md.bold(emojize(':bust_in_silhouette: Харизма', use_aliases=True)),
                            "Все эти навыки имеют диапазон от 1 до 20 очков, определяющих уровень их прокачки",
                            sep="\n")

MAIN_SKILLS_MSG_2 = md.text(emojize(_PHYSICS, use_aliases=True))
MAIN_SKILLS_MSG_3 = md.text(emojize(_INTELLIGENCE, use_aliases=True))
MAIN_SKILLS_MSG_4 = md.text(emojize(_PERCEPTION, use_aliases=True))
MAIN_SKILLS_MSG_5 = md.text(emojize(_CHARISMA, use_aliases=True))

MAIN_SKILLS_MSGS = [MAIN_SKILLS_MSG_1, MAIN_SKILLS_MSG_2, MAIN_SKILLS_MSG_3,
                    MAIN_SKILLS_MSG_4, MAIN_SKILLS_MSG_5]
