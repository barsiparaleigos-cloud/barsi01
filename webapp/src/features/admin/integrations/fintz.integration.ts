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
    fundamentals: string;
    dividends: string;
    balanceSheet: string;
  };
  rateLimit: {
    requestsPerMinute: number;
  };
  lastSync?: string;
}

export const defaultFintzConfig: FintzConfig = {
  enabled: false,
  baseUrl: 'https://api.fintz.com.br/v1',
  endpoints: {
    fundamentals: '/stocks/{ticker}/fundamentals',
    dividends: '/stocks/{ticker}/dividends',
    balanceSheet: '/stocks/{ticker}/balance-sheet',
  },
  rateLimit: {
    requestsPerMinute: 30,
  },
};

export async function testFintzConnection(config: FintzConfig): Promise<{ success: boolean; message: string }> {
  try {
    const url = `${config.baseUrl}${config.endpoints.fundamentals.replace('{ticker}', 'ITUB4')}`;
    const headers: HeadersInit = {};
    if (config.apiKey) {
      headers['X-API-Key'] = config.apiKey;
    }

    const res = await fetch(url, { headers, signal: AbortSignal.timeout(5000) });
    if (!res.ok) {
      return { success: false, message: `HTTP ${res.status}: ${res.statusText}` };
    }

    const data = await res.json();
    if (!data) {
      return { success: false, message: 'Resposta vazia' };
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
