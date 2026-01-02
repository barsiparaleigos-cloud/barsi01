import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { CheckCircle2, Clock, Info, ChevronRight } from 'lucide-react';

interface StockCardProps {
  ticker: string;
  companyName: string;
  sector: string;
  currentPrice: number;
  ceilingPrice: number;
  dividendYield: number;
  consistency: number;
  belowCeiling: boolean;
  onClick?: () => void;
}

export function StockCard({
  ticker,
  companyName,
  sector,
  currentPrice,
  ceilingPrice,
  dividendYield,
  consistency,
  belowCeiling,
  onClick
}: StockCardProps) {
  const discount = ((ceilingPrice - currentPrice) / ceilingPrice) * 100;

  const sectorColors: Record<string, string> = {
    'Bancos': 'bg-blue-100 text-blue-800',
    'Energia': 'bg-yellow-100 text-yellow-800',
    'Saneamento': 'bg-cyan-100 text-cyan-800',
    'Seguros': 'bg-purple-100 text-purple-800',
    'Telecomunicações': 'bg-green-100 text-green-800'
  };

  // Mensagem ULTRA simples para criança
  const getWhatToDo = () => {
    const hasEnoughData = currentPrice > 0 && ceilingPrice > 0;
    if (!hasEnoughData) {
      return {
        action: 'SEM DADOS',
        icon: Info,
        color: 'bg-blue-500',
        textColor: 'text-blue-700',
        bgColor: 'bg-blue-50',
        borderColor: 'border-blue-200'
      };
    }

    if (belowCeiling) {
      return {
        action: 'PODE COMPRAR',
        icon: CheckCircle2,
        color: 'bg-green-500',
        textColor: 'text-green-700',
        bgColor: 'bg-green-50',
        borderColor: 'border-green-200'
      };
    } else {
      return {
        action: 'ESPERE',
        icon: Clock,
        color: 'bg-yellow-500',
        textColor: 'text-yellow-700',
        bgColor: 'bg-yellow-50',
        borderColor: 'border-yellow-200'
      };
    }
  };

  const getSimpleReason = () => {
    const hasEnoughData = currentPrice > 0 && ceilingPrice > 0;
    if (!hasEnoughData) {
      return 'Ainda não temos preço suficiente para comparar com o preço certo.';
    }

    if (belowCeiling) {
      return `Está R$ ${(ceilingPrice - currentPrice).toFixed(2)} mais barata que o preço certo. Boa hora para comprar!`;
    } else {
      return `Está R$ ${(currentPrice - ceilingPrice).toFixed(2)} mais cara que o preço certo. Melhor esperar baixar.`;
    }
  };

  const whatToDo = getWhatToDo();
  const Icon = whatToDo.icon;

  return (
    <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={onClick}>
      <CardHeader className="pb-4">
        <div className="flex items-start justify-between mb-3">
          <div className="space-y-1">
            <CardTitle className="text-xl flex items-baseline gap-2">
              <span>{ticker}</span>
              <span className="text-xs font-normal text-muted-foreground">Código da ação (sigla na Bolsa)</span>
            </CardTitle>
            <p className="text-sm text-muted-foreground">{companyName}</p>
            <p className="text-xs text-muted-foreground">Segmento: {sector}</p>
          </div>
          <Badge className={sectorColors[sector] || 'bg-gray-100 text-gray-800'} variant="secondary">
            Segmento: {sector}
          </Badge>
        </div>

        {/* O QUE FAZER */}
        <div className={`flex items-center gap-2 p-3 rounded-lg ${whatToDo.bgColor} border-2 ${whatToDo.borderColor}`}>
          <div className={`${whatToDo.color} text-white p-1.5 rounded-md`}>
            <Icon className="size-5" />
          </div>
          <span className={`font-bold ${whatToDo.textColor}`}>
            {whatToDo.action}
          </span>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* POR QUÊ */}
        <div className="space-y-1">
          <p className="text-xs font-medium text-muted-foreground uppercase">Por quê?</p>
          <p className="text-sm">
            {getSimpleReason()}
          </p>
        </div>

        {/* PREÇOS */}
        <div className="grid grid-cols-2 gap-3">
          <div className="p-3 bg-muted/50 rounded-lg space-y-1">
            <p className="text-xs text-muted-foreground">Preço Agora</p>
            <p className="text-xl font-bold">R$ {currentPrice.toFixed(2)}</p>
          </div>

          <div className="p-3 bg-primary/5 rounded-lg space-y-1">
            <p className="text-xs text-muted-foreground">Preço Certo</p>
            <p className="text-xl font-bold text-primary">R$ {ceilingPrice.toFixed(2)}</p>
          </div>
        </div>

        {/* Info Extra Simples */}
        <div className="bg-blue-50 p-3 rounded-lg text-sm">
          <p className="text-blue-900">
            💰 Se você comprar 10 ações por <strong>R$ {(currentPrice * 10).toFixed(2)}</strong>,
            vai receber cerca de <strong>R$ {((currentPrice * 10 * dividendYield) / 100).toFixed(2)}</strong> por
            ano em dinheiro na sua conta.
          </p>
        </div>

        {/* Ações */}
        <Button size="sm" className="w-full" variant="outline">
          Ver Mais Detalhes
          <ChevronRight className="size-4 ml-1" />
        </Button>
      </CardContent>
    </Card>
  );
}