"""
Utilitários para análise de dados CSV

Este módulo contém funções puras para processamento e análise de dados CSV,
incluindo carregamento, filtragem, cálculo de estatísticas e preparação de dados para gráficos.
"""

import pandas as pd
from typing import Dict, List, Tuple, Any, Optional, Union


def load_csv_file(uploaded_file) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Carrega um arquivo CSV em um DataFrame.
    
    Args:
        uploaded_file: Arquivo CSV carregado via Streamlit
        
    Returns:
        Tuple contendo (DataFrame, mensagem_erro)
        Se sucesso: (df, None)
        Se erro: (None, mensagem_erro)
    """
    try:
        df = pd.read_csv(uploaded_file)
        return df, None
    except Exception as e:
        return None, str(e)


def get_dataframe_info(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Extrai informações básicas do DataFrame.
    
    Args:
        df: DataFrame para análise
        
    Returns:
        Dicionário com informações do DataFrame
    """
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    text_cols = df.select_dtypes(include=['object', 'string']).columns.tolist()
    
    return {
        'shape': df.shape,
        'total_rows': df.shape[0],
        'total_columns': df.shape[1],
        'numeric_columns': numeric_cols,
        'text_columns': text_cols,
        'numeric_count': len(numeric_cols),
        'text_count': len(text_cols),
        'column_types': df.dtypes.astype(str).to_dict(),
        'missing_values': df.isnull().sum().to_dict()
    }


def filter_dataframe_by_text(df: pd.DataFrame, search_text: str) -> Tuple[pd.DataFrame, int]:
    """
    Filtra DataFrame por texto em colunas de string.
    
    Args:
        df: DataFrame para filtrar
        search_text: Texto para buscar
        
    Returns:
        Tuple contendo (DataFrame filtrado, número de resultados encontrados)
    """
    if not search_text:
        return df, len(df)
    
    # Identificar colunas de texto
    text_columns = df.select_dtypes(include=['object', 'string']).columns
    
    if len(text_columns) == 0:
        return df, 0
    
    # Criar máscara de busca
    mask = df[text_columns].astype(str).apply(
        lambda x: x.str.contains(search_text, case=False, na=False)
    ).any(axis=1)
    
    filtered_df = df[mask]
    return filtered_df, len(filtered_df)


def limit_dataframe_rows(df: pd.DataFrame, max_rows: int) -> Tuple[pd.DataFrame, bool]:
    """
    Limita o número de linhas do DataFrame.
    
    Args:
        df: DataFrame para limitar
        max_rows: Número máximo de linhas
        
    Returns:
        Tuple contendo (DataFrame limitado, foi_limitado)
    """
    if len(df) > max_rows:
        return df.head(max_rows), True
    return df, False


def calculate_numeric_statistics(df: pd.DataFrame, selected_columns: List[str]) -> pd.DataFrame:
    """
    Calcula estatísticas para colunas numéricas selecionadas.
    
    Args:
        df: DataFrame com os dados
        selected_columns: Lista de colunas numéricas para analisar
        
    Returns:
        DataFrame com estatísticas calculadas
    """
    if not selected_columns:
        return pd.DataFrame()
    
    df_numeric = df[selected_columns]
    
    stats_data = {
        'Coluna': selected_columns,
        'Contagem': [df_numeric[col].count() for col in selected_columns],
        'Média': [df_numeric[col].mean() for col in selected_columns],
        'Soma': [df_numeric[col].sum() for col in selected_columns],
        'Mínimo': [df_numeric[col].min() for col in selected_columns],
        'Máximo': [df_numeric[col].max() for col in selected_columns],
        'Desvio Padrão': [df_numeric[col].std() for col in selected_columns]
    }
    
    stats_df = pd.DataFrame(stats_data)
    
    # Formatar números para melhor visualização
    stats_df['Média'] = stats_df['Média'].round(2)
    stats_df['Soma'] = stats_df['Soma'].round(2)
    stats_df['Mínimo'] = stats_df['Mínimo'].round(2)
    stats_df['Máximo'] = stats_df['Máximo'].round(2)
    stats_df['Desvio Padrão'] = stats_df['Desvio Padrão'].round(2)
    
    return stats_df


