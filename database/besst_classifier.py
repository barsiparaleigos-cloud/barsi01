"""
Classificador BESST
Sistema de classificação de empresas por setor (BESST) na metodologia
"""

import logging
from typing import Optional, Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)


class BESSTClassifier:
    """
    Classificador de setores BESST
    
    B - Bancos
    E - Energia Elétrica
    S - Saneamento
    S - Seguros
    T - Telecomunicações
    """
    
    # Palavras-chave por setor (lowercase)
    SETORES_KEYWORDS = {
        'B': {
            'keywords': [
                'banco', 'bancaria', 'bancário', 'financeiro', 'financeira',
                'credito', 'crédito', 'investimento', 'participacoes financeiras',
                'holdings financeiras'
            ],
            'nome': 'Bancos',
            'descricao': 'Instituições financeiras e bancárias'
        },
        'E': {
            'keywords': [
                'energia', 'eletrica', 'elétrica', 'eletrobras', 'hidrelétrica',
                'hidro', 'geracao de energia', 'transmissão de energia',
                'distribuição de energia', 'utilities', 'copel', 'cemig', 'cesp',
                'light', 'energisa', 'neoenergia', 'celesc', 'coelce'
            ],
            'nome': 'Energia Elétrica',
            'descricao': 'Geração, transmissão e distribuição de energia'
        },
        'S_SANEAMENTO': {
            'keywords': [
                'saneamento', 'sabesp', 'copasa', 'sanepar', 'cedae',
                'agua', 'água', 'esgoto', 'tratamento de agua',
                'tratamento de esgoto', 'abastecimento'
            ],
            'nome': 'Saneamento',
            'descricao': 'Água, esgoto e saneamento básico',
            'letra': 'S'
        },
        'S_SEGUROS': {
            'keywords': [
                'seguro', 'seguradora', 'resseguro', 'resseguradora',
                'previdencia', 'previdência', 'capitalização',
                'vida', 'porto seguro', 'sul america', 'bb seguridade'
            ],
            'nome': 'Seguros',
            'descricao': 'Seguros, resseguros e previdência',
            'letra': 'S'
        },
        'T': {
            'keywords': [
                'telecom', 'telecomunicacao', 'telecomunicação', 'telefonia',
                'telefone', 'telefônica', 'vivo', 'tim', 'claro', 'oi',
                'comunicacao', 'comunicação', 'internet', 'dados'
            ],
            'nome': 'Telecomunicações',
            'descricao': 'Telefonia, internet e comunicações'
        }
    }
    
    @classmethod
    def classificar(cls, setor: str, razao_social: str = None) -> Optional[Dict]:
        """
        Classifica empresa em setor BESST
        
        Args:
            setor: Setor da empresa (da CVM)
            razao_social: Razão social da empresa (para casos especiais)
        
        Returns:
            Dict com letra, nome e descrição ou None se não BESST
        """
        if not setor:
            return None
        
        setor_lower = setor.lower().strip()
        razao_lower = razao_social.lower().strip() if razao_social else ""
        
        # Buscar match por keywords
        for letra, config in cls.SETORES_KEYWORDS.items():
            keywords = config['keywords']
            
            for keyword in keywords:
                # Verificar no setor
                if keyword in setor_lower:
                    return {
                        'letra': config.get('letra', letra),
                        'nome': config['nome'],
                        'descricao': config['descricao']
                    }
                
                # Verificar na razão social (casos especiais)
                if razao_lower and keyword in razao_lower:
                    return {
                        'letra': config.get('letra', letra),
                        'nome': config['nome'],
                        'descricao': config['descricao']
                    }
        
        return None
    
    @classmethod
    def eh_besst(cls, setor: str, razao_social: str = None) -> bool:
        """Verifica se empresa está em setor BESST"""
        return cls.classificar(setor, razao_social) is not None
    
    @classmethod
    def get_letra(cls, setor: str, razao_social: str = None) -> Optional[str]:
        """Retorna apenas a letra do setor BESST"""
        resultado = cls.classificar(setor, razao_social)
        return resultado['letra'] if resultado else None
    
    @classmethod
    def listar_setores(cls) -> List[Dict]:
        """Lista todos os setores BESST disponíveis"""
        setores = []
        letras_vistas = set()
        
        for config in cls.SETORES_KEYWORDS.values():
            letra = config.get('letra', config['nome'][0])
            
            if letra not in letras_vistas:
                setores.append({
                    'letra': letra,
                    'nome': config['nome'],
                    'descricao': config['descricao']
                })
                letras_vistas.add(letra)
        
        return sorted(setores, key=lambda x: x['letra'])


