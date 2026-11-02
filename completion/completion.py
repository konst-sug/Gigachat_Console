from prompt_toolkit.completion import Completer, Completion
from rich.console import Console
from prompt_toolkit import PromptSession

from .domain import PROMPTS


class SlashCompleter(Completer):
    """Подсказки промпта появляются, 
        только если ввод начинается с '/'.
    """

    def __init__(self, commands: tuple[str, ...] = PROMPTS):
        self._commands = commands

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        if text.startswith("/"):
            for cmd in self._commands:
                if cmd.startswith(text):
                    yield Completion(cmd, start_position=-len(text))


class RolePrompt:
    def __init__(self, console: Console, session: PromptSession):
        self._console = console
        self._session = session

    def ask(self) -> str:
        try:
            return self._session.prompt("Введите промпт: ").strip()
        except (KeyboardInterrupt, EOFError):
            raise

    def error(self, message: str) -> None:
        self._console.print(f"[yellow]{message}[/yellow]")

    def confirm(self, role: str) -> None:
        # self._console.print(f"[green]Роль установлена: {role}[/green]")
        pass