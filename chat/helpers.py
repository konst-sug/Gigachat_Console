#helpers.py
import subprocess
import platform
import logging

from pathlib import Path


class ChatHelper:

    _logger = logging.getLogger(__name__)

    def __init__(self, content_lst: list, action: str, folder_path: str | Path):

        self.folder = Path(folder_path)
        self.content = content_lst
        self.action = action
        self.chat_content = None
        self.chat_name = None


    def run_task(self) -> str:

        match self.action:
            case "Экспорт":
                self._create_chat_content()  
                notification =  self.export_chat_content()    
            case "Копировать":
                text = self._create_clipboard_content()  
                notification = self.copy_to_clipboard(text)   
            case "Экспорт чата": 
                self._create_chat_content(True)  
                notification =  self.export_chat_content()      
            case "Код":
                notification = self._get_code()
            case _:
                notification = None     
        return notification


    def copy_to_clipboard(self, text: str) -> str:
        system = platform.system()
        encoded = text.encode("utf-8")
        try:
            if system == "Windows":
                # Используем clip: простой и всегда есть в Windows
                proc = subprocess.run(
                    ["cmd", "/c", "clip"],
                    input=encoded,
                    check=True,
                    timeout=5
                )
            elif system == "Darwin":
                # macOS: pbcopy
                proc = subprocess.run(
                    ["pbcopy"],
                    input=encoded,
                    check=True,
                    timeout=5
                )
            else:
                # Linux: пробуем xclip, если нет — xsel
                for cmd in [["xclip", "-selection", "clipboard"], ["xsel", "--clipboard"]]:
                    try:
                        proc = subprocess.run(cmd, input=encoded, check=True, timeout=5)
                        return "Текст скопирован в буфер обмена"
                    except FileNotFoundError:
                        continue
                return "Утилиты копирования не найдены"
            return "Текст скопирован в буфер обмена"
        except Exception:
            return "Ошибка копирования текста"  


    def _create_chat_content(self, answer=False):
        """
            Подготовка контента для экспорта всего чата,
            либо последнего ответа в чате.
            content: список словарей с вопросами и ответами
            answer: тип экспорта (чат/ответ)
        """
        chat_list = []
        self._make_file_name()
        if answer:
            chat_list.append(self.content[0]["stamp"])
            chat_list.append("\n")
            self.chat_content = "agent"
            for item in self.content:
                question = item.get('content')
                answer = item.get('agent')
                chat_list.append(f"**Запрос:** {question}\n")
                chat_list.append(f"# Ответ: {answer}\n")
                chat_list.append("===========================\n\n")
            self.chat_content = ''.join(chat_list)
        else:
            self.chat_name = f"last-{self.chat_name}"
            self.chat_content = self.content[-1]["agent"]
        

    def export_chat_content(self) -> str:
        file_name = self.folder / self.chat_name
        try:
            with open(file_name, "w", encoding="utf-8") as file:            
                file.write(self.chat_content)
            return f"Чат сохранен в {self.chat_name}"
        except Exception as error:
            self._logger.error("Failed to export data: %s", error)
            return "Ошибка при записи в файл"


    def _create_clipboard_content(self) -> str:
        return self.content[-1]["agent"]


    def _get_code(self):
        return "Работа модуля будет скоро добавлена"


    def _make_file_name(self):
        text_label = self.content[0]['content'][:15]
        stamp_label = self.content[0]['stamp']
        self.chat_name = f"{text_label}-{stamp_label}.md"