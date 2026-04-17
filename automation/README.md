# Automation

## Cross-platform build (single command)
```bash
python3 build_app.py
```

- Build script creates a temporary virtualenv, installs requirements, builds with PyInstaller, and cleans temporary files.
- Dependency install now auto-falls back between legacy/new Qt stacks when needed.
- On macOS 10.x, use Python 3.10/3.11 for compatible Qt5 wheels.
- Previous executable artifacts are backed up to `backups/executable_backup_<timestamp>/`.
- Run sensitive guard before push:
  ```bash
  ./automation/check_sensitive_files.sh
  ```
