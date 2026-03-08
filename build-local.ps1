# Script para Build Local do Password Manager
# Este script facilita o build local com as mesmas configurações do CI/CD

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Password Manager - Build Script" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Verifica se Python está instalado
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python não encontrado. Instale Python 3.8+ primeiro." -ForegroundColor Red
    exit 1
}

# Cria ambiente virtual se não existir
if (-not (Test-Path "venv")) {
    Write-Host ""
    Write-Host "Criando ambiente virtual..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✓ Ambiente virtual criado" -ForegroundColor Green
}

# Ativa ambiente virtual
Write-Host ""
Write-Host "Ativando ambiente virtual..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# Atualiza pip
Write-Host ""
Write-Host "Atualizando pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet

# Instala dependências
Write-Host ""
Write-Host "Instalando dependências..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
pip install pyinstaller --quiet
Write-Host "✓ Dependências instaladas" -ForegroundColor Green

# Limpa builds anteriores
Write-Host ""
Write-Host "Limpando builds anteriores..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "release") { Remove-Item -Recurse -Force "release" }
if (Test-Path "passwords-manager-windows.zip") { Remove-Item -Force "passwords-manager-windows.zip" }
Write-Host "✓ Limpeza concluída" -ForegroundColor Green

# Compila o programa
Write-Host ""
Write-Host "Compilando programa com PyInstaller..." -ForegroundColor Yellow
python -m PyInstaller --onefile --noconsole --icon=src/assets/icon/passwords-manager.ico --name=passwords-manager main.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Compilação concluída com sucesso!" -ForegroundColor Green
} else {
    Write-Host "✗ Erro na compilação" -ForegroundColor Red
    exit 1
}

# Prepara release
Write-Host ""
Write-Host "Preparando arquivos de release..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "release" | Out-Null
Copy-Item "dist\passwords-manager.exe" "release\"
Copy-Item "README.md" "release\"
Copy-Item "LICENSE" "release\"
Copy-Item "ENCRYPTION.md" "release\"
# Fallback to old name if it exists
if (!(Test-Path "ENCRYPTION.md") -and (Test-Path "CRIPTOGRAFIA.md")) {
    Copy-Item "CRIPTOGRAFIA.md" "release\ENCRYPTION.md"
}
Write-Host "✓ Arquivos preparados" -ForegroundColor Green

# Cria arquivo ZIP
Write-Host ""
Write-Host "Criando arquivo ZIP..." -ForegroundColor Yellow
Compress-Archive -Path "release\*" -DestinationPath "passwords-manager-windows.zip" -Force
Write-Host "✓ ZIP criado: passwords-manager-windows.zip" -ForegroundColor Green

# Exibe tamanho do arquivo
$zipSize = (Get-Item "passwords-manager-windows.zip").Length / 1MB
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Build concluído com sucesso!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Arquivo gerado: passwords-manager-windows.zip" -ForegroundColor White
Write-Host "Tamanho: $("{0:N2}" -f $zipSize) MB" -ForegroundColor White
Write-Host ""
Write-Host "Executável: release\passwords-manager.exe" -ForegroundColor White
Write-Host ""
Write-Host "Para testar o executável:" -ForegroundColor Yellow
Write-Host "  .\release\passwords-manager.exe" -ForegroundColor Cyan
Write-Host ""
