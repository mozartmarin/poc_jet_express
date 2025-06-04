# Caminho base do repositório principal
$basePath = "$HOME\Documents\Projetos\mozartmarin"

# Lista dos projetos com seus nomes e URLs
$projetos = @{
    "chat-mistral-pdf"        = "https://github.com/mozartmarin/chat-mistral-pdf.git"
    "projeto_inicial_jornada" = "https://github.com/mozartmarin/projeto_inicial_jornada.git"
    "poc_previsao_inovamed"   = "https://github.com/mozartmarin/poc_previsao_inovamed.git"
    "mistral_ocr"             = "https://github.com/mozartmarin/mistral_ocr.git"
    "hotel_ia_poc"            = "https://github.com/mozartmarin/hotel_ia_poc.git"
    "chatbot_refinador_gpt4"  = "https://github.com/mozartmarin/chatbot_refinador_gpt4.git"
}

# Cria pasta 'projects' se não existir
$projectsDir = Join-Path $basePath "projects"
if (-Not (Test-Path $projectsDir)) {
    New-Item -ItemType Directory -Path $projectsDir | Out-Null
}

# Entrar na pasta base
Set-Location $basePath

foreach ($nome in $projetos.Keys) {
    $url = $projetos[$nome]
    $tempDir = "$basePath\$nome"
    $destDir = "$projectsDir\$nome"

    # Clonar projeto
    git clone $url

    # Criar destino e mover arquivos
    if (-Not (Test-Path $destDir)) {
        New-Item -ItemType Directory -Path $destDir | Out-Null
    }

    Get-ChildItem -Path $tempDir -Force | Where-Object { $_.Name -ne '.git' } | ForEach-Object {
        Move-Item -Path $_.FullName -Destination $destDir -Force
    }

    # Remover pasta original clonada
    Remove-Item -Recurse -Force $tempDir
}

Write-Host "`n✅ Projetos sincronizados para 'projects/'."
Write-Host "Agora execute: git add . && git commit -m 'Importar projetos para pasta projects' && git push"
