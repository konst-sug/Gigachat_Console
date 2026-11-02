#prompt_reader.py
import re
from typing import Literal, Optional, NamedTuple, List

ActionType = Literal["file", "prompt_extend", "layout", "none"]


class ParsedCommand(NamedTuple):
    action: ActionType
    payload: Optional[str]
    clean_text: str


class CommandParser:
    """
    Изолированный парсер однострочных команд.
    Не зависит от Rich, не делает запросов, не грузит файлы.
    Только разбирает строку и возвращает структуру.
    """

    @staticmethod
    def parse(text: str) -> ParsedCommand:
        action: ActionType = "none"
        payload: Optional[str] = None
        clean_text = text.strip()

        # Ищем команды вида &file=..., &extend=..., &layout
        pattern = r'&(file|extend|output|layout)(?:=(.+?))?(?=\s|&|$)'
        matches = list(re.finditer(pattern, text, flags=re.IGNORECASE))

        if not matches:
            return ParsedCommand("none", None, clean_text)
        chain: List[ParsedCommand] = []
        
        for match in matches:
            cmd = match.group(1).lower()
            val = match.group(2)
            payload = None
            match cmd:
                case "output" | "file" | "extend":
                    payload = val.strip() if val else None                      
                case "layout":
                    payload = None
                case _:
                    cmd = None
            chain.append(ParsedCommand(cmd, payload, None))
        return chain
