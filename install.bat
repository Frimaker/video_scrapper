@echo off
setlocal
cd /d "%~dp0"

echo [1/2] Instalando dependencias Python...
python -m pip install --upgrade pip
if errorlevel 1 goto erro
python -m pip install -r requirements.txt
if errorlevel 1 goto erro

echo [2/2] Baixando modelo semantico do Hugging Face...
python hugger.py
if errorlevel 1 goto erro

echo.
echo Instalacao concluida.
pause
exit /b 0

:erro
echo.
echo A instalacao falhou. Confira a mensagem acima e tente novamente.
pause
exit /b 1
