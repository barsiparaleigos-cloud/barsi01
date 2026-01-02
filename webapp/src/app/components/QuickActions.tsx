import { Card, CardContent } from './ui/card';
import { Button } from './ui/button';
import { 
  Sparkles, 
  Calculator, 
  BookOpen, 
  TrendingUp,
  ArrowRight 
} from 'lucide-react';

interface QuickActionProps {
  onNavigate: (tab: string) => void;
}

export function QuickActions({ onNavigate }: QuickActionProps) {
  const actions = [
    {
      icon: Sparkles,
      title: 'Ver Oportunidades',
      description: 'Ações abaixo do preço ideal',
      color: 'bg-green-50 text-green-600 hover:bg-green-100',
      action: () => onNavigate('ranking')
    },
    {
      icon: Calculator,
      title: 'Simular Renda',
      description: 'Quanto posso ganhar?',
      color: 'bg-blue-50 text-blue-600 hover:bg-blue-100',
      action: () => onNavigate('simulator')
    },
    {
      icon: BookOpen,
      title: 'Aprender Método',
      description: 'Como funciona a metodologia',
      color: 'bg-purple-50 text-purple-600 hover:bg-purple-100',
      action: () => onNavigate('learn')
    },
    {
      icon: TrendingUp,
      title: 'Melhores do Mês',
      description: 'Top 5 recomendações',
      color: 'bg-orange-50 text-orange-600 hover:bg-orange-100',
      action: () => onNavigate('ranking')
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {actions.map((action) => {
        const Icon = action.icon;
        return (
          <Card 
            key={action.title}
            className="cursor-pointer hover:shadow-lg transition-all hover:-translate-y-1"
            onClick={action.action}
          >
            <CardContent className="p-6 space-y-3">
              <div className={`w-12 h-12 rounded-lg ${action.color} flex items-center justify-center transition-colors`}>
                <Icon className="size-6" />
              </div>
              <div className="space-y-1">
                <h4 className="font-medium">{action.title}</h4>
                <p className="text-sm text-muted-foreground">{action.description}</p>
              </div>
              <Button variant="ghost" size="sm" className="w-full justify-between group">
                Acessar
                <ArrowRight className="size-4 group-hover:translate-x-1 transition-transform" />
              </Button>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
