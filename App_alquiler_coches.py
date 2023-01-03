import os
import psycopg2
from flask import Flask, render_template, request, url_for, redirect

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(host='localhost',
        	database="alquiler_coches",
          # user=os.environ['DB_USERNAME'],
		      user="postgres",
		      # password=os.environ['DB_PASSWORD']
          password="postgres")
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    vehiculo = conn.cursor()
    vehiculo.execute('SELECT * FROM vehiculo')
    return render_template('index.html', vehiculo=vehiculo)

@app.route('/clientes')
def clientes():
    conn = get_db_connection()
    cliente = conn.cursor()
    cliente.execute('SELECT * FROM cliente')
    return render_template('clientes.html', cliente=cliente)

@app.route('/reservas')
def reservas():
    conn = get_db_connection()
    reserva = conn.cursor()
    reserva.execute('SELECT * FROM reserva ORDER BY codigo_reserva')
    return render_template('reservas.html', reserva=reserva)

@app.route('/registros')
def registros():
    conn = get_db_connection()
    involucra = conn.cursor()
    involucra.execute('SELECT * FROM involucra')
    return render_template('registros.html', involucra=involucra)


@app.route('/agencias')
def agencias():
    conn = get_db_connection()
    agencia = conn.cursor()
    agencia.execute('SELECT * FROM agencia')
    return render_template('agencias.html', agencia=agencia)

@app.route('/empleados')
def empleados():
    conn = get_db_connection()
    empleado = conn.cursor()
    empleado.execute('SELECT * FROM empleado')
    return render_template('empleados.html', empleado=empleado)

@app.route('/garajes')
def garajes():
    conn = get_db_connection()
    garaje = conn.cursor()
    garaje.execute('SELECT * FROM garaje ORDER BY codigo_garaje')
    return render_template('garajes.html', garaje=garaje)


@app.route('/add_vehiculo', methods=('GET', 'POST'))
def add_vehiculo():
    if request.method == 'POST':
        matricula = request.form['matricula']
        codigo_garaje = request.form['codigo_garaje']
        marca = request.form['marca']
        modelo = request.form['modelo']
        color = request.form['color']
        año = request.form['año']
        kilometros = request.form['kilometros']
        tipo = request.form['tipo']
        disponible = request.form['disponible']
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO vehiculo (matricula, codigo_garaje, marca, modelo, color, año, kilometros, tipo, disponible) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', (matricula, codigo_garaje, marca, modelo, color, año, kilometros, tipo, disponible))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('index'))

    return render_template('add_vehiculo.html')

    #Eliminar un vehiculo 
@app.route('/delete_vehiculo/', methods=('GET', 'POST'))
def delete_vehiculo():
    if request.method == 'POST':
        matricula = request.form['matricula']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('DELETE FROM vehiculo WHERE matricula = %s', (matricula,))
        if cur.rowcount == 0:
            return render_template('delete_vehiculo.html', error='No existe el vehiculo')
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('index'))

    return render_template('delete_vehiculo.html')

    #Modificar un vehiculo
@app.route('/update_vehiculo', methods=('GET', 'POST'))
def update_vehiculo():
    if request.method == 'POST':
        matricula = request.form['matricula']
        codigo_garaje = request.form['codigo_garaje']
        marca = request.form['marca']
        modelo = request.form['modelo']
        color = request.form['color']
        año = request.form['año']
        kilometros = request.form['kilometros']
        tipo = request.form['tipo']
        disponible = request.form['disponible']
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('UPDATE vehiculo SET codigo_garaje = %s, marca = %s, modelo = %s, color = %s, año = %s, kilometros = %s, tipo = %s, disponible = %s WHERE matricula = %s', (codigo_garaje, marca, modelo, color, año, kilometros, tipo, disponible, matricula))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('index'))

    return render_template('update_vehiculo.html')