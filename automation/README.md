# Automation

## macOS
```bash
./automation/build_macos.sh arm64
./automation/build_macos.sh x86_64
./automation/build_macos.sh universal2
```

## Windows (run from PowerShell on Windows)
```powershell
.\automation\build_windows.ps1
```

## Notes
- Scripts create timestamped executable backups in `backups/`.
- PyInstaller spec file is shared from repo root (`PedalArchitect.spec`).
