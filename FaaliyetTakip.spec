# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec dosyası — tek dosyalık (onefile), dosya bağımlılığı olmayan
# taşınabilir FaaliyetTakip.exe üretir. Derlemek için:
#   venv\Scripts\pyinstaller.exe FaaliyetTakip.spec --noconfirm
from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
hiddenimports = []

# PySide6 (QtQml/QtQuick modülleri + gerekli platform/qml eklentileri) ve
# keyring (OS kasası backend'lerinin entry-point tabanlı keşfi PyInstaller
# statik analiziyle bulunamaz, bu yüzden tamamı elle toplanır).
for pkg in ("PySide6", "keyring"):
    d, b, h = collect_all(pkg)
    datas += d
    binaries += b
    hiddenimports += h

# Uygulamanın kendi kaynakları — main.py'de get_resource_path() ile okunur,
# QML dosyaları da birbirine göreli yollarla (ör. "../../assets/fonts/...")
# başvurduğundan dev ortamındaki klasör yapısı aynen korunmalı.
datas += [
    ("qml", "qml"),
    ("assets", "assets"),
    ("icons", "icons"),
    ("fonts", "fonts"),
]

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="FaaliyetTakip",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="icons/icon.ico",
)
