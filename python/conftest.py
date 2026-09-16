"""Põe este diretório no caminho de importação: os módulos e os testes estão lado a lado."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
