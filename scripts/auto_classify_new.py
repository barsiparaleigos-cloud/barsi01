"""
Trigger automático para classificar novas empresas BESST
Roda após sincronização CVM
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.models import get_db
from database.besst_classifier import BESSTClassifier
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def classificar_empresas_nao_classificadas():
    """
    Classifica automaticamente empresas que ainda não foram analisadas
    """
    logger.info("="*60)
    logger.info("🔍 CLASSIFICAÇÃO AUTOMÁTICA DE NOVAS EMPRESAS")
    logger.info("="*60)
    
    db = get_db()
    cursor = db.connection.cursor()
    
    # Buscar empresas sem classificação (setor_besst IS NULL)
    cursor.execute("""
        SELECT id, cnpj, razao_social, setor, situacao
        FROM empresas
        WHERE setor_besst IS NULL
        ORDER BY id
    """)
    
    empresas_pendentes = [dict(row) for row in cursor.fetchall()]
    
    if not empresas_pendentes:
        logger.info("✅ Nenhuma empresa nova encontrada")
        logger.info("="*60)
        return {
            'total': 0,
            'classificadas': 0,
            'besst_encontradas': 0
        }
    
    logger.info(f"📊 {len(empresas_pendentes)} empresas pendentes de classificação")
    
    # Iniciar transação
    cursor.execute("BEGIN TRANSACTION")
    
    try:
        classifier = BESSTClassifier()
        classificadas = 0
        besst_encontradas = 0
        
        for empresa in empresas_pendentes:
            # Classificar
            classificacao = classifier.classificar(
                empresa.get('setor', ''),
                empresa.get('razao_social', '')
            )
            
            if classificacao:
                # É BESST!
                cursor.execute("""
                    UPDATE empresas
                    SET setor_besst = ?,
                        monitorar = TRUE,
                        ultima_analise = ?
                    WHERE id = ?
                """, (
                    classificacao['letra'],
                    datetime.now().isoformat(),
                    empresa['id']
                ))
                
                besst_encontradas += 1
                logger.info(f"  ✅ {classificacao['letra']} - {empresa['razao_social']}")
            else:
                # Não é BESST
                cursor.execute("""
                    UPDATE empresas
                    SET setor_besst = NULL,
                        monitorar = FALSE,
                        ultima_analise = ?
                    WHERE id = ?
                """, (
                    datetime.now().isoformat(),
                    empresa['id']
                ))
            
            classificadas += 1
            
            # Log de progresso a cada 100
            if classificadas % 100 == 0:
                logger.info(f"📈 Progresso: {classificadas}/{len(empresas_pendentes)}")
        
        # Commit da transação
        db.connection.commit()
        
        logger.info("="*60)
        logger.info("✅ CLASSIFICAÇÃO CONCLUÍDA")
        logger.info("="*60)
        logger.info(f"📊 Estatísticas:")
        logger.info(f"  • Total analisadas: {classificadas}")
        logger.info(f"  • ✅ BESST encontradas: {besst_encontradas}")
        logger.info(f"  • ❌ Não BESST: {classificadas - besst_encontradas}")
        logger.info("="*60)
        
        return {
            'total': len(empresas_pendentes),
            'classificadas': classificadas,
            'besst_encontradas': besst_encontradas
        }
    
    except Exception as e:
        # Rollback em caso de erro
        db.connection.rollback()
        logger.error(f"❌ Erro durante classificação: {e}")
        raise


if __name__ == '__main__':
    try:
        resultado = classificar_empresas_nao_classificadas()
        
        if resultado['besst_encontradas'] > 0:
            print(f"\n🎯 {resultado['besst_encontradas']} novas empresas BESST adicionadas ao radar!")
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
