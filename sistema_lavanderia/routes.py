from flask import Flask, abort, jsonify, render_template, current_app as app, session, make_response
from flask import url_for,redirect
from flask import Flask,render_template, request
from flask_mysqldb import MySQL     
from datetime import datetime
from flask_mysqldb import MySQL
from flask_cors import CORS
from flask import Blueprint

routes = Blueprint('routes', __name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = '1234'
app.config['MYSQL_DB'] = 'sistema_lavanderia'
mysql = MySQL(app)
cursor = mysql.connection.cursor()

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('paguser'))

@app.route('/logoutadmin')
def logoutadmin():
    session.clear()
    return redirect(url_for('admin_login_page'))


@app.context_processor
def inject_menu():
    menu = [
        {'text': 'Inicio', 'url': '/'},
        {'text': 'Servicios', 'url': '/user_servicios.html'},
        {'text': 'Productos', 'url': '/user_productos.html'},
        {'text': 'Carrito', 'url': '/user_carrito.html'},
    ]
    if session.get('logged_in'):
        opciones = [
            {'text': 'Cerrar Sesión', 'url': '/logout'}
        ]
    else:
        opciones = [
            {'text': 'Iniciar Sesión', 'url': '/inicio_sesion.html'},
            {'text': 'Registrarse', 'url': '/registro.html'}
        ]
    
    return dict(
        menu=menu,
        opciones=opciones,
        user_name=session.get('user_name')
    )

#Logica de las interfaces de usuario
@app.route('/user_carrito.html')
def carrito():
    cursor = mysql.connection.cursor()
    query="Select nombre, precio,stock,id_producto_inv from producto where stock > 0;"
    cursor.execute(query)
    productos = cursor.fetchall()   
    query="Select nombre_servicio,precio,id_servicio from servicio;"
    cursor.execute(query)
    servicios=cursor.fetchall()   

    return render_template('pg_carrito.html',productos=productos,servicios=servicios)

#lógica para guardar el carrito en la bd 
@app.route('/carrito_guardar',methods=['POST'])
def guardarCarrito():
    data=request.json
    productos = data.get('productos', [])
    servicios = data.get('servicios', []) 
    fecha=data.get('fecha')
    hora=data.get('hora')
    fechahora = f"{fecha} {hora}"      
    id_cliente = session.get('user_id')
    cursor = mysql.connection.cursor()

     
    query="INSERT INTO carrito (id_cliente, fecha_hora) values (%s,%s);"
    cursor.execute(query,(id_cliente,fechahora))
    mysql.connection.commit()


    query=("Select id_carrito from carrito order by id_carrito desc limit 1;")
    cursor.execute(query)
    id_carrito=cursor.fetchone()

    if productos:
        for producto in productos:
            query_producto = "INSERT INTO carrito_items (id_carrito, id_producto, cantidad) VALUES (%s, %s, %s);"
            cursor.execute(query_producto, (id_carrito, producto['producto_id'], producto['cantidad']))
            query="UPDATE producto set stock=stock - %s where id_producto_inv = %s;"
            cursor.execute(query,(producto['cantidad'],producto['producto_id']))
    if servicios:
        for servicio in servicios:
            query_servicio = "INSERT INTO carrito_items (id_carrito, id_servicio, cantidad) VALUES (%s, %s, %s);"
            cursor.execute(query_servicio, (id_carrito, servicio['servicio_id'], 1))
    mysql.connection.commit()

    return jsonify({"message": "Carrito guardado correctamente"}), 200

@app.route('/')
def paguser():
    
    ima = [
        
        {'image': 'images/logo_lavadora.png'},
        {'image': 'images/imagen_horario_car.jpeg'},
        {'image': 'images/publi_lava.jpg'}
    ]
    return render_template('pagina_user.html', ima=ima)

@app.route('/user_productos.html')
def user_producto():

    cursor = mysql.connection.cursor()
    query="Select nombre,descripcion, precio from producto where stock > 0;"
    cursor.execute(query)
    productos = cursor.fetchall()      
    cursor.close()

    return render_template('pg_productos_user.html', productos=productos)
    

