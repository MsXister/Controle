from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
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

# Rota para o dashboard
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        conn = sqlite3.connect('usuarios.db')
        cursor = conn.cursor()

        # Verifica se o usuário está no banco e obtém o id e is_admin
        cursor.execute('SELECT id, is_admin FROM usuarios WHERE username = ?', (session['username'],))
        resultado = cursor.fetchone()

        if resultado:
            usuario_id, is_admin = resultado

            # Busca os gastos do usuário e formata valores
            cursor.execute('SELECT descricao, ROUND(valor, 2), data FROM gastos WHERE usuario_id = ?', (usuario_id,))
            gastos = cursor.fetchall()
        else:
            gastos = []
            is_admin = False

        conn.close()

        # Renderiza o dashboard com as informações do usuário
        return render_template('dashboard.html', 
                               username=session['username'], 
                               gastos=gastos, 
                               is_admin=is_admin)

    # Se não estiver logado, redireciona para o login
    return redirect(url_for('login.login'))

@app.route('/alterar_senha', methods=['GET', 'POST'])
def alterar_senha():
    # Verificar se o usuário está logado
    if 'username' not in session:
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login.login'))

    if request.method == 'POST':
        senha_atual = request.form['senha_atual']
        nova_senha = request.form['nova_senha']
        confirmar_senha = request.form['confirmar_senha']

        # Validação: verificar se as senhas coincidem
        if nova_senha != confirmar_senha:
            flash('As senhas não coincidem. Tente novamente.', 'warning')
            return redirect(url_for('alterar_senha'))

        # Validação: verificar força da nova senha
        import re
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', nova_senha):
            flash('A nova senha deve ter no mínimo 8 caracteres, incluindo letras maiúsculas, minúsculas, números e caracteres especiais.', 'warning')
            return redirect(url_for('alterar_senha'))

        # Conectar ao banco e verificar a senha atual
        conn = sqlite3.connect('usuarios.db')
        cursor = conn.cursor()
        cursor.execute('SELECT password FROM usuarios WHERE username = ?', (session['username'],))
        senha_banco = cursor.fetchone()

        if not senha_banco or not check_password_hash(senha_banco[0], senha_atual):
            flash('Senha atual incorreta. Tente novamente.', 'danger')
            conn.close()
            return redirect(url_for('alterar_senha'))

        # Atualizar para a nova senha
        nova_senha_hash = generate_password_hash(nova_senha)
        cursor.execute('UPDATE usuarios SET password = ? WHERE username = ?', (nova_senha_hash, session['username']))
        conn.commit()
        conn.close()

        # Deslogar o usuário e exibir mensagem de sucesso
        session.pop('username', None)
        flash('Senha alterada com sucesso! Faça login novamente.', 'success')
        return redirect(url_for('login.login'))

    # Renderizar o formulário de alteração de senha
    return render_template('alterar_senha.html')


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
  
@app.route('/login/logout')
def logout():
    # Remove a sessão do usuário
    session.pop('username', None)
    session.pop('is_admin', None)  # Remove também qualquer outra chave da sessão
    flash('Você saiu da sua conta com sucesso.', 'success')
    return redirect(url_for('login.login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
