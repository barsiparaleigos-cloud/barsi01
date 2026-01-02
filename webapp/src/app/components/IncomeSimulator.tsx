import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Label } from './ui/label';
import { Input } from './ui/input';
import { Slider } from './ui/slider';
import { Button } from './ui/button';
import { TrendingUp, DollarSign, Calendar } from 'lucide-react';

export function IncomeSimulator() {
  const [initialInvestment, setInitialInvestment] = useState(10000);
  const [monthlyContribution, setMonthlyContribution] = useState(500);
  const [avgDividendYield, setAvgDividendYield] = useState(6);
  const [years, setYears] = useState(10);

  // Cálculo simplificado
  const calculateProjection = () => {
    let total = initialInvestment;
    let monthlyIncome = 0;
    
    for (let year = 1; year <= years; year++) {
      // Adiciona contribuições mensais
      total += monthlyContribution * 12;
      
      // Calcula dividendos anuais e reinveste
      const yearlyDividends = total * (avgDividendYield / 100);
      total += yearlyDividends;
    }
    
    monthlyIncome = (total * (avgDividendYield / 100)) / 12;
    
    return {
      finalValue: total,
      monthlyIncome: monthlyIncome,
      totalDividends: total - initialInvestment - (monthlyContribution * 12 * years)
    };
  };

  const projection = calculateProjection();

  return (
    <Card>
      <CardHeader>
        <CardTitle>Simulador de Renda Passiva</CardTitle>
        <CardDescription>
          Veja quanto você pode ganhar seguindo a metodologia Barsi
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Inputs */}
        <div className="grid md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <Label>Investimento Inicial</Label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">
                R$
              </span>
              <Input
                type="number"
                value={initialInvestment}
                onChange={(e) => setInitialInvestment(Number(e.target.value))}
                className="pl-10"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label>Aporte Mensal</Label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">
                R$
              </span>
              <Input
                type="number"
                value={monthlyContribution}
                onChange={(e) => setMonthlyContribution(Number(e.target.value))}
                className="pl-10"
              />
            </div>
          </div>

          <div className="space-y-3">
            <Label>Dividend Yield Médio: {avgDividendYield}%</Label>
            <Slider
              value={[avgDividendYield]}
              onValueChange={(value) => setAvgDividendYield(value[0])}
              min={3}
              max={12}
              step={0.5}
              className="w-full"
            />
            <p className="text-xs text-muted-foreground">
              Barsi recomenda mínimo de 6% ao ano
            </p>
          </div>

          <div className="space-y-3">
            <Label>Período: {years} anos</Label>
            <Slider
              value={[years]}
              onValueChange={(value) => setYears(value[0])}
              min={1}
              max={30}
              step={1}
              className="w-full"
            />
            <p className="text-xs text-muted-foreground">
              Quanto mais tempo, melhor o efeito bola de neve
            </p>
          </div>
        </div>

        {/* Resultados */}
        <div className="grid md:grid-cols-3 gap-4 pt-4">
          <div className="bg-primary/5 p-4 rounded-lg space-y-1">
            <div className="flex items-center gap-2 text-muted-foreground">
              <DollarSign className="size-4" />
              <p className="text-sm">Patrimônio Final</p>
            </div>
            <p className="text-2xl font-bold text-primary">
              R$ {projection.finalValue.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
            </p>
          </div>

          <div className="bg-green-50 p-4 rounded-lg space-y-1">
            <div className="flex items-center gap-2 text-muted-foreground">
              <TrendingUp className="size-4" />
              <p className="text-sm">Renda Mensal</p>
            </div>
            <p className="text-2xl font-bold text-green-600">
              R$ {projection.monthlyIncome.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
            </p>
          </div>

          <div className="bg-blue-50 p-4 rounded-lg space-y-1">
            <div className="flex items-center gap-2 text-muted-foreground">
              <Calendar className="size-4" />
              <p className="text-sm">Total em Dividendos</p>
            </div>
            <p className="text-2xl font-bold text-blue-600">
              R$ {projection.totalDividends.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
            </p>
          </div>
        </div>

        {/* Explicação */}
        <div className="bg-muted/50 p-4 rounded-lg space-y-2">
          <h4 className="font-medium">Como funciona?</h4>
          <p className="text-sm text-muted-foreground">
            Esta simulação mostra o poder do <strong>reinvestimento de dividendos</strong>. 
            Ao comprar ações que pagam bons dividendos e usar esse dinheiro para comprar mais 
            ações, você cria um efeito "bola de neve" que acelera o crescimento do seu patrimônio.
          </p>
          <p className="text-sm text-muted-foreground">
            Em {years} anos, você terá uma renda passiva mensal de{' '}
            <strong className="text-green-600">
              R$ {projection.monthlyIncome.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
            </strong>{' '}
            sem vender nenhuma ação!
          </p>
        </div>

        <Button className="w-full" size="lg">
          Começar a Investir Agora
        </Button>
      </CardContent>
    </Card>
  );
}
