import { TrendingUp, Settings, User, Menu } from 'lucide-react';
import { Button } from './ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from './ui/dropdown-menu';

export function Header() {
  return (
    <header className="border-b bg-white sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="bg-primary text-primary-foreground p-2 rounded-lg">
            <TrendingUp className="size-6" />
          </div>
          <div>
            <h1 className="font-bold">Dividendos para leigos</h1>
            <p className="text-xs text-muted-foreground">Invista com sabedoria</p>
          </div>
        </div>

        <nav className="hidden md:flex items-center gap-6">
          <a href="#dashboard" className="text-sm hover:text-primary transition-colors">
            Dashboard
          </a>
          <a href="#ranking" className="text-sm hover:text-primary transition-colors">
            Ranking
          </a>
          <a href="#simulador" className="text-sm hover:text-primary transition-colors">
            Simulador
          </a>
          <a href="#educacao" className="text-sm hover:text-primary transition-colors">
            Aprenda
          </a>
        </nav>

        <div className="flex items-center gap-2">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon">
                <User className="size-5" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem>Meu Perfil</DropdownMenuItem>
              <DropdownMenuItem>Sair</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          <Button variant="ghost" size="icon" className="md:hidden">
            <Menu className="size-5" />
          </Button>
        </div>
      </div>
    </header>
  );
}
