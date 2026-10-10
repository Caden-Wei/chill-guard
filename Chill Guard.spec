# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files

model_data = [('yolo26s.pt', '.'), ('yolo11s.pt', '.'), ('yolo11n.pt', '.')]
for package in Path('.models').glob('*.mlpackage'):
    manifest = Path(str(package) + '.json')
    if manifest.is_file():
        model_data.extend([(str(package), '.models/' + package.name), (str(manifest), '.models')])

a = Analysis(
    ['chill_guard_app.py'],
    pathex=[],
    binaries=[],
    datas=model_data + [('assets/ui', 'assets/ui'), ('assets/app_icon_1024.png', 'assets')] + collect_data_files('customtkinter'),
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
    bundle_identifier='com.ghostv.chillguard',
    info_plist={
        'CFBundleDisplayName': 'Chill Guard',
        'CFBundleName': 'Chill Guard',
        'CFBundleShortVersionString': '1.2.3',
        'CFBundleVersion': '20261010.3',
        'NSCameraUsageDescription': 'Chill Guard needs camera access to detect nearby people and trigger privacy protection.',
        'NSAppleEventsUsageDescription': 'Chill Guard needs automation access to hide selected apps when a risk target is detected.',
    },
)
