"""Atendimento, menus, privacidade, histórico, indicadores e CSV."""

from base_conhecimento import normalizar

import csv
import json
import os
import shutil
import time
from datetime import datetime
from pathlib import Path
from uuid import uuid4


CAMPOS_CSV = (
    "data", "origem", "pergunta", "id_orientacao", "encontrou", "ajudou",
    "tentativas", "tempo_segundos", "facilidade", "sessao_id", "pontuacao", "confianca",
)


def contem_dados_pessoais(texto):
    """Regra do briefing: @ ou 8 ou mais dígitos, mesmo separados por sinais."""
    return "@" in texto or sum(caractere.isdigit() for caractere in texto) >= 8


def ler_entrada(mensagem):
    """Ctrl+C/EOF não lançam exceções para fora do programa."""
    try:
        return input(mensagem)
    except (EOFError, KeyboardInterrupt):
        print("\nEntrada encerrada.")
        return None


class Assistente:
    def __init__(self, nome, base, caminho_historico=None, caminho_csv=None):
        self.nome = nome
        self.base = base
        pasta_dados = base.caminho.parent
        self.caminho_historico = Path(caminho_historico or (pasta_dados / "historico.json"))
        self.caminho_csv = Path(caminho_csv or (pasta_dados / "atendimentos.csv"))
        self.historico = []
        self.sessao_id = uuid4().hex  # aleatório; não identifica pessoa
        self._tentativas_correntes = 0
        self._historico_corrompido = False
        self.carregar_historico()

    def carregar_historico(self):
        try:
            with self.caminho_historico.open("r", encoding="utf-8") as arquivo:
                historico = json.load(arquivo)
            if not isinstance(historico, list) or not all(
                isinstance(item, dict) for item in historico
            ):
                raise ValueError("O histórico precisa ser uma lista de dicionários")
            self.historico = historico
        except FileNotFoundError:
            self.historico = []
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as erro:
            print(f"[AVISO] Histórico ilegível, iniciando histórico vazio: {erro}")
            self._historico_corrompido = True
            self.historico = []

    def _salvar_historico(self):
        temporario = self.caminho_historico.with_name(self.caminho_historico.name + ".tmp")
        try:
            self.caminho_historico.parent.mkdir(parents=True, exist_ok=True)
            # Uma eventual cópia do arquivo danificado não é apagada silenciosamente.
            if self._historico_corrompido and self.caminho_historico.exists():
                copia = self.caminho_historico.with_suffix(".corrompido.bak")
                if not copia.exists():
                    shutil.copy2(self.caminho_historico, copia)
                self._historico_corrompido = False
            with temporario.open("w", encoding="utf-8") as arquivo:
                json.dump(self.historico, arquivo, ensure_ascii=False, indent=2)
            os.replace(temporario, self.caminho_historico)
        except OSError as erro:
            print(f"[AVISO] Não foi possível salvar o histórico: {erro}")
            try:
                temporario.unlink(missing_ok=True)
            except OSError:
                pass

    def registrar(self, origem, pergunta, orientacao=None, encontrou=False,
                  ajudou=None, tentativas=1, tempo_segundos=0.0,
                  pontuacao=None, confianca="NÃO ENCONTRADA"):
        """Nunca persiste uma pergunta que viole a regra de privacidade."""
        if contem_dados_pessoais(pergunta):
            print("Atenção: pergunta com dado pessoal recusada e NÃO registrada.")
            return None
        registro = {
            "data": datetime.now().astimezone().isoformat(timespec="seconds"),
            "origem": origem,
            "pergunta": pergunta,
            "id_orientacao": orientacao.id if orientacao else None,
            "encontrou": encontrou,
            "ajudou": ajudou,
            "tentativas": tentativas,
            "tempo_segundos": round(tempo_segundos, 1),
            "facilidade": None,
            "sessao_id": self.sessao_id,
            "pontuacao": pontuacao,
            "confianca": confianca,
        }
        self.historico.append(registro)
        self._salvar_historico()
        return registro

    def _perguntar_ajudou(self):
        while True:
            resposta = ler_entrada("Essa orientação respondeu sua dúvida? (s/n, 0 para voltar): ")
            if resposta is None or resposta.strip() == "0":
                return None
            resposta = resposta.strip().lower()
            if resposta in ("s", "sim"):
                return True
            if resposta in ("n", "nao", "não"):
                return False
            print("Opção inválida. Responda s, n ou 0.")

    def _registrar_resultado(self, origem, pergunta, orientacao, encontrou,
                             ajudou, inicio, pontos=None, confianca="DIRETA"):
        self._tentativas_correntes += 1
        registro = self.registrar(
            origem=origem, pergunta=pergunta, orientacao=orientacao,
            encontrou=encontrou, ajudou=ajudou,
            tentativas=self._tentativas_correntes,
            tempo_segundos=time.time() - inicio,
            pontuacao=pontos, confianca=confianca,
        )
        if registro is not None:
            print(f"Tempo do atendimento: {registro['tempo_segundos']:.1f} s")
        if ajudou is True:
            self._tentativas_correntes = 0
        return registro

    def responder_conversa(self, pergunta):
        """Respostas locais de apoio; não contam como atendimento de serviço."""
        texto = normalizar(pergunta).strip()
        for saudacao in ("oi ", "ola ", "bom dia ", "boa tarde ", "boa noite "):
            if texto.startswith(saudacao):
                texto = texto[len(saudacao):]
                break
        apresentacoes = {
            "quem e voce", "quem e vc", "quem voce e", "quem vc e",
            "qual seu nome", "qual e seu nome", "voce e um robo",
            "voce e um chatbot", "o que e voce",
        }
        ajuda = {
            "ajuda", "me ajuda", "me ajude", "como funciona", "como usar",
            "o que voce faz", "o que vc faz", "para que serve",
            "o que posso perguntar", "como voce pode me ajudar",
        }
        if texto in apresentacoes:
            print(f"Sou o {self.nome}, um chatbot de orientação para jovens que estão entrando no mercado de trabalho. "
                  "Uso uma base de respostas preparada pela equipe para ajudar com documentos, primeiro emprego e serviços públicos. "
                  "Não sou um canal oficial e não emito documentos nem faço inscrições.")
        elif texto in ajuda:
            print("Escreva sua dúvida, por exemplo: 'Como acessar minha carteira de trabalho digital?' "
                  "ou 'Onde encontro uma vaga de emprego?'. Também posso orientar sobre CPF, título de eleitor, "
                  "conta gov.br, Jovem Aprendiz, estágio, FGTS e cursos gratuitos. "
                  "Digite 0 para voltar e escolha 2 no menu para navegar por categorias. Não envie dados pessoais.")
        elif texto in {"oi", "ola", "bom dia", "boa tarde", "boa noite", "tudo bem", "oi tudo bem"}:
            print(f"Olá! Sou o {self.nome}. Posso ajudar com documentos e primeiro emprego. "
                  "Qual é sua dúvida? Digite 'ajuda' para ver exemplos.")
        elif texto in {"obrigado", "obrigada", "valeu", "muito obrigado", "muito obrigada"}:
            print("Por nada! Se tiver outra dúvida sobre documentos ou primeiro emprego, pode perguntar.")
        else:
            return False
        return True

    def atender_pergunta(self, pergunta, inicio=None):
        """Atende uma única dúvida; retorna um registro ou None para entrada recusada."""
        if inicio is None:
            inicio = time.time()
        if not pergunta or not pergunta.strip():
            print("A dúvida não pode estar vazia.")
            return None
        if contem_dados_pessoais(pergunta):
            print("Atenção: não digite CPF, telefone, e-mail ou dados pessoais. Reescreva.")
            return None
        if self.responder_conversa(pergunta):
            return None
        resultados = self.base.buscar(pergunta)
        pontos, orientacao = resultados[0] if resultados else (0, None)
        if pontos < 3:
            print("\nNão encontrei uma orientação confiável para essa dúvida.")
            print("Tente usar outras palavras ou navegue pelas categorias:")
            for categoria in self.base.categorias():
                print(f" - {categoria}")
            return self._registrar_resultado(
                "pergunta", pergunta, None, False, False, inicio,
                pontos=pontos, confianca="NÃO ENCONTRADA",
            )

        confianca = self.base.confianca(pontos)
        orientacao.exibir(confianca=confianca, pontos=pontos)
        alternativas = [(p, o) for p, o in resultados[1:] if p >= 3][:2]
        if alternativas:
            print("Outras orientações que podem ajudar:")
            for p, outra in alternativas:
                print(f"  - {outra.titulo} ({p} pontos)")
        ajudou = self._perguntar_ajudou()
        return self._registrar_resultado(
            "pergunta", pergunta, orientacao, True, ajudou, inicio,
            pontos=pontos, confianca=confianca,
        )

    def perguntar(self):
        while True:
            inicio = time.time()
            pergunta = ler_entrada("\nDigite sua dúvida (0 para voltar): ")
            if pergunta is None or pergunta.strip() == "0":
                return
            self.atender_pergunta(pergunta, inicio)

    def navegar(self):
        """Menu de duas camadas, com 0 para voltar em cada tela."""
        while True:
            categorias = self.base.categorias()
            print("\n--- CATEGORIAS ---")
            if not categorias:
                print("A base está vazia. Verifique o arquivo JSON.")
                return
            for indice, categoria in enumerate(categorias, start=1):
                print(f"{indice}. {categoria}")
            print("0. Voltar")
            entrada = ler_entrada("Escolha uma categoria: ")
            if entrada is None or entrada.strip() == "0":
                return
            if not entrada.strip().isdigit() or not (1 <= int(entrada) <= len(categorias)):
                print("Opção inválida: selecione um número da lista.")
                continue
            categoria = categorias[int(entrada) - 1]
            orientacoes = self.base.por_categoria(categoria)
            while True:
                print(f"\n--- {categoria.upper()} ---")
                for indice, orientacao in enumerate(orientacoes, start=1):
                    print(f"{indice}. {orientacao.titulo}")
                print("0. Voltar")
                escolha = ler_entrada("Escolha uma orientação: ")
                if escolha is None or escolha.strip() == "0":
                    break
                if not escolha.strip().isdigit() or not (1 <= int(escolha) <= len(orientacoes)):
                    print("Opção inválida: selecione um número da lista.")
                    continue
                inicio = time.time()
                orientacao = orientacoes[int(escolha) - 1]
                orientacao.exibir(confianca="DIRETA")
                ajudou = self._perguntar_ajudou()
                self._registrar_resultado(
                    "categoria", orientacao.titulo, orientacao, True,
                    ajudou, inicio, confianca="DIRETA",
                )

    def _calcular_indicadores(self):
        total = len(self.historico)
        if not total:
            return {
                "total": 0, "encontradas_pct": 0.0, "ajudou_pct": 0.0,
                "tempo_medio": 0.0, "tentativas_medias": 0.0,
                "facilidade_media": None, "duvidas_sem_solucao": [],
            }
        encontrados = [item for item in self.historico if item.get("encontrou") is True]
        ajudaram = sum(item.get("ajudou") is True for item in self.historico)
        tempos = [
            item["tempo_segundos"] for item in encontrados
            if isinstance(item.get("tempo_segundos"), (int, float))
        ]
        tentativas = [
            item["tentativas"] for item in self.historico
            if isinstance(item.get("tentativas"), int)
        ]
        # Uma nota por sessão, mesmo se a sessão tiver vários atendimentos.
        notas_por_sessao = {}
        for indice, item in enumerate(self.historico):
            nota = item.get("facilidade")
            if isinstance(nota, int) and 1 <= nota <= 5:
                notas_por_sessao[item.get("sessao_id") or f"antigo-{indice}"] = nota
        media_facilidade = (
            sum(notas_por_sessao.values()) / len(notas_por_sessao)
            if notas_por_sessao else None
        )
        sem_solucao = list(dict.fromkeys(
            item.get("pergunta", "") for item in self.historico
            if item.get("ajudou") is False and item.get("pergunta")
        ))
        return {
            "total": total,
            "encontradas_pct": 100 * len(encontrados) / total,
            "ajudou_pct": 100 * ajudaram / total,
            "tempo_medio": sum(tempos) / len(tempos) if tempos else 0.0,
            "tentativas_medias": sum(tentativas) / len(tentativas) if tentativas else 0.0,
            "facilidade_media": media_facilidade,
            "duvidas_sem_solucao": sem_solucao,
        }

    def indicadores(self):
        dados = self._calcular_indicadores()
        print("\n--- INDICADORES ---")
        print(f"Atendimentos registrados: {dados['total']}")
        print(f"Respostas encontradas: {dados['encontradas_pct']:.1f}%")
        print(f"Taxa de acerto (ajudou / total): {dados['ajudou_pct']:.1f}%")
        print(f"Tempo médio para encontrar orientação: {dados['tempo_medio']:.1f} s")
        print(f"Tentativas médias por atendimento: {dados['tentativas_medias']:.2f}")
        facilidade = dados["facilidade_media"]
        print("Facilidade de uso: " + (
            f"{facilidade:.2f}/5" if facilidade is not None else "ainda não avaliada"
        ))
        print("Dúvidas sem solução:")
        if dados["duvidas_sem_solucao"]:
            for pergunta in dados["duvidas_sem_solucao"]:
                print(f" - {pergunta}")
        else:
            print(" - Nenhuma registrada")
        return dados

    @staticmethod
    def _proteger_formula_csv(valor):
        """Evita interpretação de texto do usuário como fórmula em planilhas."""
        if isinstance(valor, str) and valor.lstrip().startswith(("=", "+", "-", "@")):
            return "'" + valor
        return valor

    def exportar_csv(self):
        try:
            self.caminho_csv.parent.mkdir(parents=True, exist_ok=True)
            with self.caminho_csv.open("w", encoding="utf-8-sig", newline="") as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS_CSV, extrasaction="ignore")
                escritor.writeheader()
                for registro in self.historico:
                    escritor.writerow({
                        campo: self._proteger_formula_csv(registro.get(campo, ""))
                        for campo in CAMPOS_CSV
                    })
            print(f"CSV exportado: {self.caminho_csv}")
            return True
        except OSError as erro:
            print(f"[AVISO] Não foi possível exportar o CSV: {erro}")
            return False

    def _avaliar_facilidade_ao_sair(self):
        registros_sessao = [
            item for item in self.historico if item.get("sessao_id") == self.sessao_id
        ]
        if not registros_sessao:
            return
        while True:
            nota = ler_entrada("De 1 a 5, qual foi a facilidade de uso? (0 para pular): ")
            if nota is None or nota.strip() == "0":
                return
            if nota.strip() in ("1", "2", "3", "4", "5"):
                for registro in registros_sessao:
                    registro["facilidade"] = int(nota)
                self._salvar_historico()
                print("Avaliação de facilidade registrada. Obrigado!")
                return
            print("Digite uma nota de 1 a 5 ou 0 para pular.")

    def executar(self):
        print(f"\nBem-vindo ao {self.nome}!")
        print("Orientações para jovens que estão entrando no mercado de trabalho.")
        print("Não informe CPF, telefone, e-mail, senha ou outros dados pessoais.")
        print("Aviso: este assistente NÃO é um canal oficial.")
        while True:
            print("\n--- MENU PRINCIPAL ---")
            print("1. Fazer uma pergunta")
            print("2. Navegar por categorias")
            print("3. Ver indicadores")
            print("4. Exportar atendimentos para CSV")
            print("0. Sair")
            opcao = ler_entrada("Escolha uma opção: ")
            if opcao is None or opcao.strip() == "0":
                self._avaliar_facilidade_ao_sair()
                self.exportar_csv()
                print("Encerrado. Consulte sempre as fontes oficiais.")
                return
            if opcao.strip() == "1":
                self.perguntar()
            elif opcao.strip() == "2":
                self.navegar()
            elif opcao.strip() == "3":
                self.indicadores()
            elif opcao.strip() == "4":
                self.exportar_csv()
            else:
                print("Opção inválida. Escolha 0, 1, 2, 3 ou 4.")
