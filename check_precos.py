"""Script para verificar preços no banco"""
import sqlite3

conn = sqlite3.connect('data/barsi.db')
cursor = conn.cursor()

cursor.execute('''
    SELECT ticker, data, fechamento, variacao_percentual, volume, market_cap
    FROM precos 
    ORDER BY ticker
''')

rows = cursor.fetchall()

print('\n📊 PREÇOS SALVOS NO BANCO')
print('=' * 90)
print(f"{'Ticker':<8} | {'Data':<12} | {'Preço':<12} | {'Var %':<8} | {'Volume':<15}")
print('=' * 90)

for row in rows:
    ticker = row[0]
    data = row[1]
    preco = f"R$ {row[2]:.2f}"
    variacao = f"{row[3]:.2f}%" if row[3] else "N/A"
    volume = f"{row[4]:,}" if row[4] else "N/A"
    
    print(f"{ticker:<8} | {data:<12} | {preco:<12} | {variacao:<8} | {volume:<15}")

print('=' * 90)
print(f"Total: {len(rows)} registro(s)")

conn.close()
