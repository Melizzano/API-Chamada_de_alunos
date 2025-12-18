@echo off
REM ====================================================
REM populate_demo.bat - Popula banco com dados demo
REM ====================================================

echo.
echo ====================================================
echo   POPULANDO BANCO COM DADOS DEMO - IFB
echo ====================================================
echo.

if not exist "src\backend\scripts\populate_demo.py" (
    echo ERRO: Execute da pasta raiz do projeto.
    pause
    exit /b 1
)

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

cd src\backend
python scripts\populate_demo.py
cd ..\..
pause