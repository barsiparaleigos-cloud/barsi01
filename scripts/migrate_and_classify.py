#!/usr/bin/env python3
"""
Script de Migração e Classificação BESST

Executa:
1. Migrações do banco de dados (adiciona colunas BESST)
2. Classificação de todas as empresas em setores BESST
3. Marcação de empresas para monitoramento

Uso:
    python scripts/migrate_and_classify.py
"""

import sys
import logging
from pathlib import Path

# Adicionar pasta raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.models import get_db
from database.migrations import run_migrations
from database.besst_classifier import classificar_todas_empresas, BESSTClassifier

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Executa migração e classificação"""
    
    print("\n" + "=" * 80)
    print("🚀 MIGRAÇÃO E CLASSIFICAÇÃO BESST - Barsi Para Leigos")
    print("=" * 80)
    
    try:
        # 1. Executar migrações
        logger.info("\n📋 ETAPA 1/3: Migrações do Banco de Dados\n")
        run_migrations()
        
        # 2. Conectar ao banco
        logger.info("\n📋 ETAPA 2/3: Conectando ao Banco de Dados\n")
        db = get_db()
        
        # 3. Classificar empresas
        logger.info("\n📋 ETAPA 3/3: Classificação BESST\n")
        resultado = classificar_todas_empresas(db)
        
        # 4. Resumo final
        print("\n" + "=" * 80)
        print("✅ PROCESSO CONCLUÍDO COM SUCESSO")
        print("=" * 80)
        print(f"\n📊 RESUMO FINAL:")
        print(f"  • Total de empresas analisadas: {resultado['total']}")
        print(f"  • ✅ Empresas BESST (monitoradas): {resultado['besst']}")
        print(f"  • ❌ Empresas fora do radar: {resultado['nao_besst']}")
        print(f"  • 📈 Taxa de elegibilidade: {resultado['besst']*100//resultado['total']}%")
        
        print(f"\n🎯 PRÓXIMOS PASSOS:")
        print(f"  1. Acesse http://localhost:5173")
        print(f"  2. Clique em 'Empresas' no menu lateral")
        print(f"  3. Ative o filtro 'Apenas empresas BESST'")
        print(f"  4. Visualize as {resultado['besst']} empresas no seu radar!")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        logger.error(f"\n❌ Erro durante execução: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
