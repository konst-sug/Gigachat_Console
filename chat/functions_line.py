#functions_line.py
import logging
from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style

choices = ["↩", "Копировать", "Код", "Экспорт", "Экспорт чата"]


class FuncChoicer:
     
    _logger = logging.getLogger(__name__)

    def __init__(self, kb, choices=choices):
        self.result = None
        self.choices = choices
        self.current_index = 0
        self.kb = kb
        self.kb.add("left")(self._on_left)
        self.kb.add("right")(self._on_right)
        self.kb.add("enter")(self._on_enter)

    def _on_left(self, event):
        self.current_index = (self.current_index - 1) % len(self.choices)

    def _on_right(self, event):
        self.current_index = (self.current_index + 1) % len(self.choices)

    def _on_enter(self, event):
        self.result = self.choices[self.current_index]
        event.app.exit()

    def get_display(self) -> HTML:
        parts = []
        for i, choice in enumerate(self.choices):
            if i == self.current_index:
                parts.append(
                    f'<style fg="black" bg="#0055ff"><b> {choice} </b></style>'
                )
            else:
                parts.append(f'<ansicyan> {choice} </ansicyan>')

        return HTML("   ".join(parts))

    def get_choice(self):
        style = Style.from_dict({
            # Убираем стандартную инверсию фона у toolbar
            "bottom-toolbar": "noreverse",
        })
        session = PromptSession(key_bindings=self.kb)
        
        try:
            session.prompt(
                accept_default=False,
                bottom_toolbar=self.get_display,
                style=style,
            )
        except ValueError:
            return "↩"
        return self.result