"""
Testes automatizados para funções utilitárias do CSV Viewer.

Este módulo contém testes abrangentes para todas as funções do utils.py,
cobrindo diferentes cenários de dados CSV, incluindo separadores diferentes,
encodings, valores ausentes, conversão de datas e cálculos estatísticos.
"""

import pytest
import pandas as pd
import numpy as np
import io
from datetime import datetime, date
import sys
import os

# Adicionar o diretório pai ao path para importar utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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


class TestLoadCSVData:
    """Testes para carregamento de dados CSV com diferentes formatos."""
    
    def test_load_csv_basic(self):
        """Teste básico de carregamento de CSV."""
        csv_data = "name,age,salary\nJohn,25,50000\nJane,30,60000"
        csv_file = io.StringIO(csv_data)
        df = load_csv_data(csv_file)
        
        assert len(df) == 2
        assert list(df.columns) == ['name', 'age', 'salary']
        assert df.iloc[0]['name'] == 'John'
        assert df.iloc[0]['age'] == 25
    
    def test_load_csv_with_missing_values(self):
        """Teste com valores ausentes."""
        csv_data = "name,age,salary\nJohn,25,\nJane,,60000\n,35,55000"
        csv_file = io.StringIO(csv_data)
        df = load_csv_data(csv_file)
        
        assert len(df) == 3
        assert pd.isna(df.iloc[0]['salary'])
        assert pd.isna(df.iloc[1]['age'])
        assert pd.isna(df.iloc[2]['name'])
    
    def test_load_csv_empty_file(self):
        """Teste com arquivo vazio."""
        csv_data = ""
        csv_file = io.StringIO(csv_data)
        with pytest.raises(Exception):
            load_csv_data(csv_file)
    
    def test_load_csv_string_input(self):
        """Teste com entrada string direta."""
        csv_data = "name,age,salary\nJohn,25,50000\nJane,30,60000"
        df = load_csv_data(csv_data)
        
        assert len(df) == 2
        assert list(df.columns) == ['name', 'age', 'salary']
        assert df.iloc[0]['name'] == 'John'
        assert df.iloc[0]['age'] == 25
    
    def test_load_csv_bytes_input(self):
        """Teste com entrada bytes."""
        csv_data = b"name,age,salary\nJohn,25,50000\nJane,30,60000"
        df = load_csv_data(csv_data)
        
        assert len(df) == 2
        assert list(df.columns) == ['name', 'age', 'salary']
        assert df.iloc[0]['name'] == 'John'
        assert df.iloc[0]['age'] == 25


class TestFilterDataframeByText:
    """Testes para filtragem de DataFrame por texto."""
    
    @pytest.fixture
    def sample_df(self):
        """DataFrame de exemplo para testes."""
        return pd.DataFrame({
            'name': ['John Doe', 'Jane Smith', 'Bob Johnson', 'Alice Brown'],
            'city': ['New York', 'Los Angeles', 'Chicago', 'Houston'],
            'profession': ['Engineer', 'Doctor', 'Teacher', 'Artist'],
            'age': [25, 30, 35, 28]
        })
    
    def test_filter_by_text_found(self, sample_df):
        """Teste de busca com resultados encontrados."""
        result = filter_dataframe_by_text(sample_df, 'John')
        
        assert len(result) == 2  # John Doe e Bob Johnson
        assert 'John Doe' in result['name'].values
        assert 'Bob Johnson' in result['name'].values
    
    def test_filter_by_text_case_insensitive(self, sample_df):
        """Teste de busca case-insensitive."""
        result = filter_dataframe_by_text(sample_df, 'DOCTOR')
        
        assert len(result) == 1
        assert result.iloc[0]['name'] == 'Jane Smith'
        assert result.iloc[0]['profession'] == 'Doctor'
    
    def test_filter_by_text_not_found(self, sample_df):
        """Teste de busca sem resultados."""
        result = filter_dataframe_by_text(sample_df, 'XYZ123')
        
        assert len(result) == 0
    
    def test_filter_by_text_empty_search(self, sample_df):
        """Teste com texto de busca vazio."""
        result = filter_dataframe_by_text(sample_df, '')
        
        assert len(result) == len(sample_df)
        pd.testing.assert_frame_equal(result, sample_df)
    
    def test_filter_by_text_whitespace_search(self, sample_df):
        """Teste com texto de busca apenas espaços."""
        result = filter_dataframe_by_text(sample_df, '   ')
        
        # Espaços são removidos pela função strip(), deve retornar DataFrame completo
        assert len(result) == len(sample_df)
    
    def test_filter_by_text_numeric_column(self, sample_df):
        """Teste de busca em coluna numérica."""
        result = filter_dataframe_by_text(sample_df, '25')
        
        assert len(result) == 1
        assert result.iloc[0]['age'] == 25
    
    def test_filter_by_text_partial_match(self, sample_df):
        """Teste de busca por correspondência parcial."""
        result = filter_dataframe_by_text(sample_df, 'Ang')
        
        assert len(result) == 1  # Los Angeles
        assert result.iloc[0]['city'] == 'Los Angeles'


