# 🚀 Próximo Passo: Sincronizar Brapi → Supabase

## ✅ O que você já tem:
- ✅ Migração 003 aplicada no Supabase
- ✅ Tabelas `precos` e `ticker_mapping` criadas
- ✅ Integração Brapi funcionando
- ✅ 4 tickers de teste (PETR4, VALE3, ITUB4, MGLU3)

---

## 🎯 Próximo passo: TESTAR sincronização

### Opção 1: Teste Rápido (via script)

```powershell
cd "C:\Users\rafae\OneDrive\Desktop\Barsi Para Leigos\barsi01"
.\scripts\test_sync_brapi.ps1
```

### Opção 2: Teste Manual

```powershell
cd "C:\Users\rafae\OneDrive\Desktop\Barsi Para Leigos\barsi01"

# Ativar venv (se necessário)
.\venv\Scripts\Activate.ps1

# Executar job
python -m jobs.sync_precos_brapi
```

---

## 📋 O que vai acontecer:

1. 🔌 Conecta ao Supabase (usando .env.local)
2. 🔌 Conecta à Brapi
3. 📊 Busca tickers ativos (ticker_mapping)
4. 💰 Busca cotações via Brapi API
5. 💾 Salva no Supabase (tabela `precos`)
6. 📝 Registra execução (tabela `job_runs`)

---

## 🔍 Verificar resultados no Supabase:

### SQL Editor:

```sql
-- Ver preços sincronizados
SELECT 
  ticker, 
  data, 
  fechamento, 
  variacao_percentual,
  created_at
FROM precos 
ORDER BY data DESC, ticker;

-- Ver tickers ativos
SELECT * FROM ticker_mapping WHERE ativo = true;

-- Ver logs de execução
SELECT * FROM job_runs 
WHERE job_name = 'sync_precos_brapi' 
ORDER BY started_at DESC 
LIMIT 5;
```

---

## ⚠️ Pré-requisitos:

### 1. Verificar .env.local

Certifique-se que tem:
```env
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_SERVICE_ROLE_KEY=seu_service_role_key_aqui
```

> 💡 **Onde conseguir:**
> Dashboard → Project Settings → API
> - URL: Project URL
> - Key: service_role (secret)

### 2. Verificar tickers ativos

Se a query acima não retornar nada, adicione manualmente:

```sql
INSERT INTO ticker_mapping (ticker, nome, ativo, verificado)
VALUES
  ('PETR4', 'Petrobras PN', true, true),
  ('VALE3', 'Vale ON', true, true),
  ('ITUB4', 'Itaú Unibanco PN', true, true),
  ('MGLU3', 'Magazine Luiza ON', true, true)
ON CONFLICT (ticker) DO NOTHING;
```

---

## 🎯 Resultado esperado:

```
======================================================================
📈 SINCRONIZAÇÃO BRAPI → SUPABASE
======================================================================

🔌 Conectando ao Supabase...
✅ Supabase conectado

🔌 Conectando à Brapi...
✅ Brapi conectada

📅 Data: 02/01/2026

📊 Buscando tickers ativos...
📊 4 ticker(s) ativos encontrados
✅ 4 ticker(s) para processar: PETR4, VALE3, ITUB4, MGLU3

📦 Batch 1/1 (4 tickers)
  • PETR4: R$ 30.82 (+0.29%)
  • VALE3: R$ 71.96 (-0.22%)
  • ITUB4: R$ 39.23 (+0.64%)
  • MGLU3: R$ 8.94 (+0.40%)
✅ 4 preço(s) salvos no Supabase

======================================================================
📊 RELATÓRIO FINAL
======================================================================
✅ Sucesso: 4 ticker(s)
❌ Erros: 0 ticker(s)
📈 Taxa de sucesso: 100.0%
======================================================================

✅ Job registrado: success (4 rows)
```

---

## 🐛 Problemas comuns:

### Erro: "SUPABASE_URL inválida"
❌ **Causa:** Credenciais não configuradas
✅ **Solução:** Execute `.\scripts\setup_env.ps1`

### Erro: "Nenhum ticker ativo"
❌ **Causa:** Tabela `ticker_mapping` vazia
✅ **Solução:** Insira os 4 tickers de teste (SQL acima)

### Erro: "401 Unauthorized"
❌ **Causa:** SERVICE_ROLE_KEY incorreta
✅ **Solução:** Verifique a key no Dashboard → API

### Erro: "relation precos does not exist"
❌ **Causa:** Migração 003 não foi aplicada
✅ **Solução:** Reaplique o SQL da migração 003

---

## 🎉 Depois que funcionar:

1. ✅ Sistema sincronizando Brapi → Supabase
2. 🔧 Próximo: Adicionar mais empresas BESST
3. 🔧 Próximo: Buscar dividendos históricos
4. 🔧 Próximo: Calcular Dividend Yield
5. 🔧 Próximo: Exibir na UI

---

## 📞 Precisa de ajuda?

Execute o teste e me mostre a saída! 🚀