@app.route('/user_servicios.html', methods=['GET', 'POST'])
def produc_servicios():

    cursor = mysql.connection.cursor()
    query="Select nombre_servicio,descripcion, precio from servicio;"
    cursor.execute(query)
    servicios = cursor.fetchall()      
    cursor.close()

    return render_template('pg_servicios_user.html', servicios=servicios)


# Registro e inicio de sesión
@app.route('/registro.html')
def registro():
    return render_template('registro.html')

@app.route('/registroUsuario', methods=['POST'])
def nuevoUsuario():
    data=request.json
    usuario=data.get('user')
    clave=data.get('pass')
    nombres=data.get('nombre')
    apellidos=data.get('apellido')
    cedula=data.get('cedula')
    ruc=data.get('ruc')
    telefono=data.get('telefono')
    vehiculo=data.get('vehiculo')
    cursor= mysql.connection.cursor()
    banderaUser=True
    banderaCed=True
    banderaRuc=True
    banderaTel=True
    
    query="Select * from cliente where usuario_cliente = %s;"
    cursor.execute(query,(usuario,))
    nom_usuario = cursor.fetchone()
    if nom_usuario:
        banderaUser=False
        return jsonify({"error": "Hay usuario registrado con ese username."}), 404


    query="Select * from cliente where cedula = %s;"
    cursor.execute(query,(cedula,))
    ced_usuario = cursor.fetchone()
    if ced_usuario:
        banderaCed=False
        return jsonify({"error": "Hay usuario registrado con esa cedula."}), 404
    
    if ruc and ruc.strip():  
        query = "SELECT * FROM cliente WHERE ruc = %s;"
        cursor.execute(query, (ruc,))
        ruc_usuario = cursor.fetchone()
        if ruc_usuario:
            banderaRuc = False
            return jsonify({"error": "Hay usuario registrado con ese ruc."}), 404
    
    query="Select * from cliente where telefono = %s;"
    cursor.execute(query,(telefono,))
    tel_usuario = cursor.fetchone()
    if tel_usuario:
        banderaTel=False
        return jsonify({"error": "Hay usuario registrado con ese número de telefono."}), 404

    
    if banderaUser==True & banderaCed==True & banderaRuc==True &banderaTel==True:
        query="insert into cliente (usuario_cliente,clave, nombres, apellidos,cedula,ruc,telefono,vehiculo) values(%s,%s,%s,%s,%s,%s,%s,%s);"
        cursor.execute(query,(usuario,clave,nombres,apellidos,cedula,ruc,telefono,vehiculo))
        mysql.connection.commit()
        cursor.close()
        return jsonify({"message": "Se ha registrado con éxito."}), 200


@app.route('/inicio_sesion.html')
def inicioSesion():
    return render_template('pg_iniciosesion.html')

@app.route('/inicioSesion', methods=['POST'])
def iniciarSesion():
    data = request.json
    usuario = data.get('user')
    clave = data.get('pass')
    
    cursor = mysql.connection.cursor()
    query = "SELECT id_cliente, usuario_cliente, nombres, apellidos, cedula, ruc, vehiculo FROM cliente WHERE usuario_cliente = %s AND clave = %s;"
    cursor.execute(query,(usuario,clave,))
    cliente_infor = cursor.fetchone()
    cursor.close()
    
    if cliente_infor:
        nombre_inicial = cliente_infor[2][0].upper() if cliente_infor[2] else ''
        apellido_inicial = cliente_infor[3][0].upper() if cliente_infor[3] else ''
        
        session['user_id'] = cliente_infor[0]
        session['user_cedula']=cliente_infor[4]
        session['user_name'] = f"{nombre_inicial}{apellido_inicial}"
        session['logged_in'] = True
        
        return jsonify({
            "id_cliente": cliente_infor[0],
            "nombres": cliente_infor[2],
            "apellidos": cliente_infor[3],
            "cedula": cliente_infor[4],
            "ruc": cliente_infor[5],
            "vehiculo": cliente_infor[6]
        })
    else:
        return jsonify({"error": "Credenciales no validas."}), 404

#Logica de las interfaces de administración

