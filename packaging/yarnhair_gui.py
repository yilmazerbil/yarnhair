"""Entry point of the double-click program built with PyInstaller."""
import multiprocessing
import sys

from yarnhair.gui.app import main

if __name__ == "__main__":
    multiprocessing.freeze_support()   # worker processes of the frozen program
    sys.exit(main())
