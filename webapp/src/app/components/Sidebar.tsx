/**
 * Sidebar: Menu lateral escalável
 * 
 * Menu fixo à esquerda com navegação principal e admin.
 * Colapsa em mobile para economizar espaço.
 */

import { useState, useEffect } from 'react';
import {
  TrendingUp,
  BarChart3,
  Calculator,
  BookOpen,
  Settings,
  Database,
  ChevronLeft,
  ChevronRight,
  Home,
  User,
} from 'lucide-react';
import { Button } from './ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from './ui/dropdown-menu';
import { cn } from './ui/utils';

interface SidebarProps {
  activeView: string;
  onNavigate: (view: string) => void;
}

export function Sidebar({ activeView, onNavigate }: SidebarProps) {
  const [collapsed, setCollapsed] = useState(false);

  // Auto-collapse em mobile
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 768) {
        setCollapsed(true);
      }
    };

    handleResize(); // Check inicial
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const mainNavItems = [
    { id: 'home', label: 'Dashboard', icon: Home },
    { id: 'ranking', label: 'Ranking de Ações', icon: TrendingUp },
    { id: 'simulator', label: 'Simulador de Renda', icon: Calculator },
    { id: 'learn', label: 'Aprenda a Metodologia', icon: BookOpen },
    { id: 'empresas', label: 'Empresas', icon: Database },
  ];

  const adminNavItems = [
    { id: 'integrations', label: 'Integrações', icon: Database },
    { id: 'settings', label: 'Configurações', icon: Settings },
  ];

  return (
    <aside
      className={cn(
        'fixed left-0 top-0 bottom-0 bg-white border-r transition-all duration-300 z-40 shadow-sm',
        collapsed ? 'w-16' : 'w-64'
      )}
    >
      <div className="flex flex-col h-full">
        {/* Logo e Perfil */}
        <div className="border-b bg-gradient-to-r from-primary/10 to-primary/5 p-3">
          {!collapsed ? (
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <div className="bg-primary text-primary-foreground p-2 rounded-lg">
                  <TrendingUp className="size-5" />
                </div>
                <div className="flex-1 min-w-0">
                  <h1 className="font-bold text-sm truncate">Barsi para Leigos</h1>
                  <p className="text-xs text-muted-foreground truncate">Invista com sabedoria</p>
                </div>
              </div>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="sm" className="w-full justify-start gap-2">
                    <User className="size-4" />
                    <span className="text-xs">Meu Perfil</span>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="start" className="w-48">
                  <DropdownMenuItem>Meu Perfil</DropdownMenuItem>
                  <DropdownMenuItem>Sair</DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-2">
              <div className="bg-primary text-primary-foreground p-2 rounded-lg">
                <TrendingUp className="size-5" />
              </div>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="icon" className="size-8">
                    <User className="size-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="start">
                  <DropdownMenuItem>Meu Perfil</DropdownMenuItem>
                  <DropdownMenuItem>Sair</DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          )}
        </div>

        {/* Toggle Button */}
        <div className={cn("flex p-2 border-b bg-gray-50", collapsed ? "justify-center" : "justify-end")}>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setCollapsed(!collapsed)}
            className="size-8 hover:bg-gray-200"
            title={collapsed ? 'Expandir menu' : 'Recolher menu'}
          >
            {collapsed ? (
              <ChevronRight className="size-4" />
            ) : (
              <ChevronLeft className="size-4" />
            )}
          </Button>
        </div>

        {/* Main Navigation */}
        <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
          <div className="mb-4">
            {!collapsed && (
              <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2 px-3">
                Principal
              </h3>
            )}
            {mainNavItems.map((item) => (
              <button
                key={item.id}
                onClick={() => onNavigate(item.id)}
                className={cn(
                  'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all',
                  activeView === item.id
                    ? 'bg-primary text-primary-foreground shadow-sm'
                    : 'hover:bg-gray-100 text-gray-700 hover:text-gray-900'
                )}
                title={collapsed ? item.label : undefined}
              >
                <item.icon className="size-5 shrink-0" />
                {!collapsed && <span className="text-sm font-medium">{item.label}</span>}
              </button>
            ))}
          </div>

          {/* Admin Section */}
          <div className="pt-4 border-t">
            {!collapsed && (
              <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2 px-3">
                Administração
              </h3>
            )}
            {adminNavItems.map((item) => (
              <button
                key={item.id}
                onClick={() => onNavigate(item.id)}
                className={cn(
                  'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all',
                  activeView === item.id
                    ? 'bg-primary text-primary-foreground shadow-sm'
                    : 'hover:bg-gray-100 text-gray-700 hover:text-gray-900'
                )}
                title={collapsed ? item.label : undefined}
              >
                <item.icon className="size-5 shrink-0" />
                {!collapsed && <span className="text-sm font-medium">{item.label}</span>}
              </button>
            ))}
          </div>
        </nav>

        {/* Footer */}
        {!collapsed && (
          <div className="p-3 border-t bg-gray-50">
            <p className="text-xs text-muted-foreground text-center">
              Barsi para Leigos v1.0
            </p>
          </div>
        )}
      </div>
    </aside>
  );
}