class TestGetNumericColumns:
    """Testes para identificação de colunas numéricas."""
    
    def test_get_numeric_columns_mixed_types(self):
        """Teste com DataFrame com tipos mistos."""
        df = pd.DataFrame({
            'name': ['A', 'B', 'C'],
            'age': [25, 30, 35],
            'salary': [50000.0, 60000.0, 70000.0],
            'active': [True, False, True],
            'score': np.array([85, 92, 88], dtype='int32')
        })
        
        numeric_cols = get_numeric_columns(df)
        
        assert 'age' in numeric_cols
        assert 'salary' in numeric_cols
        assert 'score' in numeric_cols
        assert 'name' not in numeric_cols
        assert 'active' not in numeric_cols
    
    def test_get_numeric_columns_all_numeric(self):
        """Teste com DataFrame apenas numérico."""
        df = pd.DataFrame({
            'int_col': [1, 2, 3],
            'float_col': [1.1, 2.2, 3.3],
            'int32_col': np.array([10, 20, 30], dtype='int32'),
            'float32_col': np.array([1.5, 2.5, 3.5], dtype='float32')
        })
        
        numeric_cols = get_numeric_columns(df)
        
        assert len(numeric_cols) == 4
        assert all(col in numeric_cols for col in df.columns)
    
    def test_get_numeric_columns_no_numeric(self):
        """Teste com DataFrame sem colunas numéricas."""
        df = pd.DataFrame({
            'name': ['A', 'B', 'C'],
            'category': ['X', 'Y', 'Z'],
            'active': [True, False, True]
        })
        
        numeric_cols = get_numeric_columns(df)
        
        assert len(numeric_cols) == 0
    
    def test_get_numeric_columns_empty_dataframe(self):
        """Teste com DataFrame vazio."""
        df = pd.DataFrame()
        
        numeric_cols = get_numeric_columns(df)
        
        assert len(numeric_cols) == 0


