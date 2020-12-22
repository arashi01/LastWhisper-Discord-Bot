import logging
from pathlib import Path as _Path

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)

_Path("./files").mkdir(parents=True, exist_ok=True)
file_handler = logging.FileHandler(filename='./files/bot.log', encoding='utf-8', mode='a+')
# noinspection SpellCheckingInspection,SpellCheckingInspection
file_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))

stdout_handler = logging.StreamHandler()
# noinspection SpellCheckingInspection
stdout_handler.setFormatter(logging.Formatter('%(levelname)s:%(name)s: %(message)s'))

logger.addHandler(file_handler)
logger.addHandler(stdout_handler)
