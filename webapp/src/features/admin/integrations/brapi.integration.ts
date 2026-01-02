/**
 * Cápsula: Integração Brapi (brapi.dev)
 * 
 * Responsabilidade: Cotações em tempo real, histórico de preços e dividendos.
 * Escopo: Interface + configuração + teste de conexão + persistência isolada.
 */

export interface BrapiConfig {
  enabled: boolean;
  apiKey?: string;
  baseUrl: string;
  endpoints: {
    quote: string;
    dividends: string;
    history: string;
  };
  rateLimit: {
    requestsPerMinute: number;
  };
  lastSync?: string;
}

export const defaultBrapiConfig: BrapiConfig = {
  enabled: false,
  baseUrl: 'https://brapi.dev/api',
  endpoints: {
    quote: '/quote',
    dividends: '/dividends',
    history: '/quote/{ticker}/history',
  },
  rateLimit: {
    requestsPerMinute: 60,
  },
};

export async function testBrapiConnection(config: BrapiConfig): Promise<{ success: boolean; message: string }> {
  try {
    const url = `${config.baseUrl}${config.endpoints.quote}/ITUB4`;
    const headers: HeadersInit = {};
    if (config.apiKey) {
      headers['Authorization'] = `Bearer ${config.apiKey}`;
    }

    const res = await fetch(url, { headers, signal: AbortSignal.timeout(5000) });
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

export async function saveBrapiConfig(config: BrapiConfig): Promise<void> {
  // Persiste apenas configuração Brapi (não monolítico)
  const res = await fetch('/api/admin/integrations/brapi', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config),
  });

  if (!res.ok) {
    throw new Error(`Falha ao salvar: ${res.status}`);
  }
}

export async function loadBrapiConfig(): Promise<BrapiConfig> {
  try {
    const res = await fetch('/api/admin/integrations/brapi');
    if (!res.ok) return defaultBrapiConfig;
    return await res.json();
  } catch {
    return defaultBrapiConfig;
  }
}
