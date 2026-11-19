@echo off
setlocal
cd /d "%~dp0"
title Project 2 - Student 30-month check
echo PROJECT 2 - YOUR 30-MONTH CHECK
echo.
echo Close ChatGPT, Codex, and other generative tools before continuing.
echo Your prediction is already saved. This preserves it before the run.
echo This launcher has not been run by the assistant.
echo.
set "project2Confirmation="
set /p "project2Confirmation=Type RUN only if generative tools are closed: "
if /i not "%project2Confirmation%"=="RUN" goto cancelled
set "project2Python=%~dp0.venv\Scripts\python.exe"
if not exist "%project2Python%" set "project2Python=%~dp0..\..\.venv\Scripts\python.exe"
if not exist "%project2Python%" goto missing_python
if exist "evidence\fresh-locked-exercise\execution.json" goto existing
if not exist "evidence\fresh-locked-exercise" mkdir "evidence\fresh-locked-exercise"
if exist "evidence\fresh-locked-exercise\precommit.json" goto execute
echo Preserving your prediction and code snapshot...
"%project2Python%" fresh_locked_exercise.py --freeze docs\fresh-prediction-input.json --tools-closed > "evidence\fresh-locked-exercise\run-log.txt" 2>&1
if errorlevel 1 goto failed
:execute
echo Running the 36-to-30-month comparison...
"%project2Python%" fresh_locked_exercise.py --execute --tools-closed >> "evidence\fresh-locked-exercise\run-log.txt" 2>&1
if errorlevel 1 goto failed
echo.
type "evidence\fresh-locked-exercise\run-log.txt"
echo.
echo Finished. Keep AI closed and write your explanation in the file opening now.
echo Confirm its heading says Changed lookback: 30.
notepad "evidence\fresh-locked-exercise\student-reconciliation.md"
goto finished
:existing
echo A saved result already exists. It will not be overwritten or rerun.
echo Read the existing result and complete your own explanation with AI closed.
if exist "evidence\fresh-locked-exercise\student-reconciliation.md" notepad "evidence\fresh-locked-exercise\student-reconciliation.md"
goto finished
:failed
echo.
echo The command failed. Its real error is shown below and saved in run-log.txt.
type "evidence\fresh-locked-exercise\run-log.txt"
echo.
echo Preserve these files. After ending the closed phase, send run-log.txt.
goto finished
:missing_python
echo The prepared Python environment was not found.
echo Send this message and the folder location after ending the closed phase.
goto finished
:cancelled
echo Cancelled. No exercise was executed.
:finished
echo.
pause
endlocal
