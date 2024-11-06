from flask import Flask, redirect, url_for, session
from cadastro import cadastro_bp
from login import login_bp

app = Flask(__name__)

# Configurar uma chave secreta para as sessões
app.secret_key = 'sua_chave_secreta_aleatoria'

# Registrar os blueprints
app.register_blueprint(cadastro_bp, url_prefix='/cadastro')
app.register_blueprint(login_bp, url_prefix='/login')

# Redirecionar para login na rota inicial
@app.route('/')
def home():
    if 'username' in session:
        return f"""
        <h1>Bem-vindo de volta, {session['username']}!</h1>
        <p><a href='/login/logout'>Sair</a></p>
        """
    return redirect(url_for('login.login'))
  


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
