# Citizen Assist AI

## Integrantes

- Rodger Costa Rios — RM: 571438
- Kenichi Caio Yamamoto — RM: 569815

## Público e problema

Jovens de 16 a 24 anos entrando no mercado de trabalho, que têm dificuldade para encontrar informações claras sobre documentos, vagas e direitos trabalhistas.

## ODS relacionados

- **ODS 8 — Trabalho Decente e Crescimento Econômico:** acesso a informações sobre primeiro emprego e direitos trabalhistas.
- **ODS 4 — Educação de Qualidade:** orientação sobre cursos gratuitos e qualificação profissional.

## Como executar

Requer Python 3.9 ou superior, sem bibliotecas externas. Na pasta do projeto, execute:

```bash
python main.py
```

No Windows, também é possível usar `py main.py`. Use o menu para fazer perguntas, navegar por categorias, consultar indicadores e exportar o CSV. Digite `0` para voltar ou sair. Ao sair, informe a nota de facilidade de 1 a 5.

## Regra de pontuação

A pergunta, as palavras-chave e o título são normalizados para minúsculas, sem acentos e sem pontuação.

- Cada palavra-chave ou expressão encontrada na pergunta soma **3 pontos**.
- Cada palavra distinta da pergunta com pelo menos 4 letras presente no título soma **1 ponto**.
- **6 pontos ou mais:** confiança alta.
- **3 a 5 pontos:** confiança média.
- **Menos de 3 pontos:** orientação não encontrada; o programa sugere outras palavras ou categorias.

A busca retorna tuplas `(pontos, orientacao)` em ordem decrescente de pontuação, com desempate pelo ID. Exibe a melhor orientação e até duas alternativas com pelo menos 3 pontos. Não foram alterados os pesos ou limites do enunciado.

## Fontes consultadas

- [Emitir e acessar a Carteira de Trabalho Digital](https://www.gov.br/pt-br/servicos/obter-a-carteira-de-trabalho)
- [Consultar ou regularizar a situação do CPF](https://www.gov.br/receitafederal/pt-br/assuntos/meu-cpf)
- [Solicitar o primeiro título de eleitor](https://www.tse.jus.br/servicos-eleitorais/titulo-eleitoral/autoatendimento-eleitoral)
- [Criar e acessar uma conta gov.br](https://www.gov.br/pt-br/servicos/criar-sua-conta-gov.br)
- [Procurar vagas de trabalho pelo SINE e Emprega Brasil](https://www.gov.br/pt-br/servicos/acessar-portal-emprega-brasil-2013-trabalhador)
- [Entender o programa Jovem Aprendiz](https://www.gov.br/trabalho-e-emprego/pt-br/assuntos/aprendizagem-profissional)
- [Conseguir estágio e entender o termo de compromisso](https://www.planalto.gov.br/ccivil_03/_ato2007-2010/2008/lei/l11788.htm)
- [Consultar contratos e vínculos na Carteira de Trabalho Digital](https://www.gov.br/trabalho-e-emprego/pt-br/servicos/trabalhador/carteira-de-trabalho/perguntas-frequentes-carteira-de-trabalho-digital)
- [Consultar o saldo e o extrato do FGTS](https://www.caixa.gov.br/beneficios-trabalhador/fgts/extrato-fgts/Paginas/default.aspx)
- [Fazer cursos gratuitos de qualificação profissional](https://www.gov.br/pt-br/servicos/inscrever-se-em-cursos-autoinstrucionais-na-escola-virtual-de-governo)

## Resultados do teste com usuários

| Indicador | Resultado |
| --- | --- |
| Quantidade de participantes externos | 3 |
| Quantidade de atendimentos reais | 10 |
| Respostas encontradas (%) | 72,73% |
| Taxa de acerto (%) | 100% |
| Tempo médio | 30s |
| Tentativas por atendimento | 3 a 4 |
| Facilidade (1 a 5) | 4.5 |
| Dúvidas sem solução | 2 |

**Dúvidas sem solução:** “Quem é você?” e “Aonde eu posso arrumar uma vaga de emprego?”.

**Melhoria implementada:** adicionamos respostas de apresentação e ajuda e ampliamos as palavras-chave de busca de emprego. As duas perguntas passaram a receber respostas nos testes de validação.

## Limitações

- A busca depende de palavras-chave e pode não reconhecer outras formas de escrever a mesma dúvida.
- As orientações são estáticas e precisam de revisão quando os serviços oficiais mudam.
- O assistente não é um canal oficial, não emite documentos, não realiza inscrições e não consulta cadastros.
- O bloqueio de `@` e de 8 ou mais dígitos não detecta todos os tipos de dados pessoais. Não informe dados pessoais nas perguntas.

## Vídeo técnico

Link do YouTube (não listado): **[PREENCHER APÓS PUBLICAÇÃO]**
