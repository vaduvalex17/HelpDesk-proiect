@echo off
REM ---------------------------------------------------------------------------
REM Gaseste Python 3.12+ pe calculator si pune calea lui in variabila PY.
REM Daca Python lipseste, il instaleaza automat (winget), doar pentru utilizatorul curent.
REM Este apelat de "1. Porneste aplicatia.bat" si "2. Ruleaza testele.bat".
REM Fara diacritice in mesaje: consola Windows nu le afiseaza mereu corect.
REM ---------------------------------------------------------------------------
set "PY="
set "VERIFICA=import sys; print(sys.executable) if sys.version_info >= (3, 12) else None"

call :cauta
if defined PY goto :eof

echo.
echo  Python nu este instalat pe acest calculator.
echo  Il instalez acum automat. Dureaza 1-3 minute si are nevoie de internet.
echo  Daca Windows intreaba daca permiti modificari, apasa "Da".
echo.
where winget >nul 2>nul
if errorlevel 1 goto :fara_winget
winget install -e --id Python.Python.3.12 --scope user --silent --accept-package-agreements --accept-source-agreements
call :cauta
if defined PY goto :eof
echo.
echo  Python s-a instalat. Inchide aceasta fereastra si da din nou dublu-clic
echo  pe acelasi fisier.
goto :eof

:fara_winget
echo  Nu pot instala Python automat pe acest calculator.
echo  Se deschide pagina de descarcare: apasa butonul galben "Download Python",
echo  porneste fisierul descarcat, BIFEAZA "Add python.exe to PATH" jos in fereastra,
echo  apoi apasa "Install Now". La final, da din nou dublu-clic pe acest fisier.
start "" https://www.python.org/downloads/windows/
goto :eof

REM --- cauta Python in locurile obisnuite; seteaza PY daca il gaseste ---
:cauta
for /f "delims=" %%i in ('py -3 -c "%VERIFICA%" 2^>nul') do set "PY=%%i"
if defined PY goto :eof
for /f "delims=" %%i in ('python -c "%VERIFICA%" 2^>nul') do set "PY=%%i"
if defined PY goto :eof
for %%v in (314 313 312) do (
    if not defined PY if exist "%LOCALAPPDATA%\Programs\Python\Python%%v\python.exe" set "PY=%LOCALAPPDATA%\Programs\Python\Python%%v\python.exe"
)
goto :eof
