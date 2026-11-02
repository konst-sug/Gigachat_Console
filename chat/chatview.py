#chatview.py
import time
import logging
from datetime import datetime

from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text


class ChatUI:
    """Чат-интерфейс с ИИ-ассистентом в терминале.

    reply_fn: функция (history) -> str | Iterator[str]
    history = [{"role": "user"|"assistant", "content": str}, ...]
    Если возвращается генератор — включается режим стриминга.
    """

    _logger = logging.getLogger(__name__)

    def __init__(self, title="AI Ассистент", typewriter=True):
        self.console = Console()
        self.title = title
        self.typewriter = typewriter
        self.last_elapsed = 0.0
        self.turn = 0
    # ---------------- Отображение ----------------

    def welcome(self):
        self.console.print(Rule(title=f"🤖 [bold cyan]{self.title}[/bold cyan]"))
        self.console.print(
            "[dim]Команды: [bold]/clear[/bold] — очистить чат, "
            "[bold]/exit[/bold] — выход, "
            "[bold]/mode[/bold] — многострочный режим, "
            "[bold]/help[/bold] — справка[/dim]"
        )

    def show_user(self, text):
        self.turn += 1
        stamp = datetime.now().strftime("%H:%M")
        width = min(70, self.console.width - 2)
        panel = Panel(
            Text(text),
            title=f"[bold green]👤 Вы[/bold green] [dim]#{self.turn} · {stamp}[/dim]",
            title_align="left",
            border_style="green",
            width=width,
            padding=(0, 1),
        )
        self.console.print(panel, justify="right")  

    def show_assistant(self, text):
        panel = self._panel(text)
        if self.typewriter:
            shown = Text()
            with Live(shown, console=self.console, refresh_per_second=24) as live:
                for word in text.split(" "):
                    shown.append(word + " ")
                    live.update(shown)
                    time.sleep(0.02)
                live.update(panel)  # в конце текст «собирается» в панель
        else:
            self.console.print(panel)

    def _panel(self, text):
        stamp = datetime.now().strftime("%H:%M")
        title = (
            f"[bold blue]🤖 Ассистент[/bold blue] "
            f"[dim]· {stamp} · {self.last_elapsed:.1f} с[/dim]"
        )
        return Panel(
            Markdown(text),          # ответ рендерится как Markdown
            title=title,
            title_align="left",
            border_style="blue",
            padding=(0, 1),
        )

    def show_error(self, msg):
        self.console.print(
            Panel(Text(msg, style="bold red"), title="[red]❌ Ошибка[/red]",
                  border_style="red")
        )

   