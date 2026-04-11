@echo off
echo ================================================
echo     RielAI SuperBot - Starting...
echo ================================================
cd /d "%~dp0"
call venv\Scripts\activate
echo ✅ Venv activated
echo 🚀 Starting bot...
python main.py
pause