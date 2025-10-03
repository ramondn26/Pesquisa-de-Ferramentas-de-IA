"""
CSV Viewer - Aplicativo Streamlit para Visualização e Análise de Dados CSV

Este módulo implementa uma aplicação web usando Streamlit que permite aos usuários:
- Fazer upload de arquivos CSV
- Visualizar e filtrar dados em tabelas interativas
- Gerar estatísticas descritivas para colunas numéricas
- Criar gráficos básicos (barras e linhas)
- Buscar texto nos dados
- Controlar a exibição de linhas

Dependências:
    - streamlit: Interface web
    - pandas: Manipulação e análise de dados
    - utils: Funções utilitárias para processamento de dados

Autor: Desenvolvido como ferramenta de análise de dados CSV
Data: 2025
"""

import streamlit as st
import pandas as pd
import logging
import time
from utils import (
    load_csv_data,
    filter_dataframe_by_text,
    get_numeric_columns,
    calculate_numeric_statistics,
    get_dataset_info,
    get_column_details,
    prepare_chart_data,
    validate_chart_requirements
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def process_uploaded_file(uploaded_file):
    """
    Processa o arquivo CSV carregado pelo usuário.
    
    Carrega o arquivo CSV em um DataFrame do pandas, armazena no estado da sessão
    e exibe mensagens de confirmação com informações básicas do dataset.
    
    Args:
        uploaded_file: Arquivo carregado pelo Streamlit file_uploader
        
    Raises:
        Exception: Captura erros de leitura do arquivo CSV (formato inválido, 
                  codificação, etc.) e exibe mensagem de erro ao usuário.
    """
    start_time = time.time()
    logger.info(f"Iniciando upload de arquivo: {uploaded_file.name}")
    
    # Carrega o CSV usando função utilitária
    df = load_csv_data(uploaded_file)
    
    # Salva no estado da sessão
    st.session_state['dataframe'] = df
    st.session_state['filename'] = uploaded_file.name
    
    upload_duration = time.time() - start_time
    logger.info(f"Upload concluído: {uploaded_file.name} - {df.shape[0]} linhas, {df.shape[1]} colunas - Duração: {upload_duration:.3f}s")
    
    # Mensagem de confirmação
    st.success(f"✅ Arquivo '{uploaded_file.name}' carregado com sucesso!")
    st.info(f"📈 Dados: {df.shape[0]} linhas e {df.shape[1]} colunas")
    
    # Preview dos dados
    st.subheader("Preview dos Dados")
    st.dataframe(df.head(10))

def show_instructions():
    """
    Exibe instruções de uso quando nenhum arquivo foi carregado.
    
    Mostra um guia passo-a-passo para o usuário e limpa o estado da sessão
    de dados anteriores para evitar inconsistências.
    """
    # Instruções quando não há arquivo
    st.info("👆 **Instruções:**")
    st.markdown("""
    1. Clique no botão acima para fazer upload de um arquivo CSV
    2. O arquivo será carregado automaticamente
    3. Você verá um preview dos dados após o upload
    4. Formatos suportados: `.csv`
    """)
    
    # Limpa o estado da sessão se não há arquivo
    if 'dataframe' in st.session_state:
        del st.session_state['dataframe']
    if 'filename' in st.session_state:
        del st.session_state['filename']

def show_search_feedback(search_text, filtered_df):
    """
    Exibe feedback sobre os resultados da busca por texto.
    
    Args:
        search_text: Texto buscado pelo usuário
        filtered_df: DataFrame filtrado pelos resultados
    """
    if len(filtered_df) == 0:
        st.warning(f"⚠️ Nenhum resultado encontrado para '{search_text}'")
    else:
        st.info(f"🔍 Encontrados {len(filtered_df)} registros para '{search_text}'")

def show_numeric_statistics(df):
    """
    Gera e exibe estatísticas descritivas para colunas numéricas do dataset.
    
    Args:
        df: DataFrame com os dados para análise
    """
    st.subheader("🔢 Estatísticas das Colunas Numéricas")
    
    # Calcular estatísticas usando função utilitária
    stats_result = calculate_numeric_statistics(df)
    stats_df = stats_result['stats_df']
    summary = stats_result['summary']
    
    # Exibir tabela de estatísticas
    st.dataframe(stats_df, use_container_width=True)
    
    # Métricas principais em colunas
    st.subheader("📈 Resumo Geral das Colunas Numéricas")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total de Colunas Numéricas",
            summary['total_numeric_columns']
        )
    
    with col2:
        st.metric(
            "Total de Valores",
            f"{summary['total_values']:,}"
        )
    
    with col3:
        st.metric(
            "Soma Geral",
            f"{summary['total_sum']:,.2f}"
        )
    
    with col4:
        st.metric(
            "Média Geral",
            f"{summary['overall_mean']:.2f}"
        )

