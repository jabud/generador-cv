"""
Shared rendering logic: YAML data -> HTML (Jinja2) -> PDF (WeasyPrint).

Used by both generate_cv.py (CLI) and app.py (local web editor).
"""
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = BASE_DIR / "template"
FONTS_DIR = BASE_DIR / "fonts"
DEFAULT_DATA = BASE_DIR / "data" / "cv_data.yaml"


def load_yaml_file(path: Path) -> dict:
    """Read a YAML file from disk into a dict."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def parse_yaml_string(text: str) -> dict:
    """Parse YAML given as a string (used by the web editor)."""
    return yaml.safe_load(text)


def render_html(cv_data: dict) -> str:
    """Render the Jinja2 template into a full HTML document."""
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=True)
    template = env.get_template("cv_template.html.j2")
    return template.render(cv=cv_data, fonts_dir=FONTS_DIR.as_posix())


def render_pdf_bytes(cv_data: dict) -> bytes:
    """Render the CV straight to PDF bytes (no file on disk)."""
    html_content = render_html(cv_data)
    return HTML(string=html_content, base_url=str(BASE_DIR)).write_pdf()


def render_pdf_file(cv_data: dict, output_path: Path) -> Path:
    """Render the CV to a PDF file on disk."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    html_content = render_html(cv_data)
    HTML(string=html_content, base_url=str(BASE_DIR)).write_pdf(str(output_path))
    return output_path
