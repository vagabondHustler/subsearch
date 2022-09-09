# -*- mode: python ; coding: utf-8 -*-


block_cipher = None
added_files = [
         ( '..\\src\\subsearch\\data\\*.json', 'subsearch\\data\\' )
         ]
added_binaries = [
        ('..\\src\\subsearch\\gui\\assets\\btn\\*.png', 'subsearch\\gui\\assets\\btn\\'),
        ('..\\src\\subsearch\\gui\\assets\\checkbox\\*.png', 'subsearch\\gui\\assets\\checkbox\\'),
        ('..\\src\\subsearch\\gui\\assets\\icon\\*.ico', 'subsearch\\gui\\assets\\icon\\'),
        ('..\\src\\subsearch\\gui\\assets\\icon\\*.png', 'subsearch\\gui\\assets\\icon\\'),
        ('..\\src\\subsearch\\gui\\assets\\scale\\*.png', 'subsearch\\gui\\assets\\scale\\'),
        ('..\\src\\subsearch\\gui\\assets\\scrollbar\\*.png', 'subsearch\\gui\\assets\\scrollbar\\'),
        ('..\\src\\subsearch\\gui\\assets\\tabs\\*.png', 'subsearch\\gui\\assets\\tabs\\'),
        ('..\\src\\subsearch\\gui\\assets\\titlebar\\*.png', 'subsearch\\gui\\assets\\titlebar\\'),
        ('..\\src\\subsearch\\gui\\assets\\*.tcl', 'subsearch\\gui\\assets\\')

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
    icon='..\\src\\subsearch\\gui\\assets\\icon\\subsearch.ico',
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