@app.route('/administrador')
def index():
    buttons = [
        {'icon': 'person', 'text': 'Clientes', 'url':'/cliente.html'},
        {'icon': 'database', 'text': 'Productos', 'url':'/productos.html'},
        {'icon': 'file-earmark-check', 'text': 'Servicios','url':'/servicios.html'},
        {'icon': 'cash-stack', 'text': 'Cuentas por Cobrar'},
        {'icon': 'file-earmark-check', 'text': 'Nueva Factura','url':'/factura.html'},
        {'icon': 'file-earmark-text', 'text': 'Proformas','url':'/ver_proformas.html'},
        {'icon': 'receipt', 'text': 'Comprobantes','url':'/comprobantes.html'},
        {'icon': 'journal-text', 'text': 'Trabajadores','url':'/trabajadores.html'},
        {'icon': 'file-earmark-minus', 'text': 'Administrar Pedidos','url':'/pedidos.html'},
        {'icon': 'journal-text', 'text': 'Ver Pedidos', 'url':'/ver_pedidos.html'},
        {'icon': 'box-arrow-right', 'text': 'Cerrar Sesión', 'url': '/logoutadmin'}
    ]
    
    return render_template('pagina_principal.html', buttons=buttons)

@app.route('/ver_proformas.html')
def ver_proformas():
    cursor = mysql.connection.cursor()
    
    query = """
    SELECT cr.id_carrito, cl.nombres, cl.apellidos, cl.cedula, cr.fecha_hora, 
        SUM(
            COALESCE(cr_i.cantidad * pr.precio, 0) + 
            COALESCE(cr_i.cantidad * ser.precio, 0)
        ) AS total  
    FROM carrito AS cr 
    INNER JOIN cliente AS cl ON cl.id_cliente = cr.id_cliente
    LEFT JOIN carrito_items AS cr_i ON cr_i.id_carrito = cr.id_carrito
    LEFT JOIN producto AS pr ON pr.id_producto_inv = cr_i.id_producto
    LEFT JOIN servicio AS ser ON ser.id_servicio = cr_i.id_servicio
    WHERE cr.estado = 'pendiente' 
    GROUP BY cr.id_carrito, cl.cedula;
    """
    cursor.execute(query)
    carritos = cursor.fetchall()
    
    query = """
    SELECT car.id_carrito, pr.nombre, pr.precio, car.cantidad
    FROM producto AS pr 
    INNER JOIN carrito_items AS car ON car.id_producto = pr.id_producto_inv 
    WHERE car.id_producto IS NOT NULL;
    """
    cursor.execute(query)
    productos = cursor.fetchall()
    
    query = """
    SELECT car.id_carrito, sr.nombre_servicio, sr.precio 
    FROM servicio AS sr 
    INNER JOIN carrito_items AS car ON car.id_servicio = sr.id_servicio 
    WHERE car.id_servicio IS NOT NULL;
    """
    cursor.execute(query)
    servicios = cursor.fetchall()

    cursor.close()
    return render_template('pg_proformas.html', carritos=carritos, productos=productos, servicios=servicios)


@app.route('/eliminarCarrito/<int:id_carrito>', methods=['DELETE'])
def eliminar_carrito(id_carrito):
    cursor = mysql.connection.cursor()
    query = "DELETE FROM carrito WHERE id_carrito = %s"
    cursor.execute(query, (id_carrito,))
    mysql.connection.commit()
    cursor.close()
    return jsonify({"mensaje": "Carrito eliminado correctamente"}), 200

