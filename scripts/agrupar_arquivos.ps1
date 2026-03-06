# Caminho base do projeto
$base = "D:\Workspace\2D-AEF"

# Pasta onde vamos juntar tudo relacionado ao artigo
$bundle = Join-Path $base "artefatos_artigo_2D-AEF"

# 1) Cria a pasta (se já existir, não dá erro)
New-Item -Path $bundle -ItemType Directory -Force | Out-Null

# 2) Copia o markdown principal do artigo
Copy-Item -Path (Join-Path $base "Artigo_2D_AEF-main.md") -Destination $bundle -Force

# 3) Copia as figuras (mantendo nomes e estrutura)
Copy-Item -Path (Join-Path $base "figs") -Destination $bundle -Recurse -Force

# 4) Copia os resultados principais (CSV, matrizes, etc.)
Copy-Item -Path (Join-Path $base "outputs\unsw_mc")              -Destination $bundle -Recurse -Force
Copy-Item -Path (Join-Path $base "outputs\cic_robust")           -Destination $bundle -Recurse -Force
Copy-Item -Path (Join-Path $base "outputs\cic_robust_all")       -Destination $bundle -Recurse -Force
Copy-Item -Path (Join-Path $base "outputs\cic_robust_xgb_baseline") -Destination $bundle -Recurse -Force

# 5) (Opcional) Gera um zip com tudo
$zipPath = "$bundle.zip"
if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
Compress-Archive -Path $bundle -DestinationPath $zipPath

Write-Host "Bundle criado em: $bundle"
Write-Host "ZIP criado em:   $zipPath"
