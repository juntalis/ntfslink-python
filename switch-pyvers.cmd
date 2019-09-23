@echo off
setlocal
goto main

:clearattrs
rem Clear restrictive attributes.
set "_ATTRS=%~a1"
set _CLEAR_ARGS=
set _RESTORE_ARGS=
goto clearattrs_loop
:clearattrs_attr
rem Restrictive attribute detected
set "_CLEAR_ARGS=%_CLEAR_ARGS% -%~1"
set "_RESTORE_ARGS=%_RESTORE_ARGS% +%~1"
goto :EOF
:clearattrs_loop
rem Looping logic that iterates through attributes string
if "%_ATTRS%x"=="x" goto clearattrs_break
set "_ATTR=%_ATTRS:~0,1%"
set "_ATTRS=%_ATTRS:~1%"
rem Read-only
if /i "%_ATTR%x"=="rx" call :clearattrs_attr %_ATTR%
rem Hidden
if /i "%_ATTR%x"=="hx" call :clearattrs_attr %_ATTR%
rem System
if /i "%_ATTR%x"=="sx" call :clearattrs_attr %_ATTR%
rem Loop
goto clearattrs_loop
:clearattrs_break
rem Finished looping - time to clear
echo  - Clearing restrictive attributes on "%~1"
call attrib %_CLEAR_ARGS% "%~1"
if errorlevel 1 goto error_clearattrs
goto :EOF

:restoreattrs
rem Restores previously clear attributes.
if "%_RESTORE_ARGS%x"=="x" goto error_restoreattrs1
echo  - Restoring restrictive attributes on "%~1"
call attrib %_RESTORE_ARGS% "%~1"
if errorlevel 1 goto error_restoreattrs2
goto :EOF

:renamedir
rem Rename our virtualenv directories with error checking.
setlocal
set "_SRC=%~dp0%~1"
set "_DEST=%~dp0%~2"

rem Grab the file attributes of the source and clear the attributes that will
rem prevent us from renaming the file.
call :clearattrs "%_SRC%"
if errorlevel 1 exit /B %ERRORLEVEL%

rem Rename the folder
echo  - Renaming %~1 to %~2..
call move /Y "%_SRC%" "%_DEST%">nul 2>nul
if errorlevel 1 goto error_renamedir

rem Restore attributes to the newly renamed directory
call :restoreattrs "%_DEST%"
if errorlevel 1 exit /B %ERRORLEVEL%
endlocal & goto :EOF

:use_python2
rem Switch active python install to python2
echo Switching to Python 2..
call :renamedir .vip .vip3
if errorlevel 1 exit /B %ERRORLEVEL%
call :renamedir .vip2 .vip
if errorlevel 1 exit /B %ERRORLEVEL%
goto :EOF

:use_python3
rem Switch active python install to python3
echo Switching to Python 3..
call :renamedir .vip .vip2
if errorlevel 1 exit /B %ERRORLEVEL%
call :renamedir .vip3 .vip
if errorlevel 1 exit /B %ERRORLEVEL%
goto :EOF

:main
rem Entrypoint
set _SWITCHTO=
if exist "%~dp0.vip2" set _SWITCHTO=2
if exist "%~dp0.vip3" set _SWITCHTO=3
if "%_SWITCHTO%x"=="x" goto error_setup
goto use_python%_SWITCHTO%

:error_setup
echo ERROR: Unable to detect currently active Python version!
exit /B 1

:error_restoreattrs1
echo ERROR: restoreattrs requires a previous call to clearattrs!
exit /B 1

:error_restoreattrs2
echo ERROR: Failed to restore attributes on %~1!
exit /B 1

:error_clearattrs
echo ERROR: Failed to clear attributes on %~1!
exit /B 1

:error_renamedir
set _ERRORLEVEL=%ERRORLEVEL%
echo.
echo ERROR: Failure while attempting to rename:
echo   From:  %_SRC%
echo   To:    %_DEST%
echo   Error: %_ERRORLEVEL%!
exit /B %_ERRORLEVEL%
