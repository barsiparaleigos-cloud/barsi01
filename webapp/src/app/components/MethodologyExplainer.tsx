import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Building2, Zap, Droplet, Shield, Radio, Target, TrendingUp, Clock } from 'lucide-react';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from './ui/accordion';

const sectors = [
  {
    name: 'Bancos',
    icon: Building2,
    color: 'bg-blue-100 text-blue-800',
    description: 'Instituições financeiras essenciais com alta rentabilidade e histórico de dividendos.',
    examples: ['Itaú', 'Bradesco', 'Santander']
  },
  {
    name: 'Energia',
    icon: Zap,
    color: 'bg-yellow-100 text-yellow-800',
    description: 'Transmissão e distribuição de energia com receitas reguladas e contratos longos.',
    examples: ['Taesa', 'Copel', 'Eletrobras']
  },
  {
    name: 'Saneamento',
    icon: Droplet,
    color: 'bg-cyan-100 text-cyan-800',
    description: 'Serviços básicos indispensáveis com baixa concorrência e fluxo previsível.',
    examples: ['Sabesp', 'Copasa', 'Sanepar']
  },
  {
    name: 'Seguros',
    icon: Shield,
    color: 'bg-purple-100 text-purple-800',
    description: 'Modelo de negócio baseado em "float" com alta recorrência de receitas.',
    examples: ['BB Seguridade', 'Porto Seguro', 'SulAmérica']
  },
  {
    name: 'Telecomunicações',
    icon: Radio,
    color: 'bg-green-100 text-green-800',
    description: 'Infraestrutura crítica com demanda resiliente e base de clientes estável.',
    examples: ['Telefônica', 'Tim', 'Vivo']
  }
];

