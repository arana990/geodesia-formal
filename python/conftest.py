"""Puts this directory on the import path: the modules and the tests sit side by side."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
