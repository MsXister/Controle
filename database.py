import sqlite3

def init_db():
    conn = sqlite3.connect('usuarios.db')  # Cria ou conecta ao banco de dados
    cursor = conn.cursor()

    # Criação da tabela de usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0
        )
    ''')

    # Adicionar um usuário admin padrão (opcional)
    cursor.execute('''
        INSERT OR IGNORE INTO usuarios (username, password, is_admin)
        VALUES ('admin', 'admin123', 1)
    ''')

    conn.commit()
    conn.close()

# Chama a função para garantir que o banco está inicializado
init_db()
