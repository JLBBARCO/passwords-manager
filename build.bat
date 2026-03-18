@echo off
echo ================================================
echo   Password Manager - Build Script (Simple)
echo ================================================
echo.

if not exist ".venv\Scripts\python.exe" (
echo Criando .venv...
python -m venv .venv
)

call ".venv\Scripts\activate.bat"

echo Instalando PyInstaller...
pip install pyinstaller

echo.
echo Compilando programa...
python -m PyInstaller --onefile --noconsole --icon=src/assets/icon/passwords-manager.ico --name=passwords-manager main.py

echo.
echo ================================================
echo   Build concluido!
echo ================================================
echo.
echo Executavel gerado em: dist\passwords-manager.exe
echo.
echo Para build mais completo com empacotamento, use:
echo   powershell -ExecutionPolicy Bypass -File build-local.ps1
echo.
pause