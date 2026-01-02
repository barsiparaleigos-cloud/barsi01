/**
 * Cápsula: Integração CVM Dados Abertos
 * 
 * Responsabilidade: Balanços oficiais (DFP/ITR).
 * Escopo: Interface + configuração + teste de conexão + persistência isolada.
 */

export interface CvmConfig {
  enabled: boolean;
  baseUrl: string;
  endpoints: {
    companies: string;
    dfp: string;
    itr: string;
  };
  lastSync?: string;
}

export const defaultCvmConfig: CvmConfig = {
  enabled: false,
  baseUrl: 'https://dados.cvm.gov.br/dados',
  endpoints: {
    companies: '/CIA_ABERTA/CAD/DADOS',
    dfp: '/CIA_ABERTA/DOC/DFP',
    itr: '/CIA_ABERTA/DOC/ITR',
  },
};

export async function testCvmConnection(config: CvmConfig): Promise<{ success: boolean; message: string }> {
  try {
    // Tenta buscar o índice de empresas (arquivo CSV público)
    const url = `${config.baseUrl}${config.endpoints.companies}/cad_cia_aberta.csv`;
    const res = await fetch(url, { signal: AbortSignal.timeout(10000) });

    if (!res.ok) {
      return { success: false, message: `HTTP ${res.status}: ${res.statusText}` };
    }

    const text = await res.text();
    if (!text || text.length < 100) {
      return { success: false, message: 'Resposta inválida (CSV vazio ou incompleto)' };
    }

    return { success: true, message: 'Conexão OK (fonte oficial CVM)' };
  } catch (err: any) {
    return { success: false, message: err?.message || 'Erro desconhecido' };
  }
}

export async function saveCvmConfig(config: CvmConfig): Promise<void> {
  const res = await fetch('/api/admin/integrations/cvm', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config),
  });

  if (!res.ok) {
    throw new Error(`Falha ao salvar: ${res.status}`);
  }
}

export async function loadCvmConfig(): Promise<CvmConfig> {
  try {
    const res = await fetch('/api/admin/integrations/cvm');
    if (!res.ok) return defaultCvmConfig;
    return await res.json();
  } catch {
    return defaultCvmConfig;
  }
}
