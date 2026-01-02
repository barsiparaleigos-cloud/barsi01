"""
Database Migrations
Sistema de migração atômico para evolução do schema do banco de dados
"""

import sqlite3
import logging
from pathlib import Path
from typing import Callable, List
from datetime import datetime

logger = logging.getLogger(__name__)


class Migration:
    """Representa uma migração do banco de dados"""
    
    def __init__(self, version: int, name: str, up: Callable, down: Callable = None):
        self.version = version
        self.name = name
        self.up = up  # Função para aplicar migração
        self.down = down  # Função para reverter (opcional)


class MigrationManager:
    """
    Gerenciador de migrações com transações atômicas
    
    Garante que migrações sejam aplicadas de forma segura:
    - Transações atômicas (all-or-nothing)
    - Versionamento automático
    - Rollback em caso de erro
    - Log de auditoria
    """
    
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.conn = None
        self._ensure_migration_table()
    
    def _ensure_migration_table(self):
        """Cria tabela de controle de migrações se não existir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                execution_time_ms INTEGER
            )
        """)
        
        conn.commit()
        conn.close()
    
    def get_current_version(self) -> int:
        """Retorna a versão atual do schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT MAX(version) FROM schema_migrations")
        result = cursor.fetchone()[0]
        
        conn.close()
        
        return result if result is not None else 0
    
    def apply_migration(self, migration: Migration) -> bool:
        """
        Aplica uma migração de forma atômica
        
        Returns:
            True se sucesso, False se erro
        """
        current_version = self.get_current_version()
        
        if migration.version <= current_version:
            logger.info(f"⏭️  Migração {migration.version} já aplicada, pulando...")
            return True
        
        logger.info(f"🔄 Aplicando migração {migration.version}: {migration.name}")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            start_time = datetime.now()
            
            # Iniciar transação atômica
            cursor.execute("BEGIN TRANSACTION")
            
            # Executar migração
            migration.up(cursor)
            
            # Registrar migração aplicada
            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
            cursor.execute(
                "INSERT INTO schema_migrations (version, name, execution_time_ms) VALUES (?, ?, ?)",
                (migration.version, migration.name, execution_time)
            )
            
            # Commit atômico
            conn.commit()
            
            logger.info(f"✅ Migração {migration.version} aplicada com sucesso ({execution_time}ms)")
            return True
            
        except Exception as e:
            # Rollback automático em caso de erro
            conn.rollback()
            logger.error(f"❌ Erro ao aplicar migração {migration.version}: {e}")
            return False
            
        finally:
            conn.close()
    
    def apply_all(self, migrations: List[Migration]):
        """Aplica todas as migrações pendentes"""
        current_version = self.get_current_version()
        logger.info(f"📊 Versão atual do schema: {current_version}")
        
        pending = [m for m in migrations if m.version > current_version]
        
        if not pending:
            logger.info("✅ Nenhuma migração pendente")
            return
        
        logger.info(f"🔄 {len(pending)} migração(ões) pendente(s)")
        
        for migration in sorted(pending, key=lambda m: m.version):
            if not self.apply_migration(migration):
                logger.error("🚨 Migração falhou, abortando...")
                break


# ============================================================================
# MIGRAÇÕES DISPONÍVEIS
# ============================================================================

def migration_001_add_besst_columns(cursor):
    """
    Adiciona colunas para classificação BESST e elegibilidade da metodologia
    """
    cursor.execute("""
        ALTER TABLE empresas ADD COLUMN setor_besst TEXT DEFAULT NULL
    """)
    
    cursor.execute("""
        ALTER TABLE empresas ADD COLUMN elegivel_barsi BOOLEAN DEFAULT FALSE
    """)
    
    cursor.execute("""
        ALTER TABLE empresas ADD COLUMN dividend_yield_atual REAL DEFAULT NULL
    """)
    
    cursor.execute("""
        ALTER TABLE empresas ADD COLUMN consistencia_dividendos REAL DEFAULT NULL
    """)
    
    cursor.execute("""
        ALTER TABLE empresas ADD COLUMN monitorar BOOLEAN DEFAULT FALSE
    """)
    
    # Criar índices para performance
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_empresas_setor_besst 
        ON empresas(setor_besst)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_empresas_elegivel 
        ON empresas(elegivel_barsi)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_empresas_monitorar 
        ON empresas(monitorar)
    """)


def migration_002_add_metadata_columns(cursor):
    """
    Adiciona colunas de metadados para auditoria
    """
    cursor.execute("""
        ALTER TABLE empresas ADD COLUMN ultima_analise TIMESTAMP DEFAULT NULL
    """)
    
    cursor.execute("""
        ALTER TABLE empresas ADD COLUMN motivo_exclusao TEXT DEFAULT NULL
    """)


def migration_003_add_precos_table(cursor):
    """
    Cria tabelas para armazenar histórico de preços e mapeamento de tickers
    """
    # Tabela de cotações/preços
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS precos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            data DATE NOT NULL,
            abertura REAL,
            maxima REAL,
            minima REAL,
            fechamento REAL NOT NULL,
            volume INTEGER,
            market_cap INTEGER,
            variacao_percentual REAL,
            moeda TEXT DEFAULT 'BRL',
            fonte TEXT DEFAULT 'brapi',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(ticker, data, fonte)
        )
    """)
    
    # Índices para performance
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_precos_ticker ON precos(ticker)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_precos_data ON precos(data DESC)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_precos_ticker_data ON precos(ticker, data DESC)
    """)
    
    # Tabela para mapeamento CNPJ → Ticker
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ticker_mapping (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa_id INTEGER,
            cnpj TEXT,
            ticker TEXT NOT NULL UNIQUE,
            nome TEXT,
            tipo_acao TEXT,
            ativo BOOLEAN DEFAULT TRUE,
            verificado BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (empresa_id) REFERENCES empresas(id)
        )
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_ticker_mapping_cnpj ON ticker_mapping(cnpj)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_ticker_mapping_ticker ON ticker_mapping(ticker)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_ticker_mapping_empresa_id ON ticker_mapping(empresa_id)
    """)


# Registrar todas as migrações
MIGRATIONS = [
    Migration(
        version=1,
        name="add_besst_columns",
        up=migration_001_add_besst_columns
    ),
    Migration(
        version=2,
        name="add_metadata_columns",
        up=migration_002_add_metadata_columns
    ),
    Migration(
        version=3,
        name="add_precos_table",
        up=migration_003_add_precos_table
    ),
]


def run_migrations(db_path: str = "data/dividendos.db"):
    """Executa todas as migrações pendentes"""
    logger.info("=" * 60)
    logger.info("🔧 INICIANDO MIGRAÇÕES DO BANCO DE DADOS")
    logger.info("=" * 60)
    
    manager = MigrationManager(db_path)
    manager.apply_all(MIGRATIONS)
    
    logger.info("=" * 60)
    logger.info("✅ MIGRAÇÕES CONCLUÍDAS")
    logger.info("=" * 60)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    run_migrations()
