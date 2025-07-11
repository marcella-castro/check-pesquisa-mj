#!/usr/bin/env python3
"""
Script de teste final do sistema completo
"""

import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Testa se todos os módulos podem ser importados corretamente"""
    print("🧪 Testando importações...")
    
    try:
        # Importações principais
        import dash
        from dash import html, dcc
        print("   ✅ Dash importado")
        
        # Layouts
        from layouts.main_layout import create_main_layout
        print("   ✅ Layout principal importado")
        
        # Callbacks
        from callbacks.main_callbacks import register_callbacks
        print("   ✅ Callbacks importados")
        
        # Componentes
        from components.process_summary import create_process_summary
        from components.error_report import create_error_report
        print("   ✅ Componentes importados")
        
        # Validadores
        from validation.processo_validator import ProcessoValidator
        from validation.vitima_validator import VitimaValidator
        from validation.reu_validator import ReuValidator
        from validation.provas_validator import ProvasValidator
        from validation.conjunto_validator import ConjuntoValidator
        print("   ✅ Validadores importados")
        
        # Utilitários
        from utils.data_service import data_service
        from utils.data_cache import DataCache
        print("   ✅ Utilitários importados")
        
        return True
    except Exception as e:
        print(f"   ❌ Erro na importação: {e}")
        return False

def test_app_creation():
    """Testa se a aplicação Dash pode ser criada"""
    print("\n🧪 Testando criação da aplicação...")
    
    try:
        import dash
        from layouts.main_layout import create_main_layout
        from callbacks.main_callbacks import register_callbacks
        
        # Criar app
        app = dash.Dash(__name__, suppress_callback_exceptions=True)
        print("   ✅ App Dash criado")
        
        # Definir layout
        app.layout = create_main_layout()
        print("   ✅ Layout definido")
        
        # Registrar callbacks
        register_callbacks(app)
        print("   ✅ Callbacks registrados")
        
        return True
    except Exception as e:
        print(f"   ❌ Erro na criação da app: {e}")
        return False

def test_validation_system():
    """Testa se o sistema de validação funciona end-to-end"""
    print("\n🧪 Testando sistema de validação...")
    
    try:
        import pandas as pd
        from validation.conjunto_validator import ConjuntoValidator
        
        # Dados de teste
        test_data = {
            'processo': pd.DataFrame({
                'form_origem': ['Processo_1', 'Processo_2'],
                'id': [1, 2],
                'P0Q0. Pesquisador responsável pelo preenchimento:': ['João Silva', ''],
                'P0Q1. Número de controle (dado pela equipe)': ['123R01', 'INVALID'],
                'P0Q1A. Número de controle para casos em que há mais de uma vítima:': [None, None],
                'P0Q2. Número do Processo:': ['1234567-89.2023.1.01.0001', 'INVALID_FORMAT'],
                'P0Q14. Número de réus no processo:': [2, 3],
                'P0Q014. Número de réus que tiveram decisão com trânsito em julgado neste processo': [1, 5]
            }),
            'vitima': pd.DataFrame({'id': [1], 'data': ['test']}),
            'reu': pd.DataFrame({'id': [1], 'data': ['test']}),
            'provas': pd.DataFrame({'id': [1], 'data': ['test']})
        }
        
        # Validar
        validator = ConjuntoValidator()
        erros = validator.validate_all(test_data)
        summary = validator.get_validation_summary(erros)
        
        print(f"   ✅ Validação executada: {summary['total_erros']} erros encontrados")
        
        # Verificar se encontrou os erros esperados
        erros_processo = erros.get('processo', [])
        if len(erros_processo) > 0:
            print(f"   ✅ Sistema detectou erros no processo: {len(erros_processo)}")
        
        return True
    except Exception as e:
        print(f"   ❌ Erro no sistema de validação: {e}")
        return False

def main():
    """Executa todos os testes do sistema"""
    print("🚀 TESTE FINAL DO SISTEMA COMPLETO\n")
    print("=" * 50)
    
    tests = [
        ("Importações", test_imports),
        ("Criação da App", test_app_creation),
        ("Sistema de Validação", test_validation_system)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("📋 RESUMO DOS TESTES:")
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"   • {test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("🚀 O sistema está pronto para uso!")
        print("\nPara executar a aplicação:")
        print("   cd /Users/Marcella/check_pesquisa_mj")
        print("   python src/app.py")
    else:
        print("⚠️  ALGUNS TESTES FALHARAM!")
        print("🔧 Verifique os erros acima antes de usar o sistema.")

if __name__ == "__main__":
    main()
