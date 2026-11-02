from .layout_marker import LayoutModuleMarker


def step_layout(input_file: str, output_dir: str):
    layout = LayoutModuleMarker()
    html_path = layout.process_pdf_to_html(input_file, output_dir)
    # Теперь у тебя:
    # - картинки в output_dir/images/
    # - HTML-верстка в html_path
    return html_path