@app.route('/facturarTurno/<int:id_carrito>', methods=['POST'])
def completar_turno(id_carrito):
    cursor = mysql.connection.cursor()
    queryTotal="""
      SELECT SUM(
            COALESCE(cr_i.cantidad * pr.precio, 0) + 
            COALESCE(cr_i.cantidad * ser.precio, 0)
        ) AS total  
    FROM carrito AS cr 
    LEFT JOIN carrito_items AS cr_i ON cr_i.id_carrito = cr.id_carrito
    LEFT JOIN producto AS pr ON pr.id_producto_inv = cr_i.id_producto
    LEFT JOIN servicio AS ser ON ser.id_servicio = cr_i.id_servicio
    WHERE cr.estado = 'pendiente' and cr.id_carrito=%s
    GROUP BY cr.id_carrito;
    """
    cursor.execute(queryTotal,(id_carrito,))
    total=cursor.fetchone()

    query="""
    SELECT cr.id_cliente, cr.id_carrito ,cl.nombres, cl.apellidos, cl.cedula
    FROM carrito AS cr
    INNER JOIN cliente AS cl ON cl.id_cliente = cr.id_cliente where cr.id_carrito=%s;
    """
    cursor.execute(query, (id_carrito,))
    turnoCompleto=cursor.fetchone()
    
    query = "UPDATE carrito SET estado = 'pagado' WHERE id_carrito = %s"
    cursor.execute(query, (id_carrito,))
    mysql.connection.commit()

    query="INSERT INTO factura_cliente (id_cliente, id_carrito, total) VALUES (%s, %s, %s);"
    cursor.execute(query,(turnoCompleto[0],turnoCompleto[1],total[0]))
    mysql.connection.commit()
    
    query="SELECT id_factura from factura_cliente order by id_factura desc limit 1;"
    cursor.execute(query)
    factura=cursor.fetchone()

    cursor.close()
  
    return jsonify({"id_factura": factura[0]})


@app.route('/imprimirFac/<int:id_factura>', methods=['GET'])
def imprimir_factura_Car(id_factura):
    # Consultar la factura específica por ID
    cursor = mysql.connection.cursor()
    query="""
    SELECT fac.id_factura, cl.nombres, cl.apellidos, cl.cedula,car.fecha_hora, fac.fecha_hora, fac.total, fac.id_carrito
    from factura_cliente as fac inner join carrito as car on car.id_carrito=fac.id_carrito 
    inner join cliente as cl on cl.id_cliente=car.id_cliente where fac.id_factura=%s;
    """
    cursor.execute(query, (id_factura,))
    turnoCompleto=cursor.fetchone()

    query = """
    SELECT car.id_carrito, pr.nombre, pr.precio, car.cantidad
    FROM producto AS pr 
    INNER JOIN carrito_items AS car ON car.id_producto = pr.id_producto_inv 
    WHERE car.id_producto IS NOT NULL;
    """
    cursor.execute(query)
    productos = cursor.fetchall()
    
    query = """
    SELECT car.id_carrito, sr.nombre_servicio, sr.precio 
    FROM servicio AS sr 
    INNER JOIN carrito_items AS car ON car.id_servicio = sr.id_servicio 
    WHERE car.id_servicio IS NOT NULL;
    """
    cursor.execute(query)
    servicios = cursor.fetchall()

    factura_dict = {
        "id_factura": turnoCompleto[0],
        "nombres": turnoCompleto[1]+ " "+ turnoCompleto[2],
        "ci_ruc": turnoCompleto[3],
        "fecha_hora_car": turnoCompleto[4],
        "fecha_hora_fac": turnoCompleto[5],
        "total": turnoCompleto[6],
        "id_carrito":turnoCompleto[7]

    }

    # Renderizar la plantilla imprimible
    return render_template('imprimir_factura.html', factura=factura_dict,servicios=servicios,productos=productos)

@app.route('/turnoBuscar',methods=['POST'])
def buscarTurno():
    data=request.json
    cedula=data.get('cedula')
    cursor=mysql.connection.cursor()
    query="Select tur.id_turno, cl.nombres, cl.apellidos,cedula,ser.nombre_servicio, ser.precio,tur.fecha_hora from turno as tur inner join cliente  cl on cl.id_cliente=tur.id_cliente inner join servicio as ser on ser.id_servicio=tur.tipo_servicio where DATE(tur.fecha_hora) >= CURDATE() AND estado='pendiente' and cedula=%s order by tur.fecha_hora asc Limit 1 ;"
    cursor.execute(query,(cedula,)) 
    turno=cursor.fetchone()
    cursor.close()
    
    if turno:
        return jsonify({
            'id_turno': turno[0],
            'nombres': turno[1],
            'apellidos': turno[2],
            'cedula': turno[3],
            'nombre_servicio': turno[4],
            'precio': float(turno[5]),
            'fecha_hora': turno[6].strftime('%Y-%m-%d %H:%M:%S')  
        })

