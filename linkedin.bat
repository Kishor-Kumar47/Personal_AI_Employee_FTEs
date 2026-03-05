@echo off
REM LinkedIn Poster - Easy Launcher
REM Usage: linkedin.bat [command] [options]

set SKILLS_DIR=%~dp0.qwen\skills\linkedin-poster

if "%1"=="" goto :help
if "%1"=="login" goto :login
if "%1"=="post" goto :post
if "%1"=="schedule" goto :schedule
if "%1"=="help" goto :help

goto :help

:login
echo Opening LinkedIn for login...
python "%SKILLS_DIR%\linkedin_poster.py" login
goto :end

:post
shift
python "%SKILLS_DIR%\linkedin_poster.py" post %*
goto :end

:schedule
shift
python "%SKILLS_DIR%\linkedin_poster.py" schedule %*
goto :end

:help
echo.
echo LinkedIn Poster - Post updates to LinkedIn
echo.
echo Usage:
echo   linkedin.bat login              - Login to LinkedIn
echo   linkedin.bat post --content "Your message"  - Post update
echo   linkedin.bat schedule --content "Message" --time "2026-03-02T09:00:00"
echo.
echo Examples:
echo   linkedin.bat login
echo   linkedin.bat post --content "Excited to share our AI Employee project! #AI"
echo   linkedin.bat post --content "Business update" --image "C:\path\to\image.png"
echo.

:end
