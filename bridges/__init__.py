# bridges/__init__.py
"""
PySide6 - QML Bridge Modülleri
Python veri yapıları ve iş mantığı ile QML arayüzü arasındaki çift yönlü köprüler.
"""

from .activity_bridge import ActivityBridge, ActivityListModel
from .stats_bridge import StatsBridge
from .plan_bridge import PlanBridge, PlanListModel
from .discover_bridge import DiscoverBridge
from .settings_bridge import SettingsBridge
from .compare_bridge import CompareBridge
from .app_bridge import AppBridge

__all__ = [
    "ActivityBridge",
    "ActivityListModel",
    "StatsBridge",
    "PlanBridge",
    "PlanListModel",
    "DiscoverBridge",
    "SettingsBridge",
    "CompareBridge",
    "AppBridge",
]