@app.route('/eliminarTurno/<int:id_turno>', methods=['DELETE'])
def eliminar_turno(id_turno):
    cursor = mysql.connection.cursor()
    query = "DELETE FROM turno WHERE id_turno = %s"
    cursor.execute(query, (id_turno,))
    mysql.connection.commit()
    cursor.close()
    return jsonify({"mensaje": "Turno eliminado correctamente"}), 200

@app.route('/ver_pedidos.html', methods=['GET', 'POST'])
def verpedidos():
    cursor=mysql.connection.cursor()
    query="Select id_pedido,nombre,descripcion,total, fecha, estado from pedido where estado='pendiente';"
    cursor.execute(query)
    pendientes=cursor.fetchall()
    query="Select id_pedido,nombre,descripcion,total, fecha, estado from pedido where estado='completado';"
    cursor.execute(query)
    completados=cursor.fetchall()
    cursor.close()
    return render_template('pg_ver_pedidos.html', pedidos_pendientes=pendientes,pedidos_completados=completados)

@app.route('/pedidos.html')
def generarPedido():

    return render_template('pg_pedidos.html')

@app.route('/pedido', methods =['POST'])
def registrarpedido():
    data =request.json
    nombre=data.get('nombre')
    descripcion=data.get('descripcion')
    valor=data.get('precio')

    cursor=mysql.connection.cursor()
    query="INSERT INTO pedido (id_admin,nombre,descripcion,total,estado) values (1,%s,%s,%s, 'pendiente');"
    cursor.execute(query,(nombre,descripcion,valor))
    mysql.connection.commit()
    cursor.close()
    return jsonify({"message": "Pedido agregado con éxito"}), 200

@app.route('/pedidoBuscar',methods=['POST'])
def buscarpedido():
    data=request.json
    nombre=data.get('nombre')
    cursor=mysql.connection.cursor()
    query="SELECT id_pedido,nombre, descripcion,total,fecha,estado from pedido where nombre=%s;"
    cursor.execute(query,(nombre,))
    pedido=cursor.fetchone()
    cursor.close()

    if pedido:
        return jsonify({
            "id_pedido":pedido[0],
            "nombre":pedido[1],
            "descripcion":pedido[2],
            "total":pedido[3],
            "fecha":pedido[4],
            "estado":pedido[5]
        })

@app.route('/eliminarPedido/<int:id_pedido>', methods=['DELETE'])
def eliminar_pedido(id_pedido):
    cursor = mysql.connection.cursor()
    query = "DELETE FROM pedido WHERE id_pedido = %s"
    cursor.execute(query, (id_pedido,))
    mysql.connection.commit()
    cursor.close()
    return jsonify({"mensaje": "Pedido eliminado correctamente"}), 200

@app.route('/completarPedido/<int:id_pedido>', methods=['PUT'])
def completar_pedido(id_pedido):
    cursor = mysql.connection.cursor()
    query = "UPDATE pedido SET estado = 'completado' WHERE id_pedido = %s"
    cursor.execute(query, (id_pedido,))
    mysql.connection.commit()
    cursor.close()
    return jsonify({"mensaje": "Pedido marcado como completado"}), 200
    
        
@app.route('/cliente.html')
def pagcli():
    return render_template('cliente.html')

@app.route('/cliente', methods=['POST'])
def buscar_cliente():
    data = request.json 
    cedula = data.get('cedula')

    cursor = mysql.connection.cursor()
    # Modificamos la consulta para obtener el primer cliente registrado
    query = "SELECT id_cliente, nombres, apellidos,cedula, ruc, vehiculo FROM cliente where cedula = %s;"  
    cursor.execute(query,(cedula,))
    cliente = cursor.fetchone() 
    cursor.close()

    if cliente:
        return jsonify({
            "id_cliente": cliente[0],
            "nombres": cliente[1],
            "apellidos": cliente[2],
            "cedula": cliente[3],
            "ruc":cliente[4],
            "vehiculo": cliente[5]
        })

@app.route('/productos.html')
def pagpro():
    return render_template('pg_productos.html')

