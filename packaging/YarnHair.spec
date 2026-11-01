# PyInstaller recipe: pyinstaller packaging/YarnHair.spec --noconfirm
import sys
from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = [], [], ["openpyxl"]
for pkg in ("skimage",):          # lazily loaded submodules and their .pyi stubs
    d, b, h = collect_all(pkg)
    datas += d; binaries += b; hiddenimports += h

a = Analysis(["yarnhair_gui.py"], pathex=[".."], binaries=binaries, datas=datas,
             hiddenimports=hiddenimports, excludes=["tkinter", "matplotlib", "pytest"])
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="YarnHair", console=False,
          argv_emulation=False)
coll = COLLECT(exe, a.binaries, a.datas, name="YarnHair")
if sys.platform == "darwin":
    app = BUNDLE(coll, name="YarnHair.app", bundle_identifier="io.github.yarnhair",
                 info_plist={"NSHighResolutionCapable": True, "CFBundleShortVersionString": "1.0.0"})
