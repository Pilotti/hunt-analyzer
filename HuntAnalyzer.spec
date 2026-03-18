# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('banco/*.json', 'banco'),
        ('imagens', 'imagens'),
        ('assets', 'assets'),
        ('telas', 'telas'),
        ('utils', 'utils'),
    ],
    hiddenimports=['customtkinter', 'bcrypt', 'PIL'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='HuntAnalyzer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    windowed=True,
)