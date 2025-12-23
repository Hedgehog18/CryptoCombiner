# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [v0.0] – 2025-12-23

### Added
- Initial project architecture foundations.
- Base PySide6 UI application.
- Logging, configuration, and persistence infrastructure.
- Initial packaging pipeline using PyInstaller.
- First successful standalone `.exe` build for Windows.

### Packaging
- Verified working build using:
pyinstaller main.py --windowed --onefile
- Application launches correctly as a standalone `.exe`.
- UI renders correctly without runtime errors.
- No `.spec` file is used at this stage.

### Notes
- This entry documents a **technical baseline milestone**.
- Not intended as a user-facing release.
