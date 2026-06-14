from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'chave_secreta_mente_leve_123'

DB_PATH = 'mensagens.db'

def init_db():
    """Inicializa o banco de dados se ele não existir."""
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contatos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL,
                mensagem TEXT NOT NULL,
                data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

# Inicializa o banco de dados ao iniciar o app
init_db()

@app.route('/')
def index():
    """Rota para a página inicial do site."""
    return render_template('index.html')

@app.route('/enviar-mensagem', methods=['POST'])
def enviar_mensagem():
    """Recebe os dados do formulário de contato e salva no banco de dados."""
    nome = request.form.get('nome')
    email = request.form.get('email')
    mensagem = request.form.get('mensagem')

    if not nome or not email or not mensagem:
        flash('Por favor, preencha todos os campos.', 'erro')
        return redirect(url_for('index'))

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO contatos (nome, email, mensagem) VALUES (?, ?, ?)',
            (nome, email, mensagem)
        )
        conn.commit()
        conn.close()
        flash('Sua mensagem foi enviada com sucesso! Obrigado pelo contato.', 'sucesso')
    except Exception as e:
        flash('Ocorreu um erro ao enviar sua mensagem. Tente novamente.', 'erro')
        print(f"Erro no banco de dados: {e}")

    return redirect(url_for('index'))

@app.route('/admin/mensagens')
def admin_mensagens():
    """Painel administrativo para visualizar as mensagens recebidas (Evita Erro 404)."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Busca todas as mensagens, ordenando pelas mais recentes
        cursor.execute('SELECT nome, email, mensagem, data FROM contatos ORDER BY data DESC')
        mensagens_do_banco = cursor.fetchall()
        conn.close()
        
        # Converte o resultado para uma lista de dicionários para facilitar o uso no HTML
        mensagens = []
        for msg in mensagens_do_banco:
            mensagens.append({
                'nome': msg[0],
                'email': msg[1],
                'mensagem': msg[2],
                'data': msg[3]
            })
    except Exception as e:
        mensagens = []
        print(f"Erro ao buscar mensagens: {e}")
        flash('Erro ao carregar as mensagens do painel.', 'erro')

    return render_template('admin_mensagens.html', mensagens=mensagens)

if __name__ == '__main__':
    # Em produção (Render), o servidor gunicorn ignora esta linha,
    # mas ela continua funcionando perfeitamente para testes locais.
    app.run(debug=True)