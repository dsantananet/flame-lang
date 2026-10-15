[Setup]
AppId=dsantananet.FlameLang
AppName=FlameLang
AppVersion=0.2.0-rc.1
AppPublisher=dsantananet
DefaultDirName={localappdata}\Programs\FlameLang
DefaultGroupName=FlameLang
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
UninstallDisplayIcon={app}\FlameLang.exe
SetupIconFile=app.ico
OutputDir=..\release
OutputBaseFilename=FlameLang-0.2.0-rc.1-windows-x64-setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
WizardImageFile=wizard.bmp
WizardSmallImageFile=wizard-small.bmp
[Files]
Source: "..\dist-current\FlameLang\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
[Icons]
Name: "{group}\FlameLang"; Filename: "{app}\FlameLang.exe"
[Run]
Filename: "{app}\FlameLang.exe"; Description: "Abrir FlameLang"; Flags: nowait postinstall skipifsilent
