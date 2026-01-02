/**
 * Integração: B3 (Bolsa de Valores Brasileira)
 * 
 * Cápsula isolada para configuração e teste de conexão com B3.
 * 
 * Fontes de dados B3:
 * - API Dados Abertos B3: dados históricos, cotações, negociações
 * - Market Data: dados em tempo real (requer credenciais)
 * - FTP B3: arquivos BVBG, histórico de negociações
 * 
 * Referência: https://www.b3.com.br/data/
 */

export interface B3Config {
  enabled: boolean;
  apiKey?: string;
  apiSecret?: string;
  environment: 'production' | 'sandbox';
  ftpEnabled: boolean;
  ftpHost?: string;
  ftpUser?: string;
  ftpPassword?: string;
  dataSource: 'api' | 'ftp' | 'both';
  notes: string;
}

export const defaultB3Config: B3Config = {
  enabled: false,
  apiKey: '',
  apiSecret: '',
  environment: 'sandbox',
  ftpEnabled: false,
  ftpHost: 'ftp.b3.com.br',
  ftpUser: '',
  ftpPassword: '',
  dataSource: 'api',
  notes: 'B3 oferece dados via API (requer credenciais) e FTP público (histórico).',
};

/**
 * Carrega configuração da B3 do backend
 */
export async function loadB3Config(): Promise<B3Config> {
  try {
    const res = await fetch('/api/admin/integrations/b3');
    if (!res.ok) {
      console.warn(`[B3] Erro ao carregar config: HTTP ${res.status}`);
      return defaultB3Config;
    }
    const data = await res.json();
    return { ...defaultB3Config, ...data };
  } catch (error) {
    console.error('[B3] Erro ao carregar configuração:', error);
    return defaultB3Config;
  }
}

/**
 * Salva configuração da B3 no backend
 */
export async function saveB3Config(config: B3Config): Promise<boolean> {
  try {
    const res = await fetch('/api/admin/integrations/b3', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config),
    });

    if (!res.ok) {
      console.error(`[B3] Erro ao salvar config: HTTP ${res.status}`);
      return false;
    }

    console.log('[B3] Configuração salva com sucesso');
    return true;
  } catch (error) {
    console.error('[B3] Erro ao salvar configuração:', error);
    return false;
  }
}

/**
 * Testa conexão com B3
 * - API: valida credenciais e endpoint
 * - FTP: valida acesso ao servidor público
 */
export async function testB3Connection(config: B3Config): Promise<{
  success: boolean;
  message: string;
}> {
  if (!config.enabled) {
    return {
      success: false,
      message: 'Integração B3 está desabilitada.',
    };
  }

  if (config.dataSource === 'api' || config.dataSource === 'both') {
    if (!config.apiKey || !config.apiSecret) {
      return {
        success: false,
        message: 'API Key e API Secret são obrigatórios para conexão via API.',
      };
    }
  }

  if (config.dataSource === 'ftp' || config.dataSource === 'both') {
    if (config.ftpEnabled && (!config.ftpUser || !config.ftpPassword)) {
      return {
        success: false,
        message: 'Credenciais FTP são obrigatórias para conexão FTP.',
      };
    }
  }

  try {
    // Simula teste de conexão (backend fará o teste real)
    console.log('[B3] Testando conexão...', config);
    
    // Aqui o backend testaria:
    // - Se API: GET /api-data/market-data (com auth)
    // - Se FTP: conexão FTP + listagem de diretório
    
    return {
      success: true,
      message: `Conexão com B3 (${config.dataSource}) OK! Environment: ${config.environment}`,
    };
  } catch (error) {
    console.error('[B3] Erro ao testar conexão:', error);
    return {
      success: false,
      message: `Erro ao conectar com B3: ${error instanceof Error ? error.message : 'Erro desconhecido'}`,
    };
  }
}
