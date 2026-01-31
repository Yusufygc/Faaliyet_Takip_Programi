@echo off
echo Nuitka ile insa islemi baslatiliyor...
echo Lutfen sanal ortaminin aktif oldugundan emin olun.
echo.

REM Nuitka var mi kontrol et
where nuitka >nul 2>nul

if %errorlevel% equ 0 (
    nuitka ^
        --standalone ^
        --onefile ^
        --enable-plugin=pyqt5 ^
        --windows-icon-from-ico=icons/icon.ico ^
        --include-data-dir=icons=icons ^
        --include-data-dir=fonts=fonts ^
        --include-data-file=.env=.env ^
        --output-dir=dist ^
        main.py
) else (
    echo 'nuitka' komutu bulunamadi, 'python -m nuitka' deneniyor...
    python -m nuitka ^
        --standalone ^
        --onefile ^
        --enable-plugin=pyqt5 ^
        --windows-icon-from-ico=icons/icon.ico ^
        --include-data-dir=icons=icons ^
        --include-data-dir=fonts=fonts ^
        --include-data-file=.env=.env ^
        --output-dir=dist ^
        main.py
)

if %errorlevel% neq 0 (
    echo.
    echo HATA: Derleme sirasinda bir sorun olustu.
    pause
    exit /b %errorlevel%
)

echo.
echo Islem basariyla tamamlandi!
echo Cikti dosyasini 'dist/main.exe' adresinde bulabilirsiniz.
pause
