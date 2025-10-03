
import streamlit as st
import pandas as pd
import logging
import time
from datetime import datetime
from utils import (
    load_csv_file,
    get_dataframe_info,
    filter_dataframe_by_text,
    limit_dataframe_rows,
    calculate_numeric_statistics,
    calculate_summary_statistics,
    prepare_chart_data,
    calculate_chart_series_statistics,
    get_data_type_summary,
    create_info_dataframes
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Log apenas no console
    ]
)

logger = logging.getLogger(__name__)

"""
CSV Upload and Analysis App

Este módulo implementa uma aplicação Streamlit para upload, visualização e análise
de arquivos CSV. A aplicação oferece funcionalidades para:

- Upload de arquivos CSV com validação
- Visualização interativa dos dados com filtros de busca
- Cálculo de estatísticas descritivas para colunas numéricas
- Geração de gráficos básicos (linha e barras) usando componentes nativos do Streamlit
- Análise de tipos de dados e valores ausentes

Autor: Sistema de Análise CSV
Versão: 1.0
"""

# Configuração da página
st.set_page_config(page_title="CSV Upload App", page_icon="📊", layout="wide")

st.title("📊 Upload de Arquivo CSV")
st.write("Faça upload de um arquivo **.csv** para carregar os dados em um DataFrame.")

# Seção de upload
st.subheader("📁 Upload do Arquivo")

uploaded_file = st.file_uploader(
    "Selecione um arquivo CSV", 
    type=["csv"],
    help="Escolha um arquivo .csv do seu computador"
)

if uploaded_file is not None:
    # Log do início do upload
    start_time = time.time()
    logger.info(f"Iniciando upload do arquivo: {uploaded_file.name} (tamanho: {uploaded_file.size} bytes)")
    
    # Usar função do utils para carregar o arquivo
    df, error_message = load_csv_file(uploaded_file)
    
    if df is not None:
        # Calcular duração do upload
        upload_duration = time.time() - start_time
        logger.info(f"Upload concluído com sucesso - Arquivo: {uploaded_file.name}, "
                   f"Dimensões: {df.shape[0]}x{df.shape[1]}, "
                   f"Duração: {upload_duration:.2f}s")
        
        # Armazena no estado da sessão
        st.session_state['dataframe'] = df
        st.session_state['filename'] = uploaded_file.name
        
        # Obter informações do DataFrame usando utils
        df_info = get_dataframe_info(df)
        
        # Mensagem de confirmação
        st.success(f"✅ Arquivo **{uploaded_file.name}** carregado com sucesso!")
        st.info(f"📊 Dataset contém **{df_info['total_rows']}** linhas e **{df_info['total_columns']}** colunas")
        
        # Prévia dos dados
        with st.expander("👀 Visualizar prévia dos dados"):
            st.dataframe(df.head(10), use_container_width=True)
    else:
        logger.error(f"Erro ao carregar arquivo {uploaded_file.name}: {error_message}")
        st.error(f"❌ Erro ao carregar o arquivo: {error_message}")
        st.info("Verifique se o arquivo está no formato CSV correto.")

else:
    # Instruções quando não há arquivo
    st.info("👆 Faça upload de um arquivo CSV usando o botão acima para começar.")
    
    with st.expander("📋 Instruções"):
        st.markdown("""
        **Como usar:**
        1. Clique no botão "Browse files" acima
        2. Selecione um arquivo .csv do seu computador
        3. O arquivo será carregado automaticamente
        4. Você verá uma confirmação com o número de linhas e colunas
        
        **Requisitos do arquivo:**
        - Formato: .csv (valores separados por vírgula)
        - Encoding: UTF-8 (recomendado)
        - Primeira linha deve conter os nomes das colunas
        """)

