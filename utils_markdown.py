"""
utils_markdown.py — Temel Markdown → HTML dönüştürücü.

Desteklenen sözdizimi:
  **bold**   → <b>bold</b>
  *italic*   → <i>italic</i>
  _italic_   → <i>italic</i>
  `code`     → <code>code</code>
  - item     → <ul><li>item</li></ul>
  Satır sonu → <br>
"""

import re


def md_to_html(text: str) -> str:
    """Convert basic Markdown to HTML."""
    if not text:
        return ""

    lines = text.split("\n")
    html_lines: list[str] = []
    in_list = False

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("- ") or stripped.startswith("* "):
            item_text = stripped[2:]
            item_text = _inline(item_text)
            if not in_list:
                html_lines.append("<ul style='margin:0; padding-left:18px;'>")
                in_list = True
            html_lines.append(f"<li>{item_text}</li>")
        else:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            if stripped == "":
                html_lines.append("<br>")
            else:
                html_lines.append(_inline(line))

    if in_list:
        html_lines.append("</ul>")

    return "<br>".join(
        line for line in html_lines
        if not (line == "<br>" and html_lines.index(line) == 0)
    )


def _inline(text: str) -> str:
    """Apply inline markdown transforms."""
    # Bold: **text** or __text__
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"__(.+?)__", r"<b>\1</b>", text)
    # Italic: *text* or _text_ (after bold so ** is handled first)
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    text = re.sub(r"_(.+?)_", r"<i>\1</i>", text)
    # Code: `text`
    text = re.sub(
        r"`(.+?)`",
        r"<code style='background:#F1F5F9; padding:1px 4px; border-radius:3px;'>\1</code>",
        text,
    )
    return text
