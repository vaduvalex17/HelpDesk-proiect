@echo off
REM ---------------------------------------------------------------------------
REM HelpDesk IT - ruleaza testele automate si afiseaza rezultatul (dublu-clic).
REM Prima data instaleaza pytest (are nevoie de internet).
REM Toata logica este in scripts\prezentare.py (optiunea --teste).
REM ---------------------------------------------------------------------------
title HelpDesk IT - teste automate
cd /d "%~dp0"
echo.
echo  Pornesc testele automate... (prima data dureaza cateva minute)
call "scripts\windows\gaseste-python.bat"
if not defined PY goto :final
"%PY%" scripts\prezentare.py --teste
:final
echo.
pause
