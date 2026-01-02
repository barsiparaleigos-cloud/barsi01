import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from './ui/dialog';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Card, CardContent } from './ui/card';
import { TrendingUp, TrendingDown, Calendar, DollarSign, Building, ExternalLink } from 'lucide-react';
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface StockDetailModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  stock: {
    ticker: string;
    companyName: string;
    sector: string;
    currentPrice: number;
    ceilingPrice: number;
    dividendYield: number;
    consistency: number;
    belowCeiling: boolean;
  };
}

// Dados mock para os gráficos
const dividendHistory = [
  { month: 'Jan/24', value: 0.45 },
  { month: 'Fev/24', value: 0.52 },
  { month: 'Mar/24', value: 0.48 },
  { month: 'Abr/24', value: 0.51 },
  { month: 'Mai/24', value: 0.49 },
  { month: 'Jun/24', value: 0.53 },
  { month: 'Jul/24', value: 0.50 },
  { month: 'Ago/24', value: 0.54 },
  { month: 'Set/24', value: 0.52 },
  { month: 'Out/24', value: 0.55 },
  { month: 'Nov/24', value: 0.53 },
  { month: 'Dez/24', value: 0.56 },
];

const priceHistory = [
  { month: 'Jul/24', price: 28.5 },
  { month: 'Ago/24', price: 29.2 },
  { month: 'Set/24', price: 27.8 },
  { month: 'Out/24', price: 28.9 },
  { month: 'Nov/24', price: 30.1 },
  { month: 'Dez/24', price: 29.5 },
];

const fundamentals = [
  { label: 'P/L (Preço/Lucro)', value: '8.5x', status: 'good' },
  { label: 'P/VP (Preço/Valor Patrimonial)', value: '1.2x', status: 'good' },
  { label: 'ROE (Retorno sobre Patrimônio)', value: '15.3%', status: 'good' },
  { label: 'Margem Líquida', value: '18.7%', status: 'good' },
  { label: 'Payout Ratio', value: '45%', status: 'good' },
  { label: 'Dívida/EBITDA', value: '2.1x', status: 'neutral' },
];

