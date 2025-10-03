"""
Utilitários para processamento de dados CSV.

Este módulo contém funções puras para manipulação e análise de dados CSV,
separando a lógica de negócio da interface do usuário Streamlit.
"""

import pandas as pd
import io
from typing import List, Dict, Any, Tuple, Optional


def load_csv_data(uploaded_file) -> pd.DataFrame:
    """
    Carrega dados de um arquivo CSV em um DataFrame.
    
    Args:
        uploaded_file: Arquivo CSV, string com dados CSV, ou file-like object
        
    Returns:
        pd.DataFrame: DataFrame com os dados do arquivo CSV
        
    Raises:
        Exception: Se houver erro na leitura do arquivo CSV
    """
    try:
        # Se for string, criar StringIO
        if isinstance(uploaded_file, str):
            return pd.read_csv(io.StringIO(uploaded_file))
        # Se for bytes, criar BytesIO  
        elif isinstance(uploaded_file, bytes):
            return pd.read_csv(io.BytesIO(uploaded_file))
        # Caso contrário, assumir que é file-like object
        else:
            return pd.read_csv(uploaded_file)
    except Exception as e:
        raise Exception(f"Erro ao carregar CSV: {str(e)}")


def filter_dataframe_by_text(df: pd.DataFrame, search_text: str) -> pd.DataFrame:
    """
    Filtra DataFrame buscando texto em todas as colunas.
    
    Args:
        df: DataFrame a ser filtrado
        search_text: Texto a ser buscado (case-insensitive)
        
    Returns:
        pd.DataFrame: DataFrame filtrado contendo apenas linhas com o texto buscado
    """
    if not search_text or search_text.strip() == "":
        return df.copy()
    
    # Converte todas as colunas para string e busca o texto
    mask = df.astype(str).apply(
        lambda x: x.str.contains(search_text, case=False, na=False)
    ).any(axis=1)
    
    return df[mask]


def get_numeric_columns(df: pd.DataFrame) -> pd.Index:
    """
    Identifica colunas numéricas em um DataFrame.
    
    Args:
        df: DataFrame a ser analisado
        
    Returns:
        pd.Index: Índice com nomes das colunas numéricas
    """
    return df.select_dtypes(include=['int64', 'float64', 'int32', 'float32']).columns


def calculate_numeric_statistics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calcula estatísticas descritivas para colunas numéricas.
    
    Args:
        df: DataFrame com dados numéricos
        
    Returns:
        Dict contendo:
            - stats_df: DataFrame com estatísticas por coluna
            - summary: Dict com resumo geral das estatísticas
    """
    numeric_columns = get_numeric_columns(df)
    
    if len(numeric_columns) == 0:
        return {'stats_df': pd.DataFrame(), 'summary': {}}
    
    # Criar DataFrame com estatísticas detalhadas
    stats_data = []
    for col in numeric_columns:
        stats_data.append({
            'Coluna': col,
            'Contagem': df[col].count(),
            'Média': round(df[col].mean(), 2),
            'Soma': round(df[col].sum(), 2),
            'Mínimo': df[col].min(),
            'Máximo': df[col].max(),
            'Mediana': round(df[col].median(), 2),
            'Desvio Padrão': round(df[col].std(), 2)
        })
    
    stats_df = pd.DataFrame(stats_data)
    
    # Calcular resumo geral
    summary = {
        'total_numeric_columns': len(numeric_columns),
        'total_values': df[numeric_columns].count().sum(),
        'total_sum': round(df[numeric_columns].sum().sum(), 2),
        'overall_mean': round(df[numeric_columns].mean().mean(), 2)
    }
    
    return {'stats_df': stats_df, 'summary': summary}


def get_dataset_info(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Obtém informações gerais sobre o dataset.
    
    Args:
        df: DataFrame a ser analisado
        
    Returns:
        Dict com informações básicas e distribuição de tipos
    """
    basic_info = {
        'dimensions': f"{df.shape[0]} linhas × {df.shape[1]} colunas",
        'memory_usage_kb': round(df.memory_usage(deep=True).sum() / 1024, 1),
        'unique_values_total': df.nunique().sum(),
        'null_values_total': df.isnull().sum().sum()
    }
    
    type_distribution = df.dtypes.value_counts().to_dict()
    
    return {
        'basic_info': basic_info,
        'type_distribution': type_distribution
    }


def get_column_details(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria DataFrame com informações detalhadas das colunas.
    
    Args:
        df: DataFrame a ser analisado
        
    Returns:
        pd.DataFrame: Informações sobre cada coluna (tipo, valores únicos, nulos)
    """
    return pd.DataFrame({
        'Coluna': df.columns,
        'Tipo': df.dtypes.astype(str),
        'Valores Únicos': [df[col].nunique() for col in df.columns],
        'Valores Nulos': [df[col].isnull().sum() for col in df.columns]
    })


def prepare_chart_data(df: pd.DataFrame, x_column: str, y_columns: List[str]) -> Dict[str, Any]:
    """
    Prepara dados para geração de gráfico.
    
    Args:
        df: DataFrame com os dados originais
        x_column: Nome da coluna para eixo X
        y_columns: Lista com nomes das colunas para eixo Y
        
    Returns:
        Dict contendo:
            - chart_df: DataFrame preparado para o gráfico
            - is_date: Boolean indicando se X é uma coluna de data
            - stats: Estatísticas das colunas Y
    """
    if not y_columns or not x_column:
        return {'chart_df': pd.DataFrame(), 'is_date': False, 'stats': {}}
    
    # Verificar se as colunas existem
    missing_cols = [col for col in [x_column] + y_columns if col not in df.columns]
    if missing_cols:
        return {'chart_df': pd.DataFrame(), 'is_date': False, 'stats': {}}
    
    # Selecionar apenas as colunas necessárias
    chart_df = df[[x_column] + y_columns].copy()
    
    # Remover linhas com valores nulos
    chart_df = chart_df.dropna()
    
    if len(chart_df) == 0:
        return {'chart_df': pd.DataFrame(), 'is_date': False, 'stats': {}}
    
    # Verificar se a coluna X é uma data
    is_date = False
    try:
        pd.to_datetime(chart_df[x_column])
        is_date = True
        # Converter e ordenar por data
        chart_df[x_column] = pd.to_datetime(chart_df[x_column])
        chart_df = chart_df.sort_values(x_column)
    except:
        pass
    
    # Calcular estatísticas das colunas Y
    y_stats = {}
    for col in y_columns:
        y_stats[col] = {
            'min': chart_df[col].min(),
            'max': chart_df[col].max(),
            'mean': chart_df[col].mean()
        }
    
    return {
        'chart_df': chart_df,
        'is_date': is_date,
        'stats': y_stats
    }


def validate_chart_requirements(df: pd.DataFrame) -> Tuple[bool, str]:
    """
    Valida se o dataset atende aos requisitos para gerar gráficos.
    
    Args:
        df: DataFrame a ser validado
        
    Returns:
        Tuple[bool, str]: (é_válido, mensagem_explicativa)
    """
    if len(df.columns) < 2:
        return False, "O dataset precisa ter pelo menos 2 colunas para gerar gráficos"
    
    numeric_columns = get_numeric_columns(df)
    if len(numeric_columns) == 0:
        return False, "Nenhuma coluna numérica disponível para criar gráficos"
    
    return True, "Dataset válido para gráficos"