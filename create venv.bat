@echo off
chcp 65001 >nul
:: Переходим в папку, где лежит этот bat-файл
cd /d "%~dp0"

echo ==========================================
echo 🚀 Creating Python Virtual Environment in:
echo %CD%
echo ==========================================

python -m venv venv

call venv\Scripts\activate

python.exe -m pip install --upgrade pip

if exist requirements.txt (
    pip install -r requirements.txt
) else (
    pip install psycopg2-binary
)

echo.
echo ✅ DONE! Все готово, работаем братья!.
pause
