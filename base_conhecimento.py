"""Leitura de JSON e busca baseada exclusivamente em regras verificáveis."""

import json
import re
import unicodedata
from pathlib import Path

from orientacao import Orientacao


def normalizar(texto):
    """Remove acentos e pontuação, normaliza espaços e usa minúsculas.

    Espaços nas bordas impedem que 'sus' corresponda a 'susto'.
    """
    sem_acentos = "".join(
        caractere for caractere in unicodedata.normalize("NFD", texto.casefold())
        if unicodedata.category(caractere) != "Mn"
    )
    sem_pontuacao = re.sub(r"[^a-z0-9\s]", " ", sem_acentos)
    return " " + " ".join(sem_pontuacao.split()) + " "


class BaseConhecimento:
    def __init__(self, caminho):
        self.caminho = Path(caminho)
        self.orientacoes = []

    def carregar(self):
        """Carrega registros válidos e não trava em arquivo ausente/corrompido."""
        self.orientacoes = []
        try:
            with self.caminho.open("r", encoding="utf-8") as arquivo:
                registros = json.load(arquivo)
            if not isinstance(registros, list):
                raise ValueError("O JSON deve conter uma lista")
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as erro:
            print(f"[AVISO] Não foi possível carregar a base: {erro}")
            return False

        ids = set()
        for indice, dados in enumerate(registros, start=1):
            try:
                orientacao = Orientacao.de_dicionario(dados)
                if orientacao.id in ids:
                    raise ValueError(f"id duplicado: {orientacao.id}")
                ids.add(orientacao.id)
                self.orientacoes.append(orientacao)
            except ValueError as erro:
                print(f"[AVISO] Registro {indice} ignorado: {erro}")

        if not self.orientacoes:
            print("[AVISO] Nenhuma orientação válida foi encontrada.")
            return False
        return True

    def categorias(self):
        return sorted({item.categoria for item in self.orientacoes})

    def por_categoria(self, categoria):
        return [item for item in self.orientacoes if item.categoria == categoria]

    def pontuar(self, pergunta, orientacao):
        """+3 por chave correspondente; +1 por palavra (>=4) do título."""
        pergunta_normalizada = normalizar(pergunta)
        titulo_normalizado = normalizar(orientacao.titulo)
        pontos = 0
        for palavra_chave in orientacao.palavras_chave:
            if normalizar(palavra_chave) in pergunta_normalizada:
                pontos += 3
        palavras_pergunta = {
            palavra for palavra in pergunta_normalizada.split() if len(palavra) >= 4
        }
        for palavra in palavras_pergunta:
            if f" {palavra} " in titulo_normalizado:
                pontos += 1
        return pontos

    def buscar(self, pergunta):
        """Retorna tuplas (pontuação, Orientacao), ordenadas decrescentemente."""
        resultados = [
            (self.pontuar(pergunta, orientacao), orientacao)
            for orientacao in self.orientacoes
        ]
        resultados = [item for item in resultados if item[0] > 0]
        return sorted(resultados, key=lambda item: (-item[0], item[1].id))

    @staticmethod
    def confianca(pontos):
        if pontos >= 6:
            return "ALTA"
        if pontos >= 3:
            return "MÉDIA"
        return "NÃO ENCONTRADA"
