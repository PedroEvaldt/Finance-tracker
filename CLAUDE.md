# CLAUDE.md

## Contexto do projeto

Este projeto tem como objetivo construir uma aplicação em Python para processar arquivos CSV exportados da Nubank, limpar e padronizar os dados com `pandas`, categorizar transações financeiras, gerar tabelas analíticas e produzir saídas úteis para controle financeiro pessoal.

O projeto deve ser tratado como um software real, com foco em:

* organização de código;
* legibilidade;
* versionamento constante;
* modularidade;
* facilidade de manutenção;
* possibilidade de expansão futura.

---

## Papel esperado do Claude neste projeto

Você deve atuar como um engenheiro de software cuidadoso, pragmático e didático.

Ao trabalhar neste repositório:

* sempre preserve a clareza do código;
* prefira soluções simples e robustas antes de soluções sofisticadas;
* explique decisões importantes de arquitetura;
* evite gerar código excessivamente complexo sem necessidade;
* pense em evolução futura, mas implemente apenas o necessário para a fase atual;
* nunca misture responsabilidades em arquivos desnecessariamente grandes.

Seu trabalho deve priorizar:

1. corretude;
2. legibilidade;
3. testabilidade;
4. facilidade de manutenção;
5. evolução incremental.

---

## Objetivo funcional

A aplicação deve ser capaz de:

* ler um ou mais arquivos CSV da Nubank;
* validar o formato de entrada;
* normalizar colunas, datas, valores e descrições;
* limpar inconsistências dos dados;
* categorizar transações financeiras;
* permitir revisão de transações não classificadas ou ambíguas;
* gerar tabelas analíticas;
* exportar resultados processados;
* criar um site simples com streamlit para visualizar as tabelas e gráficos;
* possibitar o ajuste manual das categorias das despesas no site do streamlit;

---

## Escopo principal

### Ingestão

* Ler CSV com segurança.
* Validar colunas obrigatórias.
* Detectar problemas de encoding e separador quando necessário.

### Limpeza e normalização

* Converter datas para `datetime`.
* Converter valores para formato numérico consistente.
* Normalizar descrições de transação.
* Remover espaços excedentes.
* Padronizar capitalização quando fizer sentido.
* Identificar local/nome da transação
* Identificar tipo de transacao (pix, debito, credito)

### Enriquecimento

* Criar colunas derivadas como:

  * `ano`
  * `mes`
  * `ano_mes`
  * `dia_semana`
  * `valor_abs`
  * `tipo_movimentacao`
  * `descricao_normalizada`
  * `estabelecimento_normalizado`

### Categorização

* Classificar transações em categorias como:

  * alimentacao
  * mercado
  * transporte
  * moradia
  * saude
  * educacao
  * lazer
  * assinaturas
  * transferencias
  * receita
  * investimentos
  * outros
* Implementar regras baseadas em palavras-chave.
* Permitir arquivo externo de configuração de categorias.
* Marcar transações ambíguas para revisão.

### Análise

* Gerar resumo por categoria.
* Gerar resumo por mês.
* Gerar resumo por estabelecimento.
* Separar receitas e despesas.
* Detectar gastos recorrentes, quando possível.

### Exportação

* Salvar CSV limpo.
* Salvar CSV enriquecido.
* Possibilitar exportação futura para Excel e relatórios.

### Display de análises

* Criar site com streamlit
* Disponibilizar analises dos dados, separacao por categorias, ordenação por ordem crescente de gastos
* Permitir a seleção manual da categoria de cada transação no stremlit 
---

## Diretrizes de arquitetura

Organize o projeto em módulos pequenos e coesos.


Regras importantes:

* não concentrar tudo em um único arquivo;
* separar parsing, limpeza, categorização, análise e exportação;
* funções devem ter responsabilidade bem definida;
* evitar duplicação de lógica;
* usar nomes explícitos e consistentes.

---

## Diretrizes de implementação

### Estilo de código

* Use Python claro e idiomático.
* Prefira funções pequenas.
* Use nomes descritivos.
* Escreva docstrings quando agregarem valor.
* Evite comentários óbvios.
* Mantenha consistência entre módulos.

### Tipagem

* Use type hints sempre que razoável.
* Prefira assinaturas explícitas.
* Tipos devem facilitar manutenção e leitura.

### Tratamento de erros

* Não silencie erros importantes.
* Mensagens de erro devem ser claras e acionáveis.
* Diferencie erro de entrada inválida, erro de parsing e erro interno.

### Configuração

* Regras de categorização devem ficar preferencialmente fora do código, em YAML ou JSON.
* Não hardcodar valores que podem evoluir facilmente.

### Dependências

Priorizar inicialmente:

* pandas
* pyyaml
* python-dateutil
* pathlib
* pytest
* streamlit

Adicionar novas dependências apenas quando houver ganho real.

---

## Regras para categorização

Ao implementar categorização:

* normalize a descrição antes de aplicar regras;
* trate variações do mesmo estabelecimento como equivalentes;
* implemente prioridade entre regras específicas e genéricas;
* se a confiança for baixa, marque para revisão manual;
* não force categoria arbitrária quando a evidência for fraca.

