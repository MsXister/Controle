import sqlite3

def verificar_ou_adicionar_colunas():
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()

    colunas_necessarias = {
        'gastos': [
            ('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
            ('descricao', 'TEXT NOT NULL DEFAULT "Sem descrição"'),
            ('categoria', 'TEXT NOT NULL DEFAULT "Outros"'),
            ('valor', 'REAL NOT NULL DEFAULT 0.0'),
            ('data', 'TEXT NOT NULL DEFAULT "2000-01-01"'),
            ('usuario_id', 'INTEGER NOT NULL DEFAULT 1')
        ],
        'usuarios': [
            ('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
            ('username', 'TEXT NOT NULL'),
            ('password', 'TEXT NOT NULL'),
            ('is_admin', 'BOOLEAN NOT NULL DEFAULT 0')
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
