@echo off  
setlocal
goto getopt

:strip_dir
call set "%~1=%%~2"
call set "_LAST_CHAR=%%%~1:~-1%%"
if "%_LAST_CHAR%x"=="\x" call set "%~1=%%%~1:~0,-1%%"
set _LAST_CHAR=
goto :EOF

:usage
echo Usage: %~nx0 [-h^|-?^|--help] [target-dir]
echo.
echo   -h,-?,--help: Prints this helpful help text.
echo     target-dir: Directory to search and clean. ^(default=.^)
goto :EOF

:getopt
rem Parse command line arguments
rem Start by clearing any existing value in the _ARG environment variable.
set _ARG=

rem Then default our target directory to the current working directory.
set "_TARGETDIR=%CD%"
:getopt_loop
rem Inner loop of getopt
if "%~1x"=="x" goto main
set _ISFLAG=
set "_ARG=%~1"
shift /1
if "%_ARG:~0,1%x"=="-x" set _ISFLAG=1
if "%_ARG:~0,1%x"=="/x" set _ISFLAG=1
if not defined _ISFLAG goto getopt_arg
:getopt_flag
if /i "%~1x"=="hx" goto usage
if /i "%~1x"=="?x" goto usage
if /i "%~1x"=="-helpx" goto usage
echo [ERROR] Unrecognized flag/option: "%~1"
echo.
goto usage
:getopt_arg
set "_TARGETDIR=%~f1"
if "%_TARGETDIR:~-1%"=="\" set "_TARGETDIR=%_TARGETDIR:~0,-1%"
goto getopt_loop

:test_dir
setlocal
set "_ORIGDIR=%~1"
set "_SEARCH=\%~2\"
call set "_TESTDIR=%%_ORIGDIR:%_SEARCH%=%%"
if not "%_ORIGDIR%"=="%_TESTDIR%" endlocal & exit /B 1
endlocal
goto :EOF

:cleanup
rem Cleans all .pyc files and __pycache__ folders from the directory.
rem Checks directory path for occurences of ".git" and ".svn" to determine
rem whether or not this directory should be excluded from our search.
set _LOCATED_PYC=
call :strip_dir _CLEANDIR "%~1"
call :test_dir "%_CLEANDIR%" .git
if errorlevel 1 (verify>nul) & goto :EOF
call :test_dir "%_CLEANDIR%" .svn
if errorlevel 1 (verify>nul) & goto :EOF
call :test_dir "%_CLEANDIR%" .hg
if errorlevel 1 (verify>nul) & goto :EOF
if exist "%_CLEANDIR%\*.pyc" del /F /Q "%_CLEANDIR%\*.pyc" & set _LOCATED_PYC=1
if exist "%_CLEANDIR%\*.pyo" del /F /Q "%_CLEANDIR%\*.pyo" & set set _LOCATED_PYC=1
if exist "%_CLEANDIR%\__pycache__" rmdir /S /Q "%_CLEANDIR%\__pycache__" & set _LOCATED_PYC=1
if defined _LOCATED_PYC echo Compiled python files found at: "%_CLEANDIR%"
goto :EOF

:main
rem Entrypoint after option parsing
echo Searching child folders of "%_TARGETDIR%"..
for /R "%_TARGETDIR%" %%D in (.) do @call :cleanup "%%~fD"
