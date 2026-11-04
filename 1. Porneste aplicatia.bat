@echo off
REM ---------------------------------------------------------------------------
REM HelpDesk IT - porneste aplicatia pentru prezentare (dublu-clic pe acest fisier).
REM Prima data instaleaza tot ce trebuie (are nevoie de internet), apoi deschide browserul.
REM Oprire: inchide fereastra neagra.
REM Toata logica este in scripts\prezentare.py.
REM ---------------------------------------------------------------------------
title HelpDesk IT - NU inchide fereastra cat timp prezinti
cd /d "%~dp0"
echo.
echo  HelpDesk IT porneste... (prima data dureaza cateva minute)
call "scripts\windows\gaseste-python.bat"
if not defined PY goto :final
"%PY%" scripts\prezentare.py %*
:final
echo.
pause
