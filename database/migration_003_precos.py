"""
Migration 003: Adicionar tabela de preços históricos
"""

def migration_003_add_precos_table():
    """
    Cria tabela para armazenar histórico de preços das ações
    """
    return """
    -- Tabela de cotações/preços
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
    );
    
    -- Índices para performance
    CREATE INDEX IF NOT EXISTS idx_precos_ticker ON precos(ticker);
    CREATE INDEX IF NOT EXISTS idx_precos_data ON precos(data DESC);
    CREATE INDEX IF NOT EXISTS idx_precos_ticker_data ON precos(ticker, data DESC);
    
    -- Tabela para mapeamento CNPJ → Ticker
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
    );
    
    CREATE INDEX IF NOT EXISTS idx_ticker_mapping_cnpj ON ticker_mapping(cnpj);
    CREATE INDEX IF NOT EXISTS idx_ticker_mapping_ticker ON ticker_mapping(ticker);
    CREATE INDEX IF NOT EXISTS idx_ticker_mapping_empresa_id ON ticker_mapping(empresa_id);
    """
