@echo off
echo =========================================================
echo  Faaliyet Takip Programi - Setup ve Build Islemi
echo =========================================================

echo.
echo [1/2] Bagimliliklar kontrol ediliyor ve yukleniyor...
pip install -r requirements.txt

echo.
echo [2/2] Nuitka ile EXE olusturuluyor...
echo Bu islem birkac dakika surebilir, lutfen bekleyin...

if not exist dist mkdir dist

python -m nuitka ^
    --onefile ^
    --standalone ^
    --enable-plugin=pyqt5 ^
    --include-data-dir=icons=icons ^
    --include-data-dir=fonts=fonts ^
    --windows-disable-console ^
    --windows-icon-from-ico=icons/icon.ico ^
    --output-dir=dist ^
    --output-filename=FaaliyetTakip.exe ^
    --remove-output ^
    --assume-yes-for-downloads ^
    main.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo =========================================================
    echo  BASARILI! FaaliyetTakip.exe olusturuldu.
    echo =========================================================
) else (
    echo.
    echo =========================================================
    echo  Birkac hata olustu. Lutfen ciktilari kontrol edin.
    echo =========================================================
)

pause
