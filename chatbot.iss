[Setup]
AppName=Chatbot
AppVersion=1.0
DefaultDirName={pf}\Chatbot
DefaultGroupName=Chatbot
OutputDir=output
OutputBaseFilename=Deepseek chatbot
SetupIconFile=assets\robot.ico

[Files]
Source: "dist\app.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "assets\*"; DestDir: "{app}\assets"; Flags: recursesubdirs

[Icons]
Name: "{userdesktop}\Chatbot"; Filename: "{app}\app.exe"; IconFilename: "{app}\assets\robot.ico"
