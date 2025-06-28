@echo off
cd /d %~dp0

echo =============================
echo Verificando ambiente virtual
echo =============================

if not exist venv\Scripts\activate.bat (
    echo Ambiente virtual não encontrado.
    echo Criando novo ambiente com Python 3.12...
    py -3.12 -m venv venv
)

echo.
echo =============================
echo Ativando o ambiente virtual
echo =============================

call venv\Scripts\activate.bat

echo.
echo =============================
echo Instalando dependências do requirements.txt
echo =============================

pip install --upgrade pip
pip install -r requirements.txt

echo.
echo =============================
echo Iniciando o sistema Projeto Dignidade
echo =============================

python app.py

pause

