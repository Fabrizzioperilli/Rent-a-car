import os
import psycopg2
import re
from flask import Flask, abort, render_template, request, url_for, redirect
from datetime import datetime


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

@app.route('/facturas')
def facturas():
    conn = get_db_connection()
    factura = conn.cursor()
    factura.execute('SELECT * FROM factura')
    return render_template('facturas.html', factura=factura)
    
    
@app.route('/add_vehiculo', methods=('GET', 'POST'))
def add_vehiculo():
    if request.method == 'POST':

        if not re.match("^[0-9]{4}[A-Z]{3}$", request.form['matricula']):
            return abort(404 , description="La matricula no cumple el formato")

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
        cur.execute('INSERT INTO vehiculo (matricula, codigo_garaje, marca, modelo, color, año, kilometros, tipo, disponible) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
                    (matricula, codigo_garaje, marca, modelo, color, año, kilometros, tipo, disponible))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('index'))

    return render_template('add_vehiculo.html')

@app.route('/delete_vehiculo/', methods=('GET', 'POST'))
def delete_vehiculo():
    if request.method == 'POST':
        
        if not re.match("^[0-9]{4}[A-Z]{3}$", request.form['matricula']):
            return abort(404 , description="La matricula no cumple el formato")

        matricula = request.form['matricula']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('DELETE FROM vehiculo WHERE matricula = %s', (matricula,))
        if cur.rowcount == 0:
            return abort(404 , description="No existe el vehiculo con esa matricula")
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('index'))

    return render_template('delete_vehiculo.html')


@app.route('/update_vehiculo', methods=('GET', 'POST'))
def update_vehiculo():
    if request.method == 'POST':

        if not re.match("^[0-9]{4}[A-Z]{3}$", request.form['matricula']):
            return abort(404 , description="La matricula no cumple el formato")

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
        cur.execute('UPDATE vehiculo SET codigo_garaje = %s, marca = %s, modelo = %s, color = %s, año = %s, kilometros = %s, tipo = %s, disponible = %s WHERE matricula = %s',
                    (codigo_garaje, marca, modelo, color, año, kilometros, tipo, disponible, matricula))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('index'))

    return render_template('update_vehiculo.html')


@app.route('/add_cliente', methods=('GET', 'POST'))
def add_cliente():
    if request.method == 'POST':
        if request.form['codigo_cliente_avalista'] == '':
            codigo_cliente_avalista = None
        else:
            codigo_cliente_avalista = request.form['codigo_cliente_avalista']
        
        if not re.match("^[0-9]{8}[A-Z]$", request.form['dni']):
            return abort(400 , description="El dni no es válido")
        
        dni = request.form['dni']
        nombre = request.form['nombre']
        apellidos = request.form['apellidos']
        telefono = request.form['telefono']
        direccion = request.form['direccion']

        if request.form['email'] == '':
            email = None
        else:
            email = request.form['email']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO cliente (codigo_cliente_avalista, dni, nombre, apellidos, telefono, direccion, email) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                    (codigo_cliente_avalista, dni, nombre, apellidos, telefono, direccion, email))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('clientes'))

    return render_template('add_cliente.html')


@app.route('/delete_cliente/', methods=('GET', 'POST'))
def delete_cliente():
    if request.method == 'POST':
        codigo_cliente = request.form['codigo_cliente']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('DELETE FROM cliente WHERE codigo_cliente = %s',
                    (codigo_cliente,))
        if cur.rowcount == 0:
            return abort(404 , description="No existe el cliente con ese codigo")
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('clientes'))

    return render_template('delete_cliente.html')


