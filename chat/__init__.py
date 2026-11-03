import time
import logging

from rich.prompt import Prompt
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from .chatview import ChatUI, Console, Text, Live, Rule, Markdown, Panel,datetime
from .settings_reader import SettingsReader
from .functions_line import FuncChoicer
from .prompt_reader import CommandParser
from .helpers import ChatHelper
from completion import ChatCompleter
from utils import TokenUsageWatcher
from config import DOWNLOAD_DIR, TOKENS_FILE, help_md

kb = KeyBindings()


class ChatWorker:

    _logger = logging.getLogger(__name__)
    
    def __init__(self, reply_fn, limits_dict=None, typewriter=True, context=None):
            self.console = Console()
            self.reply_fn = reply_fn
            self.history: list[dict] = []
            self.chat_content: list[dict] = []
            self.turn = 0
            self.context = context
            self.viewer = ChatUI()
            self.func_menu = FuncChoicer(kb)
            self.limits = limits_dict
            self.tuw = TokenUsageWatcher(TOKENS_FILE)
            self.current_model = context.get("model")
            self.usage = None
            self.multiline_active = False

            self.code_session = PromptSession(
                history=InMemoryHistory(),
                complete_while_typing=True,)
              

    def get_answer(self):
        start = time.monotonic()
        result = None
        try:
            with self.console.status("[cyan]Ассистент думает…[/cyan]",
                                     spinner="dots"):
                result = self.reply_fn(list(self.history), context=self.context)
        except Exception as error:
            self.viewer.show_error(f"{type(error).__name__}: {error}")
            self._logger.error('Failed to get answer.', exc_info=True) 
            return None

        if isinstance(result, str):          # обычный ответ
            self.tuw.get_limits()            # обновить словарь лимитов
            answer = result
        else:                                # стриминг (генератор чанков)
            buffer = Text()
            with Live(buffer, console=self.console, refresh_per_second=20) as live:
                for data in result:
                    if data.get("usage"):
                        final_usage = data["usage"]
                        self.usage = final_usage.total_tokens
                    chunk = data.get("content")
                    if chunk is not None and chunk[0].content:
                        buffer.append(chunk[0].content[0].text)
                        live.update(buffer)
                    answer = buffer.plain
                    live.update(self.viewer._panel(answer))

        if final_usage:
            self._logger.info(f"Tokens: in={final_usage.input_tokens}, out={final_usage.output_tokens}, total={final_usage.total_tokens}")
            self._view_usage()
        action = self.func_menu.get_choice()
        self.last_elapsed = time.monotonic() - start
        self.history.clear()
        return answer, action


    def run(self):
        
        self.viewer.welcome()
        while True:
            mode_label = "[bold cyan]Многострочный (<Empty string> для отправки)[/bold cyan]" if self.multiline_active else "[bold green]Одиночный ввод[/bold green]"
            self.viewer.console.print(f"\n{mode_label} ", end="")
            try:
                if self.multiline_active:
                    completer = ChatCompleter()
                    user_text = completer.get_multiline_input("\n[bold green]Вы[/bold green]")
                else:
                    user_text = Prompt.ask("\n[bold green]Вы[/bold green]").strip()
                user_text = user_text.replace('\r\n', ' ').replace('\n', ' ')
                cmd = CommandParser.parse(user_text)
            except (KeyboardInterrupt, EOFError):
                break
            handled = self._handle_system_commands(user_text)
            if handled:
                continue

            if user_text.lower() in {"/exit", "/quit", "/q"}:
                break
            
            self.viewer.show_user(user_text)
            stamp = datetime.now().strftime("%d-%m-%Y %H:%M")
            self.history.append({"role": "user","content": user_text})

            answer, action = self.get_answer()
            self.chat_content.append({"role": "user","stamp": stamp,"content": user_text, "agent": answer})
            if action == "↩":
                continue
            helper = ChatHelper(self.chat_content, action, DOWNLOAD_DIR)
            notification = helper.run_task()
            if notification:
                self.console.print(Rule(title=notification))
                continue
            if answer is None:
                self.history.pop()           # не сохраняем неудавшийся ход
                continue

            self.history.append({"role": "assistant", "content": answer})
            self._view_usage()

        self.console.print(Rule(title="[dim]Чат завершён. Пока! 👋[/dim]"))


    def _view_usage(self):
        """
        Отображает текущий остаток токенов для выбранной модели.
        :return: None
        """
        try:
            tokens = self.tuw.update_usage(self.current_model, self.usage)
            if isinstance(tokens, int):
                notification = f'Для модели {self.current_model} остаток токенов: {tokens}'
                self.console.print(Rule(title=notification))
            else:
                raise ValueError("Incorrect tokens value")
        except Exception as error:
            self._logger.error("Failed to update tokens info: %s", error)


    def _handle_system_commands(self, user_text: str) -> bool:
        """
        Обрабатывает системные команды.
        True, если команда обработана (нужно пропустить дальнейшую логику),
        False — если это обычный пользовательский ввод.
        """
        if not user_text:
            return True

        cmd = user_text.lower()

        if cmd == "/mode":
            self.multiline_active = not self.multiline_active
            status = "включён" if self.multiline_active else "выключен"
            self.viewer.console.print(f"[yellow]Режим многострочного ввода {status}.[/yellow]")
            return True

        if cmd == "/help":
            self.viewer.console.print(Panel(Markdown(help_md), title="💡 Справка", border_style="blue"))
            #self.viewer.console.print("\nЭто страница помощи")
            return True

        if cmd == "/clear":
            self.console.clear()
            self.history.clear()
            self.turn = 0
            self.viewer.welcome()
            return True

        if cmd in {"/exit", "/quit", "/q"}:
            # Возвращаем сигнал, что нужно прервать главный цикл
            return False  #в цикле мы проверим флаг

        return False

