from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules

root = Path(SPECPATH)
hiddenimports = collect_submodules('google.genai') + ['PyQt6.sip']
datas = [
    (str(root / 'ui' / 'resources'), 'ui/resources'),
    (str(root / 'ui' / 'styles'), 'ui/styles'),
    (str(root / 'core' / 'wisely.db'), 'core'),
]

block_cipher = None
a = Analysis(
    [str(root / 'ui' / 'main.py')],
    pathex=[str(root), str(root / 'ui')],
    binaries=[], datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[], hooksconfig={}, runtime_hooks=[],
    excludes=[], noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz, a.scripts, a.binaries, a.datas, [],
    name='Wisely', debug=False, bootloader_ignore_signals=False,
    strip=False, upx=True, console=False,
    icon=str(root / 'ui' / 'resources' / 'icons' / 'icon.ico'),
)
