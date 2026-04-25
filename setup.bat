@echo off
echo ============================================
echo   Gruha Alankara - Setup
echo ============================================
echo.
echo Installing Python dependencies...
pip install -r requirements.txt
echo.
echo Seeding database...
python seed.py
echo.
echo ============================================
echo   Setup complete! Run: run.bat
echo ============================================
pause
