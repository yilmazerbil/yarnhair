# PyInstaller recipe: pyinstaller packaging/YarnSection.spec --noconfirm
import sys
from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = [], [], ["openpyxl", "scipy.stats"]
for pkg in ("skimage",):          # lazily loaded submodules and their .pyi stubs
    d, b, h = collect_all(pkg)
    datas += d; binaries += b; hiddenimports += h

a = Analysis(["yarnsection_gui.py"], pathex=[".."], binaries=binaries, datas=datas,
             hiddenimports=hiddenimports, excludes=["tkinter", "matplotlib", "pytest"])
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="YarnSection", console=False,
          argv_emulation=False)
coll = COLLECT(exe, a.binaries, a.datas, name="YarnSection")
if sys.platform == "darwin":
    app = BUNDLE(coll, name="YarnSection.app", bundle_identifier="io.github.yarnhair.yarnsection",
                 info_plist={"NSHighResolutionCapable": True, "CFBundleShortVersionString": "1.0.0"})
