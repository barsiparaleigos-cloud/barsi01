import { useEffect, useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { Settings } from './components/Settings';
import { CompanyList } from './components/CompanyList';
import { StatsCard } from './components/StatsCard';
import { StockCard } from './components/StockCard';
import { IncomeSimulator } from './components/IncomeSimulator';
import { MethodologyExplainer } from './components/MethodologyExplainer';
import { StockDetailModal } from './components/StockDetailModal';
import { OnboardingBanner } from './components/OnboardingBanner';
import { QuickActions } from './components/QuickActions';
import { SimpleExplainer } from './components/SimpleExplainer';
import { TopPicks } from './components/TopPicks';
import { Button } from './components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Input } from './components/ui/input';
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from './components/ui/select';
import { 
  TrendingUp, 
  DollarSign, 
  Target, 
  Filter,
  Search,
  Building2,
  Zap,
  Droplet,
  Shield,
  Radio
} from 'lucide-react';
import DataSourceIntegrations from '../features/admin/integrations/DataSourceIntegrations';

interface Stock {
  ticker: string;
  companyName: string;
  sector: string;
  currentPrice: number;
  ceilingPrice: number;
  dividendYield: number;
  consistency: number;
  belowCeiling: boolean;
}

export default function App() {
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [loadingStocks, setLoadingStocks] = useState(true);
  const [stocksError, setStocksError] = useState<string | null>(null);

  const [selectedStock, setSelectedStock] = useState<Stock | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [sectorFilter, setSectorFilter] = useState('all');
  const [activeTab, setActiveTab] = useState('ranking');
  const [activeView, setActiveView] = useState('ranking'); // sidebar navigation

  // Sincroniza activeTab quando navega via sidebar
  const handleNavigate = (view: string) => {
    setActiveView(view);
    if (['ranking', 'simulator', 'learn', 'home', 'empresas'].includes(view)) {
      setActiveTab(view);
    }
  };

  useEffect(() => {
    let cancelled = false;

    const loadStocks = async () => {
      try {
        setLoadingStocks(true);
        setStocksError(null);

        const res = await fetch('/api/stocks');
        if (!res.ok) throw new Error(`HTTP ${res.status}`);

        const data = await res.json();
        if (!Array.isArray(data)) throw new Error('Formato inválido');

        if (!cancelled) setStocks(data as Stock[]);
      } catch {
        if (!cancelled) {
          setStocks([]);
          setStocksError('Não foi possível carregar as ações agora.');
        }
      } finally {
        if (!cancelled) setLoadingStocks(false);
      }
    };

    loadStocks();
    return () => {
      cancelled = true;
    };
  }, []);

  // Filtrar ações
  const filteredStocks = stocks.filter((stock) => {
    const matchesSearch = stock.ticker.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         stock.companyName.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesSector = sectorFilter === 'all' || stock.sector === sectorFilter;
    return matchesSearch && matchesSector;
  });

  const belowCeilingCount = stocks.filter(s => s.belowCeiling).length;
  const avgDividendYield = stocks.length
    ? (stocks.reduce((acc, s) => acc + s.dividendYield, 0) / stocks.length).toFixed(1)
    : '0.0';

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <Sidebar activeView={activeView} onNavigate={handleNavigate} />

      <main className="pl-16 md:pl-64 pr-4 py-8 space-y-8 transition-all">
        {/* Onboarding Banner */}
        <OnboardingBanner />

        {/* Hero Section */}
        <section className="text-center space-y-4 py-8 max-w-7xl mx-auto">
          <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
            Invista como Luiz Barsi
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Descubra as melhores ações de dividendos seguindo a metodologia do maior investidor 
            de renda passiva do Brasil
          </p>
        </section>

        {/* Quick Actions */}
        <QuickActions onNavigate={handleNavigate} />

        {/* Stats Cards */}
        <section className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-7xl mx-auto">
          <StatsCard
            title="Ações Abaixo do Teto"
            value={belowCeilingCount.toString()}
            subtitle={`De ${stocks.length} analisadas`}
            icon={Target}
            trend="up"
          />
          <StatsCard
            title="Dividend Yield Médio"
            value={`${avgDividendYield}%`}
            subtitle="Acima do mínimo de 6%"
            icon={DollarSign}
            trend="up"
          />
          <StatsCard
            title="Setores BESST"
            value="5"
            subtitle="Setores à prova de balas"
            icon={TrendingUp}
            trend="neutral"
          />
        </section>

        {/* Main Content - Renderizado condicionalmente */}
        {activeView === 'integrations' && (
          <DataSourceIntegrations />
        )}

        {activeView === 'settings' && (
          <Settings />
        )}

        {activeView === 'empresas' && (
          <CompanyList />
        )}

        {['ranking', 'simulator', 'learn', 'home'].includes(activeView) && (
        <Tabs value={activeTab} onValueChange={(tab) => { setActiveTab(tab); setActiveView(tab); }} className="space-y-6">
          <TabsList className="grid w-full grid-cols-3 lg:w-auto">
            <TabsTrigger value="ranking">🏆 Ranking de Ações</TabsTrigger>
            <TabsTrigger value="simulator">📊 Simulador de Renda</TabsTrigger>
            <TabsTrigger value="learn">📚 Aprenda a Metodologia</TabsTrigger>
          </TabsList>

          {/* Ranking Tab */}
          <TabsContent value="ranking" className="space-y-6">
            {/* Top Picks */}
            <TopPicks stocks={stocks} onSelectStock={(stock) => setSelectedStock(stock)} />

            {/* Simple Explainer */}
            <SimpleExplainer />

            {/* Filtros */}
            <div className="bg-white p-4 rounded-lg border shadow-sm space-y-4">
              <div className="flex items-center gap-2 text-primary">
                <Filter className="size-5" />
                <h3 className="font-medium">Filtrar Todas as Ações</h3>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="relative md:col-span-2">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
                  <Input
                    placeholder="Buscar por ticker ou nome da empresa..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>

                <Select value={sectorFilter} onValueChange={setSectorFilter}>
                  <SelectTrigger>
                    <SelectValue placeholder="Todos os setores" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todos os setores</SelectItem>
                    <SelectItem value="Bancos">
                      <div className="flex items-center gap-2">
                        <Building2 className="size-4" />
                        Bancos
                      </div>
                    </SelectItem>
                    <SelectItem value="Energia">
                      <div className="flex items-center gap-2">
                        <Zap className="size-4" />
                        Energia
                      </div>
                    </SelectItem>
                    <SelectItem value="Saneamento">
                      <div className="flex items-center gap-2">
                        <Droplet className="size-4" />
                        Saneamento
                      </div>
                    </SelectItem>
                    <SelectItem value="Seguros">
                      <div className="flex items-center gap-2">
                        <Shield className="size-4" />
                        Seguros
                      </div>
                    </SelectItem>
                    <SelectItem value="Telecomunicações">
                      <div className="flex items-center gap-2">
                        <Radio className="size-4" />
                        Telecomunicações
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex flex-wrap gap-2">
                <Button 
                  variant={sectorFilter === 'all' ? 'default' : 'outline'} 
                  size="sm"
                  onClick={() => setSectorFilter('all')}
                >
                  Todos
                </Button>
                {['Bancos', 'Energia', 'Saneamento', 'Seguros', 'Telecomunicações'].map((sector) => (
                  <Button
                    key={sector}
                    variant={sectorFilter === sector ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setSectorFilter(sector)}
                  >
                    {sector}
                  </Button>
                ))}
              </div>
            </div>

            {/* Lista de Ações */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h2>
                  {filteredStocks.length} {filteredStocks.length === 1 ? 'ação encontrada' : 'ações encontradas'}
                </h2>
                <p className="text-sm text-muted-foreground">
                  {filteredStocks.filter(s => s.belowCeiling).length} abaixo do preço teto
                </p>
              </div>

              {loadingStocks && (
                <p className="text-sm text-muted-foreground mb-4">Carregando ações…</p>
              )}

              {!loadingStocks && stocksError && (
                <p className="text-sm text-muted-foreground mb-4">{stocksError}</p>
              )}

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredStocks.map((stock) => (
                  <StockCard
                    key={stock.ticker}
                    {...stock}
                    onClick={() => setSelectedStock(stock)}
                  />
                ))}
              </div>

              {filteredStocks.length === 0 && (
                <div className="text-center py-12">
                  <p className="text-muted-foreground">
                    Nenhuma ação encontrada com os filtros selecionados
                  </p>
                  <Button 
                    variant="outline" 
                    className="mt-4"
                    onClick={() => {
                      setSearchTerm('');
                      setSectorFilter('all');
                    }}
                  >
                    Limpar Filtros
                  </Button>
                </div>
              )}
            </div>
          </TabsContent>

          {/* Simulator Tab */}
          <TabsContent value="simulator">
            <IncomeSimulator />
          </TabsContent>

          {/* Learn Tab */}
          <TabsContent value="learn">
            <MethodologyExplainer />

          {/* Admin Tab */}
          <TabsContent value="admin">
            <DataSourceIntegrations />
          </TabsContent>
          </TabsContent>
        </Tabs>
        )}

        {/* Disclaimer */}
        <section className="bg-yellow-50 border border-yellow-200 p-6 rounded-lg">
          <h4 className="font-medium text-yellow-900 mb-2">⚠️ Aviso Importante</h4>
          <p className="text-sm text-yellow-800">
            Este sistema é uma ferramenta educacional baseada na metodologia pública de Luiz Barsi. 
            <strong> NÃO é uma recomendação de investimento.</strong> Todo investimento envolve riscos. 
            Consulte um profissional certificado e faça sua própria análise antes de investir. 
            Rentabilidade passada não garante resultados futuros.
          </p>
        </section>
      </main>

      {/* Stock Detail Modal */}
      {selectedStock && (
        <StockDetailModal
          open={!!selectedStock}
          onOpenChange={(open) => !open && setSelectedStock(null)}
          stock={selectedStock}
        />
      )}
    </div>
  );
}