import sqlite3

def init_db():
    conn = sqlite3.connect('usuarios.db')  # Conecta ou cria o banco de dados
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

    # Criação da tabela de gastos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            data TEXT NOT NULL,
            usuario_id INTEGER NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    ''')

    # Adicionar usuário admin padrão (opcional)
    cursor.execute('''
        INSERT OR IGNORE INTO usuarios (username, password, is_admin)
        VALUES ('admin', 'admin123', 1)
    ''')

    conn.commit()
    conn.close()

# Inicializa o banco de dados ao importar o módulo
init_db()
