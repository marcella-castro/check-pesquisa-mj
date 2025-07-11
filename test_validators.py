#!/usr/bin/env python3
"""
Script de teste para verificar se os validadores estão funcionando corretamente
"""

import sys
import os
import pandas as pd

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from validation.processo_validator import ProcessoValidator
from validation.conjunto_validator import ConjuntoValidator

def test_processo_validator():
    """Testa o validador de processo com dados fictícios"""
    print("🧪 Testando ProcessoValidator...")
    
    # Criar dados de teste
    data = {
        'form_origem': ['Processo_1', 'Processo_2', 'Processo_3', 'Processo_4'],
        'id': [1, 2, 3, 4],
        'P0Q0. Pesquisador responsável pelo preenchimento:': ['João Silva', 'Maria Souza', 'Pedro Santos', 'Ana Costa'],
        'P0Q1. Número de controle (dado pela equipe)': ['123R01', '456V02', 'INVALID', '789R01'],
        'P0Q1A. Número de controle para casos em que há mais de uma vítima:': [None, 'V01', None, 'V01'],  # 456V02 + V01 duplicado
        'P0Q2. Número do Processo:': ['1234567-89.2023.1.01.0001', '2345678-90.2023.2.02.0002', 'INVALID_FORMAT', '1234567-89.2023.1.01.0001'],  # último sem R01
        'P0Q14. Número de réus no processo:': [2, 3, 1, 2],
        'P0Q014. Número de réus que tiveram decisão com trânsito em julgado neste processo': [1, 5, 1, 2]  # 5 > 3 é erro
    }
    
    df = pd.DataFrame(data)
    validator = ProcessoValidator()
    
    try:
        erros = validator.validate(df)
        print(f"✅ Validação executada com sucesso!")
        print(f"📊 Total de erros encontrados: {len(erros)}")
        
        # Agrupar erros por tipo
        tipos_erro = {}
        for erro in erros:
            tipo = erro.get('Tipo de Erro', 'Desconhecido')
            tipos_erro[tipo] = tipos_erro.get(tipo, 0) + 1
        
        print("📋 Resumo por tipo de erro:")
        for tipo, count in tipos_erro.items():
            print(f"   • {tipo}: {count} erro(s)")
        
        return True
    except Exception as e:
        print(f"❌ Erro na validação: {e}")
        return False

def test_conjunto_validator():
    """Testa o validador conjunto"""
    print("\n🧪 Testando ConjuntoValidator...")
    
    # Dados de teste para todas as categorias
    all_data = {
        'processo': pd.DataFrame({
            'form_origem': ['Processo_1'],
            'id': [1],
            'P0Q0. Pesquisador responsável pelo preenchimento:': ['João Silva'],
            'P0Q1. Número de controle (dado pela equipe)': ['123R01'],
            'P0Q2. Número do Processo:': ['1234567-89.2023.1.01.0001'],
            'P0Q14. Número de réus no processo:': [2],
            'P0Q014. Número de réus que tiveram decisão com trânsito em julgado neste processo': [1]
        }),
        'vitima': pd.DataFrame({'id': [1], 'data': ['test']}),
        'reu': pd.DataFrame({'id': [1], 'data': ['test']}),
        'provas': pd.DataFrame({'id': [1], 'data': ['test']})
    }
    
    validator = ConjuntoValidator()
    
    try:
        erros = validator.validate_all(all_data)
        summary = validator.get_validation_summary(erros)
        
        print(f"✅ Validação conjunto executada com sucesso!")
        print(f"📊 Status: {summary['status']}")
        print(f"📊 Severidade: {summary['severidade']}")
        print(f"📊 Total de erros: {summary['total_erros']}")
        
        print("📋 Erros por categoria:")
        for categoria, count in summary['categorias'].items():
            if count > 0:
                print(f"   • {categoria}: {count} erro(s)")
        
        return True
    except Exception as e:
        print(f"❌ Erro na validação conjunto: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando testes dos validadores...\n")
    
    success1 = test_processo_validator()
    success2 = test_conjunto_validator()
    
    print(f"\n📋 Resumo dos testes:")
    print(f"   • ProcessoValidator: {'✅ PASSOU' if success1 else '❌ FALHOU'}")
    print(f"   • ConjuntoValidator: {'✅ PASSOU' if success2 else '❌ FALHOU'}")
    
    if success1 and success2:
        print("\n🎉 Todos os testes passaram! Os validadores estão funcionando corretamente.")
    else:
        print("\n⚠️  Alguns testes falharam. Verifique os erros acima.")
