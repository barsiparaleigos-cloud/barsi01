/**
 * CompanyList: Listagem de empresas cadastradas na CVM
 * Banco de dados local persistente com SQLite
 */

import { useState, useEffect } from 'react';
import { Card } from './ui/card';
import { Input } from './ui/input';
import { Button } from './ui/button';
import { Search, Building2, TrendingUp, DollarSign, Calendar } from 'lucide-react';

interface Empresa {
  id: number;
  cnpj: string;
  codigo_cvm: string;
  razao_social: string;
  nome_fantasia: string;
  setor: string;
  situacao: string;
  data_registro: string;
  updated_at: string;
  setor_besst: string | null;
  monitorar: boolean;
  elegivel_barsi: boolean;
  dividend_yield_atual: number | null;
  consistencia_dividendos: number | null;
}

interface Stats {
  total_empresas: number;
  empresas_ativas: number;
  empresas_besst: number;
  total_acoes: number;
  total_dividendos: number;
  database_size_mb: number;
  ultima_sincronizacao: {
    created_at: string;
    status: string;
  } | null;
}

export function CompanyList() {
  const [empresas, setEmpresas] = useState<Empresa[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filtroSituacao, setFiltroSituacao] = useState<'all' | 'ATIVO' | 'CANCELADA'>('ATIVO');
  const [filtroBesstAtivo, setFiltroBesstAtivo] = useState(false);

  useEffect(() => {
    loadData();
  }, [filtroSituacao, filtroBesstAtivo]);

  const loadData = async () => {
    try {
      setLoading(true);

      // Carregar estatísticas
      const statsRes = await fetch('http://127.0.0.1:8001/api/stats');
      const statsData = await statsRes.json();
      setStats(statsData);

      // Carregar empresas
      const url = filtroBesstAtivo 
        ? 'http://127.0.0.1:8001/api/empresas?apenas_monitoradas=true'
        : 'http://127.0.0.1:8001/api/empresas';
      
      const empresasRes = await fetch(url);
      const empresasData = await empresasRes.json();
      setEmpresas(empresasData.empresas || []);
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
    } finally {
      setLoading(false);
    }
  };

  const empresasFiltradas = empresas.filter(emp => {
    const matchSearch = 
      emp.razao_social.toLowerCase().includes(searchTerm.toLowerCase()) ||
      emp.cnpj.includes(searchTerm) ||
      (emp.nome_fantasia && emp.nome_fantasia.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchSituacao = filtroSituacao === 'all' || emp.situacao === filtroSituacao;
    
    return matchSearch && matchSituacao;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Carregando empresas...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Cabeçalho */}
      <div>
        <h2 className="text-3xl font-bold">Empresas Cadastradas</h2>
        <p className="text-muted-foreground mt-1">
          Banco de dados completo de companhias abertas na CVM
        </p>
      </div>

      {/* Estatísticas */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <Card className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary/10 rounded-lg">
                <Building2 className="size-5 text-primary" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total de Empresas</p>
                <p className="text-2xl font-bold">{stats.total_empresas.toLocaleString()}</p>
              </div>
            </div>
          </Card>

          <Card className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <TrendingUp className="size-5 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Empresas Ativas</p>
                <p className="text-2xl font-bold">{stats.empresas_ativas.toLocaleString()}</p>
              </div>
            </div>
          </Card>

          <Card className="p-4 bg-blue-50 border-blue-200">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <TrendingUp className="size-5 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-blue-700 font-medium">🎯 BESST (Radar)</p>
                <p className="text-2xl font-bold text-blue-900">{stats.empresas_besst.toLocaleString()}</p>
              </div>
            </div>
          </Card>

          <Card className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <DollarSign className="size-5 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Dividendos</p>
                <p className="text-2xl font-bold">{stats.total_dividendos.toLocaleString()}</p>
              </div>
            </div>
          </Card>

          <Card className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gray-100 rounded-lg">
                <Calendar className="size-5 text-gray-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Banco de Dados</p>
                <p className="text-2xl font-bold">{stats.database_size_mb} MB</p>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Última Sincronização */}
      {stats?.ultima_sincronizacao && (
        <Card className="p-4 bg-green-50 border-green-200">
          <div className="flex items-center gap-2 text-green-700">
            <div className="size-2 bg-green-500 rounded-full animate-pulse"></div>
            <p className="text-sm">
              <strong>Última sincronização:</strong>{' '}
              {new Date(stats.ultima_sincronizacao.created_at).toLocaleString('pt-BR')} -{' '}
              <span className="capitalize">{stats.ultima_sincronizacao.status}</span>
            </p>
          </div>
        </Card>
      )}

      {/* Filtros */}
      <Card className="p-4">
        <div className="flex flex-col gap-4">
          {/* Busca */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
            <Input
              placeholder="Buscar por razão social, CNPJ ou nome fantasia..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>

          {/* Botões de filtro */}
          <div className="flex flex-wrap gap-2 items-center">
            <span className="text-sm text-muted-foreground mr-2">Situação:</span>
            <Button
              variant={filtroSituacao === 'ATIVO' ? 'default' : 'outline'}
              onClick={() => setFiltroSituacao('ATIVO')}
              size="sm"
            >
              Ativas
            </Button>
            <Button
              variant={filtroSituacao === 'all' ? 'default' : 'outline'}
              onClick={() => setFiltroSituacao('all')}
              size="sm"
            >
              Todas
            </Button>
            <Button
              variant={filtroSituacao === 'CANCELADA' ? 'default' : 'outline'}
              onClick={() => setFiltroSituacao('CANCELADA')}
              size="sm"
            >
              Canceladas
            </Button>

            <div className="h-6 w-px bg-border mx-2"></div>

            {/* Toggle BESST */}
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={filtroBesstAtivo}
                onChange={(e) => setFiltroBesstAtivo(e.target.checked)}
                className="size-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm font-medium text-blue-700">
                🎯 Apenas empresas BESST (no radar)
              </span>
            </label>
          </div>

          {/* Alerta quando filtro BESST ativo */}
          {filtroBesstAtivo && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
              <p className="text-sm text-blue-800">
                <strong>✅ Filtro BESST ativo:</strong> Exibindo apenas empresas dos setores{' '}
                <strong>B</strong>ancos, <strong>E</strong>nergia, <strong>S</strong>aneamento/Seguros e{' '}
                <strong>T</strong>elecomunicações que estão no radar da metodologia Barsi.
              </p>
            </div>
          )}
        </div>
      </Card>

      {/* Lista de Empresas */}
      <Card>
        <div className="p-4 border-b">
          <p className="text-sm text-muted-foreground">
            Exibindo {empresasFiltradas.length} de {empresas.length} empresas
          </p>
        </div>

        <div className="divide-y max-h-[600px] overflow-y-auto">
          {empresasFiltradas.map((empresa) => {
            // Função para obter badge do setor BESST
            const getSetorBesstBadge = (letra: string | null) => {
              if (!letra) return null;
              
              const badges = {
                'B': { color: 'bg-blue-100 text-blue-700', label: '🏦 Bancos' },
                'E': { color: 'bg-yellow-100 text-yellow-700', label: '⚡ Energia' },
                'S': { color: 'bg-green-100 text-green-700', label: '💧 Saneamento/Seguros' },
                'T': { color: 'bg-purple-100 text-purple-700', label: '📡 Telecom' }
              };
              
              const badge = badges[letra as keyof typeof badges];
              if (!badge) return null;
              
              return (
                <span className={`text-xs px-2 py-1 rounded-full font-medium ${badge.color}`}>
                  {badge.label}
                </span>
              );
            };

            return (
              <div key={empresa.id} className="p-4 hover:bg-muted/50 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1 flex-wrap">
                      <h3 className="font-semibold text-lg">{empresa.razao_social}</h3>
                      <span className={`text-xs px-2 py-0.5 rounded-full ${
                        empresa.situacao === 'ATIVO' 
                          ? 'bg-green-100 text-green-700' 
                          : 'bg-gray-100 text-gray-700'
                      }`}>
                        {empresa.situacao}
                      </span>
                      {empresa.monitorar && getSetorBesstBadge(empresa.setor_besst)}
                      {empresa.elegivel_barsi && (
                        <span className="text-xs px-2 py-1 rounded-full font-medium bg-emerald-100 text-emerald-700">
                          ✅ Elegível Barsi
                        </span>
                      )}
                    </div>

                    {empresa.nome_fantasia && empresa.nome_fantasia !== empresa.razao_social && (
                      <p className="text-sm text-muted-foreground mb-2">
                        Nome fantasia: {empresa.nome_fantasia}
                      </p>
                    )}

                  <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
                    <span>
                      <strong>CNPJ:</strong> {empresa.cnpj}
                    </span>
                    <span>
                      <strong>Código CVM:</strong> {empresa.codigo_cvm}
                    </span>
                    {empresa.setor && (
                      <span>
                        <strong>Setor:</strong> {empresa.setor}
                      </span>
                    )}
                    {empresa.data_registro && (
                      <span>
                        <strong>Registro:</strong>{' '}
                        {new Date(empresa.data_registro).toLocaleDateString('pt-BR')}
                      </span>
                    )}
                  </div>
                </div>

                <Button variant="ghost" size="sm">
                  Ver Detalhes
                </Button>
              </div>
            </div>
          );
          })}

          {empresasFiltradas.length === 0 && (
            <div className="p-12 text-center">
              <Building2 className="size-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground">
                Nenhuma empresa encontrada com os filtros aplicados
              </p>
            </div>
          )}
        </div>
      </Card>

      {/* Rodapé */}
      <Card className="p-4 bg-blue-50 border-blue-200">
        <p className="text-sm text-blue-700">
          💾 <strong>Dados persistentes:</strong> Todas as informações são salvas localmente em banco de dados SQLite.
          Os dados são atualizados automaticamente através da sincronização com o Portal de Dados Abertos da CVM.
        </p>
      </Card>
    </div>
  );
}
