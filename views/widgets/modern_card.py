# views/widgets/modern_card.py
from PyQt5.QtWidgets import QFrame, QGraphicsDropShadowEffect
from PyQt5.QtCore import QVariantAnimation, QEasingCurve
from PyQt5.QtGui import QColor

# Shadow parameter ranges — single source of truth for both states.
# Change here; _on_shadow_progress picks them up automatically.
_REST  = {"blur": 20, "y": 4,  "alpha": 15}
_HOVER = {"blur": 30, "y": 8,  "alpha": 25}
_DURATION_MS = 250


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


class ModernCard(QFrame):
    """QFrame with smooth drop-shadow hover animation.

    Visual styling (background, border, border-radius) comes entirely from
    cards.qss via objectName — no inline stylesheet here.

    Args:
        card_type: objectName assigned to the frame.
                   "card"          → QFrame#card
                   "card_elevated" → QFrame#card_elevated
                   "card_stat"     → QFrame#card_stat
    """

    def __init__(self, parent=None, card_type: str = "card"):
        super().__init__(parent)
        self.setObjectName(card_type)

        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setXOffset(0)
        self._shadow.setYOffset(_REST["y"])
        self._shadow.setBlurRadius(_REST["blur"])
        self._shadow.setColor(QColor(0, 0, 0, _REST["alpha"]))
        self.setGraphicsEffect(self._shadow)

        self._anim = QVariantAnimation(self)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._anim.valueChanged.connect(self._on_shadow_progress)

    # ── Animation callbacks ────────────────────────────────────────────────

    def _on_shadow_progress(self, t: float) -> None:
        """Interpolate all three shadow properties in lockstep."""
        self._shadow.setBlurRadius(_lerp(_REST["blur"],  _HOVER["blur"],  t))
        self._shadow.setYOffset(   _lerp(_REST["y"],     _HOVER["y"],     t))
        self._shadow.setColor(QColor(0, 0, 0, round(_lerp(_REST["alpha"], _HOVER["alpha"], t))))

    def _animate_to(self, target: float) -> None:
        """Animate toward target (0.0 = resting, 1.0 = hover).

        If the cursor enters and immediately leaves mid-animation, we continue
        from the current progress value instead of snapping back to 0 or 1.
        Duration is scaled proportionally so speed feels constant regardless
        of how far the animation has progressed when it reverses.
        """
        self._anim.stop()
        current = self._anim.currentValue()
        # currentValue() is None before the first start; infer sensible default.
        if current is None:
            current = 0.0
        start = float(current)
        remaining = abs(target - start)
        self._anim.setDuration(max(1, round(_DURATION_MS * remaining)))
        self._anim.setStartValue(start)
        self._anim.setEndValue(target)
        self._anim.start()

    # ── Qt event overrides ─────────────────────────────────────────────────

    def enterEvent(self, event):
        self._animate_to(1.0)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._animate_to(0.0)
        super().leaveEvent(event)
