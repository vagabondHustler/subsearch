# -*- mode: python ; coding: utf-8 -*-


block_cipher = None
added_files = [
         ( '..\\src\\subsearch\\data\\*.json', 'subsearch\\data\\' )
         ]
added_binaries = [
        ('..\\src\\subsearch\\assets\\icons\\*.ico', 'subsearch\\assets\\icons\\'),
        ('..\\src\\subsearch\\assets\\buttons\\*.png', 'subsearch\\assets\\buttons\\')
        ('..\\src\\subsearch\\assets\\tabs\\*.png', 'subsearch\\assets\\tabs\\')
        ]

a = Analysis(
    ['..\\src\\subsearch\\__main__.py'],
    pathex=[],
    binaries=added_binaries,
    datas=added_files,
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
    name='Subsearch',
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
    icon='..\\src\\subsearch\\assets\\icons\\256.ico',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Subsearch',
)
