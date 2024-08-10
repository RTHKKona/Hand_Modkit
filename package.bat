@echo off

REM Change to the project directory
cd /d C:\Users\necro\Downloads\MHGU_Modding\Audio\MHGU-STQReader

REM Ensure PyInstaller is installed
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM Run PyInstaller to create the executable
pyinstaller --onefile --noconsole --icon=egg.ico stq_tool.py

REM Move the executable to the root of the project folder
move /y dist\stq_tool.exe .


echo Packaging complete. Executable is located in the project folder.

pause
