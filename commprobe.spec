# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['commprobe.py'],
             pathex=['./socket-test'],
             binaries=[],
             datas=[('./res', 'res'), ('./mainwindow.ui', '.')],
             hiddenimports=['pyvisa_py'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='commprobe',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          icon='res/commprobe.ico' )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='commprobe')
