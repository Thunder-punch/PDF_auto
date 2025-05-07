; ───────────────────────────────────────────────────
; PDF사무자동화 판매용 설치 스크립트
; USB 스틱 + 설치 횟수 제한(5회) + 누적 횟수 표시
; ───────────────────────────────────────────────────

[Setup]
AppName=PDF사무자동화
AppVersion=1.2.0
DefaultDirName={pf}\PDF사무자동화
DefaultGroupName=PDF사무자동화
PrivilegesRequired=admin
OutputDir=C:\Users\texcl\HaelfriendsApp\output
OutputBaseFilename=PDF사무자동화_설치파일
Compression=lzma
SolidCompression=yes
DisableReadyPage=yes
DisableProgramGroupPage=yes
DisableFinishedPage=yes

[Files]
; 실행 파일
Source: "C:\Users\texcl\HaelfriendsApp\dist\main.exe"; \
  DestDir: "{app}"; DestName: "PDF사무자동화.exe"; Flags: ignoreversion

; 리소스 전체 복사
Source: "C:\Users\texcl\HaelfriendsApp\resources\*.*"; \
  DestDir: "{app}\resources"; Flags: ignoreversion recursesubdirs createallsubdirs

; 추가 문서
Source: "C:\Users\texcl\HaelfriendsApp\README.txt"; \
  DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\PDF사무자동화"; Filename: "{app}\PDF사무자동화.exe"
Name: "{commondesktop}\PDF사무자동화"; Filename: "{app}\PDF사무자동화.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "바탕화면에 아이콘 생성"; GroupDescription: "추가 작업"

[Code]
var
  USBDir: string;
  Count: Integer;
  MaxInstalls: Integer;

function InitializeSetup(): Boolean;
var
  Success: Boolean;
  CountStr: AnsiString;
begin
  MaxInstalls := 5;  // 최대 설치 횟수
  USBDir := ExtractFilePath(ExpandConstant('{srcexe}'));

  // 1) 기존 설치 횟수 읽기
  Success := LoadStringFromFile(USBDir + 'install_count.txt', CountStr);
  if not Success then
    CountStr := '0';

  Count := StrToIntDef(CountStr, 0);




  // 2) 제한 횟수 초과 시 설치 중단
  if Count >= MaxInstalls then
  begin
    MsgBox(Format('설치 횟수(%d회)를 초과했습니다.'#13#10'고객 지원에 문의하세요.', [MaxInstalls]), mbError, MB_OK);
    Result := False;
    Exit;
  end;

  // 3) 카운터 증가 및 저장
  Inc(Count);
  SaveStringToFile(USBDir + 'install_count.txt', IntToStr(Count), True);

  // 4) 설치 시작 전 누적 횟수 표시 및 잔여 횟수 표시
  MsgBox(
    Format('이번 설치를 포함한 총 설치 횟수: %d회'#13#10'잔여 설치 가능 횟수: %d회', [Count, MaxInstalls - Count]),
    mbInformation,
    MB_OK
  );

[Registry]
Root: HKLM; Subkey: "SOFTWARE\HaelFriends\PDF사무자동화"; \
  ValueType: string; ValueName: "Installed"; ValueData: "True"; Flags: uninsdeletekey


  Result := True;
end;
