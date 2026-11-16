"""Modelo de uma orientação pública. Sem bibliotecas externas."""

from datetime import date
from urllib.parse import urlparse


class Orientacao:
    CAMPOS_OBRIGATORIOS = (
        "id", "categoria", "titulo", "palavras_chave", "resposta",
        "documentos", "onde", "fonte", "verificado_em",
    )

    def __init__(self, id, categoria, titulo, palavras_chave, resposta,
                 documentos, onde, fonte, verificado_em):
        self.id = id
        self.categoria = categoria
        self.titulo = titulo
        self.palavras_chave = palavras_chave
        self.resposta = resposta
        self.documentos = documentos
        self.onde = onde
        self.fonte = fonte
        self.verificado_em = verificado_em

    @classmethod
    def de_dicionario(cls, dados):
        """Valida a estrutura antes de criar o objeto."""
        if not isinstance(dados, dict):
            raise ValueError("A orientação deve ser um dicionário")
        ausentes = [campo for campo in cls.CAMPOS_OBRIGATORIOS if campo not in dados]
        if ausentes:
            raise ValueError("Campos ausentes: " + ", ".join(ausentes))
        if type(dados["id"]) is not int or dados["id"] <= 0:
            raise ValueError("id deve ser um inteiro positivo")
        for campo in ("categoria", "titulo", "resposta", "onde", "fonte"):
            if not isinstance(dados[campo], str) or not dados[campo].strip():
                raise ValueError(f"{campo} deve ser texto não vazio")
        for campo in ("palavras_chave", "documentos"):
            itens = dados[campo]
            if not isinstance(itens, list) or not itens or not all(
                isinstance(item, str) and item.strip() for item in itens
            ):
                raise ValueError(f"{campo} deve ser lista de textos não vazios")
        if len(dados["palavras_chave"]) < 3:
            raise ValueError("Cada orientação precisa de 3 palavras-chave ou mais")
        try:
            date.fromisoformat(dados["verificado_em"])
        except (ValueError, TypeError) as erro:
            raise ValueError("verificado_em deve usar AAAA-MM-DD") from erro
        url = urlparse(dados["fonte"])
        if url.scheme != "https" or not url.netloc:
            raise ValueError("fonte deve ser um endereço HTTPS")
        return cls(**{campo: dados[campo] for campo in cls.CAMPOS_OBRIGATORIOS})

    def exibir(self, confianca=None, pontos=None):
        """Exibe somente conteúdo conferido na base, com fonte e aviso."""
        print("\n" + "=" * 65)
        if confianca == "DIRETA":
            print("Seleção por categoria (não usa pontuação)")
        elif confianca:
            print(f"Confiança da resposta: {confianca} ({pontos} pontos)")
        print(f">> {self.titulo} [{self.categoria}]")
        print(self.resposta)
        print("Documentos ou requisitos indicados:")
        for item in self.documentos:
            print(f"  - {item}")
        print(f"Onde: {self.onde}")
        print(f"Fonte: {self.fonte} (verificado em {self.verificado_em})")
        print("Aviso: este assistente NÃO é um canal oficial.")
        print("=" * 65)
