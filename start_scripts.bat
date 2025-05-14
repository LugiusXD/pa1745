:: filepath: start_scripts.bat
@echo off
echo Starting app.py...
start cmd /k python "website\app.py"

echo Starting writescript.py...
start cmd /k python "website\writescript.py"

echo Both scripts have been started.
