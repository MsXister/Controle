from flask import Flask, redirect, url_for, session, render_template
from cadastro import cadastro_bp
from login import login_bp
import sqlite3

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
        return redirect(url_for('dashboard'))  # Redireciona para o dashboard se logado
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

        # Conecta ao banco e remove o usuário
        conn = sqlite3.connect('usuarios.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM usuarios WHERE username = ?', (username,))
        conn.commit()
        conn.close()

        session.pop('username', None)  # Limpa a sessão
        return "Conta excluída com sucesso! <a href='/login'>Voltar ao Login</a>"

    return redirect(url_for('login.login'))

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
    if 'username' in session:
        conn = sqlite3.connect('usuarios.db')
        cursor = conn.cursor()

        cursor.execute('SELECT id FROM usuarios WHERE username = ?', (session['username'],))
        resultado = cursor.fetchone()

        if resultado:
            usuario_id = resultado[0]

            # Formata os valores dos gastos para duas casas decimais
            cursor.execute('SELECT descricao, ROUND(valor, 2), data FROM gastos WHERE usuario_id = ?', (usuario_id,))
            gastos = cursor.fetchall()
        else:
            gastos = []

        conn.close()
        return render_template('dashboard.html', username=session['username'], gastos=gastos)
    
    return redirect(url_for('login.login'))


    # Se não estiver logado, redireciona para o login
    return redirect(url_for('login.login'))

  

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
