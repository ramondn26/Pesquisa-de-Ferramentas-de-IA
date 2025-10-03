# CSV Viewer# CSV Viewer

Uma aplicação Streamlit simples para visualização e análise de dados CSV.Uma aplicação Streamlit para visualização e análise de dados CSV com funcionalidades avançadas.

## 📊 Funcionalidades## ⚡ Início Rápido

- **Upload de CSV**: Carregamento de arquivos CSV```bash

- **Visualização de dados**: Tabelas interativas com filtros# 1. Criar e ativar ambiente virtual

- **Busca por texto**: Pesquisa em todas as colunaspython -m venv .venv

- **Estatísticas**: Cálculos automáticos para colunas numéricas.venv\Scripts\activate # Windows

- **Gráficos básicos**: Visualizações de barras e linhas# source .venv/bin/activate # Linux/macOS

## 🚀 Como usar# 2. Instalar dependências

pip install -r requirements.txt

### 1. Criar ambiente virtual

```bash# 3. Executar aplicação

python -m venv .venvstreamlit run app.py

```

# 4. Executar testes

### 2. Ativar ambiente virtualpython -m pytest

```bash

# Windows# 5. Gerar métricas

.venv\Scripts\activatepython scripts/bench.py

```

# Linux/macOS

source .venv/bin/activate## 📊 Funcionalidades

```````

- **Upload de CSV**: Carregamento simples de arquivos CSV

### 3. Instalar dependências- **Visualização interativa**: Tabelas com controles de filtro e paginação

```bash- **Busca por texto**: Pesquisa em todas as colunas do dataset

pip install -r requirements.txt- **Estatísticas numéricas**: Cálculos automáticos (média, soma, mediana, etc.)

```- **Gráficos básicos**: Visualizações de barras e linhas

- **Detecção de datas**: Ordenação cronológica automática

### 4. Executar aplicação- **Resumo do dataset**: Informações sobre tipos, valores nulos e únicos

```bash- **Logging**: Sistema de logs para monitoramento de operações (upload, filtros, gráficos)

streamlit run app.py

```## 🚀 Instalação e Execução



### 5. Executar testes### Pré-requisitos

```bash

python -m pytest- Python 3.8 ou superior

```- pip (gerenciador de pacotes Python)



## 📁 Estrutura do Projeto### 1. Configuração do Ambiente Virtual



``````bash

CSV_Viewer/# Navegar para o diretório do projeto

├── app.py                    # Aplicação Streamlitcd CSV_Viewer

├── utils.py                  # Funções utilitárias

├── requirements.txt          # Dependências# Criar ambiente virtual

├── pytest.ini              # Configuração de testespython -m venv .venv

├── tests/

│   └── test_utils.py        # Testes automatizados# Ativar ambiente virtual

└── README.md                # Este arquivo# Windows:

```.venv\Scripts\activate

# Linux/macOS:

## 🧪 Testessource .venv/bin/activate

```````

O projeto possui **36 testes automatizados** com **98% de cobertura**.

### 2. Instalação das Dependências

Para executar os testes:

`bash`bash

python -m pytest# Instalar dependências principais

````pip install -r requirements.txt



Para ver cobertura:# Para desenvolvimento (inclui ferramentas de teste):

```bashpip install -r requirements.txt

python -m pytest --cov=utilspip install pytest pytest-cov

````

## 🔧 Dependências### 3. Executar a Aplicação

- **streamlit**: Interface web```bash

- **pandas**: Manipulação de dados# Executar o app Streamlit

- **pytest**: Framework de testesstreamlit run app.py

- **pytest-cov**: Cobertura de código```

A aplicação será aberta automaticamente no navegador em `http://localhost:8501`

### 4. Executar Testes

```bash
# Testes básicos
python -m pytest

# Testes com cobertura
python -m pytest --cov=utils

# Scripts de conveniência por plataforma:
.\test.bat           # Windows
make test           # Linux/macOS
```

### 5. Gerar Métricas de Desempenho