def show_no_numeric_columns_warning():
    """
    Exibe aviso quando o dataset não possui colunas numéricas.
    """
    st.warning("⚠️ **Nenhuma coluna numérica encontrada no dataset**")
    st.info("""
    📝 **Informação:** 
    - O dataset não possui colunas com dados numéricos (int, float)
    - Estatísticas numéricas não podem ser calculadas
    - Verifique se os dados foram importados corretamente
    """)

def show_dataset_summary(df):
    """
    Exibe resumo geral do dataset.
    
    Args:
        df: DataFrame com os dados para análise
    """
    dataset_info = get_dataset_info(df)
    basic_info = dataset_info['basic_info']
    type_distribution = dataset_info['type_distribution']
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Informações básicas
        st.write("**Informações Básicas:**")
        st.write(f"• **Dimensões:** {basic_info['dimensions']}")
        st.write(f"• **Memória utilizada:** ~{basic_info['memory_usage_kb']} KB")
        st.write(f"• **Valores únicos totais:** {basic_info['unique_values_total']:,}")
        st.write(f"• **Valores nulos totais:** {basic_info['null_values_total']:,}")
    
    with col2:
        # Tipos de dados
        st.write("**Distribuição por Tipos:**")
        for dtype, count in type_distribution.items():
            st.write(f"• **{dtype}:** {count} colunas")

def generate_chart(df, chart_type, x_column, y_columns):
    """
    Processa e gera gráfico baseado nas seleções do usuário.
    
    Args:
        df: DataFrame com os dados
        chart_type: Tipo de gráfico ("Barras" ou "Linha")
        x_column: Nome da coluna para eixo X
        y_columns: Lista de colunas para eixo Y
    """
    start_time = time.time()
    logger.info(f"Iniciando geração de gráfico: tipo={chart_type}, x={x_column}, y={y_columns}")
    
    # Preparar dados usando função utilitária
    chart_result = prepare_chart_data(df, x_column, y_columns)
    chart_df = chart_result['chart_df']
    is_date = chart_result['is_date']
    y_stats = chart_result['stats']
    
    if len(chart_df) == 0:
        logger.warning("Gráfico não pôde ser gerado: dados válidos insuficientes")
        st.warning("⚠️ Não há dados válidos para gerar o gráfico")
        return
    
    # Informar sobre detecção de data
    if is_date:
        st.info("📅 Detectada coluna de data - dados ordenados cronologicamente")
    
    # Mostrar informações do gráfico
    st.info(f"📊 Exibindo {len(chart_df)} pontos de dados")
    
    # Preparar DataFrame para o gráfico (definir X como índice)
    chart_df_indexed = chart_df.set_index(x_column)
    
    # Gerar o gráfico baseado no tipo selecionado
    if chart_type == "Barras":
        st.bar_chart(
            chart_df_indexed[y_columns],
            height=400
        )
    else:  # Linha
        st.line_chart(
            chart_df_indexed[y_columns],
            height=400
        )
    
    # Mostrar resumo dos dados do gráfico
    with st.expander("📋 Dados do Gráfico"):
        st.dataframe(chart_df, use_container_width=True)
        
        # Estatísticas rápidas das colunas Y usando dados pré-calculados
        st.write("**Estatísticas das Colunas Y:**")
        for col in y_columns:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(f"{col} - Mínimo", f"{y_stats[col]['min']:.2f}")
            with col2:
                st.metric(f"{col} - Máximo", f"{y_stats[col]['max']:.2f}")
            with col3:
                st.metric(f"{col} - Média", f"{y_stats[col]['mean']:.2f}")
    
    chart_duration = time.time() - start_time
    logger.info(f"Gráfico gerado com sucesso: {len(chart_df)} pontos de dados - Duração: {chart_duration:.3f}s")

