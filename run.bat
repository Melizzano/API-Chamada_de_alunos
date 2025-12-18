@echo off
REM ====================================================
REM run.bat - Inicia servidor Django
REM ====================================================

echo.
echo ====================================================
echo   INICIANDO SISTEMA DE CHAMADA - IFB
echo ====================================================
echo.

REM Verificar se estamos na pasta raiz
if not exist "src\backend\manage.py" (
    echo ERRO: Execute este script da PASTA RAIZ do projeto.
    pause
    exit /b 1
)

REM Ativar venv se existir
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

echo Iniciando servidor Django...
echo.
echo URLs:
echo - Admin:     http://127.0.0.1:8000/admin/
echo - API Docs:  http://127.0.0.1:8000/api/schema/swagger/
echo - API:       http://127.0.0.1:8000/api/
echo.
echo Pressione CTRL+C para parar.
echo.

REM Abrir navegador no admin após 2 segundos
echo Abrindo navegador em 2 segundos...
timeout /t 2 /nobreak >nul
start http://127.0.0.1:8000/admin/

cd src\backend
python manage.py runserver
cd ..\..

if %errorlevel% neq 0 (
    echo.
    echo ERRO: Nao foi possivel iniciar o servidor.
    echo Verifique se:
    echo 1. O banco de dados foi criado (execute reset_db.bat)
    echo 2. As migracoes foram aplicadas
    echo 3. Nao ha outro servidor rodando na porta 8000
    pause
)