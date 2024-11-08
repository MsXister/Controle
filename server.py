from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from cadastro import cadastro_bp
from login import login_bp
import sqlite3
from utils import verificar_ou_adicionar_colunas  # Importar a função
from gastos import gastos_bp
from datetime import datetime

app = Flask(__name__)

# Configuração de uma chave secreta para gerenciar sessões
app.secret_key = 'sua_chave_secreta_aleatoria'

# Verificar colunas no banco de dados
verificar_ou_adicionar_colunas()

# Registrar os blueprints para dividir funcionalidades de cadastro e login
app.register_blueprint(gastos_bp, url_prefix='/gastos')
app.register_blueprint(cadastro_bp, url_prefix='/cadastro')
app.register_blueprint(login_bp, url_prefix='/login')



# Rota principal: redireciona para o dashboard se o usuário estiver logado, caso contrário, vai para login
@app.route('/')
def home():
    if 'username' in session:  # Verifica se o usuário está logado
        return redirect(url_for('dashboard'))  # Redireciona para o dashboard se logado
    return redirect(url_for('login.login'))  # Redireciona para login se não estiver logado

# Rota para excluir conta
@app.route('/configuracao/excluir', methods=['POST'])
def excluir_conta():
    if 'username' in session:
        username = session['username']  # Obtém o usuário logado

        # Conecta ao banco e remove o usuário
        conn = sqlite3.connect('usuarios.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM usuarios WHERE username = ?', (username,))
        conn.commit()
        conn.close()

        session.pop('username', None)  # Limpa a sessão
        return "Conta excluída com sucesso! <a href='/login'>Voltar ao Login</a>"

    return redirect(url_for('login.login'))

