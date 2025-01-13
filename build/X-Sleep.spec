# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['/home/kaloian/PycharmProjects/x-sleepGUI/main.pyw'],
    pathex=[],
    binaries=[],
    datas=[('/home/kaloian/PycharmProjects/x-sleepGUI/app', 'app/')],
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
    name='X-Sleep',
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
    version='/home/kaloian/PycharmProjects/x-sleepGUI/build/version.rc',
    icon=['/home/kaloian/PycharmProjects/x-sleepGUI/app/media/x-sleep.ico'],
    contents_directory='.',
    onefile=True,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='X-Sleep',
)