@app.route('/update_cliente', methods=('GET', 'POST'))
def update_cliente():
    if request.method == 'POST':
        if request.form['codigo_cliente_avalista'] == '':
            codigo_cliente_avalista = None
        else:
            codigo_cliente_avalista = request.form['codigo_cliente_avalista']

        codigo_cliente = request.form['codigo_cliente']
        dni = request.form['dni']
        nombre = request.form['nombre']
        apellidos = request.form['apellidos']
        telefono = request.form['telefono']
        direccion = request.form['direccion']

        if request.form['email'] == '':
            email = None
        else:
            email = request.form['email']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('UPDATE cliente SET codigo_cliente_avalista = %s, dni = %s, nombre = %s, apellidos = %s, telefono = %s, direccion = %s, email = %s WHERE codigo_cliente = %s',
                    (codigo_cliente_avalista, dni, nombre, apellidos, telefono, direccion, email, codigo_cliente))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('clientes'))

    return render_template('update_cliente.html')

@app.route('/add_reserva', methods=('GET', 'POST'))
def add_reserva():
    if request.method == 'POST':
        codigo_cliente = request.form['codigo_cliente']
        precio_total = 0
        tipo_seguro = request.form['tipo_seguro']

        fecha_actual = datetime.now()
        fecha_actual = fecha_actual.strftime("%Y-%m-%d")
        if request.form['fecha_inicio'] != '':
            if request.form['fecha_fin'] != '':
                if (request.form['fecha_inicio'] < request.form['fecha_fin'] and request.form['fecha_inicio'] > fecha_actual):
                    fecha_inicio = request.form['fecha_inicio']
                    fecha_fin = request.form['fecha_fin']
                else:
                    return abort(400, 'Error en las fecha de inicio y/o fin')
            else:
                return abort(400, 'Error en la fecha de fin')
        else:
            return abort(400, 'Error en la fecha de inicio')
        

        if request.form['combustible_litros'] != '':
            if request.form['combustible_litros'].isdigit():
                if int(request.form['combustible_litros']) > 0:
                    combustible_litros = request.form['combustible_litros']
                else:
                    return abort(400, 'Error en el numero de litros de combustible')
            else:
                return abort(400, 'Error en el numero de litros de combustible')


        entregado = False

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO reserva (codigo_cliente, precio_total, tipo_seguro, fecha_inicio, fecha_fin, combustible_litros, entregado) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                    (codigo_cliente, precio_total, tipo_seguro, fecha_inicio, fecha_fin, combustible_litros, entregado))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('reservas'))

    return render_template('add_reserva.html')


@app.route('/delete_reserva/', methods=('GET', 'POST'))
def delete_reserva():
    if request.method == 'POST':
        codigo_reserva = request.form['codigo_reserva']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('DELETE FROM reserva WHERE codigo_reserva = %s',
                    (codigo_reserva,))
        if cur.rowcount == 0:
            return abort(404, 'No existe la reserva que se quiere eliminar')
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('reservas'))

    return render_template('delete_reserva.html')

@app.route('/update_reserva', methods=('GET', 'POST'))
def update_reserva():
    if request.method == 'POST':
        if request.form['codigo_reserva'] == '':
            return abort(400, 'Error en el codigo de reserva')
        
        if request.form['codigo_cliente'] == '':
            return abort(400, 'Error en el codigo de cliente')

        codigo_reserva = request.form['codigo_reserva']
        codigo_cliente = request.form['codigo_cliente']
        
        fecha_actual = datetime.now()
        fecha_actual = fecha_actual.strftime("%Y-%m-%d")
        if request.form['fecha_inicio'] != '':
            if request.form['fecha_fin'] != '':
                if (request.form['fecha_inicio'] < request.form['fecha_fin'] and request.form['fecha_inicio'] > fecha_actual):
                    fecha_inicio = request.form['fecha_inicio']
                    fecha_fin = request.form['fecha_fin']
                else:
                    return abort(400, 'Error en las fecha de inicio y/o fin')
            else:
                return abort(400, 'Error en la fecha de fin')
        else:
            return abort(400, 'Error en la fecha de inicio')
        

        if request.form['combustible_litros'] != '':
            if request.form['combustible_litros'].isdigit():
                if int(request.form['combustible_litros']) > 0:
                    combustible_litros = request.form['combustible_litros']
                else:
                    return abort(400, 'Error en el numero de litros de combustible')
            else:
                return abort(400, 'Error en el numero de litros de combustible')

        entregado = request.form['entregado']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('UPDATE reserva SET codigo_cliente = %s, fecha_inicio = %s, fecha_fin = %s, combustible_litros = %s, entregado = %s WHERE codigo_reserva = %s',
                    (codigo_cliente, fecha_inicio, fecha_fin, combustible_litros, entregado, codigo_reserva))

        if cur.rowcount == 0:
            return abort(404, 'No existe la reserva que se quiere actualizar')

        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('reservas'))

    return render_template('update_reserva.html')


