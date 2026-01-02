/**
 * Página Admin: Integração de Fontes de Dados
 * 
 * Arquitetura modular (cápsulas):
 * - Cada API = cápsula isolada (Brapi, Fintz, HG Brasil, CVM)
 * - Salvamento por cápsula (não monolítico)
 * - UI organizada em Tabs
 */

import { useState, useEffect } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../../app/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../../app/components/ui/card';
import { Database, TrendingUp, BarChart3, Building2 } from 'lucide-react';

import { IntegrationCard } from './IntegrationCard';

// Cápsulas de integração
import {
  BrapiConfig,
  defaultBrapiConfig,
  loadBrapiConfig,
  saveBrapiConfig,
  testBrapiConnection,
} from './brapi.integration';

import {
  FintzConfig,
  defaultFintzConfig,
  loadFintzConfig,
  saveFintzConfig,
  testFintzConnection,
} from './fintz.integration';

import {
  HgBrasilConfig,
  defaultHgBrasilConfig,
  loadHgBrasilConfig,
  saveHgBrasilConfig,
  testHgBrasilConnection,
} from './hgbrasil.integration';

import {
  CvmConfig,
  defaultCvmConfig,
  loadCvmConfig,
  saveCvmConfig,
  testCvmConnection,
} from './cvm.integration';

import {
  B3Config,
  defaultB3Config,
  loadB3Config,
  saveB3Config,
  testB3Connection,
} from './b3.integration';

