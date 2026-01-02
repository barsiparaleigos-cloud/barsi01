"""
Servidor HTTP simples para API de empresas CVM
Sem dependências de Supabase ou jobs
"""

import json
import sys
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.models import get_db
from database.besst_classifier import BESSTClassifier


class APIHandler(BaseHTTPRequestHandler):
    
    def _set_cors_headers(self):
        """Set CORS headers"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def _send_json(self, data: Dict[str, Any], status: int = 200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self._set_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str, ensure_ascii=False).encode())
    
    def do_OPTIONS(self):
        """Handle preflight requests"""
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        parsed = urlparse(self.path)
        path = parsed.path
        query_params = parse_qs(parsed.query)
        
        try:
            db = get_db()
            
            # GET /api/empresas
            if path == '/api/empresas':
                situacao = query_params.get('situacao', [None])[0]
                setor_besst = query_params.get('setor_besst', [None])[0]
                apenas_monitoradas = query_params.get('apenas_monitoradas', ['false'])[0].lower() == 'true'
                limit = int(query_params.get('limit', [1000])[0])
                
                empresas = db.get_empresas(
                    situacao=situacao,
                    setor_besst=setor_besst,
                    apenas_monitoradas=apenas_monitoradas,
                    limit=limit
                )
                
                self._send_json({
                    'total': len(empresas),
                    'empresas': empresas
                })
            
            # GET /api/empresas/besst
            elif path == '/api/empresas/besst':
                situacao = query_params.get('situacao', ['ATIVO'])[0]
                empresas = db.get_empresas_besst(situacao=situacao)
                
                # Estatísticas por setor
                stats = {}
                for letra in ['B', 'E', 'S', 'T']:
                    count = len([e for e in empresas if e.get('setor_besst') == letra])
                    if count > 0:
                        stats[letra] = count
                
                self._send_json({
                    'total': len(empresas),
                    'empresas': empresas,
                    'stats_por_setor': stats
                })
            
            # GET /api/stats
            elif path == '/api/stats':
                cursor = db.connection.cursor()
                
                # Total empresas
                cursor.execute("SELECT COUNT(*) FROM empresas")
                total_empresas = cursor.fetchone()[0]
                
                # Empresas ativas
                cursor.execute("SELECT COUNT(*) FROM empresas WHERE situacao = 'ATIVO'")
                empresas_ativas = cursor.fetchone()[0]
                
                # Empresas BESST
                cursor.execute("SELECT COUNT(*) FROM empresas WHERE monitorar = TRUE")
                empresas_besst = cursor.fetchone()[0]
                
                # Total ações
                cursor.execute("SELECT COUNT(*) FROM acoes")
                total_acoes = cursor.fetchone()[0]
                
                # Total dividendos
                cursor.execute("SELECT COUNT(*) FROM dividendos")
                total_dividendos = cursor.fetchone()[0]
                
                # Tamanho do banco
                import os
                db_path = Path(__file__).parent.parent / "data" / "dividendos.db"
                database_size_mb = os.path.getsize(db_path) / (1024 * 1024) if db_path.exists() else 0
                
                self._send_json({
                    'total_empresas': total_empresas,
                    'empresas_ativas': empresas_ativas,
                    'empresas_besst': empresas_besst,
                    'total_acoes': total_acoes,
                    'total_dividendos': total_dividendos,
                    'database_size_mb': round(database_size_mb, 2),
                    'ultima_sincronizacao': None
                })
            
            # GET /api/empresa/{cnpj}
            elif path.startswith('/api/empresa/'):
                cnpj = path.split('/')[-1]
                empresa = db.get_empresa_by_cnpj(cnpj)
                
                if not empresa:
                    self._send_json({'error': 'Empresa não encontrada'}, 404)
                    return
                
                # Buscar ações
                acoes = db.get_acoes(empresa_id=empresa['id'])
                
                # Buscar dividendos
                cursor = db.connection.cursor()
                cursor.execute("""
                    SELECT * FROM dividendos
                    WHERE empresa_id = ?
                    ORDER BY ano_fiscal DESC
                """, (empresa['id'],))
                dividendos = [dict(row) for row in cursor.fetchall()]
                
                self._send_json({
                    'empresa': empresa,
                    'acoes': acoes,
                    'dividendos': dividendos
                })
            
            # 404
            else:
                self._send_json({'error': 'Not found'}, 404)
        
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            self._send_json({'error': str(e)}, 500)
    
    def do_POST(self):
        """Handle POST requests"""
        parsed = urlparse(self.path)
        path = parsed.path
        
        try:
            # POST /api/classificar-empresa
            if path == '/api/classificar-empresa':
                content_length = int(self.headers['Content-Length'])
                body = self.rfile.read(content_length)
                data = json.loads(body)
                
                empresa_id = data.get('empresa_id')
                if not empresa_id:
                    self._send_json({'error': 'empresa_id obrigatório'}, 400)
                    return
                
                db = get_db()
                cursor = db.connection.cursor()
                
                # Buscar empresa
                cursor.execute("SELECT * FROM empresas WHERE id = ?", (empresa_id,))
                row = cursor.fetchone()
                
                if not row:
                    self._send_json({'error': 'Empresa não encontrada'}, 404)
                    return
                
                empresa = dict(row)
                
                # Classificar
                classifier = BESSTClassifier()
                classificacao = classifier.classificar(
                    empresa.get('setor', ''),
                    empresa.get('razao_social', '')
                )
                
                # Atualizar banco
                if classificacao:
                    db.update_empresa(empresa_id, {
                        'setor_besst': classificacao['letra'],
                        'monitorar': True
                    })
                    resultado = {
                        'classificada': True,
                        'setor_besst': classificacao['letra'],
                        'setor_nome': classificacao['nome'],
                        'descricao': classificacao['descricao']
                    }
                else:
                    db.update_empresa(empresa_id, {
                        'setor_besst': None,
                        'monitorar': False
                    })
                    resultado = {
                        'classificada': False,
                        'motivo': 'Empresa não pertence aos setores BESST'
                    }
                
                self._send_json(resultado)
            
            else:
                self._send_json({'error': 'Not found'}, 404)
        
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            self._send_json({'error': str(e)}, 500)
    
    def log_message(self, format, *args):
        """Custom log message"""
        print(f"[{self.log_date_time_string()}] {format % args}")


def run_server(port=8001):
    """Run HTTP server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, APIHandler)
    
    print("="*60)
    print(f"🚀 Servidor Backend - Dividendos para leigos")
    print("="*60)
    print(f"📡 Servidor rodando em http://127.0.0.1:{port}")
    print(f"📊 Endpoints disponíveis:")
    print(f"  • GET  /api/empresas")
    print(f"  • GET  /api/empresas/besst")
    print(f"  • GET  /api/stats")
    print(f"  • GET  /api/empresa/{{cnpj}}")
    print(f"  • POST /api/classificar-empresa")
    print("="*60)
    print("Pressione Ctrl+C para parar o servidor\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n⏹️  Servidor encerrado")
        httpd.server_close()


if __name__ == '__main__':
    run_server()