```bash
# Executar benchmark completo
python scripts/bench.py

# Scripts de conveniência por plataforma:
.\bench.bat         # Windows
make bench          # Linux/macOS
```

Os relatórios serão salvos na pasta `reports/` com timestamp.

### 6. Desativar Ambiente Virtual

```bash
# Quando terminar de usar o projeto
deactivate
```

### 💡 Dicas Úteis

- **Verificar ambiente ativo**: O prompt deve mostrar `(.venv)` quando o ambiente virtual estiver ativo
- **Reinstalar dependências**: Se houver problemas, delete a pasta `.venv` e refaça os passos 1-2
- **Logs em tempo real**: Os logs aparecem no terminal onde o Streamlit está rodando
- **Porta ocupada**: Se a porta 8501 estiver em uso, o Streamlit automaticamente usará a próxima disponível

### 📝 Logging

A aplicação possui sistema de logging integrado que registra:

- **Upload de arquivos**: Nome do arquivo, número de linhas/colunas e duração da operação
- **Aplicação de filtros**: Termo de busca, resultados encontrados e tempo de processamento
- **Geração de gráficos**: Tipo de gráfico, colunas utilizadas, pontos de dados e duração

Os logs são exibidos no console em nível INFO com formato estruturado:

```
2025-10-03 18:14:45,581 - __main__ - INFO - Iniciando upload de arquivo: dados.csv
2025-10-03 18:14:45,674 - __main__ - INFO - Upload concluído: dados.csv - 1000 linhas, 5 colunas - Duração: 0.093s
```

**Nota**: Os logs aparecem apenas no console onde o Streamlit foi executado, não poluindo a interface do usuário.

## 🧪 Testes Automatizados

### Comando Único (Recomendado)

```bash
# Executar todos os testes
python -m pytest

# Scripts de conveniência:
# Windows:
.\test.bat

# Linux/macOS (com make):
make test
```

### Opções Avançadas

```bash
# Executar testes com cobertura de código
python -m pytest --cov=utils
# ou: .\test.bat cov

# Executar testes em modo verboso
python -m pytest -v
# ou: .\test.bat verbose

# Relatório de cobertura em HTML
python -m pytest --cov=utils --cov-report=html
# ou: .\test.bat html
```

### Executar apenas testes específicos

```bash
# Executar uma classe específica
python -m pytest tests/test_utils.py::TestLoadCSVData -v

# Executar um teste específico
python -m pytest tests/test_utils.py::TestLoadCSVData::test_load_csv_basic -v
```

O relatório será gerado na pasta `htmlcov/`

## � Métricas Automáticas de Execução

### Benchmark de Testes

Execute o script de benchmark para coletar métricas detalhadas dos testes:

```bash
# Executar benchmark completo
python scripts/bench.py

# Com script de conveniência (Windows)
.\bench.bat
```

### Métricas Coletadas

- ⏱️ **Tempo de execução**: Duração total dos testes
- 🧪 **Contagem de testes**: Total, aprovados, falharam e pulados
- 📈 **Cobertura de código**: Percentual de cobertura dos testes
- ⚠️ **Warnings**: Detecção de avisos durante execução
- 📄 **Relatórios**: Geração automática em CSV e JSON com timestamp

### Relatórios Gerados

Os relatórios são salvos automaticamente na pasta `reports/` com timestamp:

- **CSV**: `test_metrics_YYYYMMDD_HHMMSS.csv` - Métricas resumidas
- **JSON**: `test_metrics_YYYYMMDD_HHMMSS.json` - Dados detalhados com informações individuais de cada teste

## �📁 Estrutura do Projeto

