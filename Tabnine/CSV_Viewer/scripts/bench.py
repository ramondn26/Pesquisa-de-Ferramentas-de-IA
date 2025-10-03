
"""
Script de Benchmark para Testes do CSV Viewer

Este script executa os testes usando pytest, mede tempos de execução,
conta falhas e gera relatórios em CSV e JSON usando apenas bibliotecas
da stdlib do Python.

Uso:
    python scripts/bench.py
    python scripts/bench.py --verbose
    python scripts/bench.py --output-dir custom_reports
"""

import subprocess
import time
import json
import csv
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path
import re


class TestBenchmark:
    """Classe para executar benchmark dos testes e gerar relatórios."""
    
    def __init__(self, output_dir="reports", verbose=False):
        self.output_dir = Path(output_dir)
        self.verbose = verbose
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results = {
            "timestamp": self.timestamp,
            "start_time": None,
            "end_time": None,
            "total_duration": 0,
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
            "test_details": [],
            "summary": {},
            "environment": {}
        }
        
        # Criar diretório de relatórios se não existir
        self.output_dir.mkdir(exist_ok=True)
        
    def log(self, message):
        """Log de mensagens se verbose estiver ativo."""
        if self.verbose:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    
    def get_environment_info(self):
        """Coleta informações do ambiente de execução."""
        try:
            # Informações do Python
            python_version = sys.version.split()[0]
            
            # Informações do sistema
            import platform
            system_info = {
                "python_version": python_version,
                "platform": platform.platform(),
                "system": platform.system(),
                "machine": platform.machine(),
                "processor": platform.processor(),
            }
            
            # Tentar obter versão do pytest
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pytest", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    pytest_version = result.stdout.strip().split('\n')[0]
                    system_info["pytest_version"] = pytest_version
                else:
                    system_info["pytest_version"] = "não disponível"
            except Exception:
                system_info["pytest_version"] = "erro ao obter versão"
            
            self.results["environment"] = system_info
            self.log(f"Ambiente: Python {python_version}, {platform.system()}")
            
        except Exception as e:
            self.log(f"Erro ao coletar informações do ambiente: {e}")
            self.results["environment"] = {"error": str(e)}
    
    def parse_pytest_output(self, output):
        """Parse da saída do pytest para extrair informações dos testes."""
        lines = output.split('\n')
        test_details = []
        
        # Padrões regex para diferentes formatos de saída do pytest
        test_patterns = [
            # Formato: tests/test_file.py::TestClass::test_method PASSED [xx%]
            re.compile(r'^(.+?)::(.*?)::(.*?)\s+(PASSED|FAILED|SKIPPED|ERROR)\s*(?:\[.*?\])?\s*(?:\((.*?)\))?'),
            # Formato: tests/test_file.py::test_function PASSED [xx%]
            re.compile(r'^(.+?)::(.*?)\s+(PASSED|FAILED|SKIPPED|ERROR)\s*(?:\[.*?\])?\s*(?:\((.*?)\))?'),
            # Formato mais simples
            re.compile(r'^(.*?)\s+(PASSED|FAILED|SKIPPED|ERROR)\s*(?:\((.*?)\))?')
        ]
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Tentar cada padrão
            for pattern in test_patterns:
                match = pattern.match(line)
                if match:
                    groups = match.groups()
                    
                    if len(groups) >= 4 and '::' in groups[0]:  # Formato completo
                        file_path = groups[0]
                        class_name = groups[1] if groups[1] else ""
                        test_name = groups[2]
                        status = groups[3]
                        duration = groups[4] if len(groups) > 4 and groups[4] else "0s"
                    elif len(groups) >= 3 and '::' in groups[0]:  # Formato sem classe
                        file_path = groups[0]
                        class_name = ""
                        test_name = groups[1]
                        status = groups[2]
                        duration = groups[3] if len(groups) > 3 and groups[3] else "0s"
                    else:
                        continue
                    
                    # Extrair duração em segundos
                    duration_seconds = self.parse_duration(duration)
                    
                    test_detail = {
                        "file": file_path,
                        "class": class_name,
                        "test": test_name,
                        "status": status,
                        "duration": duration_seconds,
                        "duration_str": duration
                    }
                    
                    test_details.append(test_detail)
                    break
        
        return test_details
    
    def parse_duration(self, duration_str):
        """Converte string de duração para segundos."""
        if not duration_str or duration_str == "0s":
            return 0.0
        
        try:
            # Remover parênteses se existirem
            duration_str = duration_str.strip('()')
            
            # Padrões para diferentes formatos de tempo
            if 's' in duration_str and 'ms' not in duration_str:
                return float(duration_str.replace('s', ''))
            elif 'ms' in duration_str:
                return float(duration_str.replace('ms', '')) / 1000
            elif 'μs' in duration_str or 'us' in duration_str:
                return float(duration_str.replace('μs', '').replace('us', '')) / 1000000
            else:
                # Tentar converter diretamente
                return float(duration_str)
        except (ValueError, AttributeError):
            return 0.0
    
    def parse_summary(self, output):
        """Extrai resumo dos testes da saída do pytest."""
        lines = output.split('\n')
        summary = {}
        
        # Procurar linha de resumo (ex: "5 passed, 2 failed in 1.23s")
        for line in lines:
            line_lower = line.strip().lower()
            
            # Padrão para capturar números e status
            if any(word in line_lower for word in ['passed', 'failed', 'skipped', 'error']):
                # Extrair números seguidos de status
                passed_match = re.search(r'(\d+)\s+passed', line_lower)
                if passed_match:
                    summary['passed'] = int(passed_match.group(1))
                
                failed_match = re.search(r'(\d+)\s+failed', line_lower)
                if failed_match:
                    summary['failed'] = int(failed_match.group(1))
                
                skipped_match = re.search(r'(\d+)\s+skipped', line_lower)
                if skipped_match:
                    summary['skipped'] = int(skipped_match.group(1))
                
                error_match = re.search(r'(\d+)\s+error', line_lower)
                if error_match:
                    summary['errors'] = int(error_match.group(1))
            
            # Extrair duração total
            duration_match = re.search(r'in\s+([\d.]+)s', line_lower)
            if duration_match:
                summary['duration'] = float(duration_match.group(1))
        
        return summary
    
    def run_tests(self):
        """Executa os testes e coleta métricas."""
        self.log("Iniciando benchmark dos testes...")
        
        # Coletar informações do ambiente
        self.get_environment_info()
        
        # Comando pytest com saída detalhada
        cmd = [
            sys.executable, "-m", "pytest",
            "-v",  # verbose
            "--tb=short",  # traceback curto
            "--durations=0",  # mostrar duração de todos os testes
            "tests/"  # diretório de testes
        ]
        
        self.log(f"Executando comando: {' '.join(cmd)}")
        
        # Marcar tempo de início
        start_time = time.time()
        self.results["start_time"] = datetime.fromtimestamp(start_time).isoformat()
        
        try:
            # Executar pytest
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
                timeout=300  # timeout de 5 minutos
            )
            
            # Marcar tempo de fim
            end_time = time.time()
            self.results["end_time"] = datetime.fromtimestamp(end_time).isoformat()
            self.results["total_duration"] = end_time - start_time
            
            # Processar saída
            stdout = result.stdout
            stderr = result.stderr
            
            self.log(f"Pytest finalizado com código: {result.returncode}")
            self.log(f"Duração total: {self.results['total_duration']:.2f}s")
            
            if self.verbose:
                self.log("Saída do pytest:")
                print(stdout)
                if stderr:
                    self.log("Erros:")
                    print(stderr)
            
            # Parse dos resultados
            test_details = self.parse_pytest_output(stdout)
            summary = self.parse_summary(stdout)
            
            # Atualizar resultados
            self.results["test_details"] = test_details
            self.results["summary"] = summary
            self.results["return_code"] = result.returncode
            self.results["stdout"] = stdout
            self.results["stderr"] = stderr
            
            # Calcular estatísticas
            self.calculate_statistics()
            
            return True
            
        except subprocess.TimeoutExpired:
            self.log("ERRO: Timeout na execução dos testes!")
            self.results["error"] = "Timeout na execução"
            return False
            
        except FileNotFoundError:
            self.log("ERRO: pytest não encontrado!")
            self.results["error"] = "pytest não encontrado"
            return False
            
        except Exception as e:
            self.log(f"ERRO: {e}")
            self.results["error"] = str(e)
            return False
    
    def calculate_statistics(self):
        """Calcula estatísticas dos testes."""
        test_details = self.results["test_details"]
        
        # Contar por status
        status_counts = {"PASSED": 0, "FAILED": 0, "SKIPPED": 0, "ERROR": 0}
        total_test_duration = 0
        
        for test in test_details:
            status = test["status"]
            if status in status_counts:
                status_counts[status] += 1
            total_test_duration += test["duration"]
        
        # Atualizar resultados
        self.results["total_tests"] = len(test_details)
        self.results["passed"] = status_counts["PASSED"]
        self.results["failed"] = status_counts["FAILED"]
        self.results["skipped"] = status_counts["SKIPPED"]
        self.results["errors"] = status_counts["ERROR"]
        self.results["total_test_duration"] = total_test_duration
        
        # Calcular médias
        if len(test_details) > 0:
            avg_duration = total_test_duration / len(test_details)
            self.results["average_test_duration"] = avg_duration
        else:
            self.results["average_test_duration"] = 0.0
    
    def generate_csv_report(self):
        """Gera relatório CSV com detalhes dos testes."""
        csv_file = self.output_dir / f"benchmark_{self.timestamp}.csv"
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['file', 'class', 'test', 'status', 'duration', 'duration_str']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for test in self.results["test_details"]:
                writer.writerow(test)
        
        self.log(f"Relatório CSV gerado: {csv_file}")
    
    def generate_json_report(self):
        """Gera relatório JSON com todos os dados."""
        json_file = self.output_dir / f"benchmark_{self.timestamp}.json"
        
        with open(json_file, 'w', encoding='utf-8') as jsonfile:
            json.dump(self.results, jsonfile, indent=2, ensure_ascii=False)
        
        self.log(f"Relatório JSON gerado: {json_file}")
    
    def generate_summary_report(self):
        """Gera relatório resumido em texto."""
        summary_file = self.output_dir / f"summary_{self.timestamp}.txt"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("RELATÓRIO DE BENCHMARK DOS TESTES\n")
            f.write("=" * 60 + "\n")
            f.write(f"Timestamp: {self.results['timestamp']}\n")
            f.write(f"Data/Hora Início: {self.results['start_time']}\n")
            f.write(f"Data/Hora Fim: {self.results['end_time']}\n")
            f.write(f"Duração Total: {self.results['total_duration']:.2f} segundos\n")
            f.write(f"Total de Testes: {self.results['total_tests']}\n")
            f.write(f"Testes Passados: {self.results['passed']}\n")
            f.write(f"Testes Falhados: {self.results['failed']}\n")
            f.write(f"Testes Pulados: {self.results['skipped']}\n")
            f.write(f"Erros: {self.results['errors']}\n")
            f.write(f"Duração Total dos Testes: {self.results['total_test_duration']:.2f} segundos\n")
            f.write(f"Média de Duração por Teste: {self.results['average_test_duration']:.4f} segundos\n")
            f.write("\n" + "=" * 60 + "\n")
            f.write("INFORMAÇÕES DO AMBIENTE\n")
            f.write("=" * 60 + "\n")
            for key, value in self.results['environment'].items():
                f.write(f"{key}: {value}\n")
        
        self.log(f"Resumo gerado: {summary_file}")
    
    def run(self):
        """Executa todo o benchmark."""
        success = self.run_tests()
        
        if success:
            self.generate_csv_report()
            self.generate_json_report()
            self.generate_summary_report()
            self.log("Benchmark concluído com sucesso!")
            return True
        else:
            self.log("Benchmark falhou!")
            return False


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description="Benchmark dos testes do CSV Viewer")
    parser.add_argument("--verbose", action="store_true", help="Modo verboso")
    parser.add_argument("--output-dir", default="reports", help="Diretório de saída para relatórios")
    
    args = parser.parse_args()
    
    benchmark = TestBenchmark(output_dir=args.output_dir, verbose=args.verbose)
    success = benchmark.run()
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