def calculate_summary_statistics(stats_df: pd.DataFrame) -> Dict[str, float]:
    """
    Calcula estatísticas resumidas a partir do DataFrame de estatísticas.
    
    Args:
        stats_df: DataFrame com estatísticas das colunas
        
    Returns:
        Dicionário com estatísticas resumidas
    """
    if stats_df.empty:
        return {'total_sum': 0.0, 'avg_mean': 0.0, 'total_count': 0}
    
    return {
        'total_sum': stats_df['Soma'].sum(),
        'avg_mean': stats_df['Média'].mean(),
        'total_count': stats_df['Contagem'].sum()
    }


def prepare_chart_data(df: pd.DataFrame, x_col: str, y_cols: List[str], max_points: int) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Prepara dados para criação de gráficos.
    
    Args:
        df: DataFrame com os dados
        x_col: Nome da coluna para eixo X (ou "(índice)" para usar índice)
        y_cols: Lista de colunas para eixo Y
        max_points: Número máximo de pontos no gráfico
        
    Returns:
        Tuple contendo (DataFrame preparado, informações do gráfico)
    """
    if not y_cols:
        return pd.DataFrame(), {}
    
    # Limitar número de linhas
    df_chart = df.copy()
    was_limited = False
    
    if len(df_chart) > max_points:
        df_chart = df_chart.head(max_points)
        was_limited = True
    
    # Preparar dados do eixo X
    if x_col == "(índice)":
        x_data = list(range(len(df_chart)))
        x_label = "Índice"
        is_date_sorted = False
    else:
        x_label = x_col
        # Se for coluna de data, tentar ordenar
        if df_chart[x_col].dtype == 'datetime64[ns]' or 'date' in str(df_chart[x_col].dtype).lower():
            df_chart = df_chart.sort_values(by=x_col)
            is_date_sorted = True
        else:
            is_date_sorted = False
        
        x_data = df_chart[x_col].tolist()
    
    # Preparar dados do gráfico
    chart_data = {x_label: x_data}
    for y_col in y_cols:
        chart_data[y_col] = df_chart[y_col].tolist()
    
    chart_df = pd.DataFrame(chart_data)
    
    # Informações do gráfico
    chart_info = {
        'x_label': x_label,
        'y_columns': y_cols,
        'total_points': len(df_chart),
        'was_limited': was_limited,
        'original_length': len(df),
        'is_date_sorted': is_date_sorted
    }
    
    return chart_df, chart_info


def calculate_chart_series_statistics(df: pd.DataFrame, y_cols: List[str]) -> pd.DataFrame:
    """
    Calcula estatísticas das séries plotadas no gráfico.
    
    Args:
        df: DataFrame com os dados do gráfico
        y_cols: Lista de colunas Y plotadas
        
    Returns:
        DataFrame com estatísticas das séries
    """
    if not y_cols:
        return pd.DataFrame()
    
    series_stats = []
    
    for y_col in y_cols:
        if y_col in df.columns:
            stats = {
                'Série': y_col,
                'Mín': df[y_col].min(),
                'Máx': df[y_col].max(),
                'Média': df[y_col].mean().round(2),
                'Pontos': df[y_col].count()
            }
            series_stats.append(stats)
    
    return pd.DataFrame(series_stats)


def get_data_type_summary(df: pd.DataFrame) -> Dict[str, int]:
    """
    Retorna um resumo dos tipos de dados no DataFrame.
    
    Args:
        df: DataFrame para analisar
        
    Returns:
        Dicionário com contagem de cada tipo de dado
    """
    return df.dtypes.value_counts().to_dict()


def create_info_dataframes(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Cria DataFrames com informações de tipos e valores ausentes.
    
    Args:
        df: DataFrame para analisar
        
    Returns:
        Tuple contendo (DataFrame de tipos, DataFrame de valores ausentes)
    """
    types_df = pd.DataFrame({
        'Coluna': df.columns,
        'Tipo': df.dtypes.astype(str)
    })
    
    missing_df = pd.DataFrame({
        'Coluna': df.columns,
        'Ausentes': df.isnull().sum()
    })
    
    return types_df, missing_df