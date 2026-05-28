#define AppVersion GetEnv("PASSWORDS_MANAGER_VERSION")

#if AppVersion == ""
  #define AppVersion "0.0.0"
#endif

[Setup]
AppId=PasswordsManager
AppName=Passwords Manager
AppVersion={#AppVersion}
AppPublisher=JLBBARCO
DefaultDirName=C:\File Programs (x86)\Passwords Manager
DefaultGroupName=Passwords Manager
OutputDir=output
OutputBaseFilename=passwords-manager-windows-installer
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
DisableProgramGroupPage=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "..\..\release-assets\passwords-manager-windows.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\release-assets\install-passwords-manager.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\ENCRYPTION.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\src\assets\icon\passwords-manager.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Passwords Manager"; Filename: "{app}\passwords-manager-windows.exe"
Name: "{commondesktop}\Passwords Manager"; Filename: "{app}\passwords-manager-windows.exe"; Tasks: desktopicon

[Tasks]
Name: desktopicon; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked

[Run]
Filename: "{app}\passwords-manager-windows.exe"; Description: "Launch Passwords Manager"; Flags: nowait postinstall skipifsilent