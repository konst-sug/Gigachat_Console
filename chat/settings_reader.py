#settings_reader.py
from rich.console import Console
from rich.text import Text
from InquirerPy import inquirer, get_style


class SettingsReader:

    def __init__(self, typewriter=True):
        self.console = Console()
        self.typewriter = typewriter
        self.role = None
        self.model = None


    def simple_select(self, available_models: set):
        MENU_WIDTH = 60
        style = get_style({"questionmark": "#ffffff", 
                           "answer": "#000000", 
                           "pointer": "#65df0d",
                           "fuzzy_border": "#f45703"}, style_override=False)
        question_text = Text("Выберите модель GigaChat:", style="bold") 
        question_text.truncate(MENU_WIDTH, overflow="fold")

        choice = inquirer.select(
            message=question_text,
            choices=[f"{m}" for m in available_models],
            long_instruction="Используй стрелки ↑/↓, [Enter] для выбора, [Esc] для отмены",
            style=style,
            vi_mode=False, 
            border="red",
            instruction=""
            ).execute()
        
        if choice is None: 
            self.console.print("Выбор отменен.") 
            return
        return choice
