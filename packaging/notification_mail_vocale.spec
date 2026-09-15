# -*- mode: python ; coding: utf-8 -*-
# Fichier de build PyInstaller — génère un exécutable autonome.
# À lancer séparément sur chaque OS cible : PyInstaller ne compile pas
# un exécutable Windows depuis Linux/macOS, ni l'inverse.
#
# Utilisation :
#   pyinstaller packaging/notification_mail_vocale.spec
#
# L'exécutable est produit dans dist/NotificationMailVocale (ou .exe sous Windows).

import sys

block_cipher = None

hidden_imports = [
    "keyring.backends",
    "keyring.backends.Windows",
    "keyring.backends.macOS",
    "keyring.backends.SecretService",
    "keyring.backends.kwallet",
    "pystray._base",
]

# Backends spécifiques à la plateforme de build en cours
if sys.platform == "darwin":
    hidden_imports += ["pyobjc"]
elif sys.platform == "win32":
    hidden_imports += ["win32com.client"]

a = Analysis(
    ["../main.py"],
    pathex=["../"],
    binaries=[],
    datas=[
        ("../config.example.yaml", "."),
    ],
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="NotificationMailVocale",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,       # pas de fenêtre console (app de fond avec icône barre système)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,            # ex : "icon.ico" (Windows) ou "icon.icns" (macOS)
)

if sys.platform == "darwin":
    app = BUNDLE(
        exe,
        name="NotificationMailVocale.app",
        icon=None,
        bundle_identifier="com.exemple.notificationmailvocale",
        info_plist={
            "LSUIElement": True,  # cache l'icône du Dock (app "menu bar only")
            "NSHighResolutionCapable": True,
        },
    )
