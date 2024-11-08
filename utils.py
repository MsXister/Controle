# Supondo que este código esteja em utils.py
import sqlite3

def verificar_ou_adicionar_colunas():
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()

    # Definições das colunas que devem existir
    colunas_necessarias = {
        'gastos': [
            ('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
            ('descricao', 'TEXT NOT NULL DEFAULT "Sem descrição"'),
            ('categoria', 'TEXT NOT NULL DEFAULT "Outros"'),
            ('valor', 'REAL NOT NULL DEFAULT 0.0'),
            ('data', 'TEXT NOT NULL DEFAULT "2000-01-01"'),
            ('usuario_id', 'INTEGER NOT NULL DEFAULT 1'),
            ('pago', 'INTEGER DEFAULT 0'),  # Adicionando a coluna 'pago'
            ('valor_pago', 'REAL DEFAULT 0.0')  # Adicionando a coluna 'valor_pago'
        ]
    }

    for tabela, colunas in colunas_necessarias.items():
        cursor.execute(f"PRAGMA table_info({tabela});")
        colunas_existentes = [info[1] for info in cursor.fetchall()]

        for coluna, definicao in colunas:
            if coluna not in colunas_existentes:
                print(f"Adicionando coluna {coluna} à tabela {tabela}...")
                cursor.execute(f"ALTER TABLE {tabela} ADD COLUMN {coluna} {definicao};")
                conn.commit()

    conn.close()
    print("Verificação concluída. Todas as tabelas estão atualizadas.")

# Chame a função manualmente
verificar_ou_adicionar_colunas()