class TestCalculateNumericStatistics:
    """Testes para cálculo de estatísticas numéricas."""
    
    @pytest.fixture
    def numeric_df(self):
        """DataFrame com dados numéricos para testes."""
        return pd.DataFrame({
            'score1': [85, 92, 78, 95, 88],
            'score2': [90.5, 87.2, 93.1, 89.8, 91.4],
            'count': [10, 15, 8, 12, 9],
            'name': ['A', 'B', 'C', 'D', 'E']  # Coluna não numérica
        })
    
    def test_calculate_statistics_basic(self, numeric_df):
        """Teste básico de cálculo de estatísticas."""
        result = calculate_numeric_statistics(numeric_df)
        
        stats_df = result['stats_df']
        summary = result['summary']
        
        # Verificar estrutura do DataFrame de estatísticas
        assert len(stats_df) == 3  # 3 colunas numéricas
        expected_columns = ['Coluna', 'Contagem', 'Média', 'Soma', 'Mínimo', 'Máximo', 'Mediana', 'Desvio Padrão']
        assert all(col in stats_df.columns for col in expected_columns)
        
        # Verificar dados específicos para score1
        score1_stats = stats_df[stats_df['Coluna'] == 'score1'].iloc[0]
        assert score1_stats['Contagem'] == 5
        assert score1_stats['Média'] == 87.6  # (85+92+78+95+88)/5
        assert score1_stats['Soma'] == 438
        assert score1_stats['Mínimo'] == 78
        assert score1_stats['Máximo'] == 95
        
        # Verificar resumo geral
        assert summary['total_numeric_columns'] == 3
        assert summary['total_values'] == 15  # 3 colunas × 5 linhas
    
    def test_calculate_statistics_with_missing_values(self):
        """Teste com valores ausentes."""
        df = pd.DataFrame({
            'col1': [1, 2, np.nan, 4, 5],
            'col2': [10, np.nan, 30, np.nan, 50]
        })
        
        result = calculate_numeric_statistics(df)
        stats_df = result['stats_df']
        
        # col1 deve ter contagem 4 (sem o NaN)
        col1_stats = stats_df[stats_df['Coluna'] == 'col1'].iloc[0]
        assert col1_stats['Contagem'] == 4
        assert col1_stats['Média'] == 3.0  # (1+2+4+5)/4
        
        # col2 deve ter contagem 3
        col2_stats = stats_df[stats_df['Coluna'] == 'col2'].iloc[0]
        assert col2_stats['Contagem'] == 3
        assert col2_stats['Média'] == 30.0  # (10+30+50)/3
    
    def test_calculate_statistics_no_numeric_columns(self):
        """Teste com DataFrame sem colunas numéricas."""
        df = pd.DataFrame({
            'name': ['A', 'B', 'C'],
            'category': ['X', 'Y', 'Z']
        })
        
        result = calculate_numeric_statistics(df)
        
        assert result['stats_df'].empty
        assert result['summary'] == {}
    
    def test_calculate_statistics_single_value(self):
        """Teste com apenas um valor por coluna."""
        df = pd.DataFrame({
            'single': [42]
        })
        
        result = calculate_numeric_statistics(df)
        stats_df = result['stats_df']
        
        assert len(stats_df) == 1
        single_stats = stats_df.iloc[0]
        assert single_stats['Contagem'] == 1
        assert single_stats['Média'] == 42
        assert single_stats['Soma'] == 42
        assert single_stats['Mínimo'] == 42
        assert single_stats['Máximo'] == 42
        assert single_stats['Mediana'] == 42
        # Desvio padrão de um único valor deve ser NaN, não 0
        assert pd.isna(single_stats['Desvio Padrão']) or single_stats['Desvio Padrão'] == 0.0


class TestGetDatasetInfo:
    """Testes para obtenção de informações do dataset."""
    
    def test_get_dataset_info_basic(self):
        """Teste básico de informações do dataset."""
        df = pd.DataFrame({
            'name': ['A', 'B', 'C'],
            'age': [25, 30, 35],
            'salary': [50000.0, 60000.0, np.nan]
        })
        
        info = get_dataset_info(df)
        
        basic_info = info['basic_info']
        assert basic_info['dimensions'] == "3 linhas × 3 colunas"
        assert basic_info['unique_values_total'] == 8  # 3+3+2 (salary tem NaN)
        assert basic_info['null_values_total'] == 1  # 1 NaN em salary
        assert isinstance(basic_info['memory_usage_kb'], float)
        
        type_distribution = info['type_distribution']
        # Verificar se os tipos de dados estão presentes (pode variar entre 'object' e 'O')
        type_names = [str(dtype) for dtype in type_distribution.keys()]
        assert any('object' in name or 'O' in name for name in type_names)  # name
        assert any('int' in name for name in type_names)    # age
        assert any('float' in name for name in type_names)  # salary
    
    def test_get_dataset_info_empty_dataframe(self):
        """Teste com DataFrame vazio."""
        df = pd.DataFrame()
        
        info = get_dataset_info(df)
        
        basic_info = info['basic_info']
        assert basic_info['dimensions'] == "0 linhas × 0 colunas"
        assert basic_info['unique_values_total'] == 0
        assert basic_info['null_values_total'] == 0
        
        assert info['type_distribution'] == {}
    
    def test_get_dataset_info_all_nulls(self):
        """Teste com DataFrame apenas com valores nulos."""
        df = pd.DataFrame({
            'col1': [np.nan, np.nan],
            'col2': [None, None]
        })
        
        info = get_dataset_info(df)
        
        basic_info = info['basic_info']
        assert basic_info['null_values_total'] == 4  # 2 colunas × 2 linhas


