#ifndef AppVersion
  #error AppVersion must be provided by build_windows_installer.ps1.
#endif

#define AppName "Meeting Assistant AI"
#define AppExeName "MeetingAssistantAI.exe"

[Setup]
AppId={{6B50D119-6058-4A17-B071-61A7D20BD235}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppName}
DefaultDirName={localappdata}\Programs\Meeting Assistant AI
DefaultGroupName=Meeting Assistant AI
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
OutputDir=..\dist\installer
OutputBaseFilename=MeetingAssistantAI-Setup-{#AppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
Uninstallable=yes
CreateUninstallRegKey=yes
UninstallDisplayIcon={app}\{#AppExeName}
CloseApplications=yes
RestartApplications=no

[Files]
Source: "..\dist\MeetingAssistantAI\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Icons]
Name: "{group}\Meeting Assistant AI"; Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"
Name: "{userdesktop}\Meeting Assistant AI"; Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,Meeting Assistant AI}"; WorkingDir: "{app}"; Flags: nowait postinstall skipifsilent
