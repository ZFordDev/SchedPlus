#define MyAppName "SchedPlus"
#define MyAppVersion GetEnv("SCHEDPLUS_VERSION")
#define MyAppPublisher "ZFordDev"
#define MyAppURL "https://github.com/ZFordDev/SchedPlus"
#define MyAppExeName "SchedPlusStandard.exe"

[Setup]
AppId={{0C6F3E15-5245-4C9F-AB2F-5FF94DC9D85E}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={localappdata}\Programs\SchedPlus
DefaultGroupName=SchedPlus
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir={#GetEnv("SCHEDPLUS_OUTPUT_DIR")}
OutputBaseFilename=SchedPlus-Setup-{#MyAppVersion}-windows-x86_64
SetupIconFile=..\..\assets\windows\SchedPlus.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
VersionInfoCompany=ZFordDev
VersionInfoDescription=SchedPlus Standard installer
VersionInfoProductName=SchedPlus
VersionInfoProductVersion={#MyAppVersion}
VersionInfoVersion={#MyAppVersion}
LicenseFile=..\..\LICENSE

[Files]
Source: "{#GetEnv("SCHEDPLUS_FROZEN_DIR")}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "SOURCE.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\SchedPlus"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{group}\Uninstall SchedPlus"; Filename: "{uninstallexe}"
