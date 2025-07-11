#!/usr/bin/env python3
"""
Script de teste detalhado para verificar todas as validações implementadas
"""

import sys
import os
import pandas as pd

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from validation.processo_validator import ProcessoValidator

def test_detailed_processo_validator():
    """Testa detalhadamente todas as validações do processo"""
    print("🧪 Teste detalhado do ProcessoValidator...")
    
    # Criar dados com vários tipos de erro
    data = {
        'form_origem': ['Processo_1', 'Processo_2', 'Processo_3', 'Processo_4', 'Processo_5', 'Processo_6'],
        'id': [1, 2, 3, 4, 5, 6],
        'P0Q0. Pesquisador responsável pelo preenchimento:': ['João Silva', 'Maria Souza', '', 'Ana Costa', 'Pedro Lima', 'Carlos Mendes'],
        'P0Q1. Número de controle (dado pela equipe)': ['123R01', '456V02', 'INVALID', '789R01', '111R03', '222R01'],
        'P0Q1A. Número de controle para casos em que há mais de uma vítima:': [None, 'V01', None, 'V01', None, None],  
        'P0Q2. Número do Processo:': [
            '1234567-89.2023.1.01.0001',  # ok
            '2345678-90.2023.2.02.0002',  # ok 
            'INVALID_FORMAT',             # formato inválido
            '3456789-01.2023.3.03.0003',  # processo sem R01
            '',                           # campo vazio
            '4567890-12.2023.4.04.0004'   # ok
        ],
        'P0Q14. Número de réus no processo:': [2, 3, 1, 2, None, 4],
        'P0Q014. Número de réus que tiveram decisão com trânsito em julgado neste processo': [1, 5, 1, 2, 1, 3]  # 5 > 3 é erro
    }
    
    df = pd.DataFrame(data)
    print("📋 Dados de teste criados:")
    print(df[['P0Q1. Número de controle (dado pela equipe)', 'P0Q2. Número do Processo:']].to_string())
    
    validator = ProcessoValidator()
    
    # Testar cada validação individualmente
    print("\n🔍 Teste 1: Validação do número de controle")
    erros_controle = validator._validate_numero_controle(df)
    print(f"   Erros encontrados: {len(erros_controle)}")
    for erro in erros_controle:
        print(f"   • {erro['Tipo de Erro']}: {erro['Valor Encontrado']}")
    
    print("\n🔍 Teste 2: Validação do número do processo")
    erros_processo = validator._validate_numero_processo(df)
    print(f"   Erros encontrados: {len(erros_processo)}")
    for erro in erros_processo:
        print(f"   • {erro['Tipo de Erro']}: {erro['Valor Encontrado']}")
    
    print("\n🔍 Teste 3: Validação processo tem R01")
    erros_r01 = validator._validate_processo_tem_R01(df)
    print(f"   Erros encontrados: {len(erros_r01)}")
    for erro in erros_r01:
        print(f"   • {erro['Tipo de Erro']}: {erro['Valor Encontrado']}")
    
    print("\n🔍 Teste 4: Validação duplicidade controles")
    erros_dup = validator._validate_duplicidade_controles(df)
    print(f"   Erros encontrados: {len(erros_dup)}")
    for erro in erros_dup:
        print(f"   • {erro['Tipo de Erro']}: {erro['Valor Encontrado']}")
    
    print("\n🔍 Teste 5: Validação número de réus")
    erros_reus = validator._validate_numero_reus(df)
    print(f"   Erros encontrados: {len(erros_reus)}")
    for erro in erros_reus:
        print(f"   • {erro['Tipo de Erro']}: {erro['Valor Encontrado']}")
    
    print("\n🔍 Teste 6: Validação campos obrigatórios")
    erros_obrig = validator._validate_campos_obrigatorios(df)
    print(f"   Erros encontrados: {len(erros_obrig)}")
    for erro in erros_obrig:
        print(f"   • {erro['Tipo de Erro']}: {erro['Valor Encontrado']}")
    
    print("\n🔍 Validação completa")
    erros_total = validator.validate(df)
    print(f"   Total de erros: {len(erros_total)}")
    
    # Agrupar por tipo
    tipos = {}
    for erro in erros_total:
        tipo = erro['Tipo de Erro']
        tipos[tipo] = tipos.get(tipo, 0) + 1
    
    print("   Resumo por tipo:")
    for tipo, count in tipos.items():
        print(f"      • {tipo}: {count}")

if __name__ == "__main__":
    test_detailed_processo_validator()