def show_chart_section(df, numeric_columns):
    """
    Interface para configuração e geração de gráficos básicos.
    
    Args:
        df: DataFrame com os dados
        numeric_columns: Colunas numéricas disponíveis
    """
    st.subheader("🎨 Configuração do Gráfico")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        # Seleção do tipo de gráfico
        chart_type = st.selectbox(
            "Tipo de Gráfico:",
            ["Barras", "Linha"],
            help="Escolha o tipo de visualização"
        )
    
    with col2:
        # Seleção da coluna X
        x_column = st.selectbox(
            "Eixo X:",
            df.columns.tolist(),
            help="Coluna para o eixo horizontal"
        )
    
    with col3:
        # Seleção das colunas Y (numéricas)
        y_columns = st.multiselect(
            "Eixo Y (Colunas Numéricas):",
            numeric_columns.tolist(),
            default=[numeric_columns[0]] if len(numeric_columns) > 0 else [],
            help="Selecione uma ou mais colunas numéricas para o eixo Y"
        )
    
    # Gerar gráfico se as seleções estão válidas
    if y_columns and x_column:
        try:
            generate_chart(df, chart_type, x_column, y_columns)
        except Exception as e:
            st.error(f"❌ Erro ao gerar gráfico: {str(e)}")
            st.info("💡 Dica: Verifique se as colunas selecionadas contêm dados válidos")
    
    elif not y_columns and len(numeric_columns) > 0:
        st.info("👆 Selecione pelo menos uma coluna numérica para o eixo Y")

# Configuração da página
st.set_page_config(
    page_title="CSV Viewer",
    page_icon="📊",
    layout="wide"
)

# Título do app
st.title("📊 CSV Viewer")

# Seção de upload
st.header("Upload de Arquivo CSV")

# Widget de upload
uploaded_file = st.file_uploader(
    "Escolha um arquivo CSV",
    type=['csv'],
    help="Selecione um arquivo CSV para visualizar"
)

# Processamento do arquivo
if uploaded_file is not None:
    try:
        process_uploaded_file(uploaded_file)
    except Exception as e:
        st.error(f"❌ Erro ao carregar o arquivo: {str(e)}")
else:
    show_instructions()

# Seção de visualização completa (só aparece se há dados carregados)
if 'dataframe' in st.session_state and 'filename' in st.session_state:
    st.header("📋 Visualização Completa dos Dados")
    
    df = st.session_state['dataframe']
    
    # Informações do dataset
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Linhas", df.shape[0])
    with col2:
        st.metric("Total de Colunas", df.shape[1])
    with col3:
        st.metric("Arquivo", st.session_state['filename'])
    
    # Controles de filtro e visualização
    st.subheader("🔍 Controles de Visualização")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Busca por texto
        search_text = st.text_input(
            "Buscar texto nos dados:",
            placeholder="Digite um termo para buscar...",
            help="A busca será feita em todas as colunas (texto)"
        )
    
    with col2:
        # Controle de quantidade de linhas
        max_rows = st.number_input(
            "Máximo de linhas:",
            min_value=10,
            max_value=len(df),
            value=min(100, len(df)),
            step=10,
            help="Limite a quantidade de linhas exibidas"
        )
    
    # Aplicar filtros usando função utilitária
    start_time = time.time()
    filtered_df = filter_dataframe_by_text(df, search_text)
    filter_duration = time.time() - start_time
    
    if search_text:
        logger.info(f"Filtro aplicado: '{search_text}' - {len(filtered_df)} registros encontrados - Duração: {filter_duration:.3f}s")
    
    # Feedback sobre busca por texto
    if search_text:
        show_search_feedback(search_text, filtered_df)
    
    # Limitar quantidade de linhas
    display_df = filtered_df.head(max_rows)
    
    # Exibir informações do filtro
    if len(filtered_df) > max_rows:
        st.info(f"📊 Exibindo {max_rows} de {len(filtered_df)} linhas filtradas")
    
    # Tabela principal
    st.subheader("📈 Dados")
    st.dataframe(
        display_df,
        use_container_width=True,
        height=400
    )
    
    # Seção de Estatísticas
    st.header("📊 Estatísticas dos Dados")
    
    # Obter colunas numéricas usando função utilitária
    numeric_columns = get_numeric_columns(df)
    
    if len(numeric_columns) > 0:
        show_numeric_statistics(df)
    else:
        show_no_numeric_columns_warning()
    
    # Resumo geral do dataset
    st.subheader("📋 Resumo Geral do Dataset")
    show_dataset_summary(df)
    
    # Seção de Gráficos
    st.header("📈 Gráficos Básicos")
    
    # Validar requisitos para gráficos usando função utilitária
    chart_valid, chart_message = validate_chart_requirements(df)
    
    if chart_valid:
        show_chart_section(df, numeric_columns)
    else:
        st.warning(f"⚠️ {chart_message}")
    
    # Informações adicionais usando função utilitária
    with st.expander("ℹ️ Informações das Colunas"):
        col_info = get_column_details(df)
        st.dataframe(col_info, use_container_width=True)