# Rota para listar todos os usuários (apenas para admins)
@app.route('/usuarios')
def listar_usuarios():
    if 'username' in session and session.get('is_admin'):
        conn = sqlite3.connect('usuarios.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, is_admin FROM usuarios')
        usuarios = cursor.fetchall()
        conn.close()

        return render_template('usuarios.html', usuarios=usuarios)
    return redirect(url_for('login.login'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash('Por favor, faça login para acessar o dashboard.', 'warning')
        return redirect(url_for('login.login'))

    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()

    # Verifica se o usuário está no banco e obtém o id e is_admin
    cursor.execute('SELECT id, is_admin FROM usuarios WHERE username = ?', (session['username'],))
    resultado = cursor.fetchone()

    if resultado:
        usuario_id, is_admin = resultado

        # Busca os últimos 5 gastos do usuário
        cursor.execute('''
            SELECT descricao, ROUND(valor, 2), data 
            FROM gastos 
            WHERE usuario_id = ? 
            ORDER BY data DESC 
            LIMIT 5
        ''', (usuario_id,))
        gastos_recentes = cursor.fetchall()

        # Resumo de gastos por categoria para o usuário atual
        cursor.execute('''
            SELECT categoria, ROUND(SUM(valor), 2) 
            FROM gastos 
            WHERE usuario_id = ? 
            GROUP BY categoria
        ''', (usuario_id,))
        resumo_categorias = cursor.fetchall()

        # Busca todos os gastos de todos os usuários para visualização geral
        cursor.execute('''
            SELECT g.descricao, ROUND(g.valor, 2), g.data, g.categoria, u.username
            FROM gastos g
            JOIN usuarios u ON g.usuario_id = u.id
            ORDER BY g.data DESC
        ''')
        todos_gastos = cursor.fetchall()
    else:
        # Caso o usuário não seja encontrado no banco
        gastos_recentes = []
        resumo_categorias = []
        todos_gastos = []
        is_admin = False

    conn.close()

    # Renderiza o dashboard com os dados
    return render_template('dashboard.html',
                           username=session['username'],
                           gastos_recentes=gastos_recentes,
                           resumo_categorias=resumo_categorias,
                           todos_gastos=todos_gastos,
                           is_admin=is_admin)




    # Se não estiver logado, redireciona para o login
    return redirect(url_for('login.login'))

@app.route('/alterar_senha', methods=['GET', 'POST'])
def alterar_senha():
    if request.method == 'POST':
        username = request.form.get('username', session.get('username'))  # Usar o username da sessão ou o fornecido
        senha_atual = request.form.get('senha_atual')  # Opcional se não estiver logado
        nova_senha = request.form['nova_senha']
        confirmar_senha = request.form['confirmar_senha']

        # Validação: senhas devem coincidir
        if nova_senha != confirmar_senha:
            flash('As senhas não coincidem. Tente novamente.', 'warning')
            return redirect(url_for('alterar_senha'))

        # Validação: força da nova senha
        import re
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', nova_senha):
            flash('A nova senha deve ter no mínimo 8 caracteres, incluindo letras maiúsculas, minúsculas, números e caracteres especiais.', 'warning')
            return redirect(url_for('alterar_senha'))

        # Conectar ao banco
        conn = sqlite3.connect('usuarios.db')
        cursor = conn.cursor()
        cursor.execute('SELECT password FROM usuarios WHERE username = ?', (username,))
        senha_banco = cursor.fetchone()

        if not senha_banco:
            flash('Usuário não encontrado.', 'danger')
            conn.close()
            return redirect(url_for('alterar_senha'))

        # Validar senha atual apenas se o usuário estiver logado
        if 'username' in session:
            if not check_password_hash(senha_banco[0], senha_atual):
                flash('Senha atual incorreta. Tente novamente.', 'danger')
                conn.close()
                return redirect(url_for('alterar_senha'))

        # Atualizar a nova senha
        nova_senha_hash = generate_password_hash(nova_senha)
        cursor.execute('UPDATE usuarios SET password = ? WHERE username = ?', (nova_senha_hash, username))
        conn.commit()
        conn.close()

        flash('Senha alterada com sucesso! Faça login novamente.', 'success')
        session.pop('username', None)  # Desloga o usuário se estiver logado
        return redirect(url_for('login.login'))

    return render_template('alterar_senha.html', is_logged_in='username' in session)

from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime
import sqlite3

app = Flask(__name__)

@app.route('/todos_gastos', methods=['GET', 'POST'])
def todos_gastos():
    if 'username' not in session:
        flash('Por favor, faça login para acessar os gastos.', 'warning')
        return redirect(url_for('login.login'))

    mes_atual = request.args.get('mes', datetime.now().strftime('%Y-%m'))
    
    # Substitua essa parte pela sua lógica de consulta de gastos
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT g.descricao, ROUND(g.valor, 2), g.data, g.categoria, u.username, g.id, g.pago, g.valor_pago
        FROM gastos g
        JOIN usuarios u ON g.usuario_id = u.id
        WHERE strftime('%Y-%m', g.data) = ?
    ''', (mes_atual,))
    todos_gastos = cursor.fetchall()
    conn.close()

    return render_template('todos_gastos.html', mes_atual=mes_atual, todos_gastos=todos_gastos, year=datetime.now().year)



  
# Rota para gerenciar usuários (apenas admins)
@app.route('/gerenciar_usuarios')
def gerenciar_usuarios():
    if 'is_admin' in session and session['is_admin']:
        conn = sqlite3.connect('usuarios.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM usuarios')
        usuarios = cursor.fetchall()
        conn.close()
        return render_template('gerenciar_usuarios.html', usuarios=usuarios)
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Exibe a senha inserida no terminal
        print(f"Senha inserida para {username}: {password}")

        # Continue com a lógica de validação...

  
@app.route('/login/logout', endpoint='logout')
def logout():
    # Remove a sessão do usuário
    session.pop('username', None)
    session.pop('is_admin', None)  # Remove também o status de admin
    flash('Você saiu da sua conta com sucesso.', 'success')
    return redirect(url_for('login.login'))

def exibir_senha(username):
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()
    cursor.execute('SELECT password FROM usuarios WHERE username = ?', (username,))
    senha = cursor.fetchone()
    conn.close()
    
    if senha:
        print(f"Senha armazenada para {username}: {senha[0]}")
    else:
        print(f"Usuário {username} não encontrado.")
exibir_senha('fabio.andrades')

# Filtro personalizado para formatar a data no formato DD/MM/YYYY
def formatar_data(data):
    try:
        return datetime.strptime(data, "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError:
        return data  # Retorna o valor original se não for uma data válida

# Registro do filtro no ambiente Jinja2
app.jinja_env.filters['formatar_data'] = formatar_data

# Filtro para formatar valores como moeda
def formatar_valor(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

app.jinja_env.filters['formatar_valor'] = formatar_valor

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
