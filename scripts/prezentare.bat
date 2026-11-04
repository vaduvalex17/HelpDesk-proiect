@echo off
REM Porneste HelpDesk IT pentru prezentare si deschide browserul (Windows).
REM Utilizare: dublu-clic pe fisier sau, din terminal:  scripts\prezentare.bat [--pastreaza]
REM Toata logica e in prezentare.py; aici doar gasim Python si il rulam.
cd /d "%~dp0.."
where py >nul 2>nul
if %errorlevel%==0 (
    py -3 scripts\prezentare.py %*
) else (
    python scripts\prezentare.py %*
)
pause
