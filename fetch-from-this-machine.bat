rem https://stackoverflow.com/questions/7170683/copy-all-files-and-folders-from-one-drive-to-another-drive-using-dos-command-pr

XCOPY %APPDATA%\Code\User\snippets              .\vscode\snippets /i/y
XCOPY %APPDATA%\Code\User\keybindings.json      .\vscode /y
XCOPY %APPDATA%\Code\User\settings.json         .\vscode /y
XCOPY %APPDATA%\Code\User\vsicons.settings.json .\vscode /y