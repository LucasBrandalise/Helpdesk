from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import sqlite3

app = Flask(__name__)

# Classe para mapear os chamados do banco para objetos Python
class ChamadoDB:
    def __init__(self, id, titulo, descricao, prioridade, status, data_criacao):
        self.id = id
        self.titulo = titulo
        self.descricao = descricao
        self.prioridade = prioridade
        self.status = status
        # Converter string para datetime, para usar no template
        if isinstance(data_criacao, str):
            self.data_criacao = datetime.strptime(data_criacao, '%Y-%m-%d %H:%M:%S')
        else:
            self.data_criacao = data_criacao

# Rota da dashboard (pode deixar como estava)
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

# Listar chamados - busca direto do banco
@app.route('/ocorrencias')
def ocorrencias():
    conn = sqlite3.connect('chamados.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, titulo, descricao, prioridade, status, data_criacao FROM chamados')
    chamados_db = cursor.fetchall()
    conn.close()

    chamados = [ChamadoDB(*chamado) for chamado in chamados_db]

    return render_template('ocorrencias.html', chamados=chamados)

# Buscar detalhes do chamado pelo ID
@app.route('/ocorrencias/<int:chamado_id>')
def detalhes_chamado(chamado_id):
    conn = sqlite3.connect('chamados.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, titulo, descricao, prioridade, status, data_criacao FROM chamados WHERE id = ?', (chamado_id,))
    resultado = cursor.fetchone()
    conn.close()

    if not resultado:
        return "Chamado não encontrado", 404

    chamado = ChamadoDB(*resultado)
    return render_template('detalhes_chamado.html', chamado=chamado)

# Criar novo chamado
@app.route('/ocorrencias/novo', methods=['GET', 'POST'])
@app.route('/novo_chamado', methods=['GET', 'POST'])
def novo_chamado():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        prioridade = request.form['prioridade']
        status = request.form['status']

        conn = sqlite3.connect('chamados.db')
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO chamados (titulo, descricao, prioridade, status, data_criacao)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (titulo, descricao, prioridade, status))
        conn.commit()
        conn.close()

        return redirect(url_for('ocorrencias'))

    return render_template('novo_chamado.html')

if __name__ == '__main__':
    app.run(debug=True)
