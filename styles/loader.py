from string import Template
from pathlib import Path

_DIR = Path(__file__).parent
_cache: dict[str, str] = {}


def _tokens() -> dict:
    from styles.tokens import TOKENS
    return TOKENS


def load(*names: str) -> str:
    """Load and return one or more QSS sheets with tokens substituted.

    Usage:
        widget.setStyleSheet(load("inputs"))
        dialog.setStyleSheet(load("inputs", "buttons", "cards"))
    """
    tokens = _tokens()
    parts: list[str] = []
    for name in names:
        if name not in _cache:
            path = _DIR / f"{name}.qss"
            raw = path.read_text(encoding="utf-8")
            _cache[name] = Template(raw).safe_substitute(tokens)
        parts.append(_cache[name])
    return "\n".join(parts)


def invalidate_cache() -> None:
    _cache.clear()
