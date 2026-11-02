from .config_logging import LOGGING_CONFIG
from .vars import help_md
import json
import os

import logging
import logging.config
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
logging.config.dictConfig(LOGGING_CONFIG)

G_CHAT_KEY = os.getenv("giga_chat_key")
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR")
WORK_DIR = os.getenv("WORK_DIR", "~/snake/work/")
TOKENS_FILE = os.getenv("TOKENS_FILE", "tokens.json")
PROMPTS_FILE = os.getenv("PROMPTS_FILE")
ALLOWED_ROLES = ("", "/admin", "/user", "/moderator", "/guest")

try:
    with open(PROMPTS_FILE, 'r', encoding='utf-8') as f:
            prompts = json.load(f)
except Exception as err:
            prompts = {}
            logger.error('Failed to read prompts_json file: %s', err)

PROMPTS = tuple(prompts.keys()) + ("",) if prompts else tuple("")