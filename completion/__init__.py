import logging
from rich.console import Console
from rich.prompt import Prompt
from prompt_toolkit import PromptSession

from .completion import SlashCompleter, RolePrompt
from .domain import RoleValidator
from .selector import TemplateSelector


class ChatCompleter:

    _logger = logging.getLogger(__name__)
    
    def __init__(self):
        self.console = Console()
        self.multiline_session = PromptSession(
            completer=SlashCompleter(),
            complete_while_typing=True,
            multiline=True,
        )


    def complete_chat(self):
        session = PromptSession(
            completer=SlashCompleter(),
            complete_while_typing=True,
        )
        selector = TemplateSelector(
            prompt=RolePrompt(self.console, session),
            validator=RoleValidator(),
        )
        return selector.get_template()


    def get_multiline_input(self, prompt_msg: str) -> str:
        if prompt_msg:
            self.console.print(f"\n{prompt_msg}")
        lines = []
        lines.append(self.complete_chat())
        while True:
            try:
                line = Prompt.ask("", console=self.console, default="")
            except (KeyboardInterrupt, EOFError):
                raise
            if line.strip() == "":
                break

            lines.append(line)

        return "\n".join(lines).lstrip("\n")


