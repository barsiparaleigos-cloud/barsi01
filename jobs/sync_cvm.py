"""
Job: Sincronização de dados CVM
Executa periodicamente para atualizar dados das companhias abertas
Salva dados no banco SQLite para persistência permanente
"""

import sys
from pathlib import Path

# Adicionar diretório raiz ao path
root = Path(__file__).parent.parent
sys.path.insert(0, str(root))

import logging
from datetime import datetime
from integrations.cvm_integration import CVMIntegration
from database.models import get_db
import json
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def sync_cvm_data():
    """
    Sincroniza dados da CVM:
    1. Baixa cadastro atualizado de empresas
    2. Baixa DFP do ano fiscal mais recente
    3. Extrai dividendos e patrimônio líquido
    4. Salva dados processados localmente
    """
    logger.info("=" * 60)
    logger.info("INICIANDO SINCRONIZAÇÃO CVM")
    logger.info("=" * 60)
    
    try:
        cvm = CVMIntegration()
        db = get_db()  # Banco de dados SQLite
        
        # 1. Testar conexão
        logger.info("\n[1/5] Testando conexão com CVM...")
        status = cvm.test_connection()
        if status['status'] != 'success':
            raise Exception(f"Falha na conexão: {status['message']}")
        logger.info("✅ Conexão OK")
        
        # 2. Baixar cadastro de empresas
        logger.info("\n[2/5] Baixando cadastro de empresas...")
        df_cadastro = cvm.download_cadastro_empresas()
        logger.info(f"✅ {len(df_cadastro)} empresas cadastradas")
        
        # **SALVAR NO BANCO DE DADOS**
        logger.info("💾 Salvando empresas no banco de dados...")
        empresas_novas = 0
        empresas_atualizadas = 0
        
        for idx, row in df_cadastro.iterrows():
            cnpj = str(row.get('CNPJ_CIA', '')).strip()
            if not cnpj:
                continue
            
            empresa_data = {
                'cnpj': cnpj,
                'codigo_cvm': str(row.get('CD_CVM', '')),
                'razao_social': str(row.get('DENOM_SOCIAL', '')),
                'nome_fantasia': str(row.get('DENOM_COMERC', '')),
                'setor': str(row.get('SETOR_ATIV', '')),
                'situacao': str(row.get('SIT', '')),
                'data_registro': str(row.get('DT_REG', '')),
                'data_cancelamento': str(row.get('DT_CANCEL', ''))
            }
            
            # Verificar se é novo ou atualização
            existing = db.get_empresa_by_cnpj(cnpj)
            db.insert_empresa(empresa_data)
            
            if existing:
                empresas_atualizadas += 1
            else:
                empresas_novas += 1
        
        logger.info(f"✅ Persistência: {empresas_novas} novas, {empresas_atualizadas} atualizadas")
        
        # **CLASSIFICAÇÃO AUTOMÁTICA DE NOVAS EMPRESAS BESST**
        if empresas_novas > 0:
            logger.info(f"\n🎯 Classificando {empresas_novas} empresas novas no filtro BESST...")
            try:
                from database.besst_classifier import BESSTClassifier
                from datetime import datetime
                
                classifier = BESSTClassifier()
                cursor = db.connection.cursor()
                
                # Buscar empresas sem classificação (adicionadas nesta sync)
                cursor.execute("""
                    SELECT id, cnpj, razao_social, setor
                    FROM empresas
                    WHERE setor_besst IS NULL
                    ORDER BY id DESC
                    LIMIT ?
                """, (empresas_novas,))
                
                empresas_pendentes = [dict(row) for row in cursor.fetchall()]
                
                besst_encontradas = 0
                cursor.execute("BEGIN TRANSACTION")
                
                for empresa in empresas_pendentes:
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
                            SET monitorar = FALSE,
                                ultima_analise = ?
                            WHERE id = ?
                        """, (
                            datetime.now().isoformat(),
                            empresa['id']
                        ))
                
                db.connection.commit()
                logger.info(f"✅ Classificação BESST: {besst_encontradas}/{empresas_novas} novas empresas no radar")
                
            except Exception as e:
                logger.warning(f"⚠️  Erro na classificação BESST: {e}")
                db.connection.rollback()
        
        # Salvar cadastro processado (JSON backup)
        output_dir = root / 'data' / 'processed'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        cadastro_file = output_dir / 'cvm_cadastro.json'
        df_cadastro.to_json(cadastro_file, orient='records', force_ascii=False, indent=2)
        logger.info(f"Cadastro salvo em: {cadastro_file}")
        
        # 3. Baixar DFP do ano mais recente
        current_year = datetime.now().year
        # Tentar ano atual primeiro, depois anterior (DFP pode não estar disponível ainda)
        years_to_try = [current_year - 1, current_year - 2]  # 2024, 2023
        
        demonstracoes = None
        dfp_year = None
        
        for year in years_to_try:
            logger.info(f"\n[3/5] Tentando baixar DFP {year}...")
            try:
                demonstracoes = cvm.download_dfp(year)
                dfp_year = year
                logger.info(f"✅ DFP {year} baixado com sucesso")
                break
            except Exception as e:
                logger.warning(f"⚠️ DFP {year} não disponível: {e}")
                continue
        
        if not demonstracoes:
            raise Exception("Nenhum DFP disponível nos últimos 2 anos")
        
        # 4. Extrair dividendos
        logger.info(f"\n[4/5] Processando dados do DFP {dfp_year}...")
        
        dividendos = None
        patrimonio = None
        dividendos_salvos = 0
        patrimonio_salvos = 0
        
        if 'DRE' in demonstracoes:
            dividendos = cvm.extrair_dividendos(demonstracoes['DRE'])
            logger.info(f"✅ Dividendos: {len(dividendos)} empresas")
            
            # **SALVAR DIVIDENDOS NO BANCO**
            logger.info("💾 Salvando dividendos no banco de dados...")
            for idx, row in dividendos.iterrows():
                cnpj = str(row.get('CNPJ_CIA', '')).strip()
                if not cnpj:
                    continue
                
                # Buscar empresa_id
                empresa = db.get_empresa_by_cnpj(cnpj)
                
                div_data = {
                    'empresa_id': empresa['id'] if empresa else None,
                    'cnpj': cnpj,
                    'ano_fiscal': dfp_year,
                    'data_referencia': str(row.get('DT_REFER', '')),
                    'tipo': 'PROVENTOS',
                    'valor_total': float(row.get('PROVENTOS_TOTAL', 0)) if pd.notna(row.get('PROVENTOS_TOTAL')) else 0,
                }
                
                db.insert_dividendo(div_data)
                dividendos_salvos += 1
        
        # 5. Extrair patrimônio líquido
        if 'BPP' in demonstracoes:
            patrimonio = cvm.extrair_patrimonio_liquido(demonstracoes['BPP'])
            logger.info(f"✅ Patrimônio Líquido: {len(patrimonio)} empresas")
            
            # **SALVAR PATRIMÔNIO NO BANCO**
            logger.info("💾 Salvando patrimônio no banco de dados...")
            for idx, row in patrimonio.iterrows():
                cnpj = str(row.get('CNPJ_CIA', '')).strip()
                if not cnpj:
                    continue
                
                empresa = db.get_empresa_by_cnpj(cnpj)
                
                pl_data = {
                    'empresa_id': empresa['id'] if empresa else None,
                    'cnpj': cnpj,
                    'ano_fiscal': dfp_year,
                    'data_referencia': str(row.get('DT_REFER', '')),
                    'valor': float(row.get('PATRIMONIO_LIQUIDO', 0)) if pd.notna(row.get('PATRIMONIO_LIQUIDO')) else 0,
                }
                
                db.insert_patrimonio(pl_data)
                patrimonio_salvos += 1
        
        # Salvar JSON de backup dos dividendos
        div_file = None
        if dividendos is not None:
            div_file = output_dir / f'cvm_dividendos_{dfp_year}.json'
            dividendos.to_json(div_file, orient='records', force_ascii=False, indent=2)
            logger.info(f"Backup JSON dividendos salvo em: {div_file}")
        
        # Salvar JSON de backup do patrimônio
        pl_file = None
        if patrimonio is not None:
            pl_file = output_dir / f'cvm_patrimonio_{dfp_year}.json'
            patrimonio.to_json(pl_file, orient='records', force_ascii=False, indent=2)
            logger.info(f"Backup JSON patrimônio salvo em: {pl_file}")
        
        # Relatório final expandido
        report = {
            'empresas_novas': empresas_novas,
            'empresas_atualizadas': empresas_atualizadas,
            'empresas_com_dividendos': len(dividendos) if dividendos is not None else 0,
            'empresas_com_pl': len(patrimonio) if patrimonio is not None else 0,
            'dividendos_salvos': dividendos_salvos,
            'patrimonio_salvos': patrimonio_salvos,
            'demonstracoes_baixadas': list(demonstracoes.keys()),
            'database': str(db.db_path),
            'database_size_mb': round(db.db_path.stat().st_size / 1024 / 1024, 2) if db.db_path.exists() else 0,
            'files': {
                'cadastro': str(cadastro_file),
                'dividendos': str(div_file) if div_file else None,
                'patrimonio': str(pl_file) if pl_file else None
            }
        }
        
        # Salvar log no banco
        db.log_sync(
            tipo='CVM_COMPLETO',
            fonte='Portal Dados Abertos CVM',
            status='success',
            registros_processados=len(df_cadastro),
            registros_novos=empresas_novas,
            registros_atualizadas=empresas_atualizadas,
            mensagem=f'Sincronização DFP {dfp_year} concluída',
            detalhes=report
        )
        
        # Relatório final
        logger.info("\n✅ Sincronização CVM concluída!")
        logger.info(f"\n📊 RELATÓRIO DE PERSISTÊNCIA:")
        logger.info(f"  ➕ Empresas novas: {report['empresas_novas']}")
        logger.info(f"  🔄 Empresas atualizadas: {report['empresas_atualizadas']}")
        logger.info(f"  💰 Dividendos salvos: {dividendos_salvos}")
        logger.info(f"  📈 Patrimônios salvos: {patrimonio_salvos}")
        logger.info(f"  💾 Banco de dados: {report['database']} ({report['database_size_mb']} MB)")
        logger.info("=" * 60)
        
        return report
        
    except Exception as e:
        logger.error(f"\n❌ ERRO NA SINCRONIZAÇÃO: {e}", exc_info=True)
        
        # Salvar relatório de erro
        error_report = {
            'timestamp': datetime.now().isoformat(),
            'status': 'error',
            'error': str(e)
        }
        
        report_file = output_dir / 'cvm_sync_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(error_report, f, indent=2, ensure_ascii=False)
        
        raise


if __name__ == '__main__':
    try:
        sync_cvm_data()
        sys.exit(0)
    except Exception:
        sys.exit(1)
