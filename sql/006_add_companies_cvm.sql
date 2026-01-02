-- Migração 006: Adicionar Tabela de Empresas CVM
-- Armazena cadastro oficial de companhias abertas da CVM
-- Data: 2026-01-02

-- ==========================================
-- TABELA: companies_cvm
-- ==========================================
-- Cadastro oficial de empresas da CVM (Comissão de Valores Mobiliários)
-- Fonte: https://dados.cvm.gov.br/
-- Atualização: Diária (sincronizada via job)

CREATE TABLE IF NOT EXISTS companies_cvm (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    
    -- Identificadores
    cnpj TEXT NOT NULL UNIQUE,           -- CNPJ da empresa (PK business)
    cvm_code TEXT,                        -- Código CVM da empresa
    
    -- Denominações
    denominacao_social TEXT NOT NULL,     -- Razão social oficial
    denominacao_comercial TEXT,           -- Nome fantasia/comercial
    
    -- Classificação
    setor_atividade TEXT,                 -- Setor de atividade econômica
    uf TEXT,                              -- Estado (UF)
    municipio TEXT,                       -- Cidade
    
    -- Datas importantes
    data_registro_cvm DATE,               -- Data de registro na CVM
    data_constituicao DATE,               -- Data de constituição da empresa
    
    -- Status
    situacao_cvm TEXT,                    -- ATIVO, CANCELADA, etc.
    
    -- Metadados
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ==========================================
-- ÍNDICES
-- ==========================================

-- Busca rápida por CNPJ (já é UNIQUE, mas explicitamos)
CREATE INDEX IF NOT EXISTS idx_companies_cvm_cnpj ON companies_cvm(cnpj);

-- Busca por código CVM
CREATE INDEX IF NOT EXISTS idx_companies_cvm_code ON companies_cvm(cvm_code);

-- Busca por situação (filtrar empresas ativas)
CREATE INDEX IF NOT EXISTS idx_companies_cvm_situacao ON companies_cvm(situacao_cvm);

-- Busca por setor (análise setorial)
CREATE INDEX IF NOT EXISTS idx_companies_cvm_setor ON companies_cvm(setor_atividade);

-- Busca por denominação social (autocomplete)
CREATE INDEX IF NOT EXISTS idx_companies_cvm_denominacao 
ON companies_cvm USING gin(to_tsvector('portuguese', denominacao_social));

-- ==========================================
-- TRIGGER: Atualizar updated_at
-- ==========================================

-- Reutilizar função existente (criada na migração 003)
CREATE TRIGGER companies_cvm_updated_at
    BEFORE UPDATE ON companies_cvm
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ==========================================
-- COMENTÁRIOS
-- ==========================================

COMMENT ON TABLE companies_cvm IS 
'Cadastro oficial de companhias abertas da CVM. Sincronizado diariamente via job sync_fundamentals_cvm.';

COMMENT ON COLUMN companies_cvm.cnpj IS 
'CNPJ da empresa (formato: XX.XXX.XXX/XXXX-XX). Chave primária business.';

COMMENT ON COLUMN companies_cvm.cvm_code IS 
'Código único da empresa na CVM (ex: 23264 para Petrobras).';

COMMENT ON COLUMN companies_cvm.setor_atividade IS 
'Setor de atividade econômica conforme classificação CVM.';

COMMENT ON COLUMN companies_cvm.situacao_cvm IS 
'Status da empresa na CVM: ATIVO (operando), CANCELADA (inativa), etc.';

-- ==========================================
-- ROW LEVEL SECURITY (RLS)
-- ==========================================

-- Habilitar RLS
ALTER TABLE companies_cvm ENABLE ROW LEVEL SECURITY;

-- Política: Leitura pública (dados abertos da CVM)
CREATE POLICY "Leitura publica de empresas CVM"
ON companies_cvm FOR SELECT
USING (true);

-- Política: Apenas service_role pode inserir/atualizar (via jobs)
CREATE POLICY "Apenas service_role pode modificar"
ON companies_cvm FOR ALL
USING (auth.role() = 'service_role');

-- ==========================================
-- DADOS INICIAIS (OPCIONAL)
-- ==========================================

-- Nenhum dado inicial necessário
-- A tabela será populada pelo job sync_fundamentals_cvm

-- ==========================================
-- TESTE DA MIGRAÇÃO
-- ==========================================

-- Verificar se tabela foi criada
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_name = 'companies_cvm'
    ) THEN
        RAISE NOTICE '[OK] Tabela companies_cvm criada com sucesso';
    ELSE
        RAISE EXCEPTION '[ERRO] Tabela companies_cvm nao foi criada';
    END IF;
END $$;

-- Verificar índices
DO $$
DECLARE
    idx_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO idx_count
    FROM pg_indexes
    WHERE tablename = 'companies_cvm';
    
    IF idx_count >= 5 THEN
        RAISE NOTICE '[OK] % indices criados para companies_cvm', idx_count;
    ELSE
        RAISE WARNING '[AVISO] Apenas % indices encontrados (esperados: 5+)', idx_count;
    END IF;
END $$;

-- Verificar trigger
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_trigger 
        WHERE tgname = 'companies_cvm_updated_at'
    ) THEN
        RAISE NOTICE '[OK] Trigger updated_at configurado';
    ELSE
        RAISE WARNING '[AVISO] Trigger updated_at nao encontrado';
    END IF;
END $$;

-- ==========================================
-- ROLLBACK (se necessário)
-- ==========================================

-- Para reverter esta migração, execute:
-- DROP TABLE IF EXISTS companies_cvm CASCADE;
