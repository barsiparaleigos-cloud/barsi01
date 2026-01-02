/**
 * Cápsula: Integração Fintz (fintz.com.br)
 * 
 * Responsabilidade: Dados contábeis normalizados e histórico de proventos.
 * Escopo: Interface + configuração + teste de conexão + persistência isolada.
 */

export interface FintzConfig {
  enabled: boolean;
  apiKey?: string;
  baseUrl: string;
  endpoints: {
    search: string;
    indicatorsByTicker: string;
    accountingItemsByTicker: string;
    dividends: string;
    ohlcHistory: string;
  };
  rateLimit: {
    requestsPerMinute: number;
  };
  lastSync?: string;
}

export const defaultFintzConfig: FintzConfig = {
  enabled: false,
  baseUrl: 'https://api.fintz.com.br',
  endpoints: {
    search: '/bolsa/b3/avista/busca',
    indicatorsByTicker: '/bolsa/b3/avista/indicadores/por-ticker',
    accountingItemsByTicker: '/bolsa/b3/avista/itens-contabeis/por-ticker',
    dividends: '/bolsa/b3/avista/proventos',
    ohlcHistory: '/bolsa/b3/avista/cotacoes/historico',
  },
  rateLimit: {
    requestsPerMinute: 30,
  },
};

export async function testFintzConnection(config: FintzConfig): Promise<{ success: boolean; message: string }> {
  try {
    // Endpoint simples para probe: busca de ativos (exige key; sem key deve retornar 401/403).
    const url = `${config.baseUrl}${config.endpoints.search}?q=ITUB&ativo=true`;
    const headers: HeadersInit = {};
    if (config.apiKey) {
      headers['X-API-Key'] = config.apiKey;
    }

    const res = await fetch(url, { headers, signal: AbortSignal.timeout(5000) });
    if (!res.ok) {
      if (res.status === 401 || res.status === 403) {
        return { success: false, message: `Autenticação falhou (HTTP ${res.status}). Verifique a API Key.` };
      }
      return { success: false, message: `HTTP ${res.status}: ${res.statusText}` };
    }

    const data = await res.json();
    if (!Array.isArray(data)) {
      return { success: false, message: 'Resposta inválida (esperado array)' };
    }

    return { success: true, message: 'Conexão OK' };
  } catch (err: any) {
    return { success: false, message: err?.message || 'Erro desconhecido' };
  }
}

export async function saveFintzConfig(config: FintzConfig): Promise<void> {
  const res = await fetch('/api/admin/integrations/fintz', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config),
  });

  if (!res.ok) {
    throw new Error(`Falha ao salvar: ${res.status}`);
  }
}

export async function loadFintzConfig(): Promise<FintzConfig> {
  try {
    const res = await fetch('/api/admin/integrations/fintz');
    if (!res.ok) return defaultFintzConfig;
    return await res.json();
  } catch {
    return defaultFintzConfig;
  }
}
