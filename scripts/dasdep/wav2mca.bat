@echo off

REM Check if the input WAV file is provided (dragged onto the script)
if "%~1"=="" (
    echo Error: No input file provided. Please drag and drop a .wav file onto the .bat.
    pause
    exit /b 1
)

REM Set the base directory to the location of the batch file
set "BASE_DIR=%~dp0"

REM Print the base directory and the file name being processed
echo Base Directory: %BASE_DIR%
echo Input File: %~1

REM Step 1: Run wav2dsp.exe to convert WAV to DSP
echo Running wav2dsp.exe...
echo "%BASE_DIR%wav2dsp.exe" "%~1"
"%BASE_DIR%wav2dsp.exe" "%~1"
if %errorlevel% neq 0 (
    echo Error: WAV to DSP conversion failed!
    pause
    exit /b 1
)

REM Check if the DSP file was created
if not exist "%~n1.dsp" (
    echo Error: DSP file not created!
    pause
    exit /b 1
)

REM Step 2: Run mcatool.py with Python 2.7 to convert WAV to MCA (pass the original WAV file)
echo Running mcatool.py...
echo "%BASE_DIR%python27\python.exe" "%BASE_DIR%mcatool.py" --mhx "%~1"
"%BASE_DIR%python27\python.exe" "%BASE_DIR%mcatool.py" --mhx "%~1"
if %errorlevel% neq 0 (
    echo Error: DSP to MCA conversion failed!
    pause
    exit /b 1
)

REM Check if the MCA file was created
if not exist "%~n1.mca" (
    echo Error: MCA file not created! 
    pause
    exit /b 1
)

REM Step 3: Delete the intermediate DSP file
echo Deleting DSP file...
del "%~n1.dsp"
if %errorlevel% neq 0 (
    echo Warning: Failed to delete the DSP file!
)

echo Conversion complete!
pause
