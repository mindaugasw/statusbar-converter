# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['../start.py'],
    pathex=[],
    binaries=[],
    datas=[('../assets', 'assets'), ('../config', 'config'), ('../version', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Statusbar Converter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='arm64',
    codesign_identity=None,
    entitlements_file=None,
    icon=['../assets/icon_macos.png'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Statusbar Converter',
)
app = BUNDLE(
    coll,
    name='Statusbar Converter.app',
    icon='../assets/icon_macos.png',
    bundle_identifier='com.mindaugasw.statusbar_converter',
    info_plist={
        # These keys are needed to completely hide the dock icon
        'LSUIElement': True,
        'LSBackgroundOnly': True,
    },
)
