# Convierte base_inicial.sql de UTF-16 a UTF-8 (PostgreSQL en Docker).
$path = Join-Path $PSScriptRoot "base_inicial.sql"
$bytes = [System.IO.File]::ReadAllBytes($path)
if ($bytes.Length -ge 2 -and $bytes[0] -eq 0xFF -and $bytes[1] -eq 0xFE) {
    $text = [System.Text.Encoding]::Unicode.GetString($bytes)
} elseif ($bytes.Length -ge 2 -and $bytes[0] -eq 0xFE -and $bytes[1] -eq 0xFF) {
    $text = [System.Text.Encoding]::BigEndianUnicode.GetString($bytes)
} else {
    Write-Host "base_inicial.sql ya parece UTF-8."
    exit 0
}
if ($text.Length -gt 0 -and [int][char]$text[0] -eq 0xFEFF) { $text = $text.Substring(1) }
$text = $text -replace "`r`n", "`n" -replace "`r", "`n"
$utf8 = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText($path, $text, $utf8)
Write-Host "Convertido. Ejecuta: docker compose down -v; docker compose up --build"
