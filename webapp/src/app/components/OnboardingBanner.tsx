import { Card, CardContent } from './ui/card';
import { Button } from './ui/button';
import { X, Lightbulb, TrendingUp, DollarSign } from 'lucide-react';
import { useState } from 'react';

export function OnboardingBanner() {
  const [isVisible, setIsVisible] = useState(true);

  if (!isVisible) return null;

  return (
    <Card className="bg-gradient-to-r from-primary to-primary/80 text-primary-foreground border-none relative overflow-hidden max-w-7xl mx-auto">
      <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full -mr-32 -mt-32" />
      <div className="absolute bottom-0 left-0 w-48 h-48 bg-white/10 rounded-full -ml-24 -mb-24" />
      
      <CardContent className="p-6 relative">
        <Button
          variant="ghost"
          size="icon"
          className="absolute top-2 right-2 text-primary-foreground hover:bg-white/20"
          onClick={() => setIsVisible(false)}
        >
          <X className="size-4" />
        </Button>

        <div className="flex flex-col md:flex-row items-start md:items-center gap-6">
          <div className="bg-white/20 p-4 rounded-full">
            <Lightbulb className="size-8" />
          </div>

          <div className="flex-1 space-y-2">
            <h3 className="text-xl font-bold">Bem-vindo! Aqui você aprende a investir de forma fácil 👋</h3>
            <p className="text-primary-foreground/90">
              Mostramos quais empresas estão com preço bom para comprar hoje. 
              Quando você compra ações dessas empresas, elas te dão dinheiro todo mês! 
              É tipo ganhar mesada das empresas! 💰
            </p>
          </div>

          <div className="flex flex-col gap-2 min-w-[200px]">
            <Button variant="secondary" className="w-full">
              <TrendingUp className="size-4 mr-2" />
              Ver as Melhores
            </Button>
            <Button variant="outline" className="w-full bg-white/10 border-white/30 hover:bg-white/20 text-white">
              <DollarSign className="size-4 mr-2" />
              Calcular Ganhos
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6 pt-6 border-t border-white/20">
          <div className="space-y-1">
            <p className="text-sm font-medium">1️⃣ Olhe a Lista</p>
            <p className="text-xs text-primary-foreground/80">
              Veja quais ações estão baratas hoje
            </p>
          </div>
          <div className="space-y-1">
            <p className="text-sm font-medium">2️⃣ Entenda o Porquê</p>
            <p className="text-xs text-primary-foreground/80">
              Cada uma tem uma explicação fácil
            </p>
          </div>
          <div className="space-y-1">
            <p className="text-sm font-medium">3️⃣ Veja Quanto Ganha</p>
            <p className="text-xs text-primary-foreground/80">
              Descubra quanto dinheiro você vai receber
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}