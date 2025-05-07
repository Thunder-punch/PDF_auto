[Setup]
AppName            = PDF사무자동화
AppVersion         = 1.2.1
DefaultDirName     = {pf}\PDF사무자동화
DefaultGroupName   = PDF사무자동화
PrivilegesRequired = admin
ArchitecturesInstallIn64BitMode=x64
OutputDir          = C:\Users\texcl\HaelfriendsApp\output
OutputBaseFilename = PDF사무자동화_설치파일
Compression        = lzma
SolidCompression   = yes
DisableReadyPage        = yes
DisableProgramGroupPage = yes
DisableFinishedPage     = yes

[Files]
Source: "C:\Users\texcl\HaelfriendsApp\dist\main.exe"; \
  DestDir: "{app}"; DestName: "PDF사무자동화.exe"; Flags: ignoreversion
Source: "C:\Users\texcl\HaelfriendsApp\resources\*.*"; \
  DestDir: "{app}\resources"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\texcl\HaelfriendsApp\README.txt"; \
  DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\PDF사무자동화";        Filename: "{app}\PDF사무자동화.exe"
Name: "{commondesktop}\PDF사무자동화"; Filename: "{app}\PDF사무자동화.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "바탕화면에 아이콘 생성"; GroupDescription: "추가 작업"

[Code]
function GetMachineGuid(Param: String): String;
var
  MachineGuid: String;
begin
  if RegQueryStringValue(HKLM, 'SOFTWARE\\Microsoft\\Cryptography', 'MachineGuid', MachineGuid) then
    Result := MachineGuid
  else if RegQueryStringValue(HKLM, 'SOFTWARE\\Wow6432Node\\Microsoft\\Cryptography', 'MachineGuid', MachineGuid) then
    Result := MachineGuid
  else
    Result := 'UNKNOWN';
end;

[Registry]
Root: HKLM64; Subkey: "SOFTWARE\\HaelFriends\\PDF사무자동화"; \
  ValueType: string; ValueName: "Installed"; ValueData: "True"; \
  Flags: preservestringtype

Root: HKLM64; Subkey: "SOFTWARE\\HaelFriends\\PDF사무자동화"; \
  ValueType: string; ValueName: "HWID"; \
  ValueData: "{code:GetMachineGuid}"; \
  Flags: preservestringtype

Root: HKLM32; Subkey: "SOFTWARE\\Wow6432Node\\HaelFriends\\PDF사무자동화"; \
  ValueType: string; ValueName: "Installed"; ValueData: "True"; \
  Flags: preservestringtype

Root: HKLM32; Subkey: "SOFTWARE\\Wow6432Node\\HaelFriends\\PDF사무자동화"; \
  ValueType: string; ValueName: "HWID"; \
  ValueData: "{code:GetMachineGuid}"; \
  Flags: preservestringtype