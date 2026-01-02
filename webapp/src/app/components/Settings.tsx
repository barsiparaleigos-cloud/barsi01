/**
 * Página de Configurações
 * 
 * Configurações gerais do sistema para o usuário.
 */

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Label } from './ui/label';
import { Input } from './ui/input';
import { Button } from './ui/button';
import { Settings as SettingsIcon, User, Bell, Shield } from 'lucide-react';

export function Settings() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <SettingsIcon className="size-8" />
          Configurações
        </h1>
        <p className="text-muted-foreground mt-2">
          Ajuste suas preferências e configurações do sistema.
        </p>
      </div>

      {/* Perfil */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="size-5" />
            Perfil do Usuário
          </CardTitle>
          <CardDescription>
            Informações básicas da sua conta.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">Nome</Label>
            <Input id="name" placeholder="Seu nome completo" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="email">E-mail</Label>
            <Input id="email" type="email" placeholder="seu@email.com" />
          </div>
          <Button>Salvar Perfil</Button>
        </CardContent>
      </Card>

      {/* Notificações */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="size-5" />
            Notificações
          </CardTitle>
          <CardDescription>
            Configure como você quer receber alertas.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Alertas de Oportunidade</p>
              <p className="text-sm text-muted-foreground">
                Receba notificações quando ações ficarem abaixo do preço-teto
              </p>
            </div>
            <input type="checkbox" className="w-10 h-6" defaultChecked />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Newsletter Semanal</p>
              <p className="text-sm text-muted-foreground">
                Receba resumo semanal das melhores ações
              </p>
            </div>
            <input type="checkbox" className="w-10 h-6" />
          </div>

          <Button>Salvar Preferências</Button>
        </CardContent>
      </Card>

      {/* Segurança */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="size-5" />
            Segurança
          </CardTitle>
          <CardDescription>
            Proteja sua conta e dados pessoais.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="current-password">Senha Atual</Label>
            <Input id="current-password" type="password" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="new-password">Nova Senha</Label>
            <Input id="new-password" type="password" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="confirm-password">Confirmar Nova Senha</Label>
            <Input id="confirm-password" type="password" />
          </div>
          <Button>Alterar Senha</Button>
        </CardContent>
      </Card>
    </div>
  );
}