@app.route('/producto', methods=['POST'])
def buscar_producto():
    data = request.json 
    nom = data.get('nombre')

    cursor = mysql.connection.cursor()
    query = "SELECT id_producto_inv, nombre, descripcion,stock, precio, fecha FROM producto where nombre = %s;"  
    cursor.execute(query,(nom,))
    producto = cursor.fetchone()  
    cursor.close()

    if producto:
        return jsonify({
            "id_producto_inv": producto[0],
            "nombre": producto[1],
            "descripcion": producto[2],
            "stock": producto[3],
            "precio":producto[4],
            "fecha":producto[5]
        })
    else:
        return jsonify({"error": "No hay productos registrados"}), 404

@app.route('/producto/agregar-actualizar', methods=['POST'])
def agregar_actualizar_producto():
    data = request.json
    nom = data.get('nombre')
    desc = data.get('descripcion')
    stock = data.get('stock')
    precio = data.get('precio') 

    cursor = mysql.connection.cursor()
    query = "CALL insertarProducto(%s, %s, %s, %s)"  
    cursor.execute(query, (nom, desc, stock, precio))
    mysql.connection.commit()  
    cursor.close()
    return jsonify({"message": "Producto agregado o actualizado con éxito"}), 200


@app.route('/servicios.html')
def pagser():
    return render_template('pg_servicios.html')

@app.route('/servicios', methods=['POST'])
def buscar_servicio():
    data = request.json 
    nom = data.get('nombre')

    cursor = mysql.connection.cursor()
 
    query = "SELECT id_servicio, nombre_servicio, descripcion, precio, fecha_creacion FROM servicio where nombre_servicio = %s;"  
    cursor.execute(query,(nom,))
    producto = cursor.fetchone() 
    cursor.close()

    if producto:
        return jsonify({
            "id_servicio": producto[0],
            "nombre": producto[1],
            "descripcion": producto[2],
            "precio":producto[3],
            "fecha":producto[4]
        })
    else:
        return jsonify({"error": "No hay servicio registrado"}), 404

@app.route('/servicioAgregar',methods=['POST'])
def servicio_agre_act():
    data = request.json
    nom = data.get('nombre')
    desc = data.get('descripcion')
    precio = data.get('precio') 
# Validar datos
    if not nom or not desc or precio is None or not isinstance(precio, (int, float)):
            return jsonify({"error": "Datos inválidos"}), 400
    cursor = mysql.connection.cursor()
    query = "INSERT INTO servicio(nombre_servicio,descripcion, precio)values(%s, %s, %s)"  
    cursor.execute(query, (nom, desc, precio))
    mysql.connection.commit()  
    cursor.close()
    return jsonify({"message": "Servicio agregado con éxito"}), 200

@app.route('/factura.html', methods=['GET'])
def mostrar_formulario():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id_factura FROM factura_no_cliente order by id_factura desc")
    resultado = cursor.fetchone()
    siguiente_factura = resultado[0]+1 if resultado else 1  
    query="Select nombre_servicio from servicio;"
    cursor.execute(query)
    servicios=cursor.fetchall()
    return render_template('factura.html', id_factura=siguiente_factura,servicios=servicios)

# Ruta para generar la factura
@app.route('/generar-factura', methods=['POST'])
def generar_factura():
    # Obtener los datos del formulario
    id_factura = request.form.get('id_factura')
    nombres = request.form['nombres']
    ci_ruc = request.form['ci_ruc']
    servicio = request.form['servicio']
    total = request.form['total']
    cursor = mysql.connection.cursor()
    query = "INSERT INTO factura_no_cliente (id_factura, nombres, ci_ruc, servicio, total) VALUES (%s, %s, %s, %s, %s);"
    cursor.execute(query, (id_factura, nombres, ci_ruc, servicio, total))
    
    mysql.connection.commit()
    
    query="SELECT fecha_hora from factura_no_cliente where id_factura=%s;"

    cursor.execute(query,(id_factura,))

    fecha_hora=cursor.fetchone()[0]
    fecha_hora = fecha_hora.strftime("%Y-%m-%d %H:%M:%S")

    # Renderizar la página con los datos generados
    return render_template(
        'factura_generada.html',
        id_factura=id_factura,
        nombres=nombres,
        ci_ruc=ci_ruc,
        fecha_hora=fecha_hora,
        servicio=servicio,
        total=total
    )
    
