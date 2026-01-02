/**
 * Cápsula: Integração HG Brasil Finance
 * 
 * Responsabilidade: Cotações, índices e moedas.
 * Escopo: Interface + configuração + teste de conexão + persistência isolada.
 */

export interface HgBrasilConfig {
  enabled: boolean;
  apiKey?: string;
  baseUrl: string;
  endpoints: {
    stockPrice: string;
    taxes: string;
    dividendsV2: string;
    indicatorsV2: string;
    historicalV2: string;
  };
  rateLimit: {
    requestsPerMinute: number;
  };
  lastSync?: string;
}

export const defaultHgBrasilConfig: HgBrasilConfig = {
  enabled: false,
  baseUrl: 'https://api.hgbrasil.com',
  endpoints: {
    stockPrice: '/finance/stock_price',
    taxes: '/finance/taxes',
    dividendsV2: '/v2/finance/dividends',
    indicatorsV2: '/v2/finance/indicators',
    historicalV2: '/v2/finance/historical',
  },
  rateLimit: {
    requestsPerMinute: 60,
  },
};

export async function testHgBrasilConnection(config: HgBrasilConfig): Promise<{ success: boolean; message: string }> {
  try {
    const url = `${config.baseUrl}${config.endpoints.stockPrice}?key=${config.apiKey || ''}&symbol=ITUB4`;
    const res = await fetch(url, { signal: AbortSignal.timeout(5000) });

    if (!res.ok) {
      return { success: false, message: `HTTP ${res.status}: ${res.statusText}` };
    }

    const data = await res.json();
    if (!data || !data.results) {
      return { success: false, message: 'Resposta inválida (esperado campo "results")' };
    }

    return { success: true, message: 'Conexão OK' };
  } catch (err: any) {
    return { success: false, message: err?.message || 'Erro desconhecido' };
  }
}

export async function saveHgBrasilConfig(config: HgBrasilConfig): Promise<void> {
  const res = await fetch('/api/admin/integrations/hgbrasil', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config),
  });

  if (!res.ok) {
    throw new Error(`Falha ao salvar: ${res.status}`);
  }
}

export async function loadHgBrasilConfig(): Promise<HgBrasilConfig> {
  try {
    const res = await fetch('/api/admin/integrations/hgbrasil');
    if (!res.ok) return defaultHgBrasilConfig;
    return await res.json();
  } catch {
    return defaultHgBrasilConfig;
  }
}
