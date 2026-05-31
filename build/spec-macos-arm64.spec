# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['../src/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[('../assets', 'assets'), ('../config', 'config'), ('../version', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

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
    # Custom added
    # These keys are needed to completely hide the dock icon
    info_plist={
        'LSUIElement': True,
        'LSBackgroundOnly': True,
    },
)
