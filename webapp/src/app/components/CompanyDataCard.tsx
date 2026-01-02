/**
 * CompanyDataCard: Card de Modelagem de Dados de Empresa
 * 
 * Exibe estrutura de dados completa de uma empresa com todos os campos
 * Útil para desenvolvimento e debug
 */

import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { 
  Building2, Database, Calendar, MapPin, Phone, Mail, 
  Globe, TrendingUp, DollarSign, Shield, CheckCircle, XCircle 
} from 'lucide-react';

interface EmpresaData {
  // Identificação
  id: number;
  cnpj: string;
  codigo_cvm: string;
  razao_social: string;
  nome_fantasia: string;
  
  // Classificação
  setor: string;
  setor_besst: string | null;
  situacao: string;
  
  // Flags de controle
  monitorar: boolean;
  elegivel_barsi: boolean;
  
  // Métricas Barsi
  dividend_yield_atual: number | null;
  consistencia_dividendos: number | null;
  
  // Datas
  data_registro: string;
  data_cancelamento: string | null;
  created_at: string;
  updated_at: string;
  ultima_analise: string | null;
  
  // Contato
  website: string | null;
  email_ri: string | null;
  telefone_ri: string | null;
  
  // Metadados
  motivo_exclusao: string | null;
}

interface CompanyDataCardProps {
  empresa: EmpresaData;
  compact?: boolean;
}

