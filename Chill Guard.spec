# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['chill_guard_app.py'],
    pathex=[],
    binaries=[],
    datas=[('yolo11s.pt', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'polars',
        '_polars_runtime_32',
        'polars_cloud',
        'scipy',
        'matplotlib',
    ],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Chill Guard',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Chill Guard',
)
app = BUNDLE(
    coll,
    name='Chill Guard.app',
    icon='assets/app_icon_1024.png',
    bundle_identifier='io.github.ghostv.chillguard',
    info_plist={
        'CFBundleDisplayName': 'Chill Guard',
        'CFBundleName': 'Chill Guard',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1',
        'NSCameraUsageDescription': 'Chill Guard needs camera access to detect nearby people and trigger privacy protection.',
        'NSAppleEventsUsageDescription': 'Chill Guard needs automation access to hide selected apps when a risk target is detected.',
    },
)
