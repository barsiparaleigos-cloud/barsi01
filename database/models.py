"""
Database Models - Persistência de dados do projeto Barsi
SQLite para dados locais seguros e permanentes
"""

import sqlite3
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class Database:
    """Gerenciador de banco de dados SQLite"""
    
    def __init__(self, db_path: str = "data/barsi.db"):
        """
        Inicializa conexão com banco de dados
        
        Args:
            db_path: Caminho para arquivo SQLite
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = None
        self._connect()
        self._create_tables()
    
    @property
    def conn(self):
        """Alias para connection (compatibilidade)"""
        return self.connection
    
    @property
    def cursor(self):
        """Retorna cursor do banco"""
        return self.connection.cursor()
    
    def _connect(self):
        """Conecta ao banco de dados"""
        self.connection = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.connection.row_factory = sqlite3.Row  # Retornar dicts
        logger.info(f"✅ Conectado ao banco: {self.db_path}")
    
    def _create_tables(self):
        """Cria todas as tabelas necessárias"""
        cursor = self.connection.cursor()
        
        # Tabela: Empresas (Companhias Abertas)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS empresas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cnpj TEXT UNIQUE NOT NULL,
                codigo_cvm TEXT,
                razao_social TEXT NOT NULL,
                nome_fantasia TEXT,
                setor TEXT,
                situacao TEXT,
                data_registro TEXT,
                data_cancelamento TEXT,
                website TEXT,
                email_ri TEXT,
                telefone_ri TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela: Ações (Tickers)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS acoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT UNIQUE NOT NULL,
                empresa_id INTEGER,
                cnpj TEXT,
                tipo TEXT,
                mercado TEXT,
                segmento TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (empresa_id) REFERENCES empresas(id)
            )
        """)
        
        # Tabela: Dividendos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dividendos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                empresa_id INTEGER,
                cnpj TEXT,
                ano_fiscal INTEGER,
                data_referencia TEXT,
                tipo TEXT,
                valor_total REAL,
                moeda TEXT DEFAULT 'BRL',
                escala TEXT DEFAULT 'MIL',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (empresa_id) REFERENCES empresas(id)
            )
        """)
        
        # Tabela: Patrimônio Líquido
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patrimonio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                empresa_id INTEGER,
                cnpj TEXT,
                ano_fiscal INTEGER,
                data_referencia TEXT,
                valor REAL,
                moeda TEXT DEFAULT 'BRL',
                escala TEXT DEFAULT 'MIL',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (empresa_id) REFERENCES empresas(id)
            )
        """)
        
        # Tabela: Relações com Investidores (RI)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS relacoes_investidores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                empresa_id INTEGER UNIQUE,
                cnpj TEXT UNIQUE,
                website TEXT,
                email TEXT,
                telefone TEXT,
                endereco TEXT,
                cidade TEXT,
                estado TEXT,
                cep TEXT,
                diretor_ri TEXT,
                ultima_atualizacao TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (empresa_id) REFERENCES empresas(id)
            )
        """)
        
        # Tabela: Sincronizações (Log)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sync_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL,
                fonte TEXT NOT NULL,
                status TEXT NOT NULL,
                registros_processados INTEGER,
                registros_novos INTEGER,
                registros_atualizados INTEGER,
                mensagem TEXT,
                detalhes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Índices para performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_empresas_cnpj ON empresas(cnpj)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_empresas_situacao ON empresas(situacao)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_acoes_ticker ON acoes(ticker)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_dividendos_cnpj ON dividendos(cnpj)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_patrimonio_cnpj ON patrimonio(cnpj)")
        
        self.connection.commit()
        logger.info("✅ Tabelas criadas/verificadas")
    
    def insert_empresa(self, data: Dict[str, Any]) -> int:
        """
        Insere ou atualiza empresa
        
        Args:
            data: Dicionário com dados da empresa
            
        Returns:
            ID da empresa inserida/atualizada
        """
        cursor = self.connection.cursor()
        
        # Verificar se já existe
        cursor.execute("SELECT id FROM empresas WHERE cnpj = ?", (data.get('cnpj'),))
        existing = cursor.fetchone()
        
        if existing:
            # Atualizar
            cursor.execute("""
                UPDATE empresas SET
                    codigo_cvm = ?,
                    razao_social = ?,
                    nome_fantasia = ?,
                    setor = ?,
                    situacao = ?,
                    data_registro = ?,
                    data_cancelamento = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE cnpj = ?
            """, (
                data.get('codigo_cvm'),
                data.get('razao_social'),
                data.get('nome_fantasia'),
                data.get('setor'),
                data.get('situacao'),
                data.get('data_registro'),
                data.get('data_cancelamento'),
                data.get('cnpj')
            ))
            empresa_id = existing['id']
        else:
            # Inserir
            cursor.execute("""
                INSERT INTO empresas (
                    cnpj, codigo_cvm, razao_social, nome_fantasia,
                    setor, situacao, data_registro, data_cancelamento
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.get('cnpj'),
                data.get('codigo_cvm'),
                data.get('razao_social'),
                data.get('nome_fantasia'),
                data.get('setor'),
                data.get('situacao'),
                data.get('data_registro'),
                data.get('data_cancelamento')
            ))
            empresa_id = cursor.lastrowid
        
        self.connection.commit()
        return empresa_id
    
    def insert_acao(self, data: Dict[str, Any]) -> int:
        """Insere ou atualiza ação (ticker)"""
        cursor = self.connection.cursor()
        
        cursor.execute("SELECT id FROM acoes WHERE ticker = ?", (data.get('ticker'),))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute("""
                UPDATE acoes SET
                    empresa_id = ?,
                    cnpj = ?,
                    tipo = ?,
                    mercado = ?,
                    segmento = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE ticker = ?
            """, (
                data.get('empresa_id'),
                data.get('cnpj'),
                data.get('tipo'),
                data.get('mercado'),
                data.get('segmento'),
                data.get('ticker')
            ))
            acao_id = existing['id']
        else:
            cursor.execute("""
                INSERT INTO acoes (ticker, empresa_id, cnpj, tipo, mercado, segmento)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                data.get('ticker'),
                data.get('empresa_id'),
                data.get('cnpj'),
                data.get('tipo'),
                data.get('mercado'),
                data.get('segmento')
            ))
            acao_id = cursor.lastrowid
        
        self.connection.commit()
        return acao_id
    
    def insert_dividendo(self, data: Dict[str, Any]) -> int:
        """Insere dividendo (único por empresa/ano)"""
        cursor = self.connection.cursor()
        
        # Verificar duplicata
        cursor.execute("""
            SELECT id FROM dividendos 
            WHERE cnpj = ? AND ano_fiscal = ?
        """, (data.get('cnpj'), data.get('ano_fiscal')))
        
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute("""
                UPDATE dividendos SET
                    valor_total = ?,
                    data_referencia = ?,
                    tipo = ?
                WHERE id = ?
            """, (
                data.get('valor_total'),
                data.get('data_referencia'),
                data.get('tipo'),
                existing['id']
            ))
            return existing['id']
        else:
            cursor.execute("""
                INSERT INTO dividendos (
                    empresa_id, cnpj, ano_fiscal, data_referencia,
                    tipo, valor_total, moeda, escala
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.get('empresa_id'),
                data.get('cnpj'),
                data.get('ano_fiscal'),
                data.get('data_referencia'),
                data.get('tipo'),
                data.get('valor_total'),
                data.get('moeda', 'BRL'),
                data.get('escala', 'MIL')
            ))
            self.connection.commit()
            return cursor.lastrowid
    
    def insert_patrimonio(self, data: Dict[str, Any]) -> int:
        """Insere patrimônio líquido"""
        cursor = self.connection.cursor()
        
        cursor.execute("""
            SELECT id FROM patrimonio 
            WHERE cnpj = ? AND ano_fiscal = ?
        """, (data.get('cnpj'), data.get('ano_fiscal')))
        
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute("""
                UPDATE patrimonio SET valor = ?, data_referencia = ?
                WHERE id = ?
            """, (data.get('valor'), data.get('data_referencia'), existing['id']))
            return existing['id']
        else:
            cursor.execute("""
                INSERT INTO patrimonio (
                    empresa_id, cnpj, ano_fiscal, data_referencia,
                    valor, moeda, escala
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                data.get('empresa_id'),
                data.get('cnpj'),
                data.get('ano_fiscal'),
                data.get('data_referencia'),
                data.get('valor'),
                data.get('moeda', 'BRL'),
                data.get('escala', 'MIL')
            ))
            self.connection.commit()
            return cursor.lastrowid
    
    def log_sync(self, tipo: str, fonte: str, status: str, **kwargs):
        """Registra log de sincronização"""
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO sync_log (
                tipo, fonte, status, registros_processados,
                registros_novos, registros_atualizados, mensagem, detalhes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            tipo,
            fonte,
            status,
            kwargs.get('registros_processados', 0),
            kwargs.get('registros_novos', 0),
            kwargs.get('registros_atualizados', 0),
            kwargs.get('mensagem'),
            json.dumps(kwargs.get('detalhes', {}))
        ))
        self.connection.commit()
    
    def get_empresas(self, situacao: Optional[str] = None, setor_besst: Optional[str] = None, 
                     apenas_monitoradas: bool = False, limit: int = 1000) -> List[Dict]:
        """Lista empresas com filtros opcionais"""
        cursor = self.connection.cursor()
        
        query = "SELECT * FROM empresas WHERE 1=1"
        params = []
        
        if situacao:
            query += " AND situacao = ?"
            params.append(situacao)
        
        if setor_besst:
            query += " AND setor_besst = ?"
            params.append(setor_besst)
        
        if apenas_monitoradas:
            query += " AND monitorar = TRUE"
        
        query += " ORDER BY razao_social LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, tuple(params))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_empresas_besst(self, situacao: str = 'ATIVO') -> List[Dict]:
        """Retorna apenas empresas BESST (monitoradas)"""
        cursor = self.connection.cursor()
        
        query = """
            SELECT * FROM empresas 
            WHERE monitorar = TRUE
        """
        params = []
        
        if situacao:
            query += " AND situacao = ?"
            params.append(situacao)
        
        query += " ORDER BY setor_besst, razao_social"
        
        cursor.execute(query, tuple(params))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_all_empresas(self) -> List[Dict]:
        """Retorna TODAS as empresas sem limite"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM empresas ORDER BY id")
        return [dict(row) for row in cursor.fetchall()]
    
    def update_empresa(self, empresa_id: int, dados: dict) -> bool:
        """Atualiza campos de uma empresa"""
        if not dados:
            return False
        
        campos = []
        valores = []
        
        for campo, valor in dados.items():
            campos.append(f"{campo} = ?")
            valores.append(valor)
        
        valores.append(empresa_id)
        
        query = f"UPDATE empresas SET {', '.join(campos)} WHERE id = ?"
        
        cursor = self.connection.cursor()
        cursor.execute(query, tuple(valores))
        self.connection.commit()
        
        return cursor.rowcount > 0
    
    def get_empresa_by_cnpj(self, cnpj: str) -> Optional[Dict]:
        """Busca empresa por CNPJ"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM empresas WHERE cnpj = ?", (cnpj,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_acoes(self, empresa_id: Optional[int] = None) -> List[Dict]:
        """Lista ações"""
        cursor = self.connection.cursor()
        
        if empresa_id:
            cursor.execute("""
                SELECT a.*, e.razao_social
                FROM acoes a
                LEFT JOIN empresas e ON a.empresa_id = e.id
                WHERE a.empresa_id = ?
            """, (empresa_id,))
        else:
            cursor.execute("""
                SELECT a.*, e.razao_social
                FROM acoes a
                LEFT JOIN empresas e ON a.empresa_id = e.id
                ORDER BY a.ticker
            """)
        
        return [dict(row) for row in cursor.fetchall()]
    
    def close(self):
        """Fecha conexão com banco"""
        if self.connection:
            self.connection.close()
            logger.info("Banco de dados fechado")


# Singleton global
_db_instance = None

def get_db() -> Database:
    """Retorna instância singleton do banco"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance
