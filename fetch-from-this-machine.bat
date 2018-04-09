rem https://stackoverflow.com/questions/7170683/copy-all-files-and-folders-from-one-drive-to-another-drive-using-dos-command-pr

cd "C:\_mik\gh\MyProjectTemplates"

XCOPY /i/y %APPDATA%\Code\User\snippets            .\vscode\snippets
XCOPY /y %APPDATA%\Code\User\keybindings.json      .\vscode\
XCOPY /y %APPDATA%\Code\User\settings.json         .\vscode\
XCOPY /y %APPDATA%\Code\User\vsicons.settings.json .\vscode\

XCOPY /i/y/E "C:\_mik\BATCH"       ".\PATH"
rem ROBOCOPY /S /E "C:\_mik\BATCH"       ".\PATH"

XCOPY /i/y/E "%APPDATA%\Sublime Text 3\Packages\User"       ".\sublime"
rmdir /s /q ".\sublime\"

