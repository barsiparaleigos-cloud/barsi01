# 🚀 Migração 003 - Supabase

## 📋 O que essa migração faz?

Adiciona 2 novas tabelas para integração com a API Brapi:

1. **`precos`** - Armazena cotações diárias das ações
2. **`ticker_mapping`** - Mapeia CNPJ (CVM) → Ticker (B3)

---

## ✅ Opção 1: Aplicar via Dashboard (RECOMENDADO)

### Passo 1: Acessar SQL Editor
1. Acesse: https://supabase.com/dashboard
2. Selecione seu projeto
3. Menu lateral: **SQL Editor**

### Passo 2: Executar SQL
1. Clique em **New Query**
2. Copie o conteúdo completo de: `sql/003_add_precos_and_ticker_mapping.sql`
3. Cole no editor
4. Clique em **RUN** (ou Ctrl+Enter)

### Passo 3: Verificar
Execute esta query para confirmar:

```sql
SELECT 
  table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name IN ('precos', 'ticker_mapping');
```

Deve retornar 2 linhas.

---

## ⚡ Opção 2: Aplicar via Supabase CLI

```powershell
# 1. Instalar Supabase CLI (se não tiver)
npm install -g supabase

# 2. Login
supabase login

# 3. Linkar projeto
supabase link --project-ref SEU_PROJECT_REF

# 4. Aplicar migração
supabase db push
```

Ou use o script pronto:
```powershell
.\scripts\apply_migration_003.ps1
```

---

## 🧪 Testar após migração

### 1. Verificar tabelas criadas
```sql
-- No SQL Editor do Supabase:
SELECT * FROM precos LIMIT 5;
SELECT * FROM ticker_mapping;
```

### 2. Testar sync de preços (local)
```powershell
cd "C:\Users\rafae\OneDrive\Desktop\Barsi Para Leigos\barsi01"
python jobs\sync_precos.py --test
```

Deve sincronizar 4 ações: PETR4, MGLU3, VALE3, ITUB4

---

## 📊 Estrutura das tabelas

### `precos`
| Coluna               | Tipo      | Descrição                    |
|----------------------|-----------|------------------------------|
| id                   | bigserial | PK                           |
| ticker               | text      | Código da ação (PETR4)       |
| data                 | date      | Data da cotação              |
| fechamento           | numeric   | Preço de fechamento (OBRIG.) |
| abertura             | numeric   | Preço de abertura            |
| maxima               | numeric   | Máxima do dia                |
| minima               | numeric   | Mínima do dia                |
| volume               | bigint    | Volume negociado             |
| market_cap           | bigint    | Market Cap                   |
| variacao_percentual  | numeric   | Variação %                   |
| fonte                | text      | brapi, yahoo, manual         |
| created_at           | timestamptz | Timestamp inserção        |

**Índice único:** `(ticker, data, fonte)` → permite UPSERT

### `ticker_mapping`
| Coluna       | Tipo      | Descrição                      |
|--------------|-----------|--------------------------------|
| id           | bigserial | PK                             |
| empresa_id   | bigint    | FK para tabela empresas        |
| cnpj         | text      | CNPJ da empresa                |
| ticker       | text      | Código da ação (ÚNICO)         |
| nome         | text      | Nome da empresa                |
| tipo_acao    | text      | PN, ON, UNIT                   |
| ativo        | boolean   | Se está ativo na B3            |
| verificado   | boolean   | Se foi verificado manualmente  |
| created_at   | timestamptz | Criado em                    |
| updated_at   | timestamptz | Atualizado em (auto-trigger) |

**Dados iniciais:** 4 tickers de teste (PETR4, VALE3, ITUB4, MGLU3)

---

## 🔒 RLS (Row Level Security)

Por padrão, a migração **NÃO ativa RLS**.

Se quiser ativar (recomendado para produção):

```sql
-- Ativar RLS
alter table public.precos enable row level security;
alter table public.ticker_mapping enable row level security;

-- Permitir leitura pública
create policy "Leitura pública de precos"
  on public.precos for select
  using (true);

create policy "Leitura pública de ticker_mapping"
  on public.ticker_mapping for select
  using (true);

-- Apenas service_role pode escrever (jobs)
create policy "Service role escreve precos"
  on public.precos for all
  using (auth.role() = 'service_role');

create policy "Service role escreve ticker_mapping"
  on public.ticker_mapping for all
  using (auth.role() = 'service_role');
```

---

## 🚨 Rollback (se necessário)

```sql
-- Remover tabelas (CUIDADO: perde dados!)
drop table if exists public.precos cascade;
drop table if exists public.ticker_mapping cascade;

-- Remover função do trigger
drop function if exists public.update_updated_at_column() cascade;
```

---

## 📝 Checklist

- [ ] Migração 003 aplicada no Supabase
- [ ] Tabelas `precos` e `ticker_mapping` criadas
- [ ] 4 tickers de teste inseridos
- [ ] Job `sync_precos.py` testado localmente
- [ ] Dados sincronizando corretamente
- [ ] (Opcional) RLS configurado

---

## 🆘 Problemas?

### Erro: "relation already exists"
✅ Normal! A migração usa `if not exists`, pode rodar múltiplas vezes.

### Erro: "permission denied"
❌ Verifique se está usando a chave `service_role_key` nos jobs.

### Erro: "duplicate key value"
✅ Normal ao re-executar! O índice único impede duplicatas.

---

## 🎯 Próximos passos

1. ✅ Migração 003 aplicada
2. 🔧 Popular `ticker_mapping` com mais empresas BESST
3. 🔧 Criar job para sync diário automático
4. 🔧 Calcular Dividend Yield
5. 🔧 Exibir DY na UI

