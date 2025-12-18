@echo off
REM ====================================================
REM setup.bat - Configurador do Projeto IFB
REM ====================================================

echo.
echo ====================================================
echo   CONFIGURANDO PROJETO IFB - SISTEMA DE CHAMADA
echo ====================================================
echo.

REM ----------------------------------------------------
REM Verificar se estamos na pasta raiz
REM ----------------------------------------------------
if not exist "src\backend\manage.py" (
    echo ERRO: Execute este script a partir da PASTA RAIZ do projeto.
    echo.
    echo Estrutura esperada:
    echo   API_CHAMADA_DE_ALUNOS\setup.bat
    echo   API_CHAMADA_DE_ALUNOS\src\backend\manage.py
    echo.
    pause
    exit /b 1
)

REM ----------------------------------------------------
REM Criar ambiente virtual
REM ----------------------------------------------------
echo Criando ambiente virtual Python...
echo.

if exist "venv" (
    echo Ambiente virtual 'venv' ja existe.
    echo Deseja recriar? (S/N)
    set /p recriar=
    if /i "%recriar%"=="S" (
        echo.
        echo Removendo ambiente virtual antigo...
        rmdir /s /q venv 2>nul
        python -m venv venv
        echo Ambiente virtual recriado com sucesso.
    ) else (
        echo.
        echo Usando ambiente virtual existente.
    )
) else (
    python -m venv venv
    echo Ambiente virtual criado com sucesso.
)

echo.

REM ----------------------------------------------------
REM AVISO IMPORTANTE SOBRE ATIVACAO DO VENV
REM ----------------------------------------------------
echo ====================================================
echo ATENCAO:
echo Durante a ativacao do ambiente virtual, o terminal
echo pode parecer que "travou".
echo.
echo Isso e NORMAL no Windows / VSCode.
echo.
echo Quando isso acontecer, apenas pressione ENTER
echo para que o script continue.
echo ====================================================
echo.

pause

REM ----------------------------------------------------
REM Ativar ambiente virtual
REM ----------------------------------------------------
echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

if %errorlevel% neq 0 (
    echo ERRO: Nao foi possivel ativar o ambiente virtual!
    pause
    exit /b 1
)

echo.
echo Ambiente virtual ativado com sucesso.
echo.

REM ----------------------------------------------------
REM Atualizar pip
REM ----------------------------------------------------
echo Atualizando pip...
python -m pip install --upgrade pip
echo pip atualizado com sucesso.
echo.

REM ----------------------------------------------------
REM Instalar dependencias
REM ----------------------------------------------------
echo Instalando dependencias do projeto...
cd src\backend

echo.
echo Instalando Django 5.2...
pip install Django==5.2

echo.
echo Instalando Django REST Framework...
pip install djangorestframework==3.15.2

echo.
echo Instalando dependencias adicionais...
pip install django-filter==24.3
pip install drf-spectacular==0.29.0
pip install asgiref==3.11.0
pip install sqlparse==0.5.3

echo.
echo Verificando requirements.txt...
if exist "requirements.txt" (
    echo requirements.txt encontrado.
    echo Instalando dependencias do arquivo...
    pip install -r requirements.txt
) else (
    echo AVISO: requirements.txt nao encontrado.
    echo Instalando dependencias basicas...
    pip install certifi idna pytz tzdata requests urllib3
)

cd ..\..

REM ----------------------------------------------------
REM Verificacoes finais
REM ----------------------------------------------------
echo.
echo ====================================================
echo   INSTALACAO CONCLUIDA!
echo ====================================================
echo.

echo Verificando instalacao do Django...
python -c "import django; print('Django:', django.__version__)" 2>nul
if %errorlevel% neq 0 (
    echo AVISO: Django nao parece estar instalado corretamente.
) else (
    echo Django instalado com sucesso!
)

echo.
echo Verificando instalacao do Django REST Framework...
python -c "import rest_framework; print('DRF:', rest_framework.VERSION)" 2>nul
if %errorlevel% neq 0 (
    echo AVISO: DRF nao parece estar instalado corretamente.
) else (
    echo DRF instalado com sucesso!
)

REM ----------------------------------------------------
REM Informacoes finais ao usuario
REM ----------------------------------------------------
echo.
echo PROXIMOS PASSOS:
echo 1. Execute reset_db.bat para criar o banco de dados
echo 2. Execute populate_demo.bat para popular com dados
echo 3. Execute run.bat para iniciar o servidor
echo.

echo COMANDOS DISPONIVEIS:
echo - reset_db.bat      : Reseta banco de dados
echo - populate_demo.bat : Popula com dados de demonstracao
echo - run.bat           : Inicia servidor Django
echo.

echo URLs DO SISTEMA:
echo - Admin:    http://127.0.0.1:8000/admin/
echo - API Docs: http://127.0.0.1:8000/api/schema/swagger/
echo.
echo Login padrao:
echo Usuario: admin
echo Senha:   admin123
echo.

pause