@app.route('/comprobantes.html', methods=['GET'])
def ver_comprobantes():
    # Consultar todas las facturas en la base de datos
    cursor = mysql.connection.cursor()
    query = "SELECT id_factura, nombres, ci_ruc, fecha_hora, servicio, total FROM factura_no_cliente"
    cursor.execute(query)
    facturas = cursor.fetchall()  # Recupera todas las filas como lista de tuplas

    query="""
    SELECT fac.id_cliente , fac.id_factura ,cl.nombres, cl.apellidos, cl.cedula, fac.fecha_hora, fac.total
    FROM factura_cliente AS fac
    INNER JOIN cliente AS cl ON cl.id_cliente = fac.id_cliente;
    """
    cursor.execute(query)
    facturasCar=cursor.fetchall()
    # Convertir las filas a una estructura más legible si es necesario
    facturas_lista = [
        {
            "id_factura": factura[0],
            "nombres": factura[1],
            "ci_ruc": factura[2],
            "fecha_hora": factura[3],
            "servicio": factura[4],
            "total": factura[5]
        }
        for factura in facturas
    ]

    facturas_listaCar = [
        {
            "id_cliente": factura[0],
            "id_factura": factura[1],
            "nombres": factura[2],
            "apellidos": factura[3],
            "cedula": factura[4],
            "fecha_hora":factura[5],
            "total":factura[6]
        }
        for factura in facturasCar
    ]
    # Renderizar la plantilla con los datos de las facturas
    return render_template('comprobantes.html', facturas=facturas_lista,facturasCar=facturas_listaCar)


@app.route('/buscar_comprobantes', methods=['GET'])
def buscar_comprobantes():
    cedula = request.args.get('cedula', None)
    
    if not cedula:
        return redirect(url_for('ver_comprobantes'))
        
    cursor = mysql.connection.cursor()
    
    # Query for facturas_cliente
    query_clientes = """
        SELECT fc.id_factura, cl.nombres, cl.apellidos, cl.cedula, fc.fecha_hora, fc.total
        FROM factura_cliente AS fc
        INNER JOIN cliente AS cl ON cl.id_cliente = fc.id_cliente
        WHERE cl.cedula = %s
    """
    cursor.execute(query_clientes, (cedula,))
    facturas_carrito = cursor.fetchall()
    
    # Query for factura_no_cliente
    query_servicios = """
        SELECT id_factura, nombres, ci_ruc, fecha_hora, servicio, total
        FROM factura_no_cliente
        WHERE ci_ruc = %s
    """
    cursor.execute(query_servicios, (cedula,))
    facturas_servicios = cursor.fetchall()
    
    # Convert results to dictionaries
    facturas_lista = [
        {
            "id_factura": factura[0],
            "nombres": factura[1],
            "ci_ruc": factura[2],
            "fecha_hora": factura[3],
            "servicio": factura[4],
            "total": factura[5]
        }
        for factura in facturas_servicios
    ]
    
    facturas_listaCar = [
        {
            "id_factura": factura[0],
            "nombres": factura[1],
            "apellidos": factura[2],
            "cedula": factura[3],
            "fecha_hora": factura[4],
            "total": factura[5]
        }
        for factura in facturas_carrito
    ]
    
    cursor.close()
    
    return render_template(
        'comprobantes.html',
        facturas=facturas_lista,
        facturasCar=facturas_listaCar
    )

@app.route('/imprimir/<int:id_factura>', methods=['GET'])
def imprimir_factura(id_factura):
    # Consultar la factura específica por ID
    cursor = mysql.connection.cursor()
    query = "SELECT id_factura, nombres, ci_ruc, fecha_hora, servicio, total FROM factura_no_cliente WHERE id_factura = %s"
    cursor.execute(query, (id_factura,))
    factura = cursor.fetchone()

    # Verificar si la factura existe
    if not factura:
        return "Factura no encontrada", 404

    # Convertir la factura en un diccionario para facilitar el uso
    factura_dict = {
        "id_factura": factura[0],
        "nombres": factura[1],
        "ci_ruc": factura[2],
        "fecha_hora": factura[3],
        "servicio": factura[4],
        "total": factura[5]
    }

    # Renderizar la plantilla imprimible
    return render_template('imprimir_factura.html', factura=factura_dict)

