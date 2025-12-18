@echo off
REM ====================================================
REM reset_db.bat - Reseta banco de dados
REM ====================================================

echo.
echo ====================================================
echo   RESETANDO BANCO DE DADOS - IFB
echo ====================================================
echo.

if not exist "src\backend\scripts\reset_database.py" (
    echo ERRO: Execute da pasta raiz do projeto.
    pause
    exit /b 1
)

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

cd src\backend
python scripts\reset_database.py
cd ..\..
pause