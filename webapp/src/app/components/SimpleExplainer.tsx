import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { CheckCircle2, Clock, XCircle } from 'lucide-react';

export function SimpleExplainer() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Como Entender as Recomendações?</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-start gap-4 p-4 bg-green-50 rounded-lg border-2 border-green-200">
          <div className="bg-green-500 text-white p-2 rounded-lg shrink-0">
            <CheckCircle2 className="size-6" />
          </div>
          <div className="flex-1 space-y-1">
            <div className="flex items-center gap-2">
              <Badge className="bg-green-500">PODE COMPRAR</Badge>
              <span className="text-sm font-medium">Está Barato! 🎉</span>
            </div>
            <p className="text-sm text-muted-foreground">
              A ação está <strong>mais barata</strong> que o "preço certo". 
              É tipo quando você acha um brinquedo em promoção! 
              É uma boa hora para comprar porque você paga menos e vai ganhar mais dinheiro de volta.
            </p>
            <p className="text-xs text-green-700 font-medium mt-2">
              💡 Quanto mais barato estiver, melhor é a oportunidade!
            </p>
          </div>
        </div>

        <div className="flex items-start gap-4 p-4 bg-yellow-50 rounded-lg border-2 border-yellow-200">
          <div className="bg-yellow-500 text-white p-2 rounded-lg shrink-0">
            <Clock className="size-6" />
          </div>
          <div className="flex-1 space-y-1">
            <div className="flex items-center gap-2">
              <Badge className="bg-yellow-500">ESPERE</Badge>
              <span className="text-sm font-medium">Está Caro! ⏳</span>
            </div>
            <p className="text-sm text-muted-foreground">
              A ação está <strong>mais cara</strong> que o "preço certo". 
              É tipo quando você quer comprar algo mas está muito caro na loja. 
              É melhor esperar até o preço baixar para você comprar mais barato.
            </p>
            <p className="text-xs text-yellow-700 font-medium mt-2">
              💡 Coloque na sua lista de favoritos e espere o preço baixar!
            </p>
          </div>
        </div>

        <div className="flex items-start gap-4 p-4 bg-gray-50 rounded-lg border-2 border-gray-200">
          <div className="bg-gray-400 text-white p-2 rounded-lg shrink-0">
            <XCircle className="size-6" />
          </div>
          <div className="flex-1 space-y-1">
            <div className="flex items-center gap-2">
              <Badge variant="secondary">SEM DADOS</Badge>
              <span className="text-sm font-medium">Não Sabemos Ainda 🤷</span>
            </div>
            <p className="text-sm text-muted-foreground">
              Não temos informações suficientes sobre essa empresa ainda. 
              É tipo quando você não conhece bem um jogo novo - é melhor esperar conhecer melhor 
              antes de gastar seu dinheiro.
            </p>
            <p className="text-xs text-gray-700 font-medium mt-2">
              💡 É melhor escolher empresas que a gente já conhece bem!
            </p>
          </div>
        </div>

        <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
          <h4 className="font-medium mb-3 flex items-center gap-2">
            <span>📚</span>
            Palavras Importantes:
          </h4>
          <div className="space-y-3 text-sm">
            <div className="flex gap-3">
              <span className="font-bold text-blue-700 shrink-0">Preço Agora:</span>
              <span>É quanto a ação custa hoje na loja de ações (bolsa de valores).</span>
            </div>
            <div className="flex gap-3">
              <span className="font-bold text-blue-700 shrink-0">Preço Certo:</span>
              <span>
                É o preço máximo que você deveria pagar para ganhar bem. 
                Se estiver mais barato que isso, é bom negócio!
              </span>
            </div>
            <div className="flex gap-3">
              <span className="font-bold text-blue-700 shrink-0">Dinheiro que Recebe:</span>
              <span>
                Toda empresa divide um pouco do dinheiro que ela ganha com quem tem ações. 
                É tipo um presente em dinheiro que ela dá para você!
              </span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}