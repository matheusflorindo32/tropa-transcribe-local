#define MyAppName "Tropa Transcribe Local"
#define MyAppVersion "0.3.0-alpha"
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
VersionInfoVersion=0.3.0.0
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
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  ModelsDirectory: String;
begin
  if CurUninstallStep = usUninstall then
  begin
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