@app.route('/add_registro', methods=('GET', 'POST'))
def add_registro():
    if request.method == 'POST':
        if request.form['codigo_reserva'] == '':
            return abort(400, 'Error en el codigo de reserva')
        
        if request.form['codigo_empleado'] == '':
            return abort(400, 'Error en el codigo de empleado')

        if not re.match("^[0-9]{4}[A-Z]{3}$", request.form['matricula']):
            return abort(400 , description="La matricula no cumple el formato")

        if request.form['precio_alquiler'] != '':
            if request.form['precio_alquiler'].isdigit():
                if int(request.form['precio_alquiler']) < 0:
                    return abort(400, 'Error en el precio de alquiler')
        
        precio_alquiler = request.form['precio_alquiler']    
        codigo_reserva = request.form['codigo_reserva']
        codigo_empleado = request.form['codigo_empleado']
        matricula = request.form['matricula']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO involucra (codigo_reserva, codigo_empleado, matricula, precio_alquiler) VALUES (%s, %s, %s, %s)',
                    (codigo_reserva, codigo_empleado, matricula, precio_alquiler))
        conn.commit()
        if cur.rowcount == 0:
            return abort(404, 'No se puede registrar la reserva')
        cur.close()
        conn.close()
        return redirect(url_for('registros'))

    return render_template('add_registro.html')

@app.route('/delete_registro/', methods=('GET', 'POST'))
def delete_registro():
    if request.method == 'POST':
        codigo_reserva = request.form['codigo_reserva']
        codigo_empleado = request.form['codigo_empleado']
        matricula = request.form['matricula']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('DELETE FROM involucra WHERE codigo_reserva = %s AND codigo_empleado = %s AND matricula = %s',
                    (codigo_reserva, codigo_empleado, matricula))
        if cur.rowcount == 0:
            return abort(404, 'No existe el registro que se quiere eliminar')
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('registros'))

    return render_template('delete_registro.html')

@app.route('/update_registro', methods=('GET', 'POST'))
def update_registro():
    if request.method == 'POST':
        if request.form['codigo_reserva'] == '':
            return abort(400, 'Error en el codigo de reserva')
        
        if request.form['codigo_empleado'] == '':
            return abort(400, 'Error en el codigo de empleado')

        if request.form['precio_alquiler'] != '':
            if request.form['precio_alquiler'].isdigit():
                if int(request.form['precio_alquiler']) < 0:
                    return abort(400, 'Error en el precio de alquiler')
        
        precio_alquiler = request.form['precio_alquiler']    
        codigo_reserva = request.form['codigo_reserva']
        codigo_empleado = request.form['codigo_empleado']
        matricula = request.form['matricula']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('UPDATE involucra SET precio_alquiler = %s WHERE codigo_reserva = %s AND codigo_empleado = %s AND matricula = %s',
                    (precio_alquiler, codigo_reserva, codigo_empleado, matricula))

        if cur.rowcount == 0:
            return abort(404, 'No existe el registro que se quiere actualizar')

        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('registros'))

    return render_template('update_registro.html')

