# Teste Técnico para Engenheiro de Dados: Processamento de logs de Eventos

Pipeline para processar logs de atividades de usuários a partir de arquivos JSON.

## 1. Estrutura do Projeto

```
case-rd-station/
├── events/                 # Diretório com os arquivos de entrada
├── src/
│   ├── aggregator.py       # Cálculo das estatísticas
│   ├── reader.py           # Leitura dos arquivos JSON
│   ├── validator.py        # Validação e filtragem dos eventos
│   └── writer.py           # Escrita dos arquivos de saída
├── tests/
│   └── test_processor.py   # Testes unitários
├── processor.py            # Orquestrador do pipeline
└── README.md
````

## 2. Instruções de Execução

### Pipeline

```bash
python processor.py \
    --input-dir ./events \
    --output stats.csv \
    --deadletter deadletter.json \
    --window-days 30
```

Onde:

- `--input-dir:` diretório com os arquivos `.json` de entrada;
- `--output:` caminho do arquivo `stats.csv` de saída;
- `--deadletter:` caminho do arquivo `deadletter.json` de saída;
- `--window-days:` janela de tempo em dias.

O arquivo `summary.json` é gerado automaticamente no mesmo diretório do `stats.csv`.

### Testes

```bash
python -m unittest tests.test_processor -v
```

## 3. Arquitetura

O pipeline segue um fluxo linear com responsabilidades separadas:

```
Leitura → Validação → Filtragem → Cálculos → Escrita
```

Onde:
- `reader.py:` lê todos os arquivos `.json` do diretório de entrada;
- `validator.py:` valida cada evento com as regras pré-estabelecidas e filtra pela janela de tempo;
- `aggregator.py:` calcula as estatísticas dos eventos válidos;
- `writer.py:` gera os arquivos de saída (`stats.csv`, `summary.json`, `deadletter.json`);
- `processor.py:` orquestra todas as etapas acima.

Esse design foi adotado por manter cada etapa separada das demais, e estando responsável pela execução de uma única tarefa, o que facilita testes, manutenção e extensão do código.

## 4. Perguntas

**a) Qual foi a decisão de design mais importante que você tomou e por quê?**

Separar a filtragem da validação foi uma das decisões mais importantes, para que os eventos fora da janela de tempo sejam descartados e não considerados inválidos, de modo que não sejam registrados no deadletter.

Outro ponto importante foi o tratamento do timezone no timestamp. Como o Python não aceita o `Z` do formato `ISO 8601` diretamente, que é o formato dos dados de entrada, foi necessário substituí-lo por `+00:00` antes de converter para `datetime`, garantindo que a comparação com o `execution_time` funcionasse corretamente.

**b) O que você faria diferente com mais tempo?**

Criaria classes melhor estruturadas dentro dos módulos, adicionaria informações de logs em vez de `print`, trataria melhor os erros na leitura dos arquivos e cobriria os módulos `reader.py` e `writer.py` com testes unitários usando arquivos de exemplo.

**c) Como você adicionaria suporte a uma nova fonte de dados (ex.: arquivos CSV)?**

Dentro do módulo `reader.py`, dividiria a função `read_events` em duas, criando uma função `read_events_csv` e outra `read_json_events` (que permaneceria com a estrutura atual). De todos os arquivos de entrada disponíveis, separaria o que é `.csv` do que é `.json` (talvez com a ajuda de uma outra função prévia) e cada função leria seus arquivos específicos. A função que lê os arquivos `.csv` retornaria a mesma estrutura de lista de dicionários que o `reader.py` atual já retorna. O restante do pipeline não precisaria mudar.

**d) O que mudaria na sua abordagem se o volume fosse de 10 milhões de eventos distribuídos em centenas de arquivos?**

Processaria os arquivos em lotes em vez de carregar na memória de uma única vez, usaria `multiprocessing` para paralelizar a leitura e validação dos arquivos. Também consideraria migrar para uma ferramenta como `PySpark` que lida melhor com grandes volumes de dados.