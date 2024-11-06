from flask import Flask, redirect, url_for, session, render_template
from cadastro import cadastro_bp
from login import login_bp

app = Flask(__name__)

# Configuração de uma chave secreta para gerenciar sessões
app.secret_key = 'sua_chave_secreta_aleatoria'

# Registrar os blueprints para dividir funcionalidades de cadastro e login
app.register_blueprint(cadastro_bp, url_prefix='/cadastro')
app.register_blueprint(login_bp, url_prefix='/login')

# Rota principal: redireciona para o dashboard se o usuário estiver logado, caso contrário, vai para login
@app.route('/')
def home():
    if 'username' in session:  # Verifica se o usuário está logado
        return redirect(url_for('dashboard'))  # Redireciona para o dashboard
    return redirect(url_for('login.login'))  # Redireciona para login se não estiver logado

# Rota do dashboard: exibe informações do usuário logado
@app.route('/dashboard')
def dashboard():
    if 'username' in session:  # Verifica se o usuário está logado
        return render_template('dashboard.html', username=session['username'])  # Renderiza o dashboard
    return redirect(url_for('login.login'))  # Redireciona para login se não estiver logado
  
@app.route('/configuracao', methods=['GET'])
def configuracao():
    if 'username' in session:  # Verifica se o usuário está logado
        return render_template('configuracao.html')  # Exibe o menu de configuração
    return redirect(url_for('login.login'))  # Redireciona para login se não estiver logado

  
@app.route('/configuracao/excluir', methods=['POST'])
def excluir_conta():
    if 'username' in session:
        username = session['username']  # Obtém o usuário logado
        # Remove o usuário do "banco de dados" (no caso, o dicionário)
        if username in usuarios:
            del usuarios[username]
        session.pop('username', None)  # Limpa a sessão
        return "Conta excluída com sucesso! <a href='/login'>Voltar ao Login</a>"
    return redirect(url_for('login.login'))
  
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        conn = sqlite3.connect('usuarios.db')
        cursor = conn.cursor()

        # Obter o ID do usuário logado
        cursor.execute('SELECT id FROM usuarios WHERE username = ?', (session['username'],))
        usuario_id = cursor.fetchone()[0]

        # Buscar dados relacionados (ex: gastos)
        cursor.execute('SELECT descricao, valor, data FROM gastos WHERE usuario_id = ?', (usuario_id,))
        gastos = cursor.fetchall()

        conn.close()

        return render_template('dashboard.html', username=session['username'], gastos=gastos)

    return redirect(url_for('login.login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