export function CompanyDataCard({ empresa, compact = false }: CompanyDataCardProps) {
  
  const getSetorBesstBadge = (letra: string | null) => {
    if (!letra) return null;
    
    const config: Record<string, { name: string; color: string }> = {
      'B': { name: 'Bancos', color: 'bg-blue-100 text-blue-700' },
      'E': { name: 'Energia', color: 'bg-yellow-100 text-yellow-700' },
      'S': { name: 'Saneamento/Seguros', color: 'bg-green-100 text-green-700' },
      'T': { name: 'Telecom', color: 'bg-purple-100 text-purple-700' },
    };
    
    const info = config[letra] || { name: letra, color: 'bg-gray-100 text-gray-700' };
    
    return (
      <Badge className={info.color}>
        {letra} • {info.name}
      </Badge>
    );
  };
  
  if (compact) {
    return (
      <Card className="p-4">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <Building2 className="size-5 text-primary" />
              <h3 className="font-bold text-lg">{empresa.razao_social}</h3>
            </div>
            
            <div className="flex flex-wrap gap-2 mb-3">
              {empresa.setor_besst && getSetorBesstBadge(empresa.setor_besst)}
              
              {empresa.monitorar && (
                <Badge variant="success">
                  <CheckCircle className="size-3 mr-1" />
                  Monitorada
                </Badge>
              )}
              
              {empresa.elegivel_barsi && (
                <Badge variant="success">
                  ✅ Elegível Barsi
                </Badge>
              )}
              
              <Badge variant={empresa.situacao === 'ATIVO' ? 'default' : 'secondary'}>
                {empresa.situacao}
              </Badge>
            </div>
            
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>
                <span className="text-muted-foreground">CNPJ:</span>
                <span className="ml-2 font-mono">{empresa.cnpj}</span>
              </div>
              <div>
                <span className="text-muted-foreground">CVM:</span>
                <span className="ml-2 font-mono">{empresa.codigo_cvm}</span>
              </div>
            </div>
          </div>
        </div>
      </Card>
    );
  }
  
  // Modo completo (para debug/desenvolvimento)
  return (
    <Card className="p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-start justify-between mb-3">
          <div>
            <h2 className="text-2xl font-bold mb-1">{empresa.razao_social}</h2>
            {empresa.nome_fantasia && empresa.nome_fantasia !== empresa.razao_social && (
              <p className="text-muted-foreground">Nome fantasia: {empresa.nome_fantasia}</p>
            )}
          </div>
          
          <div className="flex flex-col gap-2 items-end">
            {empresa.monitorar ? (
              <Badge variant="success" className="text-sm">
                <CheckCircle className="size-4 mr-1" />
                No Radar BESST
              </Badge>
            ) : (
              <Badge variant="secondary" className="text-sm">
                <XCircle className="size-4 mr-1" />
                Fora do Radar
              </Badge>
            )}
          </div>
        </div>
        
        <div className="flex flex-wrap gap-2">
          {empresa.setor_besst && getSetorBesstBadge(empresa.setor_besst)}
          
          {empresa.elegivel_barsi && (
            <Badge variant="success">✅ Elegível Barsi</Badge>
          )}
          
          <Badge variant={empresa.situacao === 'ATIVO' ? 'default' : 'secondary'}>
            {empresa.situacao}
          </Badge>
        </div>
      </div>
      
      {/* Seção: Identificação */}
      <div className="mb-6">
        <h3 className="font-semibold mb-3 flex items-center gap-2">
          <Database className="size-4" />
          Identificação
        </h3>
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div className="flex items-center gap-2">
            <span className="text-muted-foreground w-24">ID:</span>
            <code className="font-mono bg-muted px-2 py-1 rounded">{empresa.id}</code>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-muted-foreground w-24">CNPJ:</span>
            <code className="font-mono bg-muted px-2 py-1 rounded">{empresa.cnpj}</code>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-muted-foreground w-24">Código CVM:</span>
            <code className="font-mono bg-muted px-2 py-1 rounded">{empresa.codigo_cvm}</code>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-muted-foreground w-24">Setor CVM:</span>
            <span className="truncate">{empresa.setor || 'N/A'}</span>
          </div>
        </div>
      </div>
      
      {/* Seção: Métricas Barsi */}
      {empresa.monitorar && (
        <div className="mb-6 bg-blue-50 p-4 rounded-lg border border-blue-200">
          <h3 className="font-semibold mb-3 flex items-center gap-2 text-blue-700">
            <TrendingUp className="size-4" />
            Métricas Metodologia Barsi
          </h3>
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <DollarSign className="size-4 text-blue-600" />
                <span className="text-muted-foreground">Dividend Yield:</span>
              </div>
              {empresa.dividend_yield_atual !== null ? (
                <p className="text-2xl font-bold text-blue-700">
                  {empresa.dividend_yield_atual.toFixed(2)}%
                </p>
              ) : (
                <p className="text-muted-foreground">Não calculado</p>
              )}
            </div>
            <div>
              <div className="flex items-center gap-2 mb-1">
                <Shield className="size-4 text-blue-600" />
                <span className="text-muted-foreground">Consistência:</span>
              </div>
              {empresa.consistencia_dividendos !== null ? (
                <p className="text-2xl font-bold text-blue-700">
                  {empresa.consistencia_dividendos.toFixed(0)}%
                </p>
              ) : (
                <p className="text-muted-foreground">Não calculado</p>
              )}
            </div>
          </div>
        </div>
      )}
      
      {/* Seção: Contato RI */}
      {(empresa.website || empresa.email_ri || empresa.telefone_ri) && (
        <div className="mb-6">
          <h3 className="font-semibold mb-3 flex items-center gap-2">
            <Phone className="size-4" />
            Relações com Investidores
          </h3>
          <div className="space-y-2 text-sm">
            {empresa.website && (
              <div className="flex items-center gap-2">
                <Globe className="size-4 text-muted-foreground" />
                <a 
                  href={empresa.website} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-primary hover:underline"
                >
                  {empresa.website}
                </a>
              </div>
            )}
            {empresa.email_ri && (
              <div className="flex items-center gap-2">
                <Mail className="size-4 text-muted-foreground" />
                <a 
                  href={`mailto:${empresa.email_ri}`}
                  className="text-primary hover:underline"
                >
                  {empresa.email_ri}
                </a>
              </div>
            )}
            {empresa.telefone_ri && (
              <div className="flex items-center gap-2">
                <Phone className="size-4 text-muted-foreground" />
                <span>{empresa.telefone_ri}</span>
              </div>
            )}
          </div>
        </div>
      )}
      
      {/* Seção: Datas */}
      <div className="mb-6">
        <h3 className="font-semibold mb-3 flex items-center gap-2">
          <Calendar className="size-4" />
          Datas
        </h3>
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div>
            <span className="text-muted-foreground block mb-1">Registro CVM:</span>
            <span className="font-mono">
              {empresa.data_registro ? new Date(empresa.data_registro).toLocaleDateString('pt-BR') : 'N/A'}
            </span>
          </div>
          <div>
            <span className="text-muted-foreground block mb-1">Última Análise:</span>
            <span className="font-mono">
              {empresa.ultima_analise ? new Date(empresa.ultima_analise).toLocaleDateString('pt-BR') : 'Nunca'}
            </span>
          </div>
          <div>
            <span className="text-muted-foreground block mb-1">Criado em:</span>
            <span className="font-mono">
              {new Date(empresa.created_at).toLocaleDateString('pt-BR')}
            </span>
          </div>
          <div>
            <span className="text-muted-foreground block mb-1">Atualizado em:</span>
            <span className="font-mono">
              {new Date(empresa.updated_at).toLocaleDateString('pt-BR')}
            </span>
          </div>
        </div>
      </div>
      
      {/* Seção: Metadados */}
      {empresa.motivo_exclusao && (
        <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
          <h3 className="font-semibold mb-2 text-yellow-700">Motivo de Exclusão</h3>
          <p className="text-sm">{empresa.motivo_exclusao}</p>
        </div>
      )}
      
      {/* Debug Info (apenas em desenvolvimento) */}
      {process.env.NODE_ENV === 'development' && (
        <details className="mt-6">
          <summary className="cursor-pointer text-sm text-muted-foreground hover:text-foreground">
            🔧 Ver JSON completo (debug)
          </summary>
          <pre className="mt-2 p-4 bg-muted rounded-lg overflow-auto text-xs">
            {JSON.stringify(empresa, null, 2)}
          </pre>
        </details>
      )}
    </Card>
  );
}
