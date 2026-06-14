from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

def inicializar_banco():
    conexao = sqlite3.connect('mensagens.db')
    cursor = conexao.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contatos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL,
            mensagem TEXT NOT NULL
        )
    ''')
    conexao.commit()
    conexao.close()

inicializar_banco()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/enviar', methods=['POST'])
def enviar_mensagem():
    nome = request.form.get('nome')
    email = request.form.get('email')
    mensagem = request.form.get('mensagem')

    conexao = sqlite3.connect('mensagens.db')
    cursor = conexao.cursor()
    cursor.execute('''
        INSERT INTO contatos (nome, email, mensagem)
        VALUES (?, ?, ?)
    ''', (nome, email, mensagem))
    conexao.commit()
    conexao.close()

    return redirect(url_for('home'))
# Rota secreta para ver as mensagens enviadas pelo site novo
@app.route('/admin/mensagens')
def ver_mensagens():
    conexao = sqlite3.connect('mensagens.db')
    cursor = conexao.cursor()
    # Busca o nome, email e a mensagem salvos
    cursor.execute('SELECT nome, email, mensagem FROM contatos')
    todas_mensagens = cursor.fetchall()
    conexao.close()
    
    # Monta uma página simples com o visual esverdeado para exibir os dados
    html = """
    <html>
    <head>
        <title>Painel de Mensagens</title>
        <style>
            body { font-family: sans-serif; background: #f8faf9; color: #2c3e50; padding: 2rem; }
            h1 { color: #1e5e48; border-bottom: 2px solid #2d7d5f; padding-bottom: 0.5rem; }
            .card { background: white; padding: 1.5rem; margin-bottom: 1rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
            strong { color: #2d7d5f; }
        </style>
    </head>
    <body>
        <h1>🌿 Mensagens Recebidas — MenteLeve</h1>
    """
    
    if not todas_mensagens:
        html += "<p>Nenhuma mensagem enviada ainda.</p>"
    
    for msg in todas_mensagens:
        html += f"""
        <div class="card">
            <p><strong>Nome:</strong> {msg[0]}</p>
            <p><strong>E-mail:</strong> {msg[1]}</p>
            <p><strong>Mensagem:</strong> {msg[2]}</p>
        </div>
        """
        
    html += "</body></html>"
    return html
if __name__ == '__main__':
    # Mantido na porta 8080 conforme sua preferência anterior
    app.run(debug=True, port=8080)