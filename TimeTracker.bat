:: filepath: TimeTracker.bat
@echo off
echo Starting app.py...
start cmd /k python "website\app.py"

echo Starting writescript.py...
start cmd /k python "website\writescript.py"

echo Waiting for the web server to start...
timeout /t 5 >nul

echo Opening the website in the default browser...
start http://127.0.0.1:5000

echo Both scripts have been started, and the website is open.