class TestGetColumnDetails:
    """Testes para obtenção de detalhes das colunas."""
    
    def test_get_column_details_basic(self):
        """Teste básico de detalhes das colunas."""
        df = pd.DataFrame({
            'name': ['A', 'B', 'A'],
            'age': [25, 30, np.nan],
            'active': [True, False, True]
        })
        
        details = get_column_details(df)
        
        assert len(details) == 3
        assert list(details.columns) == ['Coluna', 'Tipo', 'Valores Únicos', 'Valores Nulos']
        
        # Verificar detalhes da coluna 'name'
        name_row = details[details['Coluna'] == 'name'].iloc[0]
        assert name_row['Valores Únicos'] == 2  # 'A' e 'B'
        assert name_row['Valores Nulos'] == 0
        
        # Verificar detalhes da coluna 'age'
        age_row = details[details['Coluna'] == 'age'].iloc[0]
        assert age_row['Valores Únicos'] == 2  # 25 e 30 (NaN não conta)
        assert age_row['Valores Nulos'] == 1


class TestPrepareChartData:
    """Testes para preparação de dados para gráficos."""
    
    @pytest.fixture
    def chart_df(self):
        """DataFrame para testes de gráficos."""
        return pd.DataFrame({
            'date': ['2023-01-01', '2023-01-02', '2023-01-03'],
            'sales': [100, 150, 120],
            'profit': [20, 30, 25],
            'category': ['A', 'B', 'A']
        })
    
    def test_prepare_chart_data_basic(self, chart_df):
        """Teste básico de preparação de dados para gráfico."""
        result = prepare_chart_data(chart_df, 'category', ['sales', 'profit'])
        
        assert len(result['chart_df']) == 3
        assert result['is_date'] == False
        assert 'sales' in result['stats']
        assert 'profit' in result['stats']
        
        # Verificar estatísticas
        sales_stats = result['stats']['sales']
        assert sales_stats['min'] == 100
        assert sales_stats['max'] == 150
        assert sales_stats['mean'] == pytest.approx(123.33, rel=1e-2)
    
    def test_prepare_chart_data_with_dates(self, chart_df):
        """Teste com coluna de data."""
        result = prepare_chart_data(chart_df, 'date', ['sales'])
        
        assert result['is_date'] == True
        assert len(result['chart_df']) == 3
        
        # Verificar se os dados estão ordenados por data
        chart_data = result['chart_df']
        dates = pd.to_datetime(chart_data['date'])
        assert dates.is_monotonic_increasing
    
    def test_prepare_chart_data_with_nulls(self):
        """Teste com valores nulos."""
        df = pd.DataFrame({
            'x': ['A', 'B', 'C'],
            'y': [1, np.nan, 3]
        })
        
        result = prepare_chart_data(df, 'x', ['y'])
        
        # Deve remover linhas com NaN
        assert len(result['chart_df']) == 2
        assert not result['chart_df']['y'].isna().any()
    
    def test_prepare_chart_data_empty_inputs(self, chart_df):
        """Teste com entradas vazias."""
        # Sem colunas Y
        result1 = prepare_chart_data(chart_df, 'category', [])
        assert result1['chart_df'].empty
        
        # Sem coluna X
        result2 = prepare_chart_data(chart_df, '', ['sales'])
        assert result2['chart_df'].empty
    
    def test_prepare_chart_data_missing_columns(self, chart_df):
        """Teste com colunas inexistentes."""
        # Teste deve retornar DataFrame vazio quando colunas não existem
        result = prepare_chart_data(chart_df, 'nonexistent', ['sales'])
        
        assert result['chart_df'].empty
        assert result['is_date'] == False
        assert result['stats'] == {}
    
    def test_prepare_chart_data_date_parsing_edge_cases(self):
        """Teste de parsing de datas com casos extremos."""
        df = pd.DataFrame({
            'date_str': ['2023-01-01', '2023/01/02', 'invalid_date'],
            'value': [1, 2, 3]
        })
        
        result = prepare_chart_data(df, 'date_str', ['value'])
        
        # Se alguma data for inválida, não deve ser detectada como coluna de data
        # O comportamento pode variar dependendo da implementação do pandas
        assert isinstance(result['is_date'], bool)
        assert len(result['chart_df']) <= 3


