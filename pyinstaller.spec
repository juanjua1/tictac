"""
PyInstaller spec para generar un ejecutable de una sola pieza.
Build (Windows recomendado ejecutarlo en Windows):
    pyinstaller --clean --onefile --name t3bot pyinstaller.spec
Salida:
    dist/t3bot.exe (Windows) o dist/t3bot (Linux)

Nota: Los YAML de flujo se leen desde el disco (misma carpeta que el .exe). Copiá el .yaml junto al ejecutable.
"""

block_cipher = None

from PyInstaller.utils.hooks import copy_metadata
import glob

a = Analysis(
    ['src/scraper/cli.py'],
    pathex=['.'],
    binaries=[],
    datas=copy_metadata('playwright') +
          [(f, '.') for f in glob.glob('flow_spec*.yaml')] +
          [(f, '.') for f in glob.glob('flow_spect*.yaml')] +
          [('windows/README_WINDOWS.md', 'windows'), ('windows/run_t3bot.bat', 'windows')],
    hiddenimports=['playwright', 'playwright.sync_api', 'dotenv', 'yaml', 'rich'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='t3bot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
