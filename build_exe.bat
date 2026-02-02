@echo off
chcp 65001

echo ==========================================
echo      СБОРКА ЧЕРЕЗ VENV (HARD MODE)
echo ==========================================

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist


set VENV_PYTHON=C:\Users\Falke\AmazonInventoryHub\venv\Scripts\python.exe


"%VENV_PYTHON%" -m PyInstaller --noconsole --onefile ^
 --name="AmazonManager" ^
 --icon="Amazon.ico" ^
 --collect-all customtkinter ^
 --hidden-import=PIL ^
 --hidden-import=psycopg2 ^
 app_main.py

echo.
echo ==========================================
pause