# Verificar se há dados carregados no estado da sessão
if 'dataframe' in st.session_state:
    df = st.session_state['dataframe']
    df_info = get_dataframe_info(df)
    
    st.markdown("---")
    st.subheader("💾 Dados Carregados")
    st.write(f"Arquivo atual: **{st.session_state.get('filename', 'N/A')}**")
    st.write(f"Dimensões: **{df_info['total_rows']}** linhas × **{df_info['total_columns']}** colunas")
    
    if st.button("🗑️ Limpar dados carregados"):
        filename = st.session_state.get('filename', 'arquivo desconhecido')
        logger.info(f"Limpando dados carregados do arquivo: {filename}")
        del st.session_state['dataframe']
        del st.session_state['filename']
        st.rerun()

    # Exibição do DataFrame com controles
    st.markdown("---")
    st.subheader("📋 Visualização dos Dados")
    
    # Controles de filtro e exibição
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_text = st.text_input(
            "🔍 Buscar texto nos dados",
            placeholder="Digite um termo para filtrar os dados...",
            help="A busca será feita em todas as colunas de texto"
        )
    
    with col2:
        max_rows = st.number_input(
            "📊 Máximo de linhas a exibir",
            min_value=10,
            max_value=10000,
            value=100,
            step=50,
            help="Limite a quantidade de linhas para melhor performance"
        )
    
    # Aplicar filtros usando funções do utils
    start_filter_time = time.time()
    df_display = df.copy()
    original_rows = len(df_display)
    
    # Filtro de busca por texto
    if search_text:
        logger.info(f"Aplicando filtro de busca: '{search_text}' em dataset com {original_rows} linhas")
        
        df_display, found_count = filter_dataframe_by_text(df_display, search_text)
        
        filter_duration = time.time() - start_filter_time
        
        logger.info(f"Filtro aplicado - Termo: '{search_text}', "
                   f"Resultados: {found_count}/{original_rows} linhas, "
                   f"Duração: {filter_duration:.3f}s")
        
        if found_count == 0:
            st.warning(f"⚠️ Nenhum resultado encontrado para '{search_text}'")
        elif len(df_info['text_columns']) == 0:
            st.warning("⚠️ Não há colunas de texto para realizar a busca")
        else:
            st.info(f"🔍 Encontrados {found_count} registros contendo '{search_text}'")
    
    # Limitar número de linhas
    df_display, was_limited = limit_dataframe_rows(df_display, max_rows)
    if was_limited:
        st.info(f"📊 Exibindo as primeiras {max_rows} linhas de {len(df)} total")
    
    # Exibir informações do DataFrame filtrado
    st.write(f"**Shape atual:** {df_display.shape[0]} linhas × {df_display.shape[1]} colunas")
    
    # Exibir o DataFrame
    st.dataframe(df_display, use_container_width=True, height=500)
    
    # Informações adicionais usando funções do utils
    with st.expander("ℹ️ Informações detalhadas"):
        info_col1, info_col2 = st.columns(2)
        
        types_df, missing_df = create_info_dataframes(df_display)
        
        with info_col1:
            st.markdown("**Tipos de dados:**")
            st.dataframe(types_df, use_container_width=True)
        
        with info_col2:
            st.markdown("**Valores ausentes:**")
            st.dataframe(missing_df, use_container_width=True)
    
    # Seção de estatísticas
    st.markdown("---")
    st.subheader("📊 Estatísticas do Dataset")
    
    # Resumo geral do dataset
    st.markdown("### 📋 Resumo Geral")
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    
    with summary_col1:
        st.metric("Total de Linhas", f"{df_info['total_rows']:,}")
    
    with summary_col2:
        st.metric("Total de Colunas", f"{df_info['total_columns']:,}")
    
    with summary_col3:
        st.metric("Colunas Numéricas", df_info['numeric_count'])
    
    with summary_col4:
        st.metric("Colunas de Texto", df_info['text_count'])
    
    # Estatísticas para colunas numéricas
    st.markdown("### 🔢 Estatísticas das Colunas Numéricas")
    
    if df_info['numeric_count'] > 0:
        # Seletor de colunas numéricas
        default_cols = df_info['numeric_columns'][:5] if len(df_info['numeric_columns']) <= 5 else df_info['numeric_columns'][:3]
        
        selected_numeric_cols = st.multiselect(
            "Selecione as colunas numéricas para análise:",
            options=df_info['numeric_columns'],
            default=default_cols,
            help="Escolha quais colunas numéricas deseja analisar"
        )
        
        if selected_numeric_cols:
            # Log do cálculo de estatísticas
            start_stats_time = time.time()
            logger.info(f"Calculando estatísticas para {len(selected_numeric_cols)} colunas numéricas: {selected_numeric_cols}")
            
            # Calcular estatísticas usando função do utils
            stats_df = calculate_numeric_statistics(df, selected_numeric_cols)
            
            stats_duration = time.time() - start_stats_time
            logger.info(f"Estatísticas calculadas - Colunas: {len(selected_numeric_cols)}, "
                       f"Duração: {stats_duration:.3f}s")
            
            # Exibir tabela de estatísticas
            st.dataframe(stats_df, use_container_width=True, hide_index=True)
            
            # Estatísticas resumidas em métricas usando função do utils
            summary_stats = calculate_summary_statistics(stats_df)
            
            st.markdown("#### 📈 Resumo das Estatísticas Selecionadas")
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            
            with metric_col1:
                st.metric("Soma Total", f"{summary_stats['total_sum']:,.2f}")
            
            with metric_col2:
                st.metric("Média das Médias", f"{summary_stats['avg_mean']:.2f}")
            
            with metric_col3:
                st.metric("Total de Valores", f"{summary_stats['total_count']:,}")
            
        else:
            st.info("👆 Selecione pelo menos uma coluna numérica para ver as estatísticas.")
    
    else:
        # Aviso quando não há colunas numéricas
        st.warning("⚠️ **Não há colunas numéricas no dataset**")
        st.info("""
        📝 **O que isso significa:**
        - Todas as colunas contêm dados de texto, datas ou outros tipos não numéricos
        - Não é possível calcular médias, somas ou outras estatísticas numéricas
        - Considere converter colunas relevantes para formato numérico se necessário
        """)
        
        # Mostrar tipos de dados disponíveis
        st.markdown("**Tipos de dados encontrados:**")
        type_summary = get_data_type_summary(df)
        for dtype, count in type_summary.items():
            st.write(f"- **{dtype}**: {count} coluna(s)")

    # Seção de gráficos
    st.markdown("---")
    st.subheader("📈 Visualização Gráfica")
    
    # Verificar se há colunas numéricas para o gráfico
    if df_info['numeric_count'] > 0:
        # Controles do gráfico
        graph_col1, graph_col2 = st.columns([1, 2])
        
        with graph_col1:
            # Tipo do gráfico
            chart_type = st.radio(
                "📊 Tipo do gráfico:",
                ["Linha", "Barras"],
                help="Escolha o tipo de visualização"
            )
        
        with graph_col2:
            # Coluna do eixo X
            all_cols = df.columns.tolist()
            x_options = ["(índice)"] + all_cols
            
            x_col = st.selectbox(
                "🔢 Coluna do eixo X:",
                options=x_options,
                help="Escolha a coluna para o eixo horizontal"
            )
        
        # Colunas do eixo Y
        y_cols = st.multiselect(
            "📊 Colunas do eixo Y (apenas numéricas):",
            options=df_info['numeric_columns'],
            default=df_info['numeric_columns'][:1] if len(df_info['numeric_columns']) > 0 else [],
            help="Selecione uma ou mais colunas numéricas para plotar"
        )
        
        # Controle de limite de dados
        max_points = st.slider(
            "🎯 Máximo de pontos no gráfico:",
            min_value=50,
            max_value=10000,
            value=200,
            step=50,
            help="Limite a quantidade de pontos para melhor performance"
        )
        
        if y_cols:
            try:
                # Log da preparação do gráfico
                start_chart_time = time.time()
                logger.info(f"Preparando gráfico - Tipo: {chart_type}, Eixo X: {x_col}, Eixo Y: {y_cols}")
                
                # Preparar dados para o gráfico usando função do utils
                chart_df, chart_info = prepare_chart_data(df, x_col, y_cols, max_points)
                
                chart_duration = time.time() - start_chart_time
                logger.info(f"Dados para gráfico preparados - Pontos: {len(chart_df)}, "
                           f"Duração: {chart_duration:.3f}s")
                
                # Mostrar informação sobre limitação de dados
                if chart_info['was_limited']:
                    st.info(f"📊 Exibindo os primeiros {len(chart_df)} pontos de {len(df)} total")
                
                # Criar gráfico
                if chart_type == "Linha":
                    st.line_chart(chart_df.set_index(chart_info['x_label']), use_container_width=True)
                else:
                    st.bar_chart(chart_df.set_index(chart_info['x_label']), use_container_width=True)
                
                # Informações do gráfico
                st.markdown("#### 📋 Informações do Gráfico")
                info_col1, info_col2, info_col3 = st.columns(3)
                
                with info_col1:
                    st.write(f"**Tipo:** {chart_type}")
                
                with info_col2:
                    st.write(f"**Eixo X:** {chart_info['x_label']}")
                
                with info_col3:
                    st.write(f"**Séries Y:** {len(y_cols)}")
                
                # Mostrar estatísticas básicas das séries
                st.markdown("#### 📊 Estatísticas das Séries Plotadas")
                series_stats_df = calculate_chart_series_statistics(chart_df, y_cols)
                st.dataframe(series_stats_df, use_container_width=True, hide_index=True)
            
            except Exception as e:
                logger.error(f"Erro ao gerar gráfico: {str(e)}")
                st.error(f"❌ Erro ao gerar o gráfico: {str(e)}")
                st.info("Verifique se as colunas selecionadas contêm dados válidos para plotagem.")
        
        else:
            st.info("👆 Selecione pelo menos uma coluna numérica para o eixo Y.")
    
    else:
        # Aviso quando não há colunas numéricas
        st.warning("⚠️ **Não é possível criar gráficos sem colunas numéricas**")
        st.info("""
        📝 **Para criar gráficos você precisa de:**
        - Pelo menos uma coluna com dados numéricos
        - Os dados devem estar em formato adequado (números, não texto)
        
        💡 **Dica:** Verifique se suas colunas numéricas foram carregadas corretamente na seção de tipos de dados acima.
        """)
