param(
  [string]$PythonExe = "python",
  [string]$SpecPath = "PedalArchitect.spec"
)

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $Root

$stamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$backup = Join-Path $Root "backups/executable_backup_$stamp"
New-Item -ItemType Directory -Path $backup -Force | Out-Null

$targets = @("PedalArchitect.exe", "PedalArchitect")
foreach ($target in $targets) {
  $full = Join-Path $Root $target
  if (Test-Path $full) {
    Move-Item -Path $full -Destination (Join-Path $backup $target)
  }
}

& $PythonExe -m PyInstaller --noconfirm --clean --distpath $Root --workpath (Join-Path $Root "build/windows") $SpecPath
Write-Host "Windows build complete."
Write-Host "Backup directory: $backup"