export default function DataSourceIntegrations() {
  const [brapiConfig, setBrapiConfig] = useState<BrapiConfig>(defaultBrapiConfig);
  const [fintzConfig, setFintzConfig] = useState<FintzConfig>(defaultFintzConfig);
  const [hgBrasilConfig, setHgBrasilConfig] = useState<HgBrasilConfig>(defaultHgBrasilConfig);
  const [cvmConfig, setCvmConfig] = useState<CvmConfig>(defaultCvmConfig);
  const [b3Config, setB3Config] = useState<B3Config>(defaultB3Config);

  useEffect(() => {
    loadBrapiConfig().then(setBrapiConfig);
    loadFintzConfig().then(setFintzConfig);
    loadHgBrasilConfig().then(setHgBrasilConfig);
    loadCvmConfig().then(setCvmConfig);
    loadB3Config().then(setB3Config);
  }, []);

  return (
    <div className="container mx-auto px-4 py-8 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <Database className="size-8" />
          Integração de Fontes de Dados
        </h1>
        <p className="text-muted-foreground mt-2">
          Configure e gerencie as integrações com APIs de mercado para alimentar o motor de dividendos.
        </p>
      </div>

      {/* Tabs (cada API = Tab isolado) */}
      <Tabs defaultValue="brapi" className="w-full">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="brapi">
            <TrendingUp className="size-4 mr-2" />
            Brapi
          </TabsTrigger>
          <TabsTrigger value="fintz">
            <BarChart3 className="size-4 mr-2" />
            Fintz
          </TabsTrigger>
          <TabsTrigger value="hgbrasil">
            <TrendingUp className="size-4 mr-2" />
            HG Brasil
          </TabsTrigger>
          <TabsTrigger value="cvm">
            <Building2 className="size-4 mr-2" />
            CVM Oficial
          </TabsTrigger>
          <TabsTrigger value="b3">
            <Database className="size-4 mr-2" />
            B3
          </TabsTrigger>
        </TabsList>

        {/* Tab: Brapi */}
        <TabsContent value="brapi" className="space-y-4">
          <IntegrationCard
            name="Brapi (brapi.dev)"
            description="Cotações em tempo real, histórico de preços e dividendos."
            enabled={brapiConfig.enabled}
            baseUrl={brapiConfig.baseUrl}
            apiKey={brapiConfig.apiKey}
            lastSync={brapiConfig.lastSync}
            onToggle={(enabled) => {
              const updated = { ...brapiConfig, enabled };
              setBrapiConfig(updated);
              saveBrapiConfig(updated);
            }}
            onSave={async (partial) => {
              const updated = { ...brapiConfig, ...partial };
              setBrapiConfig(updated);
              await saveBrapiConfig(updated);
            }}
            onTest={() => testBrapiConnection(brapiConfig)}
          />

          <Card className="bg-blue-50 border-blue-200">
            <CardHeader>
              <CardTitle className="text-sm">ℹ️ Sobre esta integração</CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-muted-foreground">
              <p>
                <strong>Brapi</strong> é uma API brasileira com plano gratuito que fornece cotações,
                histórico de preços e dividendos de ações da B3. Ideal para o MVP.
              </p>
              <p className="mt-2">
                <strong>Limite:</strong> varia por plano (use cache + sync).
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab: Fintz */}
        <TabsContent value="fintz" className="space-y-4">
          <IntegrationCard
            name="Fintz (fintz.com.br)"
            description="Dados contábeis normalizados e histórico de proventos."
            enabled={fintzConfig.enabled}
            baseUrl={fintzConfig.baseUrl}
            apiKey={fintzConfig.apiKey}
            lastSync={fintzConfig.lastSync}
            onToggle={(enabled) => {
              const updated = { ...fintzConfig, enabled };
              setFintzConfig(updated);
              saveFintzConfig(updated);
            }}
            onSave={async (partial) => {
              const updated = { ...fintzConfig, ...partial };
              setFintzConfig(updated);
              await saveFintzConfig(updated);
            }}
            onTest={() => testFintzConnection(fintzConfig)}
          />

          <Card className="bg-blue-50 border-blue-200">
            <CardHeader>
              <CardTitle className="text-sm">ℹ️ Sobre esta integração</CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-muted-foreground">
              <p>
                <strong>Fintz</strong> fornece dados contábeis limpos e normalizados (DFP/ITR) e
                histórico de proventos ajustados para eventos corporativos.
              </p>
              <p className="mt-2">
                <strong>Limite:</strong> varia por plano (use cache + sync).
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab: HG Brasil */}
        <TabsContent value="hgbrasil" className="space-y-4">
          <IntegrationCard
            name="HG Brasil Finance"
            description="Cotações, índices e moedas."
            enabled={hgBrasilConfig.enabled}
            baseUrl={hgBrasilConfig.baseUrl}
            apiKey={hgBrasilConfig.apiKey}
            lastSync={hgBrasilConfig.lastSync}
            onToggle={(enabled) => {
              const updated = { ...hgBrasilConfig, enabled };
              setHgBrasilConfig(updated);
              saveHgBrasilConfig(updated);
            }}
            onSave={async (partial) => {
              const updated = { ...hgBrasilConfig, ...partial };
              setHgBrasilConfig(updated);
              await saveHgBrasilConfig(updated);
            }}
            onTest={() => testHgBrasilConnection(hgBrasilConfig)}
          />

          <Card className="bg-blue-50 border-blue-200">
            <CardHeader>
              <CardTitle className="text-sm">ℹ️ Sobre esta integração</CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-muted-foreground">
              <p>
                <strong>HG Brasil</strong> é uma API estável para cotações, índices (Ibovespa, S&P500) e moedas.
              </p>
              <p className="mt-2">
                <strong>Limite:</strong> varia por plano (use cache + sync).
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab: CVM */}
        <TabsContent value="cvm" className="space-y-4">
          <IntegrationCard
            name="CVM Dados Abertos"
            description="Balanços oficiais (DFP/ITR) da fonte regulatória."
            enabled={cvmConfig.enabled}
            baseUrl={cvmConfig.baseUrl}
            lastSync={cvmConfig.lastSync}
            onToggle={(enabled) => {
              const updated = { ...cvmConfig, enabled };
              setCvmConfig(updated);
              saveCvmConfig(updated);
            }}
            onSave={async (partial) => {
              const updated = { ...cvmConfig, ...partial };
              setCvmConfig(updated);
              await saveCvmConfig(updated);
            }}
            onTest={() => testCvmConnection(cvmConfig)}
          />

          <Card className="bg-blue-50 border-blue-200">
            <CardHeader>
              <CardTitle className="text-sm">ℹ️ Sobre esta integração</CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-muted-foreground">
              <p>
                <strong>CVM Dados Abertos</strong> é a fonte oficial e gratuita da Comissão de Valores Mobiliários.
                Contém todos os balanços (DFP/ITR) em formato CSV/XML.
              </p>
              <p className="mt-2">
                <strong>Limitação:</strong> Exige ETL (os arquivos são grandes e precisam de processamento).
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        {/* B3 Tab */}
        <TabsContent value="b3" className="space-y-4">
          <IntegrationCard
            name="B3 (Bolsa de Valores)"
            description="Dados oficiais da Bolsa: cotações, histórico, market data e FTP público"
            enabled={b3Config.enabled}
            baseUrl={b3Config.dataSource === 'ftp' ? (b3Config.ftpHost || 'ftp.b3.com.br') : 'https://api.b3.com.br'}
            apiKey={b3Config.apiKey}
            onToggle={(enabled) => {
              const updated = { ...b3Config, enabled };
              setB3Config(updated);
              saveB3Config(updated);
            }}
            onSave={async (partial) => {
              const updated = { ...b3Config, ...partial };
              setB3Config(updated);
              await saveB3Config(updated);
            }}
            onTest={() => testB3Connection(b3Config)}
          />

          <Card className="bg-blue-50 border-blue-200">
            <CardHeader>
              <CardTitle className="text-sm">ℹ️ Sobre esta integração</CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-muted-foreground">
              <p>
                <strong>B3 (Bolsa de Valores)</strong> oferece dados oficiais via API Market Data (requer credenciais) 
                e FTP público com históricos de negociação (arquivos BVBG).
              </p>
              <p className="mt-2">
                <strong>API:</strong> Requer cadastro e aprovação da B3.<br />
                <strong>FTP:</strong> Acesso público com históricos diários.
              </p>
              <div className="mt-4 p-3 bg-white rounded border space-y-3">
                <div>
                  <label className="block text-sm font-medium mb-1">Fonte de dados</label>
                  <select
                    className="w-full px-3 py-2 border rounded-md"
                    value={b3Config.dataSource}
                    onChange={(e) => setB3Config({ ...b3Config, dataSource: e.target.value as 'api' | 'ftp' | 'both' })}
                    aria-label="Fonte de dados B3"
                  >
                    <option value="api">API Market Data</option>
                    <option value="ftp">FTP Público (histórico)</option>
                    <option value="both">Ambos (API + FTP)</option>
                  </select>
                </div>

                {(b3Config.dataSource === 'api' || b3Config.dataSource === 'both') && (
                  <>
                    <div>
                      <label className="block text-sm font-medium mb-1">Ambiente</label>
                      <select
                        className="w-full px-3 py-2 border rounded-md"
                        value={b3Config.environment}
                        onChange={(e) => setB3Config({ ...b3Config, environment: e.target.value as 'production' | 'sandbox' })}
                        aria-label="Ambiente B3"
                      >
                        <option value="sandbox">Sandbox (testes)</option>
                        <option value="production">Produção</option>
                      </select>
                    </div>
                  </>
                )}

                {(b3Config.dataSource === 'ftp' || b3Config.dataSource === 'both') && (
                  <div className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      id="b3FtpEnabled"
                      checked={b3Config.ftpEnabled}
                      onChange={(e) => setB3Config({ ...b3Config, ftpEnabled: e.target.checked })}
                    />
                    <label htmlFor="b3FtpEnabled" className="text-sm">Habilitar FTP</label>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Rodapé de orientação */}
      <Card className="bg-yellow-50 border-yellow-200">
        <CardHeader>
          <CardTitle className="text-sm">⚠️ Importante</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          <ul className="list-disc list-inside space-y-1">
            <li>
              <strong>Nunca</strong> commite chaves de API no código. Use variáveis de ambiente (`.env.local`).
            </li>
            <li>
              Cada integração é salva <strong>isoladamente</strong> (arquitetura modular, não monolítica).
            </li>
            <li>
              Teste a conexão antes de habilitar a integração em produção.
            </li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