Exemplo de abordagem:

1. verificar mapeamento exato de estabelecimento;
2. verificar regras por palavras-chave específicas;
3. verificar regras genéricas;
4. marcar como `outros` ou `revisar`.

---

## Colunas derivadas esperadas

Sempre que fizer sentido, o dataframe processado deve conter colunas como:

* `data`
* `descricao`
* `descricao_normalizada`
* `valor`
* `categoria`
* `subcategoria`
* `tipo_movimentacao`
* `estabelecimento_normalizado`
* `ano`
* `mes`
* `ano_mes`
* `dia_semana`
* `confianca_categoria`
* `revisao_manual`

---

## Saídas esperadas

O projeto deve gerar saídas úteis e verificáveis.

Exemplos:

* `transactions_cleaned.csv`
* `transactions_categorized.csv`
* `category_summary.csv`
* `monthly_summary.csv`
* `review_needed.csv`

Sempre que uma nova saída for criada, o nome deve ser claro e previsível.

---

## Testes

Sempre que alterar comportamento importante, adicione ou atualize testes.

Cobrir principalmente:

* parsing do CSV;
* normalização de texto;
* parsing de datas;
* parsing de valores;
* categorização;
* tratamento de duplicatas;
* tratamento de entradas inválidas.

Prefira testes pequenos e determinísticos.

Não escreva testes frágeis que dependam de detalhes irrelevantes.

---

## Como o Claude deve responder ao trabalhar no projeto

Ao propor mudanças:

* explique brevemente o objetivo da alteração;
* explique impacto nos arquivos afetados;
* mantenha a mudança pequena e controlada quando possível;
* indique riscos, limitações e próximos passos naturais.

Ao gerar código:

* entregue código completo e consistente com a estrutura do projeto;
* respeite módulos já existentes;
* não quebre compatibilidade sem dizer isso explicitamente;
* não invente comportamento oculto.

Ao refatorar:

* preserve comportamento esperado;
* melhore nomes, estrutura ou clareza sem mudar regra de negócio sem necessidade;
* atualize testes se necessário.

---

## Regras de Git e versionamento

O versionamento é obrigatório durante todo o projeto.

### Princípios

* faça commits frequentes;
* cada commit deve registrar uma mudança pequena e compreensível;
* não acumule muitas alterações diferentes no mesmo commit;
* commits devem permitir voltar para um estado anterior estável caso algo dê errado;
* mensagens devem ser simples, claras e diretas.

## Regras para mensagens de commit

As mensagens devem ser:

* curtas;
* claras;
* em inglês simples ou português simples, mas com consistência;
* descritivas o suficiente para entender o que mudou.

Prefira o formato:

```text
<verbo> <o que foi feito>
```

Exemplos bons:

* `add initial project structure`
* `implement nubank csv parser`
* `normalize transaction descriptions`
Exemplos ruins:

* `update`
* `changes`
---

## Política de commits durante o projeto

Sempre que concluir uma etapa pequena e funcional, gere um commit.

Exemplos de momentos adequados para commit:

* após criar a estrutura inicial do projeto;
* após implementar o parser do CSV;
* após adicionar normalização de colunas;
* após implementar categorização inicial;
* após gerar primeira tabela analítica;
* após adicionar testes;
* após corrigir bug específico.

Não espere uma grande quantidade de mudanças para commitar.

---

## Regra de segurança com Git

Antes de mudanças maiores:

* garanta que o repositório esteja limpo ou com tudo commitado;
* não misture refatoração ampla com correção de bug em um único commit;
* se uma mudança for arriscada, faça commits intermediários menores;
* preserve um histórico que facilite rollback.

Se algo quebrar, o histórico deve permitir identificar rapidamente:

* quando quebrou;
* qual arquivo mudou;
* qual foi a intenção da alteração.

---

## O que evitar

* Não gerar arquivos gigantes com múltiplas responsabilidades.
* Não criar abstrações desnecessárias cedo demais.
* Não depender de comportamento implícito difícil de entender.
* Não fazer commit de mudanças não revisadas.
* Não usar mensagens de commit vagas.
* Não alterar muitas áreas diferentes do projeto sem separar em commits.
* Não acoplar regras de negócio ao formato exato de um único CSV sem isolamento.

---

## Resultado esperado do projeto

Ao final, este repositório deve demonstrar:

* boa organização de projeto Python;
* uso prático de `pandas`;
* tratamento e limpeza de dados reais;
* categorização de transações financeiras;
* geração de análises úteis;
* geração de streamlit com tabelas e gráficos gerados
* versionamento disciplinado com Git;
* base sólida para evoluções futuras.

---

## Instrução final para o Claude

Ao contribuir neste projeto, trabalhe sempre de forma incremental, clara e segura.

Priorize código legível, modular e fácil de testar.

Sempre sugira o próximo passo mais lógico.

Sempre considere se a alteração merece um commit separado.

Sempre preserve a rastreabilidade do projeto por meio de commits simples e claros.