@app.route('/trabajadores.html')
def pagtrabajadores():
    return render_template('pg_trabajadores.html')

@app.route('/trabajador', methods=['POST'])
def buscar_trabajador():
    data = request.json
    cedula = data.get('cedula', None)

    cursor = mysql.connection.cursor()

    if cedula:
        # Buscar trabajadores por cédula
        query = """SELECT id_trabajador, nombres, apellidos, cedula, contrato, fecha_contrato, salario 
                   FROM trabajador WHERE cedula LIKE %s"""
        cursor.execute(query, (f"%{cedula}%",))
    else:
        # Obtener todos los trabajadores si no se envió una cédula
        query = """SELECT id_trabajador, nombres, apellidos, cedula, contrato, fecha_contrato, salario 
                   FROM trabajador"""
        cursor.execute(query)

    trabajadores = cursor.fetchall()
    cursor.close()

    if not trabajadores:
        return jsonify({'error': 'No se encontraron trabajadores'}), 404

    # Convertir los resultados en una lista de diccionarios
    trabajadores_data = [
        {
            'id_trabajador': trabajador[0],
            'nombres': trabajador[1],
            'apellidos': trabajador[2],
            'cedula': trabajador[3],
            'contrato': trabajador[4],
            'fecha_contrato': trabajador[5].strftime('%Y-%m-%d'),
            'salario': trabajador[6]
        }
        for trabajador in trabajadores
    ]

    return jsonify(trabajadores_data), 200

# Ruta para agregar o actualizar un trabajador
@app.route('/trabajador/agregar-actualizar', methods=['POST'])
def agregar_actualizar_trabajador():
    data = request.json
    nombres = data.get('nombres', None)
    apellidos = data.get('apellidos', None)
    cedula = data.get('cedula', None)
    contrato = data.get('contrato', None)
    fecha_contrato = data.get('fecha_contrato', None)
    salario = data.get('salario', None)

    if not (nombres and apellidos and cedula and contrato and fecha_contrato and salario):
        return jsonify({'error': 'Todos los campos son obligatorios'}), 400

    cursor = mysql.connection.cursor()

    # Verificar si el trabajador ya existe por cédula
    query_check = "SELECT id_trabajador FROM trabajador WHERE cedula = %s"
    cursor.execute(query_check, (cedula,))
    trabajador = cursor.fetchone()

    if trabajador:
        # Actualizar trabajador existente
        query_update = """UPDATE trabajador SET nombres=%s, apellidos=%s, contrato=%s, 
                          fecha_contrato=%s, salario=%s WHERE cedula=%s"""
        cursor.execute(query_update, (nombres, apellidos, contrato, fecha_contrato, salario, cedula))
    else:
        # Insertar nuevo trabajador
        query_insert = """INSERT INTO trabajador (nombres, apellidos, cedula, contrato, fecha_contrato, salario) 
                          VALUES (%s, %s, %s, %s, %s, %s)"""
        cursor.execute(query_insert, (nombres, apellidos, cedula, contrato, fecha_contrato, salario))

    mysql.connection.commit()
    return jsonify({'message': 'Trabajador guardado/actualizado correctamente'}), 200




# Ruta para mostrar la página de inicio de sesión del administrador
@app.route('/admin')
def admin_login_page():
    return render_template('pg_admin_login.html')

# Ruta para procesar el inicio de sesión del administrador
@app.route('/adminLogin', methods=['POST'])
def admin_login():
    data = request.json
    cedula = data.get('cedula')
    clave = data.get('clave')

    cursor = mysql.connection.cursor()
    query = "SELECT ad.id_admin, tb.cedula, tb.nombres, tb.apellidos FROM administrador as ad  inner join trabajador as tb on tb.id_trabajador=ad.id_trabajador WHERE tb.cedula = %s AND ad.clave = %s;"
    cursor.execute(query, (cedula, clave))
    admin_data = cursor.fetchone()
    cursor.close()

    if admin_data:
        session['admin_id'] = admin_data[0]
        session['logged_in'] = True
        return jsonify({"id_admin": admin_data[0], "nombre": f"{admin_data[2]} {admin_data[3]}"})
    else:
        return jsonify({"error": "Credenciales no válidas para Administrador."}), 404
