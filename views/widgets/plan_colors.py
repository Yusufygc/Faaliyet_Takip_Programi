# views/widgets/plan_colors.py
from views.styles import COLORS as GLOBAL_COLORS

COLORS = {
    'bg_main': '#F4F7F6',
    'bg_card': '#FFFFFF',
    'text_main': '#2C3E50',
    'text_sub': '#7F8C8D',
    'primary': GLOBAL_COLORS['primary'],
    'primary_gradient': f"qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {GLOBAL_COLORS['primary']}, stop:1 #3498DB)",
    'success_gradient': "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #27AE60, stop:1 #2ECC71)",
    'danger': '#E74C3C',
    'border': '#E0E6ED'
}

PRIORITY_CFG = {
    'low':    {'bg': '#E8F6F3', 'fg': '#1ABC9C', 'label': 'Düşük',  'dot': '●'},
    'medium': {'bg': '#FEF9E7', 'fg': '#F1C40F', 'label': 'Orta',   'dot': '●'},
    'high':   {'bg': '#FDEDEC', 'fg': '#E74C3C', 'label': 'Yüksek', 'dot': '●'}
}
