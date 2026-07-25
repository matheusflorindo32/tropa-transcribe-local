#define MyAppName "Tropa Transcribe Local"
#define MyAppVersion "0.3.1-alpha"
#define MyAppPublisher "Tropa Científica"
#define MyAppExeName "TropaTranscribeLocal.exe"

#ifndef GuiDistDir
  #define GuiDistDir "..\..\dist\TropaTranscribeLocal"
#endif

[Setup]
AppId={{B28A70F4-B633-48B7-9BB5-D717474A866B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppComments=Aplicativo independente, local, sem conta, telemetria ou upload
VersionInfoVersion=0.3.1.0
DefaultDirName={localappdata}\Programs\TropaTranscribeLocal
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=..\..\dist\installer
OutputBaseFilename=TropaTranscribeLocal-{#MyAppVersion}-setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\{#MyAppExeName}
LicenseFile=..\..\LICENSE
InfoBeforeFile=..\..\packaging\windows\PRE-RELEASE-NOTICE.txt
CloseApplications=yes
RestartApplications=no
SetupLogging=yes
ChangesEnvironment=no
ChangesAssociations=no
PrivilegesRequiredOverridesAllowed=dialog commandline

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Files]
Source: "{#GuiDistDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{userdesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na área de trabalho"; GroupDescription: "Atalhos:"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Abrir {#MyAppName}"; Flags: nowait postinstall skipifsilent

[Code]
function HasExactParameter(const Value: String): Boolean;
var
  Index: Integer;
begin
  Result := False;
  for Index := 1 to ParamCount do
  begin
    if CompareText(ParamStr(Index), Value) = 0 then
    begin
      Result := True;
      Exit;
    end;
  end;
end;

function InitializeSetup(): Boolean;
begin
  Result := True;
  if WizardSilent and not HasExactParameter('/ACCEPTLICENSE=YES') then
  begin
    SuppressibleMsgBox(
      'A instalação silenciosa exige consentimento controlado. ' +
      'Leia LICENSE, THIRD-PARTY-NOTICES.md e execute novamente com ' +
      '/ACCEPTLICENSE=YES.',
      mbCriticalError, MB_OK, IDOK);
    Result := False;
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  ModelsDirectory: String;
  RuntimeDirectory: String;
begin
  if (CurUninstallStep = usUninstall) and not UninstallSilent then
  begin
    RuntimeDirectory := ExpandConstant('{localappdata}\TropaTranscribeLocal\runtime-v2');
    if DirExists(RuntimeDirectory) and
      (MsgBox(
        'Deseja excluir também os runtimes locais FFmpeg e whisper.cpp?' + #13#10 +
        'Eles poderão ser baixados novamente pelo assistente.',
        mbConfirmation, MB_YESNO) = IDYES) then
    begin
      if not DelTree(RuntimeDirectory, True, True, True) then
        MsgBox(
          'Não foi possível excluir todos os runtimes. Os arquivos remanescentes ' +
          'foram preservados.',
          mbInformation, MB_OK);
    end;

    ModelsDirectory := ExpandConstant('{localappdata}\TropaTranscribeLocal\models');
    if DirExists(ModelsDirectory) and
      (MsgBox(
        'Deseja também excluir os modelos locais?' + #13#10 + #13#10 +
        'As transcrições e demais arquivos fora da pasta de modelos serão preservados.',
        mbConfirmation, MB_YESNO) = IDYES) then
    begin
      if not DelTree(ModelsDirectory, True, True, True) then
        MsgBox(
          'Não foi possível excluir todos os modelos. A desinstalação continuará e ' +
          'os arquivos remanescentes serão preservados.',
          mbInformation, MB_OK);
    end;
  end;
end;
