import os
import re
from pathlib import Path
from typing import List, Dict, Any

from marker import convert_pdf

class LayoutModuleMarker:
    @staticmethod
    def process_pdf_to_html(
        pdf_path: str,
        output_dir: str,
        images_subdir: str = "images"
    ) -> str:
        """
        Вход: путь к PDF.
        Выход: путь к сгенерированному HTML-файлу.
        
        Что делает:
          1. Создаёт output_dir и папку для картинок.
          2. Запускает Marker: он парсит PDF, вытаскивает картинки и делает Markdown.
          3. Конвертирует Markdown-структуру Marker в HTML с сохранением картинок и стилей.
          4. Сохраняет HTML и возвращает путь к нему.
        """
        pdf_path = Path(pdf_path)
        out_dir = Path(output_dir)
        img_dir = out_dir / images_subdir

        # Создаём папки
        img_dir.mkdir(parents=True, exist_ok=True)
        out_dir.mkdir(parents=True, exist_ok=True)

        # 1. Marker делает конвертацию PDF -> Markdown + картинки
        # keep_images=True заставляет Marker сохранять картинки в отдельную папку
        md_text = convert_pdf(
            str(pdf_path),
            keep_images=True,
            image_folder=str(img_dir)
        )

        # 2. Превращаем Markdown от Marker в HTML
        html_content = LayoutModuleMarker._md_to_html_with_images(md_text, img_dir, pdf_path.stem)

        # 3. Сохраняем HTML
        html_path = out_dir / f"{pdf_path.stem}.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return str(html_path)

    @staticmethod
    def _md_to_html_with_images(
        md_text: str,
        img_dir: Path,
        doc_name: str
    ) -> str:
        """
        Простой конвертер Markdown -> HTML, который:
          - сохраняет картинки (Marker уже положил их в img_dir),
          - добавляет CSS для типографики и отступов.
        
        Важно: Markdown от Marker уже содержит структуру (заголовки, списки, абзацы).
        Мы просто оборачиваем это в HTML + добавляем свои стили.
        """
        lines = md_text.splitlines()
        html_lines: List[str] = [
            "<!DOCTYPE html>",
            "<html lang=\"ru\">",
            "<head>",
            "  <meta charset=\"utf-8\">",
            "  <title>Верстка: " + doc_name + "</title>",
            "  <style>",
            "    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 850px; margin: 40px auto; line-height: 1.6; color: #333; }",
            "    h1 { color: #1a1a1a; border-bottom: 3px solid #2c3e50; padding-bottom: 10px; }",
            "    h2 { color: #2c3e50; margin-top: 30px; border-left: 5px solid #3498db; padding-left: 12px; }",
            "    p { margin-bottom: 16px; text-align: justify; }",
            "    ul, ol { margin-bottom: 16px; padding-left: 24px; }",
            "    li { margin-bottom: 6px; }",
            "    img { max-width: 100%; height: auto; border: 1px solid #ddd; margin: 12px 0; }",
            "    .page-break { page-break-after: always; break-after: page; margin: 32px 0; border-top: 1px dashed #ccc; padding-top: 20px; }",
            "  </style>",
            "</head>",
            "<body>",
            "  <div class=\"layout-output\">"
        ]

        i = 0
        while i < len(lines):
            line = lines[i]

            # Заголовки
            if line.startswith("### "):
                html_lines.append(f"    <h3>{_escape_html(line[4:].strip())}</h3>")
                i += 1
                continue
            if line.startswith("## "):
                html_lines.append(f"    <h2>{_escape_html(line[3:].strip())}</h2>")
                i += 1
                continue
            if line.startswith("# "):
                html_lines.append(f"    <h1>{_escape_html(line[2:].strip())}</h1>")
                i += 1
                continue

            # Картинки: Marker сохраняет как ![alt](path/to/image.png)
            img_match = re.match(r'^!\[(.*?)\]\((.*?)\)$', line.strip())
            if img_match:
                alt, src_path = img_match.groups()
                # src_path может быть относительным или абсолютным — нормализуем к нашей папке
                img_name = Path(src_path).name
                # В HTML пишем относительный путь к images/
                html_lines.append(f'    <img src="images/{img_name}" alt="{_escape_html(alt)}">')
                i += 1
                continue

            # Списки
            if re.match(r'^[\-*]\s+', line):
                item = line[2:].strip()
                if not html_lines[-1].strip().endswith("<ul>"):
                    html_lines.append("    <ul>")
                html_lines.append(f"      <li>{_escape_html(item)}</li>")
                # Закрываем список, если следующая строка не элемент списка
                j = i + 1
                if j >= len(lines) or not re.match(r'^[\-*]\s+', lines[j].strip()):
                    html_lines.append("    </ul>")
                i += 1
                continue

            # Абзацы
            if line.strip():
                html_lines.append(f"    <p>{_escape_html(line.strip())}</p>")
            else:
                # Пустая строка — можно добавить визуальный отступ
                html_lines.append("    <div style=\"height:12px;\"></div>")

            i += 1

        html_lines.extend([
            "  </div>",
            "</body>",
            "</html>"
        ])

        return "\n".join(html_lines)


def _escape_html(text: str) -> str:
    return (
        text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
