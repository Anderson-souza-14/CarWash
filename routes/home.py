from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app

home_bp = Blueprint('home', __name__)

USUARIO = 'anderson'
SENHA = '123456789'

@home_bp.route('/acesso', methods=['GET', 'POST'])
def acesso():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']
        if usuario == USUARIO and senha == SENHA:
            session['usuario'] = usuario 
            return redirect(url_for('home.index'))
        else:
            flash('Usuário ou senha inválidos!')
    return render_template('acesso.html')

@home_bp.route('/index')
def index():
    if 'usuario' not in session:
        return redirect(url_for('home.acesso'))
    mysql = current_app.mysql
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT * FROM veiculos
    WHERE status = 'aguardando'
    ORDER BY 
        aguarda_local DESC,
        CASE WHEN aguarda_local = 1 THEN hora_entrada ELSE hora_retirada END ASC,
        CASE WHEN aguarda_local = 1 THEN id ELSE hora_entrada END ASC,
        CASE WHEN aguarda_local = 1 THEN 0 ELSE id END ASC
    """)
    veiculos = cur.fetchall()
    cur.close()
    return render_template('index.html', usuario=session['usuario'], veiculos=veiculos)
    

@home_bp.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('home.acesso'))

@home_bp.route('/veiculos', methods=['GET', 'POST'])
def veiculos_view():
    if 'usuario' not in session:
        return redirect(url_for('home.acesso'))
    mysql = current_app.mysql
    if request.method == 'POST':
        marca = request.form['marca']
        modelo = request.form['modelo']
        cor = request.form['cor']
        placa = request.form['placa']
        proprietario = request.form['proprietario']
        hora_entrada = request.form['hora_entrada']
        hora_retirada = request.form['hora_retirada']
        tipo = request.form['tipo']
        aguarda_local = 1 if request.form.get('aguarda_local') == 'on' else 0 
        status = 'aguardando'
        if hora_retirada < hora_entrada:
            flash('A hora de retirada não pode ser anterior à hora de entrada!')
        else:
            cur = mysql.connection.cursor()
            cur.execute("""INSERT INTO veiculos (marca, modelo, cor, placa, proprietario, hora_entrada,hora_retirada, tipo, aguarda_local, status)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (marca, modelo, cor, placa, proprietario, hora_entrada, hora_retirada, tipo, aguarda_local, status))
            mysql.connection.commit()
            cur.close()
            flash('Veículo cadastrado com sucesso!')
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM veiculos WHERE status = 'aguardando' ORDER BY hora_entrada ASC, id ASC")
    veiculos = cur.fetchall()
    cur.close()
    return render_template('veiculos.html', usuario=session['usuario'], veiculos=veiculos)

@home_bp.route('/index/concluir/<int:veiculo_id>', methods=['POST'])
def concluir_veiculo(veiculo_id):
    if 'usuario' not in session:
        return redirect(url_for('home.acesso'))
    mysql = current_app.mysql
    data_saida = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cur = mysql.connection.cursor()
    cur.execute("UPDATE veiculos SET status = 'concluido', hora_saida = %s WHERE id = %s", (data_saida, veiculo_id))
    mysql.connection.commit()
    cur.close()
    flash('Serviço concluído com sucesso!')
    return redirect(url_for('home.index'))

@home_bp.route('/concluidos')
def concluidos():
    if 'usuario' not in session:
        return redirect(url_for('home.acesso'))
    mysql = current_app.mysql
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM veiculos WHERE status = 'concluido' ORDER BY hora_saida DESC")
    veiculos_concluidos = cur.fetchall()
    cur.close()
    return render_template('concluidos.html', concluidos=veiculos_concluidos)

@home_bp.route('/concluidos/apagar', methods=['POST'])
def apagar_concluidos():
    if 'usuario' not in session:
        return redirect(url_for('home.login'))
    mysql = current_app.mysql
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM veiculos WHERE status = 'concluido'")
    mysql.connection.commit()
    cur.close()
    flash('Histórico de concluídos apagado!')
    return redirect(url_for('home.concluidos'))