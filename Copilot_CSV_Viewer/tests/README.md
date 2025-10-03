# CSV Viewer - Testes

Este diretório contém os testes automatizados para o CSV Viewer.

## Executando os testes

Para executar todos os testes:

```bash
# Instalar dependências (pytest já incluído em requirements.txt)
pip install -r requirements.txt

# Executar todos os testes (comando simples)
python -m pytest

# Executar com mais detalhes
python -m pytest -v

# Executar com cobertura de código
python -m pytest --cov=utils

# Relatório de cobertura detalhado
python -m pytest --cov=utils --cov-report=term-missing
```

## Estrutura dos testes

- `test_utils.py`: Testes para todas as funções utilitárias
  - Carregamento de CSV com diferentes separadores e encodings
  - Filtragem por texto
  - Identificação de colunas numéricas
  - Cálculos estatísticos
  - Preparação de dados para gráficos
  - Validação de requisitos
  - Cenários de integração
