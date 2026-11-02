from config import PROMPTS, prompts
import logging


class RoleValidationError(ValueError):
    pass


class RoleValidator:
    """Правила валидации промпта. Тестируется без терминала."""
    _logger = logging.getLogger(__name__)

    def __init__(self, allowed: tuple[str, ...] = PROMPTS):
        self._allowed = allowed

    def validate(self, raw: str) -> str:
        role = raw.strip()
        if role not in self._allowed:
            self._logger.error('Failed to prompt.', exc_info=True) 
            raise RoleValidationError(
                f"Неизвестный промпт: {role}. Доступно: {', '.join(self._allowed)}"
            )
        result = prompts[role].replace("\n", "") if role else ""
        return result