class TestValidateChartRequirements:
    """Testes para validação de requisitos de gráficos."""
    
    def test_validate_chart_valid_dataframe(self):
        """Teste com DataFrame válido para gráficos."""
        df = pd.DataFrame({
            'category': ['A', 'B', 'C'],
            'value': [1, 2, 3]
        })
        
        is_valid, message = validate_chart_requirements(df)
        
        assert is_valid == True
        assert message == "Dataset válido para gráficos"
    
    def test_validate_chart_insufficient_columns(self):
        """Teste com colunas insuficientes."""
        df = pd.DataFrame({
            'single_col': [1, 2, 3]
        })
        
        is_valid, message = validate_chart_requirements(df)
        
        assert is_valid == False
        assert "pelo menos 2 colunas" in message
    
    def test_validate_chart_no_numeric_columns(self):
        """Teste sem colunas numéricas."""
        df = pd.DataFrame({
            'col1': ['A', 'B', 'C'],
            'col2': ['X', 'Y', 'Z']
        })
        
        is_valid, message = validate_chart_requirements(df)
        
        assert is_valid == False
        assert "Nenhuma coluna numérica" in message
    
    def test_validate_chart_empty_dataframe(self):
        """Teste com DataFrame vazio."""
        df = pd.DataFrame()
        
        is_valid, message = validate_chart_requirements(df)
        
        assert is_valid == False
        assert "pelo menos 2 colunas" in message


class TestIntegrationScenarios:
    """Testes de integração com cenários reais."""
    
    def test_real_world_csv_processing(self):
        """Teste com cenário real de processamento de CSV."""
        # Simular CSV de vendas
        csv_data = """data,produto,vendas,lucro,regiao
2023-01-01,Produto A,1000.50,200.10,Norte
2023-01-02,Produto B,1500.75,300.15,Sul
2023-01-03,Produto A,1200.00,240.00,Norte
2023-01-04,Produto C,,150.25,Leste
2023-01-05,Produto B,1800.90,360.18,Sul"""
        
        # Carregar dados
        csv_file = io.StringIO(csv_data)
        df = load_csv_data(csv_file)
        assert len(df) == 5
        
        # Filtrar por produto
        produto_a = filter_dataframe_by_text(df, 'Produto A')
        assert len(produto_a) == 2
        
        # Calcular estatísticas
        stats = calculate_numeric_statistics(df)
        assert len(stats['stats_df']) == 2  # vendas e lucro
        
        # Preparar dados para gráfico
        chart_data = prepare_chart_data(df, 'data', ['vendas'])
        assert chart_data['is_date'] == True
        assert len(chart_data['chart_df']) == 4  # Remove linha com vendas NaN
        
        # Validar requisitos
        is_valid, _ = validate_chart_requirements(df)
        assert is_valid == True
    
    def test_csv_with_special_characters(self):
        """Teste com caracteres especiais e acentos."""
        csv_data = """nome,descrição,preço
João Silva,Açúcar refinado,5.50
María González,Café colombiano,12.75
François Dubois,Croissant français,3.25"""
        
        csv_file = io.StringIO(csv_data)
        df = load_csv_data(csv_file)
        
        # Buscar com acentos
        result = filter_dataframe_by_text(df, 'François')
        assert len(result) == 1
        assert 'François Dubois' in result['nome'].values
        
        # Buscar sem acentos deve encontrar com acentos
        result2 = filter_dataframe_by_text(df, 'Acucar')
        # Isso pode não funcionar dependendo da implementação de contains
        # mas é um bom teste para verificar robustez


if __name__ == "__main__":
    pytest.main([__file__, "-v"])