export function MethodologyExplainer() {
  return (
    <div className="space-y-6">
      {/* Hero */}
      <Card className="bg-gradient-to-br from-primary/5 to-primary/10 border-primary/20">
        <CardHeader className="text-center pb-3">
          <CardTitle className="text-2xl">A Metodologia de Dividendos</CardTitle>
          <CardDescription className="text-base">
            Aprenda a investir como um dos maiores investidores de dividendos do Brasil
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-3 gap-4">
            <div className="bg-white/80 p-4 rounded-lg space-y-2 text-center">
              <div className="bg-primary/10 size-12 rounded-full flex items-center justify-center mx-auto">
                <TrendingUp className="size-6 text-primary" />
              </div>
              <h4 className="font-medium">Renda Passiva</h4>
              <p className="text-sm text-muted-foreground">
                Foco em dividendos para criar uma aposentadoria tranquila
              </p>
            </div>

            <div className="bg-white/80 p-4 rounded-lg space-y-2 text-center">
              <div className="bg-primary/10 size-12 rounded-full flex items-center justify-center mx-auto">
                <Clock className="size-6 text-primary" />
              </div>
              <h4 className="font-medium">Longo Prazo</h4>
              <p className="text-sm text-muted-foreground">
                Compre e mantenha por décadas, vendendo apenas se deteriorar
              </p>
            </div>

            <div className="bg-white/80 p-4 rounded-lg space-y-2 text-center">
              <div className="bg-primary/10 size-12 rounded-full flex items-center justify-center mx-auto">
                <Target className="size-6 text-primary" />
              </div>
              <h4 className="font-medium">Preço Disciplinado</h4>
              <p className="text-sm text-muted-foreground">
                Só compre quando o preço garantir no mínimo 6% de retorno
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* BESST Sectors */}
      <Card>
        <CardHeader>
          <CardTitle>Setores BESST: Onde Investir</CardTitle>
          <CardDescription>
            A metodologia concentra o foco em 5 setores "à prova de balas"
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {sectors.map((sector) => {
              const Icon = sector.icon;
              return (
                <Card key={sector.name} className="border-2 hover:border-primary/50 transition-colors">
                  <CardContent className="p-4 space-y-3">
                    <div className="flex items-center gap-3">
                      <div className={`p-2 rounded-lg ${sector.color}`}>
                        <Icon className="size-5" />
                      </div>
                      <h4 className="font-bold">{sector.name}</h4>
                    </div>
                    <p className="text-sm text-muted-foreground">{sector.description}</p>
                    <div className="flex flex-wrap gap-1">
                      {sector.examples.map((example) => (
                        <Badge key={example} variant="secondary" className="text-xs">
                          {example}
                        </Badge>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Regra dos 6% */}
      <Card>
        <CardHeader>
          <CardTitle>A Regra dos 6% e o Preço-Teto</CardTitle>
          <CardDescription>
            O coração da metodologia: só compre se o retorno em dividendos for no mínimo 6%
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="bg-primary/5 p-6 rounded-lg space-y-4">
            <div className="space-y-2">
              <h4 className="font-medium">Como calcular o Preço-Teto?</h4>
              <div className="bg-white p-4 rounded-lg border-2 border-primary/20">
                <p className="text-center font-mono text-lg">
                  Preço-Teto = <span className="text-primary font-bold">DPA médio</span> ÷ <span className="text-primary font-bold">0,06</span>
                </p>
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <h5 className="text-sm font-medium">DPA (Dividendo por Ação)</h5>
                <p className="text-sm text-muted-foreground">
                  É quanto a empresa pagou de dividendos por cada ação nos últimos anos. 
                  Calculamos a média dos últimos 5 anos para ter um número confiável.
                </p>
              </div>

              <div className="space-y-2">
                <h5 className="text-sm font-medium">Por que 6%?</h5>
                <p className="text-sm text-muted-foreground">
                  É o retorno mínimo que consideramos aceitável. Abaixo disso, não 
                  vale a pena o risco. Quanto maior o DY, melhor!
                </p>
              </div>
            </div>
          </div>

          {/* Exemplo Prático */}
          <div className="bg-green-50 border-2 border-green-200 p-4 rounded-lg space-y-3">
            <h4 className="font-medium text-green-900">📚 Exemplo Prático</h4>
            <div className="space-y-2 text-sm">
              <p>
                <strong>Empresa XYZ</strong> pagou em média <strong>R$ 3,00</strong> de dividendos 
                por ação nos últimos 5 anos.
              </p>
              <p className="font-mono bg-white p-2 rounded border border-green-300">
                Preço-Teto = R$ 3,00 ÷ 0,06 = <strong className="text-green-700">R$ 50,00</strong>
              </p>
              <div className="space-y-1 pt-2">
                <p>✅ Preço atual <strong>R$ 42,00</strong> → <span className="text-green-600 font-medium">COMPRE!</span> (16% abaixo do teto)</p>
                <p>❌ Preço atual <strong>R$ 58,00</strong> → <span className="text-red-600 font-medium">AGUARDE!</span> (16% acima do teto)</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* FAQ */}
      <Card>
        <CardHeader>
          <CardTitle>Perguntas Frequentes</CardTitle>
        </CardHeader>
        <CardContent>
          <Accordion type="single" collapsible className="w-full">
            <AccordionItem value="item-1">
              <AccordionTrigger>Quanto dinheiro preciso para começar?</AccordionTrigger>
              <AccordionContent className="text-muted-foreground">
                Você pode começar com qualquer valor! Muitas ações custam menos de R$ 50. 
                O importante é criar o hábito de investir regularmente. Começar com R$ 100-500 
                por mês já é um ótimo começo.
              </AccordionContent>
            </AccordionItem>

            <AccordionItem value="item-2">
              <AccordionTrigger>Quando vou receber os dividendos?</AccordionTrigger>
              <AccordionContent className="text-muted-foreground">
                As empresas pagam dividendos em datas diferentes. Algumas pagam mensalmente, 
                outras trimestralmente ou semestralmente. Nosso sistema mostra o histórico e 
                prevê as próximas datas de pagamento para cada empresa.
              </AccordionContent>
            </AccordionItem>

            <AccordionItem value="item-3">
              <AccordionTrigger>Posso vender minhas ações depois?</AccordionTrigger>
              <AccordionContent className="text-muted-foreground">
                Sim, mas a metodologia recomenda só vender se a empresa deteriorar fundamentalmente 
                (mudar de negócio, parar de pagar dividendos, ter problemas sérios). A ideia 
                é manter para sempre e viver dos dividendos, não do lucro da venda.
              </AccordionContent>
            </AccordionItem>

            <AccordionItem value="item-4">
              <AccordionTrigger>O que fazer com os dividendos recebidos?</AccordionTrigger>
              <AccordionContent className="text-muted-foreground">
                <strong>Reinvista!</strong> Use os dividendos para comprar mais ações. Esse é o 
                "efeito bola de neve" que faz sua renda crescer exponencialmente ao longo do tempo. 
                Quanto mais ações você tem, mais dividendos recebe, que compram mais ações...
              </AccordionContent>
            </AccordionItem>

            <AccordionItem value="item-5">
              <AccordionTrigger>É garantido receber 6% ao ano?</AccordionTrigger>
              <AccordionContent className="text-muted-foreground">
                Não existe garantia em investimentos! Os 6% são uma meta baseada no histórico. 
                As empresas podem pagar mais ou menos dependendo do lucro. Por isso escolhemos 
                empresas com histórico consistente de pagamento nos setores mais estáveis.
              </AccordionContent>
            </AccordionItem>
          </Accordion>
        </CardContent>
      </Card>
    </div>
  );
}