def classificar_todas_empresas(db):
    """
    Classifica todas as empresas do banco em setores BESST
    
    Usa transação atômica para garantir consistência
    """
    logger.info("=" * 60)
    logger.info("🔍 INICIANDO CLASSIFICAÇÃO BESST")
    logger.info("=" * 60)
    
    # Buscar todas as empresas
    empresas = db.get_empresas(limit=10000)
    total = len(empresas)
    
    logger.info(f"📊 Total de empresas a classificar: {total}")
    
    # Contadores
    classificadas = 0
    besst_encontradas = 0
    nao_besst = 0
    
    # Classificar e atualizar em lote (transação atômica)
    try:
        db.conn.execute("BEGIN TRANSACTION")
        
        for i, empresa in enumerate(empresas, 1):
            resultado = BESSTClassifier.classificar(
                empresa.get('setor', ''),
                empresa.get('razao_social', '')
            )
            
            if resultado:
                # Empresa é BESST
                db.cursor.execute("""
                    UPDATE empresas 
                    SET 
                        setor_besst = ?,
                        monitorar = TRUE,
                        ultima_analise = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (resultado['letra'], empresa['id']))
                
                besst_encontradas += 1
                
                if i % 10 == 0:
                    logger.info(f"  ✅ {resultado['letra']} - {empresa['razao_social'][:50]}")
            else:
                # Empresa NÃO é BESST
                db.cursor.execute("""
                    UPDATE empresas 
                    SET 
                        setor_besst = NULL,
                        monitorar = FALSE,
                        ultima_analise = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (empresa['id'],))
                
                nao_besst += 1
            
            classificadas += 1
            
            # Log de progresso
            if i % 100 == 0:
                logger.info(f"📈 Progresso: {i}/{total} ({i*100//total}%)")
        
        # Commit atômico
        db.conn.commit()
        
        logger.info("=" * 60)
        logger.info("✅ CLASSIFICAÇÃO CONCLUÍDA")
        logger.info("=" * 60)
        logger.info(f"📊 Estatísticas:")
        logger.info(f"  • Total analisadas: {classificadas}")
        logger.info(f"  • ✅ BESST encontradas: {besst_encontradas} ({besst_encontradas*100//total}%)")
        logger.info(f"  • ❌ Não BESST: {nao_besst} ({nao_besst*100//total}%)")
        
        # Detalhar por setor
        logger.info(f"\n📋 Distribuição por setor BESST:")
        cursor = db.connection.cursor()
        for letra in ['B', 'E', 'S', 'T']:
            cursor.execute(
                "SELECT COUNT(*) FROM empresas WHERE setor_besst = ? AND situacao = 'ATIVO'",
                (letra,)
            )
            result = cursor.fetchone()
            count = result[0] if result else 0
            setor_info = next((s for s in BESSTClassifier.listar_setores() if s['letra'] == letra), None)
            if setor_info and count > 0:
                logger.info(f"  • {letra} ({setor_info['nome']}): {count} empresas")
        
        logger.info("=" * 60)
        
        return {
            'total': classificadas,
            'besst': besst_encontradas,
            'nao_besst': nao_besst
        }
        
    except Exception as e:
        # Rollback em caso de erro
        db.conn.rollback()
        logger.error(f"❌ Erro durante classificação: {e}")
        raise


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Teste de classificação
    print("\n🧪 Teste de Classificação BESST")
    print("=" * 60)
    
    testes = [
        ("Bancos", "Banco do Brasil S.A."),
        ("Energia Elétrica", "Companhia Energética de Minas Gerais"),
        ("Saneamento", "Companhia de Saneamento Básico do Estado de São Paulo"),
        ("Seguros", "Porto Seguro S.A."),
        ("Telecomunicações", "Telefônica Brasil S.A."),
        ("Varejo", "Magazine Luiza S.A."),  # Não BESST
    ]
    
    for setor, empresa in testes:
        resultado = BESSTClassifier.classificar(setor, empresa)
        if resultado:
            print(f"✅ {empresa[:40]:40} → {resultado['letra']} ({resultado['nome']})")
        else:
            print(f"❌ {empresa[:40]:40} → NÃO BESST")
