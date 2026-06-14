from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'chave_secreta_mente_leve_123'

# SOLUÇÃO DO ERRO 500: Define o caminho absoluto para funcionar no servidor Linux do Render
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'mensagens_seguras.db')

def init_db():
    """Inicializa o banco de dados e garante que a tabela exista com certeza."""
    try:
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
        print("Base de dados inicializada com sucesso!")
    except Exception as e:
        print(f"Erro crítico ao inicializar base de dados: {e}")

# Garante a criação correta assim que o servidor inicia
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/enviar-mensagem', methods=['POST'])
def enviar_mensagem():
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
        print(f"Erro ao inserir no banco de dados: {e}")

    return redirect(url_for('index'))

@app.route('/admin/mensagens')
def admin_mensagens():
    mensagens = []
    try:
        # Garante que a tabela existe antes de fazer a consulta para evitar o Erro 500
        init_db()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT nome, email, mensagem, data FROM contatos ORDER BY data DESC')
        mensagens_do_banco = cursor.fetchall()
        conn.close()
        
        for msg in mensagens_do_banco:
            mensagens.append({
                'nome': msg[0],
                'email': msg[1],
                'mensagem': msg[2],
                'data': msg[3]
            })
    except Exception as e:
        print(f"Erro ao buscar mensagens do banco: {e}")
        # Removido o flash de erro daqui para não gerar loops na página de administração

    return render_template('admin_mensagens.html', mensagens=mensagens)

if __name__ == '__main__':
    app.run(debug=True)