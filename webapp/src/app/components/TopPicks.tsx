import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { CheckCircle2, ChevronRight, Star } from 'lucide-react';

interface Stock {
  ticker: string;
  companyName: string;
  sector: string;
  currentPrice: number;
  ceilingPrice: number;
  dividendYield: number;
  consistency: number;
  belowCeiling: boolean;
  discount?: number;
}

interface TopPicksProps {
  stocks: Stock[];
  onSelectStock: (stock: Stock) => void;
}

export function TopPicks({ stocks, onSelectStock }: TopPicksProps) {
  // Pegar as 5 melhores oportunidades (maior desconto abaixo do teto)
  const topStocks = stocks
    .filter(s => s.currentPrice > 0 && s.ceilingPrice > 0 && s.currentPrice < s.ceilingPrice)
    .sort((a, b) => {
      const discountA = ((a.ceilingPrice - a.currentPrice) / a.ceilingPrice) * 100;
      const discountB = ((b.ceilingPrice - b.currentPrice) / b.ceilingPrice) * 100;
      return discountB - discountA;
    })
    .slice(0, 5);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <CardTitle className="flex items-center gap-2">
              <Star className="size-5 text-yellow-500 fill-yellow-500" />
              As 5 Melhores Opções para Comprar Hoje
            </CardTitle>
            <CardDescription>
              Estas ações estão com preço mais barato que o ideal
            </CardDescription>
          </div>
          <Badge variant="secondary" className="bg-green-100 text-green-800">
            Atualizado Hoje
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {topStocks.map((stock, index) => {
            const savings = stock.ceilingPrice - stock.currentPrice;
            
            return (
              <div
                key={stock.ticker}
                className="flex items-center gap-4 p-4 bg-gradient-to-r from-green-50 to-transparent rounded-lg border-2 border-green-200 hover:border-green-300 transition-all cursor-pointer"
                onClick={() => onSelectStock(stock)}
              >
                {/* Número */}
                <div className="flex items-center justify-center w-10 h-10 bg-green-500 text-white rounded-full font-bold text-lg shrink-0">
                  {index + 1}
                </div>

                {/* Conteúdo Principal */}
                <div className="flex-1 min-w-0 space-y-2">
                  {/* Nome */}
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-lg">{stock.ticker}</span>
                      <span className="text-xs text-muted-foreground">Código da ação (sigla na Bolsa)</span>
                      <span className="text-sm text-muted-foreground">•</span>
                      <span className="text-sm text-muted-foreground truncate">{stock.companyName}</span>
                      <span className="text-sm text-muted-foreground">•</span>
                      <span className="text-sm text-muted-foreground">Segmento: {stock.sector}</span>
                    </div>
                  </div>

                  {/* O que fazer */}
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="size-4 text-green-600 shrink-0" />
                    <Badge className="bg-green-500">PODE COMPRAR</Badge>
                  </div>

                  {/* Por quê */}
                  <p className="text-sm text-muted-foreground">
                    💡 <strong>Por quê?</strong> Está R$ {savings.toFixed(2)} mais barata que o preço certo. 
                    Você economiza dinheiro comprando agora!
                  </p>

                  {/* Preços */}
                  <div className="flex items-center gap-4 text-sm">
                    <div>
                      <span className="text-muted-foreground">Preço Agora: </span>
                      <strong className="text-lg">R$ {stock.currentPrice.toFixed(2)}</strong>
                    </div>
                    <span className="text-muted-foreground">→</span>
                    <div>
                      <span className="text-muted-foreground">Preço Certo: </span>
                      <strong className="text-lg text-primary">R$ {stock.ceilingPrice.toFixed(2)}</strong>
                    </div>
                  </div>
                </div>

                {/* Botão */}
                <Button size="sm" variant="ghost" className="shrink-0">
                  Ver Detalhes
                  <ChevronRight className="size-4 ml-1" />
                </Button>
              </div>
            );
          })}
        </div>

        {topStocks.length === 0 && (
          <div className="text-center py-8 text-muted-foreground">
            <p>😔 Nenhuma ação está barata hoje.</p>
            <p className="text-sm mt-2">Continue olhando! Sempre aparecem boas oportunidades.</p>
          </div>
        )}

        <div className="mt-6 pt-6 border-t">
          <div className="bg-blue-50 p-4 rounded-lg">
            <h5 className="font-medium text-blue-900 mb-2">🎓 Dica para Iniciantes</h5>
            <p className="text-sm text-blue-800">
              Não precisa comprar todas! Escolha uma ou duas empresas que você conhece 
              (tipo banco que sua família usa, ou empresa de luz da sua cidade). 
              Compre um pouquinho todo mês quando estiver barato.
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}