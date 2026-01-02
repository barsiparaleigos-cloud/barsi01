"""
Endpoints para consulta de empresas e ações
Dados persistentes do banco SQLite
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.models import get_db
from typing import Dict, List, Any, Optional


def handle_empresas_list(
    situacao: Optional[str] = None,
    setor: Optional[str] = None,
    limit: int = 1000,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Lista empresas cadastradas
    
    Query params:
        - situacao: ATIVO, CANCELADA, etc
        - setor: filtro por setor
        - limit: quantidade de resultados
        - offset: paginação
    """
    db = get_db()
    empresas = db.get_empresas(situacao=situacao, limit=limit)
    
    # Filtrar por setor se especificado
    if setor:
        empresas = [e for e in empresas if e.get('setor') == setor]
    
    # Paginação
    total = len(empresas)
    empresas = empresas[offset:offset + limit]
    
    return {
        "total": total,
        "count": len(empresas),
        "limit": limit,
        "offset": offset,
        "empresas": empresas
    }


def handle_empresa_detail(cnpj: str) -> Dict[str, Any]:
    """
    Detalhes de uma empresa específica
    
    Path param:
        - cnpj: CNPJ da empresa
    """
    db = get_db()
    empresa = db.get_empresa_by_cnpj(cnpj)
    
    if not empresa:
        return {"error": "Empresa não encontrada"}
    
    # Buscar ações relacionadas
    acoes = db.get_acoes(empresa_id=empresa['id'])
    
    # Buscar dividendos
    cursor = db.connection.cursor()
    cursor.execute("""
        SELECT * FROM dividendos
        WHERE empresa_id = ?
        ORDER BY ano_fiscal DESC
    """, (empresa['id'],))
    dividendos = [dict(row) for row in cursor.fetchall()]
    
    # Buscar patrimônio
    cursor.execute("""
        SELECT * FROM patrimonio
        WHERE empresa_id = ?
        ORDER BY ano_fiscal DESC
    """, (empresa['id'],))
    patrimonio = [dict(row) for row in cursor.fetchall()]
    
    return {
        "empresa": empresa,
        "acoes": acoes,
        "dividendos": dividendos,
        "patrimonio": patrimonio
    }


def handle_acoes_list(ticker: Optional[str] = None) -> Dict[str, Any]:
    """
    Lista ações (tickers)
    
    Query params:
        - ticker: filtro por ticker específico
    """
    db = get_db()
    
    if ticker:
        cursor = db.connection.cursor()
        cursor.execute("""
            SELECT a.*, e.razao_social, e.cnpj
            FROM acoes a
            LEFT JOIN empresas e ON a.empresa_id = e.id
            WHERE a.ticker = ?
        """, (ticker,))
        acao = cursor.fetchone()
        
        if not acao:
            return {"error": "Ação não encontrada"}
        
        return {"acao": dict(acao)}
    else:
        acoes = db.get_acoes()
        return {
            "total": len(acoes),
            "acoes": acoes
        }


def handle_stats() -> Dict[str, Any]:
    """Estatísticas gerais do banco de dados"""
    db = get_db()
    cursor = db.connection.cursor()
    
    # Contar registros
    cursor.execute("SELECT COUNT(*) as count FROM empresas")
    total_empresas = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM empresas WHERE situacao = 'ATIVO'")
    empresas_ativas = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM acoes")
    total_acoes = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM dividendos")
    total_dividendos = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM patrimonio")
    total_patrimonio = cursor.fetchone()['count']
    
    # Última sincronização
    cursor.execute("""
        SELECT created_at, tipo, status 
        FROM sync_log 
        ORDER BY created_at DESC 
        LIMIT 1
    """)
    ultima_sync = cursor.fetchone()
    
    # Tamanho do banco
    db_size = db.db_path.stat().st_size if db.db_path.exists() else 0
    
    return {
        "total_empresas": total_empresas,
        "empresas_ativas": empresas_ativas,
        "total_acoes": total_acoes,
        "total_dividendos": total_dividendos,
        "total_patrimonio": total_patrimonio,
        "ultima_sincronizacao": dict(ultima_sync) if ultima_sync else None,
        "database_size_mb": round(db_size / 1024 / 1024, 2),
        "database_path": str(db.db_path)
    }