export function StockDetailModal({ open, onOpenChange, stock }: StockDetailModalProps) {
  const discount = ((stock.ceilingPrice - stock.currentPrice) / stock.ceilingPrice) * 100;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-start justify-between">
            <div>
              <DialogTitle className="text-2xl flex items-baseline gap-2">
                <span>{stock.ticker}</span>
                <span className="text-sm font-normal text-muted-foreground">Código da ação (sigla na Bolsa)</span>
              </DialogTitle>
              <DialogDescription className="text-base mt-1">
                {stock.companyName}
              </DialogDescription>
              <p className="text-sm text-muted-foreground mt-1">Segmento: {stock.sector}</p>
            </div>
            <Badge variant="secondary" className="bg-blue-100 text-blue-800">
              Segmento: {stock.sector}
            </Badge>
          </div>
        </DialogHeader>

        {/* Visão Geral */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4 space-y-1">
              <p className="text-xs text-muted-foreground">Preço Atual</p>
              <p className="text-xl font-bold">R$ {stock.currentPrice.toFixed(2)}</p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4 space-y-1">
              <p className="text-xs text-muted-foreground">Preço Teto</p>
              <p className="text-xl font-bold text-primary">R$ {stock.ceilingPrice.toFixed(2)}</p>
            </CardContent>
          </Card>

          <Card className={stock.belowCeiling ? 'bg-green-50' : 'bg-red-50'}>
            <CardContent className="p-4 space-y-1">
              <p className="text-xs text-muted-foreground">Desconto/Prêmio</p>
              <div className="flex items-center gap-1">
                {stock.belowCeiling ? (
                  <TrendingDown className="size-4 text-green-600" />
                ) : (
                  <TrendingUp className="size-4 text-red-600" />
                )}
                <p className={`text-xl font-bold ${stock.belowCeiling ? 'text-green-600' : 'text-red-600'}`}>
                  {Math.abs(discount).toFixed(1)}%
                </p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4 space-y-1">
              <p className="text-xs text-muted-foreground">Dividend Yield</p>
              <p className="text-xl font-bold text-primary">{stock.dividendYield.toFixed(2)}%</p>
            </CardContent>
          </Card>
        </div>

        {/* Recomendação */}
        <Card className={stock.belowCeiling ? 'bg-green-50 border-green-200' : 'bg-yellow-50 border-yellow-200'}>
          <CardContent className="p-4">
            <h4 className="font-medium mb-2">
              {stock.belowCeiling ? '✅ Oportunidade de Compra' : '⚠️ Aguardar Correção'}
            </h4>
            <p className="text-sm text-muted-foreground">
              {stock.belowCeiling ? (
                <>
                  Esta ação está <strong className="text-green-700">{discount.toFixed(1)}% abaixo do preço teto</strong>, 
                  o que significa que ela está oferecendo um retorno em dividendos acima dos 6% mínimos recomendados 
                  por esta metodologia. Este é um bom momento para considerar a compra segundo a metodologia.
                </>
              ) : (
                <>
                  Esta ação está <strong className="text-red-700">{Math.abs(discount).toFixed(1)}% acima do preço teto</strong>. 
                  Segundo a metodologia, o ideal é aguardar uma correção de preço antes de comprar, 
                  para garantir um dividend yield de no mínimo 6% ao ano.
                </>
              )}
            </p>
          </CardContent>
        </Card>

        {/* Tabs com Informações Detalhadas */}
        <Tabs defaultValue="dividends" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="dividends">
              <DollarSign className="size-4 mr-2" />
              Dividendos
            </TabsTrigger>
            <TabsTrigger value="fundamentals">
              <Building className="size-4 mr-2" />
              Fundamentos
            </TabsTrigger>
            <TabsTrigger value="history">
              <Calendar className="size-4 mr-2" />
              Histórico
            </TabsTrigger>
          </TabsList>

          <TabsContent value="dividends" className="space-y-4">
            <Card>
              <CardContent className="p-4">
                <h4 className="font-medium mb-4">Histórico de Dividendos (12 meses)</h4>
                <ResponsiveContainer width="100%" height={250}>
                  <AreaChart data={dividendHistory}>
                    <defs>
                      <linearGradient id="colorDividend" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" fontSize={12} />
                    <YAxis fontSize={12} />
                    <Tooltip />
                    <Area 
                      type="monotone" 
                      dataKey="value" 
                      stroke="#10b981" 
                      fillOpacity={1} 
                      fill="url(#colorDividend)" 
                    />
                  </AreaChart>
                </ResponsiveContainer>

                <div className="grid grid-cols-3 gap-4 mt-4 pt-4 border-t">
                  <div>
                    <p className="text-xs text-muted-foreground">DPA Médio (12m)</p>
                    <p className="font-bold">R$ 0.51</p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">Total Pago (12m)</p>
                    <p className="font-bold text-green-600">R$ 6.12</p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">Consistência</p>
                    <p className="font-bold">{stock.consistency}%</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg">
              <h5 className="font-medium text-blue-900 mb-2">💡 O que isso significa?</h5>
              <p className="text-sm text-muted-foreground">
                Esta empresa tem um histórico <strong>consistente</strong> de pagamento de dividendos. 
                Se você comprar 100 ações a R$ {stock.currentPrice.toFixed(2)}, investindo{' '}
                <strong>R$ {(stock.currentPrice * 100).toFixed(2)}</strong>, você receberá cerca de{' '}
                <strong className="text-green-700">R$ {((stock.currentPrice * 100) * (stock.dividendYield / 100)).toFixed(2)}</strong>{' '}
                por ano em dividendos.
              </p>
            </div>
          </TabsContent>

          <TabsContent value="fundamentals" className="space-y-4">
            <Card>
              <CardContent className="p-4">
                <h4 className="font-medium mb-4">Indicadores Fundamentalistas</h4>
                <div className="grid md:grid-cols-2 gap-4">
                  {fundamentals.map((item) => (
                    <div key={item.label} className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                      <span className="text-sm text-muted-foreground">{item.label}</span>
                      <span className="font-bold">{item.value}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <div className="bg-purple-50 border border-purple-200 p-4 rounded-lg">
              <h5 className="font-medium text-purple-900 mb-2">📊 Análise Resumida</h5>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>✓ <strong>P/L abaixo de 10:</strong> A empresa está com preço atrativo em relação ao lucro</li>
                <li>✓ <strong>ROE acima de 15%:</strong> Boa rentabilidade sobre o patrimônio</li>
                <li>✓ <strong>Payout de 45%:</strong> Distribui quase metade do lucro, guardando o resto para crescer</li>
                <li>✓ <strong>Margem líquida saudável:</strong> A empresa é lucrativa e eficiente</li>
              </ul>
            </div>
          </TabsContent>

          <TabsContent value="history" className="space-y-4">
            <Card>
              <CardContent className="p-4">
                <h4 className="font-medium mb-4">Evolução de Preço (6 meses)</h4>
                <ResponsiveContainer width="100%" height={250}>
                  <LineChart data={priceHistory}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" fontSize={12} />
                    <YAxis fontSize={12} />
                    <Tooltip />
                    <Line 
                      type="monotone" 
                      dataKey="price" 
                      stroke="#030213" 
                      strokeWidth={2}
                      dot={{ fill: '#030213', r: 4 }}
                    />
                  </LineChart>
                </ResponsiveContainer>

                <div className="grid grid-cols-4 gap-4 mt-4 pt-4 border-t">
                  <div>
                    <p className="text-xs text-muted-foreground">Mínima 52s</p>
                    <p className="font-bold text-red-600">R$ 27.50</p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">Máxima 52s</p>
                    <p className="font-bold text-green-600">R$ 32.80</p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">Média 52s</p>
                    <p className="font-bold">R$ 29.87</p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">Volatilidade</p>
                    <p className="font-bold">Baixa</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Ações */}
        <div className="flex gap-2 pt-4">
          <Button variant="outline" className="flex-1">
            <ExternalLink className="size-4 mr-2" />
            Ver no RI da Empresa
          </Button>
          <Button className="flex-1">
            Adicionar à Lista de Acompanhamento
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
