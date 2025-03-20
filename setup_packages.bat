@echo off
echo Installing required packages...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
echo.
echo Done! You can now run LightCraft using Launch_LightCraft.bat
echo.
pause
