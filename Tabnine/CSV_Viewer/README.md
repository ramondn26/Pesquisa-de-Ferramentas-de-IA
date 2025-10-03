# CSV Viewer - Aplicação Streamlit

Uma aplicação web desenvolvida em Streamlit para upload, visualização e análise de arquivos CSV.

## 🚀 Funcionalidades

- **Upload de arquivos CSV** com validação automática
- **Visualização interativa** dos dados com filtros de busca
- **Cálculo de estatísticas descritivas** para colunas numéricas
- **Geração de gráficos** (linha e barras) usando componentes nativos do Streamlit
- **Análise de tipos de dados** e valores ausentes
- **Interface responsiva** e intuitiva
- **Logging detalhado** das operações principais

## 📋 Requisitos

- Python 3.8 ou superior
- Streamlit 1.28.0 ou superior
- Pandas 2.0.0 ou superior
- NumPy 1.24.0 ou superior

## 🛠️ Instalação e Configuração

### 1. Clone o repositório

```bash
git clone <url-do-repositorio>
cd CSV_Viewer

### 2. Crie um ambiente virtual e ative-o:

```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

### 3. Instale as dependências:

```bash
pip install -r requirements.txt
```

## ▶️ Como Rodar

Para executar a aplicação:

```bash
streamlit run app.py
```

## 🧪 Como Rodar os Testes

Para rodar os testes com pytest:

```bash
pytest
```

Ou para rodar os testes com cobertura:

```bash
pytest --cov=app
```

## 📊 Como Gerar Métricas

Para gerar métricas de cobertura de código:

```bash
pytest --cov=app --cov-report=html
```

Isso criará uma pasta `htmlcov` com relatórios interativos.

## 📁 Estrutura do Projeto

```
CSV_Viewer/
├── app.py              # Código principal da aplicação Streamlit
├── requirements.txt    # Dependências do projeto
├── pytest.ini          # Configuração do pytest
├── tests/              # Diretório de testes
│   └── test_app.py     # Testes da aplicação
└── README.md           # Documentação do projeto
```

## 📊 Exemplo de Uso

1. Execute a aplicação com `streamlit run app.py`
2. Faça upload de um arquivo CSV
3. Visualize os dados na tabela interativa
4. Utilize os filtros para analisar partes específicas dos dados
5. Gere gráficos para visualizar tendências
6. Analise estatísticas descritivas das colunas numéricas

## 🤝 Contribuições

Sinta-se à vontade para contribuir com melhorias, correções de bugs e novas funcionalidades!

## 📄 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.
