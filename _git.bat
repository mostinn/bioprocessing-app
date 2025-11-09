@echo off
REM Git committing and pushing
REM cd /d "C:\Users\mstef\OneDrive\Documents\Tolvur-Computers\Pyton-apps\Bioprocessing-app"

echo.
echo === Adding changes to Git ===
git add .
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to add files.
    exit /b %ERRORLEVEL%
)

echo.
echo === Committing changes ===
git commit -m "Updating to include about page."
IF %ERRORLEVEL% NEQ 0 (
    echo [INFO] No changes to commit or commit failed.
)

echo.
echo === Pushing to GitHub ===
git push origin main
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Push failed.
    exit /b %ERRORLEVEL%
)

echo.
echo [SUCCESS] GitHub updated successfully.
pause