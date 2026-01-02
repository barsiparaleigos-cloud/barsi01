/**
 * Componente Card de Integração (genérico, reutilizável)
 * 
 * Usado para renderizar cada API de forma isolada dentro de um Tab.
 */

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/app/components/ui/card';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import { Label } from '@/app/components/ui/label';
import { Badge } from '@/app/components/ui/badge';
import { CheckCircle2, XCircle, Loader2, AlertCircle } from 'lucide-react';

export interface IntegrationCardProps {
  name: string;
  description: string;
  enabled: boolean;
  baseUrl: string;
  apiKey?: string;
  lastSync?: string;
  onToggle: (enabled: boolean) => void;
  onSave: (config: { apiKey?: string; baseUrl: string }) => Promise<void>;
  onTest: () => Promise<{ success: boolean; message: string }>;
}

export function IntegrationCard({
  name,
  description,
  enabled,
  baseUrl,
  apiKey,
  lastSync,
  onToggle,
  onSave,
  onTest,
}: IntegrationCardProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [localApiKey, setLocalApiKey] = useState(apiKey || '');
  const [localBaseUrl, setLocalBaseUrl] = useState(baseUrl);
  const [isSaving, setIsSaving] = useState(false);
  const [isTesting, setIsTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await onSave({ apiKey: localApiKey, baseUrl: localBaseUrl });
      setIsEditing(false);
      setTestResult(null);
    } catch (err: any) {
      alert(`Erro ao salvar: ${err.message}`);
    } finally {
      setIsSaving(false);
    }
  };

  const handleTest = async () => {
    setIsTesting(true);
    setTestResult(null);
    try {
      const result = await onTest();
      setTestResult(result);
    } catch (err: any) {
      setTestResult({ success: false, message: err.message });
    } finally {
      setIsTesting(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <CardTitle>{name}</CardTitle>
            <CardDescription>{description}</CardDescription>
          </div>
          <Badge variant={enabled ? 'default' : 'secondary'}>
            {enabled ? 'Ativo' : 'Inativo'}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Toggle */}
        <div className="flex items-center justify-between">
          <Label htmlFor={`toggle-${name}`}>Habilitar integração</Label>
          <input
            id={`toggle-${name}`}
            type="checkbox"
            checked={enabled}
            onChange={(e) => onToggle(e.target.checked)}
            className="w-10 h-6"
          />
        </div>

        {/* Campos de configuração */}
        {isEditing ? (
          <>
            <div className="space-y-2">
              <Label htmlFor={`url-${name}`}>URL Base</Label>
              <Input
                id={`url-${name}`}
                value={localBaseUrl}
                onChange={(e) => setLocalBaseUrl(e.target.value)}
                placeholder="https://api.exemplo.com"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor={`key-${name}`}>API Key (opcional)</Label>
              <Input
                id={`key-${name}`}
                type="password"
                value={localApiKey}
                onChange={(e) => setLocalApiKey(e.target.value)}
                placeholder="Cole sua chave de API aqui"
              />
            </div>

            <div className="flex gap-2">
              <Button onClick={handleSave} disabled={isSaving}>
                {isSaving ? <Loader2 className="animate-spin size-4 mr-2" /> : null}
                Salvar
              </Button>
              <Button variant="outline" onClick={() => setIsEditing(false)}>
                Cancelar
              </Button>
            </div>
          </>
        ) : (
          <>
            <div className="text-sm text-muted-foreground">
              <p><strong>URL:</strong> {baseUrl}</p>
              {apiKey && <p><strong>API Key:</strong> ••••••••</p>}
              {lastSync && <p><strong>Última sincronização:</strong> {lastSync}</p>}
            </div>

            <div className="flex gap-2">
              <Button variant="outline" onClick={() => setIsEditing(true)}>
                Editar
              </Button>
              <Button variant="secondary" onClick={handleTest} disabled={isTesting}>
                {isTesting ? <Loader2 className="animate-spin size-4 mr-2" /> : null}
                Testar Conexão
              </Button>
            </div>
          </>
        )}

        {/* Resultado do teste */}
        {testResult && (
          <div
            className={`flex items-center gap-2 p-3 rounded-lg border ${
              testResult.success
                ? 'bg-green-50 border-green-200 text-green-800'
                : 'bg-red-50 border-red-200 text-red-800'
            }`}
          >
            {testResult.success ? (
              <CheckCircle2 className="size-5 shrink-0" />
            ) : (
              <XCircle className="size-5 shrink-0" />
            )}
            <span className="text-sm">{testResult.message}</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
