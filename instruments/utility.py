import logging
import sys

from emoji import emojize
import aiogram.utils.markdown as md


TOKEN = "TOKEN"
ADMIN = 390919747

levels = [
        50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000,
        2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800,
        3900, 4000
]

logger = logging.getLogger(__name__)

handler = logging.StreamHandler(stream=sys.stdout)
logging.basicConfig(format='[%(asctime)s %(levelname)s]:%(message)s', handlers=[handler], level=logging.INFO)


START_MSG = """
Здравствуй!
Этот бот предназначен для помощи в отыгрыше Словесной РПГ.
Сейчас нам нужно создать твоего персонажа, введи своё имя!
P.S. Если у тебя уже есть персонаж, введи команду /return
"""

MAIN_SKILLS_MSG_0 = md.text(
    md.text("Теперь необходимо распределить основные навыки вашего персонажа."),
    md.text("Для большего понимания ролевой системой можете ознакомиться со страницой на"),
    md.text(md.hlink("Notion", "https://lucky-nutmeg-f9f.notion.site/4-0-4263657f00e34e7fbb9de3859dae6bd3"))
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
                            "Все эти навыки имеют диапазон от 1 до 20 очков, определяющих уровень их прокачки.",
                            md.text("Запомните, что сумма всех навыков должна ", md.bold("не превышать 45"),
                                    "но и должна быть ", md.bold("не меньше 4")),
                            sep="\n")

MAIN_SKILLS_MSG_2 = md.text(emojize(_PHYSICS, use_aliases=True))
MAIN_SKILLS_MSG_3 = md.text(emojize(_INTELLIGENCE, use_aliases=True))
MAIN_SKILLS_MSG_4 = md.text(emojize(_PERCEPTION, use_aliases=True))
MAIN_SKILLS_MSG_5 = md.text(emojize(_CHARISMA, use_aliases=True))

MAIN_SKILLS_MSGS = [MAIN_SKILLS_MSG_1, MAIN_SKILLS_MSG_2, MAIN_SKILLS_MSG_3,
                    MAIN_SKILLS_MSG_4, MAIN_SKILLS_MSG_5]

MASTER_MESSAGE = md.text(md.bold(emojize(":mortar_board: ***Меню гейм мастера***", use_aliases=True)),
                         "Для выполнения любых действий со стороны гейммастера используйте данный синтаксис:",
                         md.code("!к [название_команды] [аргументы команды]"),
                         md.text("Аргументами команды может быть всё, что угодно, смотрите"), md.hlink("пособие", ""),
                         sep="\n")

MENU_BUTTONS = [
                emojize(":clipboard: Профиль", use_aliases=True),
                emojize(":earth_asia: Местоположение", use_aliases=True),
                emojize(":email: Отправить текст отыгрыша", use_aliases=True),
                emojize(":scroll: Журнал", use_aliases=True),
                emojize(":turtle: Бесстиарий", use_aliases=True)
                ]

PROFILE_BUTTONS = [emojize(":floppy_disk: Основные навыки", use_aliases=True),
                   emojize(":game_die: Дополнительные навыки", use_aliases=True),
                   emojize(":red_circle: Состояние", use_aliases=True),
                   emojize(":handbag: Инвентарь", use_aliases=True),
                   emojize(":leftwards_arrow_with_hook: Обратно в меню", use_aliases=True)]

MASTER_BUTTONS = [
    emojize(":bar_chart: Список холопов", use_aliases=True),
    emojize(":scroll: Журнал", use_aliases=True),
    emojize(":mega: Поорать", use_aliases=True),
    emojize(":city_sunset: Покалякать в журнал", use_aliases=True),
    emojize(":turtle: Бесстиарий", use_aliases=True)
]
