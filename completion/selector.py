from .domain import RoleValidator, RoleValidationError, logging
from .completion import RolePrompt


class TemplateSelector:

    _logger = logging.getLogger(__name__)

    def __init__(self, prompt: RolePrompt, validator: RoleValidator):
        self._prompt = prompt
        self._validator = validator

    def get_template(self) -> str:
        while True:
            raw = self._prompt.ask()
            try:
                template = self._validator.validate(raw)
            except RoleValidationError as error:
                self._logger.error('Failed to validate prompt.', exc_info=True) 
                self._prompt.error(str(error))
                continue
            self._prompt.confirm(template)
            return template