```
CSV_Viewer/
├── app.py                    # Aplicação principal Streamlit
├── utils.py                  # Funções utilitárias (lógica de negócio)
├── requirements.txt          # Dependências principais
├── requirements-test.txt     # Dependências de teste
├── pytest.ini              # Configuração do pytest
├── README.md                # Este arquivo
├── TESTS_SUMMARY.md         # Resumo detalhado dos testes
├── Makefile                 # Comandos de automação (Linux/macOS)
├── test.bat                 # Script de testes (Windows)
├── scripts/                 # Scripts de automação
│   ├── bench.py            # Benchmark de testes e métricas
│   └── README.md           # Documentação dos scripts
├── reports/                 # Relatórios de métricas (gerados automaticamente)
│   ├── test_metrics_*.csv  # Relatórios CSV com timestamp
│   └── test_metrics_*.json # Relatórios JSON detalhados
├── tests/                   # Diretório de testes
│   ├── __init__.py         # Pacote Python
│   ├── test_utils.py       # Testes das funções utilitárias
│   └── README.md           # Documentação dos testes
└── relacao_consumo_*.csv   # Arquivo CSV de exemplo
```

## 🔧 Arquitetura

### Separação de Responsabilidades

- **`app.py`**: Interface do usuário (Streamlit) - apenas apresentação
- **`utils.py`**: Lógica de negócio - funções puras e testáveis
- **`tests/`**: Testes automatizados - cobertura de 98%

### Funções Principais (`utils.py`)

- `load_csv_data()`: Carregamento de arquivos CSV
- `filter_dataframe_by_text()`: Busca por texto
- `get_numeric_columns()`: Identificação de colunas numéricas
- `calculate_numeric_statistics()`: Cálculos estatísticos
- `prepare_chart_data()`: Preparação de dados para gráficos
- `validate_chart_requirements()`: Validação de dados para visualização

## 📋 Testes

### Cobertura de Testes

- ✅ **36 testes** automatizados
- ✅ **98% de cobertura** de código
- ✅ Testes unitários e de integração
- ✅ Casos extremos incluídos

### Cenários Testados

- Carregamento de CSV com diferentes formatos
- Filtragem por texto (case-insensitive)
- Cálculos estatísticos com valores ausentes
- Detecção e ordenação de datas
- Validação de dados para visualização
- Caracteres especiais e acentos

### Executar Testes de Desenvolvimento

```bash
# Instalar dependências de teste
pip install -r requirements-test.txt

# Executar todos os testes
python -m pytest

# Executar com relatório de cobertura
python -m pytest --cov=utils --cov-report=term-missing

# Executar testes específicos por categoria
python -m pytest tests/test_utils.py::TestLoadCSVData -v
python -m pytest tests/test_utils.py::TestCalculateNumericStatistics -v
```

## 📊 Exemplo de Uso

1. **Faça upload** de um arquivo CSV
2. **Visualize** os dados em tabela interativa
3. **Use a busca** para filtrar informações específicas
4. **Analise estatísticas** das colunas numéricas
5. **Crie gráficos** selecionando colunas X e Y
6. **Explore** informações detalhadas das colunas

## 🛠️ Desenvolvimento

### Adicionando Novos Recursos

1. Implemente a lógica em `utils.py` (funções puras)
2. Adicione testes em `tests/test_utils.py`
3. Execute os testes: `pytest`
4. Adicione a interface em `app.py`
5. Teste manualmente com `streamlit run app.py`

### Boas Práticas

- Mantenha funções puras em `utils.py`
- Adicione testes para toda nova funcionalidade
- Use type hints nas funções
- Documente funções com docstrings
- Mantenha alta cobertura de testes (>95%)

## 📝 Dependências

### Principais

- `streamlit>=1.30`: Framework web para aplicações de dados
- `pandas>=2.0`: Manipulação e análise de dados
- `pytest>=7.4.3`: Framework de testes
- `pytest-cov>=4.1.0`: Plugin de cobertura de código

### Desenvolvimento

Veja `requirements-test.txt` para dependências adicionais de teste.

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Adicione testes para a nova funcionalidade
4. Execute os testes (`pytest`)
5. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
6. Push para a branch (`git push origin feature/nova-feature`)
7. Abra um Pull Request

## 📄 Licença

Este projeto está sob licença MIT. Veja o arquivo LICENSE para mais detalhes.

---

**Desenvolvido com ❤️ usando Streamlit e Python**
