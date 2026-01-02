"""
Script para testar integração CVM localmente
Executa o download e processamento de dados
"""

import sys
from pathlib import Path

# Adicionar raiz ao path
root = Path(__file__).parent.parent
sys.path.insert(0, str(root))

from integrations.cvm_integration import CVMIntegration
import logging

# Aceitar argumento --auto-yes para testes automatizados
AUTO_YES = '--auto-yes' in sys.argv or '-y' in sys.argv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    print("=" * 70)
    print("TESTE DE INTEGRAÇÃO CVM - PORTAL DE DADOS ABERTOS")
    if AUTO_YES:
        print("🤖 MODO AUTOMÁTICO - Respostas automáticas ativadas")
    print("=" * 70)
    print()
    print("🔓 Dados públicos - SEM necessidade de login ou API key")
    print("📊 Download direto via HTTP")
    print("💰 Totalmente gratuito")
    print()
    print("=" * 70)
    print()
    
    try:
        cvm = CVMIntegration()
        
        # 1. Testar conexão
        print("1️⃣  Testando conexão com CVM...")
        status = cvm.test_connection()
        
        if status['status'] == 'success':
            print("   ✅ CONEXÃO OK")
            print(f"   📍 Base URL: {status['base_url']}")
            print(f"   🔐 Requer autenticação: {status['requires_auth']}")
            print(f"   💰 Custo: {status['cost']}")
            print(f"   🔄 Atualização: {status['update_frequency']}")
        else:
            print(f"   ❌ ERRO: {status['message']}")
            return
        
        print()
        
        # 2. Baixar cadastro (arquivo pequeno, rápido)
        print("2️⃣  Baixando cadastro de companhias abertas...")
        print("   (Arquivo CSV ~500KB, atualização diária)")
        
        df_cadastro = cvm.download_cadastro_empresas()
        
        print(f"   ✅ {len(df_cadastro)} empresas cadastradas")
        print(f"   📁 Colunas disponíveis: {len(df_cadastro.columns)}")
        
        print("\n   📋 Amostra do cadastro (5 primeiras empresas):")
        print(f"   {'-' * 66}")
        
        # Mostrar apenas colunas relevantes
        cols_to_show = ['CNPJ_CIA', 'DENOM_SOCIAL', 'CD_CVM', 'SIT', 'SETOR_ATIV']
        available_cols = [col for col in cols_to_show if col in df_cadastro.columns]
        
        for idx, row in df_cadastro.head().iterrows():
            print(f"   {row.get('DENOM_SOCIAL', 'N/A')[:40]:40} | CNPJ: {row.get('CNPJ_CIA', 'N/A')}")
        
        print()
        
        # 3. Perguntar se quer baixar DFP (arquivo grande)
        print("3️⃣  Baixar Demonstrações Financeiras Padronizadas (DFP)?")
        print("   ⚠️  ATENÇÃO: Arquivo ZIP grande (~50-200 MB)")
        print("   ⏱️  Download pode levar 2-5 minutos dependendo da conexão")
        print()
        
        if AUTO_YES:
            print("   🤖 Modo automático: continuando com download...")
            response = 's'
        else:
            response = input("   Deseja continuar? (s/N): ").strip().lower()
        
        if response == 's':
            print()
            print("   Baixando DFP 2024 (último ano disponível)...")
            print("   🔽 Aguarde, isso pode demorar alguns minutos...")
            
            demonstracoes = cvm.download_dfp(2024)
            
            print(f"   ✅ DFP baixado: {len(demonstracoes)} demonstrações")
            print(f"   📊 Disponíveis: {', '.join(demonstracoes.keys())}")
            print()
            
            # 4. Processar dividendos
            if 'DRE' in demonstracoes:
                print("4️⃣  Extraindo dividendos da DRE...")
                dividendos = cvm.extrair_dividendos(demonstracoes['DRE'])
                
                print(f"   ✅ {len(dividendos)} empresas com dividendos registrados")
                
                if len(dividendos) > 0:
                    print("\n   💰 Top 5 pagadoras de dividendos (2024):")
                    print(f"   {'-' * 66}")
                    
                    top5 = dividendos.nlargest(5, 'PROVENTOS_TOTAL')
                    
                    for idx, row in top5.iterrows():
                        empresa = row['DENOM_CIA'][:35]
                        valor = row['PROVENTOS_TOTAL']
                        print(f"   {empresa:35} | R$ {valor:,.0f} mil")
                
                print()
            
            # 5. Processar PL
            if 'BPP' in demonstracoes:
                print("5️⃣  Extraindo Patrimônio Líquido do BPP...")
                patrimonio = cvm.extrair_patrimonio_liquido(demonstracoes['BPP'])
                
                print(f"   ✅ {len(patrimonio)} empresas com PL registrado")
                
                if len(patrimonio) > 0:
                    print("\n   💎 Top 5 maiores patrimônios líquidos (2024):")
                    print(f"   {'-' * 66}")
                    
                    top5 = patrimonio.nlargest(5, 'PATRIMONIO_LIQUIDO')
                    
                    for idx, row in top5.iterrows():
                        empresa = row['DENOM_CIA'][:35]
                        valor = row['PATRIMONIO_LIQUIDO']
                        print(f"   {empresa:35} | R$ {valor:,.0f} mil")
                
                print()
        
        else:
            print("   ⏭️  Download de DFP pulado")
            print()
        
        # Resumo final
        print("=" * 70)
        print("✅ TESTE CONCLUÍDO COM SUCESSO")
        print("=" * 70)
        print()
        print("📁 Arquivos salvos em: data/cvm/")
        print()
        print("🚀 PRÓXIMOS PASSOS:")
        print("   1. Configure autoSync=true no painel de integrações")
        print("   2. Execute: python -m jobs.sync_cvm")
        print("   3. Dados serão atualizados automaticamente")
        print()
        print("💡 DICA: A integração CVM não precisa de API key!")
        print("   Os dados são públicos e atualizados semanalmente pela CVM.")
        print()
        print("=" * 70)
        
    except Exception as e:
        print()
        print("=" * 70)
        print("❌ ERRO NO TESTE")
        print("=" * 70)
        print(f"Erro: {e}")
        print()
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
