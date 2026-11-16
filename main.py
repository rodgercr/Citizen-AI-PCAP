"""Ponto de entrada: executar com `python main.py`."""

from pathlib import Path

from assistente import Assistente
from base_conhecimento import BaseConhecimento


def main():
    diretorio = Path(__file__).resolve().parent
    base = BaseConhecimento(diretorio / "data" / "base_conhecimento.json")
    base.carregar()
    assistente = Assistente("Citizen Assist AI", base)
    assistente.executar()


if __name__ == "__main__":
    main()
