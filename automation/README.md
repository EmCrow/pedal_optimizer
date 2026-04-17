# Automation

## Cross-platform build (single command)
```bash
python3 build_app.py
```

- Build script creates a temporary virtualenv, installs requirements, builds with PyInstaller, and cleans temporary files.
- Previous executable artifacts are backed up to `backups/executable_backup_<timestamp>/`.
- Run sensitive guard before push:
  ```bash
  ./automation/check_sensitive_files.sh
  ```
