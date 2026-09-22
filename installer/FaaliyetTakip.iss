; FaaliyetTakip.iss — Inno Setup kurulum sihirbazı script'i
;
; Önkoşul: dist\FaaliyetTakip.exe zaten üretilmiş olmalı
; (bkz. proje kökünde: venv\Scripts\pyinstaller.exe FaaliyetTakip.spec --noconfirm)
;
; Derlemek için:
;   "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\FaaliyetTakip.iss
; Çıktı: installer\output\FaaliyetTakip_Kurulum_<versiyon>.exe

#define MyAppName "Faaliyet Takip Programı"
#define MyAppVersion "2.0.0"
#define MyAppPublisher "MYY Yazılım"
#define MyAppExeName "FaaliyetTakip.exe"

[Setup]
; Bu GUID sabit tutulmalı — sürüm güncellemelerinde aynı uygulamayı tanımlar,
; böylece yükseltme kurulumu eski sürümün üzerine düzgün yazılır.
AppId={{AC2833E1-3424-4BDA-B2B8-8F400853AB79}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppSupportURL=https://github.com/Yusufygc/Faaliyet_Takip_Programi
AppUpdatesURL=https://github.com/Yusufygc/Faaliyet_Takip_Programi
DefaultDirName={localappdata}\Programs\FaaliyetTakip
DefaultGroupName={#MyAppName}
; Program Files yerine kullanıcı profiline kurar — yönetici izni gerekmez,
; UAC istemi çıkmaz (kişisel/taşınabilir kullanım senaryosuna uygun).
PrivilegesRequired=lowest
DisableProgramGroupPage=yes
OutputDir=output
OutputBaseFilename=FaaliyetTakip_Kurulum_{#MyAppVersion}
SetupIconFile=..\icons\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
DisableWelcomePage=no

[Languages]
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Tek dosyalık (onefile) exe — dış dosya bağımlılığı yok, tüm kaynaklar
; (qml/, assets/, icons/, fonts/) exe içine gömülü.
Source: "..\dist\FaaliyetTakip.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Not: kullanıcı verisi (veritabanı, loglar — %LOCALAPPDATA%\FaaliyetTakip\) kasıtlı
; olarak silinmiyor; sadece uygulama dosyaları kaldırılıyor. Veriyi de silmek
; isteyen kullanıcı bunu elle yapmalı.
