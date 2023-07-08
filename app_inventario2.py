import sqlite3
from flask import Flask, jsonify, request

# Configurar la conexión a la base de datos SQLite
DATABASE = 'inventario.db'
#crea la coneccion con la bd
def get_db_connection():
    print("Obteniendo conexión...") # Para probar que se ejecuta la función
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn
# Crear la tabla 'productos' si no existe
def create_table():
    print("Creando tabla productos...") # Para probar que se ejecuta la función
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            codigo INTEGER PRIMARY KEY,
            descripcion TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            precio REAL NOT NULL,
            modelo TEXT NOT NULL,
            formato TEXT NOT NULL,
            imagen TEXT NOT NULL,
            marca TEXT NOT NULL
        ) ''')
    conn.commit()
    cursor.close()
    conn.close()
# Verificar si la base de datos existe, si no, crearla y crear la tabla
def create_database():
    print("Creando la BD...") # Para probar que se ejecuta la función
    conn = sqlite3.connect(DATABASE)
    conn.close()
    create_table()
# Programa principal
# Crear la base de datos y la tabla si no existen
create_database()


class Producto:
    # Definimos el constructor e inicializamos los atributos de instancia
    def __init__(self, codigo, descripcion, cantidad, precio,modelo,formato,imagen,marca):
        self.codigo = codigo           # Código
        self.descripcion = descripcion  # Descripción
        self.cantidad = cantidad       # Cantidad disponible (stock)
        self.precio = precio           # Precio
        self.modelo = modelo           # modelo
        self.formato = formato          #formato
        self.imagen = imagen            #imagen
        self.marca = marca              #marca

    # Este método permite modificar un producto.
    def modificar(self, nueva_descripcion, nueva_cantidad, nuevo_precio, nuevo_modelo, nuevo_formato, nueva_imagen, nueva_marca):
        self.descripcion = nueva_descripcion  # Modifica la descripción
        self.cantidad = nueva_cantidad        # Modifica la cantidad
        self.precio = nuevo_precio            # Modifica el precio
        self.modelo = nuevo_modelo
        self.formato = nuevo_formato
        self.imagen =nueva_imagen
        self.marca = nueva_marca

class Inventario:
    # Definimos el constructor e inicializamos los atributos de instancia
    def __init__(self):
        self.conexion = get_db_connection()  #Se establece la conexión a la base de datos
        self.cursor = self.conexion.cursor() #Se crea un objeto cursor a partir de la conexión a la base de datos


    def agregar_producto(self, codigo, descripcion, cantidad, precio, modelo, formato, imagen, marca):
        producto_existente = self.consultar_producto(codigo)
        if producto_existente: #comprueba que el codigo del producto no se repita
            return jsonify({'message': 'Ya existe un producto con ese código.'}), 400
            return False
        sql = f'INSERT INTO productos VALUES ({codigo}, "{descripcion}", {cantidad}, {precio}, "{modelo}", "{formato}", "{imagen}", "{marca}");'#genera interaccion sql carga 
        self.cursor.execute(sql) #insertar una nueva fila en la tabla "productos"
        self.conexion.commit()#guarda el cambio
        return jsonify({'message': 'Producto agregado correctamente.'}), 200

    # Este método permite consultar datos de productos que están en el inventario
    # Devuelve el producto correspondiente al código proporcionado o False si no existe.

    def consultar_producto(self, codigo):
        sql = f'SELECT * FROM productos WHERE codigo = {codigo};'#crea un string con el id codigo del producto
        self.cursor.execute(sql) #busca el codigo
        row = self.cursor.fetchone()#trae la primer linea de los resultados
        if row:#si encuentra el codigo
            codigo, descripcion, cantidad, precio, modelo, formato, imagen, marca = row #crea tula row
            return Producto(codigo, descripcion, cantidad, precio, modelo, formato, imagen, marca)
        return None

    # Este método permite modificar datos de productos que están en el inventario
    # Utiliza el método consultar_producto del inventario y modificar del producto.
    def modificar_producto(self, codigo, nueva_descripcion, nueva_cantidad, nuevo_precio,nuevo_modelo, nuevo_formato, nueva_imagen, nueva_marca):
        producto = self.consultar_producto(codigo)#obtiene el codigo del producto a modificar
        if producto:#en caso de encontrarlo
            producto.modificar(nueva_descripcion, nueva_cantidad, nuevo_precio, nuevo_modelo, nuevo_formato, nueva_imagen, nueva_marca)#llama a modificar 
            
            #se crea un ftring con las modificaciones de producto
            sql = f'''
            UPDATE productos 
            SET descripcion = "{nueva_descripcion}", 
                cantidad = {nueva_cantidad}, 
                precio = {nuevo_precio},
                modelo = "{nuevo_modelo}",
                formato = "{nuevo_formato}",
                imagen = "{nueva_imagen}",
                marca = "{nueva_marca}"
            WHERE codigo = {codigo};
        '''
            self.cursor.execute(sql)#actualiza la base de datso con el string guardado en sql
            self.conexion.commit()#confirma el cambio
            return jsonify({'message': 'Producto modificado correctamente.'}), 200
        return jsonify({'message': 'Producto no encontrado.'}), 404

    # Este método elimina el producto indicado por codigo de la lista mantenida en el inventario.
    def eliminar_producto(self, codigo):
        sql = f'DELETE FROM productos WHERE codigo = {codigo};' #genera el fstring con la sentencia slq que eliminara el producto con el id codigo
        self.cursor.execute(sql)#ejecuta la sentencia sql
        if self.cursor.rowcount > 0:#veridica si se elimino al menos una fila de la bd
            self.conexion.commit()#confirma 
            return jsonify({'message': 'Producto eliminado correctamente.'}), 200#mensaje de exito
        return jsonify({'message': 'Producto no encontrado.'}), 404

    # Este método imprime en la terminal una lista con los datos de los productos que figuran en el inventario.
    def listar_productos(self):
        
        self.cursor.execute("SELECT * FROM productos")#selecciona todos los productos de la tabla productos
        rows = self.cursor.fetchall()#recupera todas las filas de la respuesta slq
        productos=[]#crea lista vacia de productos
        for row in rows:#recorre las cuplas para imprimir el resultado 
            codigo, descripcion, cantidad, precio, modelo, formato, imagen, marca = row
            producto = {'codigo': codigo, 'descripcion': descripcion, 'cantidad': cantidad, 'precio': precio, 'modelo': modelo, 'formato':formato, 'imagen':imagen, 'marca':marca}#carga todos parametros en producto
            productos.append(producto)#carga producto a la lista de productos
        return jsonify(productos), 200#codigo exitoso

class Carrito:
    # Definimos el constructor e inicializamos los atributos de instancia
    def __init__(self):
        self.conexion = sqlite3.connect('inventario.db')  # Conexión a la BD
        self.cursor = self.conexion.cursor()#crea cursor para ejecutar consultas sql
        self.items = []#inicia una lista vacia

    # Este método permite agregar productos del inventario al carrito.
    def agregar(self, codigo, cantidad, inventario):
        producto = inventario.consultar_producto(codigo)#obtiene el producto mediante el metodo consultar_producto("codigo")
        
        if producto is None:#si no encuentra producto
            return jsonify({'message': 'El producto no existe.'}), 404
        if producto.cantidad < cantidad:#si producto.cantidad es menor a la cantidad solicitada
            return jsonify({'message': 'Cantidad en stock insuficiente.'}), 400

        for item in self.items:#recorre los items del carrito
            if item.codigo == codigo:#si encuentra un itep con el mismo codigo lo acumula
                item.cantidad += cantidad
                sql = f'UPDATE productos SET cantidad = cantidad - {cantidad}  WHERE codigo = {codigo};'#crea el fstring con la sentencia sql 
                self.cursor.execute(sql)#ejecuta la sentencia
                self.conexion.commit()#actualiza 
                return jsonify({'message': 'Producto agregado al carrito correctamente.'}), 200

        nuevo_item = Producto(codigo, producto.descripcion, cantidad, producto.precio, producto.modelo, producto.formato, producto.imagen, producto.marca)#crea nuevo producto
        self.items.append(nuevo_item)#actualiza el item nuevo en la lista
        sql = f'UPDATE productos SET cantidad = cantidad - {cantidad}  WHERE codigo = {codigo};'#crea el fstring con el comando sql
        self.cursor.execute(sql)#ejecuta la sentencia
        self.conexion.commit()#actualza
        return jsonify({'message': 'Producto agregado al carrito correctamente.'}), 200

    # Este método quita unidades de un elemento del carrito, o lo elimina.
    
    def quitar(self, codigo, cantidad, inventario):
        for item in self.items:#recorre los items en inventario
            if item.codigo == codigo:#si encuentra el codigo dado 
                if cantidad > item.cantidad:#prueba que la cantidad que se quiere sacar sea menor a la cantidad del carrito 
                    print("Cantidad a quitar mayor a la cantidad en el carrito.")
                    return jsonify({'message': 'Cantidad a quitar mayor a la cantidad en el carrito.'}), 400
                item.cantidad -= cantidad#resta la cantidad del producto solicitado
                if item.cantidad == 0:#si el item queda en 0
                    self.items.remove(item)#se elimina el item de la lista
                sql = f'UPDATE productos SET cantidad = cantidad + {cantidad} WHERE codigo = {codigo};'#se crea el fstring para ejecutar la sentencia sql
                self.cursor.execute(sql)#ejecuta la sentencia
                self.conexion.commit()#actualiza
                return jsonify({'message': 'Producto quitado del carrito correctamente.'}), 200
        return jsonify({'message': 'El producto no se encuentra en el carrito.'}), 404

    #este metodo lista los objetos en del carrito
    def mostrar(self):
        productos_carrito = []#crea lista de productos 
        for item in self.items:#recorre los items de el carritos
            producto = {'codigo': item.codigo, 'descripcion': item.descripcion, 'cantidad': item.cantidad,'imagen':item.imagen, 'precio': item.precio}
            productos_carrito.append(producto)
        return jsonify(productos_carrito), 200


app = Flask(__name__)

carrito = Carrito()         # Instanciamos un carrito
inventario = Inventario()   # Instanciamos un inventario


# Ruta para obtener los datos de un producto según su código
@app.route('/productos/<int:codigo>', methods=['GET'])#define que para entrar a cada productos se deve ingresar /productos/"codigo"
def obtener_producto(codigo):
    producto = inventario.consultar_producto(codigo)#obtiene producto por el codigo
    if producto:#si encuentra un producto
        #devuelve un objeto json con las caracteristicas del producto
        return jsonify({
            'codigo': producto.codigo,
            'descripcion': producto.descripcion,
            'cantidad': producto.cantidad,
            'precio': producto.precio,
            'modelo': producto.modelo,
            'formato': producto.formato,
            'imagen': producto.imagen,
            'marca': producto.marca
        }), 200#codigo de exito
    return jsonify({'message': 'Producto no encontrado.'}), 404#en caso de no encontrar el producto

# Ruta para obtener la lista de productos del inventario
@app.route('/')
def index():
    return 'API de Inventario'#si vez esto al correr el programa esta funcionando 

# Ruta para obtener la lista de productos del inventario
@app.route('/productos', methods=['GET'])
def obtener_productos():
    return inventario.listar_productos()

# Ruta para agregar un producto al inventario
@app.route('/productos', methods=['POST'])
def agregar_producto():
    codigo = request.json.get('codigo')
    descripcion = request.json.get('descripcion')
    cantidad = request.json.get('cantidad')
    precio = request.json.get('precio')
    modelo = request.json.get('modelo')
    formato= request.json.get('formato')
    imagen= request.json.get('imagen')
    marca= request.json.get('marca')
    return inventario.agregar_producto(codigo, descripcion, cantidad, precio, modelo, formato, imagen, marca)


# Ruta para modificar un producto del inventario
@app.route('/productos/<int:codigo>', methods=['PUT'])
def modificar_producto(codigo):
    nueva_descripcion = request.json.get('descripcion')
    nueva_cantidad = request.json.get('cantidad')
    nuevo_precio = request.json.get('precio')
    nuevo_modelo= request.json.get('modelo')
    nuevo_formato = request.json.get('formato')
    nueva_imagen = request.json.get('formato')
    nueva_marca = request.json.get('marca')
    return inventario.modificar_producto( codigo, nueva_descripcion, nueva_cantidad, nuevo_precio, nuevo_modelo, nuevo_formato, nueva_imagen, nueva_marca)

# Ruta para eliminar un producto del inventario
@app.route('/productos/<int:codigo>', methods=['DELETE'])
def eliminar_producto(codigo):
    return inventario.eliminar_producto(codigo)

# Ruta para agregar un producto al carrito
@app.route('/carrito', methods=['POST'])
def agregar_carrito():
    codigo = request.json.get('codigo')
    cantidad = request.json.get('cantidad')
    inventario = Inventario()
    return carrito.agregar(codigo, cantidad, inventario)

# Ruta para quitar un producto del carrito
@app.route('/carrito', methods=['DELETE'])
def quitar_carrito():
    codigo = request.json.get('codigo')
    cantidad = request.json.get('cantidad')
    inventario = Inventario()
    return carrito.quitar(codigo, cantidad, inventario)

# Ruta para obtener el contenido del carrito
@app.route('/carrito', methods=['GET'])
def obtener_carrito():
    return carrito.mostrar()



# # Programa principal (test de clase producto)
# producto = Producto(1, 'Teclado USB 101 teclas', 10, 4500,'k552','tkl','URL','Red Dragon')
# # Accedemos a los atributos del objeto
# print(f'{producto.codigo} | {producto.descripcion} | {producto.cantidad} | {producto.precio} |{producto.modelo} | {producto.formato} |{producto.imagen} | {producto.marca}')
# # Modificar los datos del producto
# producto.modificar('Teclado Mecánico USB', 20, 4800,'moonlander','split','url','zkl') 
# print(f'{producto.codigo} | {producto.descripcion} | {producto.cantidad} | {producto.precio} |{producto.modelo} | {producto.formato} |{producto.imagen} | {producto.marca}')


# # Programa principal (test de clase inventario)
# # Crear una instancia de la clase Inventario
# mi_inventario = Inventario() 

# # Agregar productos 
# mi_inventario.agregar_producto(1, 'Teclado mecanico', 10, 4500,'k552','tkl','URL','Red Dragon')
# mi_inventario.agregar_producto(2, 'Teclado dividido', 20, 4800,'moonlander','linear','url','asd')
# mi_inventario.agregar_producto(3, 'Teclado Mecánico USB', 20, 4800,'moonlander','split','url','zkl')
# mi_inventario.agregar_producto(4, 'Teclado mecanico', 10, 4500,'k552','tkl','URL','Red Dragon')
# mi_inventario.agregar_producto(5, 'Teclado dividido', 20, 4800,'moonlander','linear','url','asd')

# # Consultar un producto 
# producto = mi_inventario.consultar_producto(3)
# if producto != False:
#     print(f'Producto encontrado:\nCódigo: {producto.codigo}\nDescripción: {producto.descripcion}\nCantidad: {producto.cantidad}\nPrecio: {producto.precio}\nModelo: {producto.modelo}\nformato: {producto.formato}\nimagen: {producto.imagen}\nmarca: {producto.marca}')  
# else:
#     print("Producto no encontrado.")

# # Modificar un producto 
# mi_inventario.modificar_producto(3, 'Monitor LCD 24 pulgadas', 5, 62000, 'x123','gamer','url','lg')

# # Listar todos los productos
# mi_inventario.listar_productos()

# # Eliminar un producto 
# mi_inventario.eliminar_producto(2)

# # Confirmamos que haya sido eliminado
# mi_inventario.listar_productos()


# # Programa principal (test de la clase carrito)
# # Crear una instancia de la clase Inventario
# mi_inventario = Inventario()

# # Crear una instancia de la clase Carrito
# mi_carrito = Carrito()

# # Crear 5 productos y agregarlos al inventario
# mi_inventario.agregar_producto(1, 'Teclado mecanico', 10, 4500,'k552','tkl','URL','Red Dragon')
# mi_inventario.agregar_producto(2, 'Teclado dividido', 20, 4800,'moonlander','linear','url','asd')
# mi_inventario.agregar_producto(3, 'Teclado Mecánico USB', 2000, 4800,'moonlander','split','url','zkl')
# mi_inventario.agregar_producto(4, 'Teclado mecanico', 10, 4500,'k552','tkl','URL','Red Dragon')
# mi_inventario.agregar_producto(5, 'Teclado dividido', 20, 4800,'moonlander','linear','url','asd')

# # Listar todos los productos del inventario
# mi_inventario.listar_productos()

# # Agregar 2 productos al carrito
# mi_carrito.agregar(1, 2, mi_inventario) # Agregar 2 unidades del producto con código 1 al carrito
# mi_carrito.agregar(3, 4, mi_inventario) # Agregar 1 unidad del producto con código 3 al carrito
# mi_carrito.quitar (1, 1, mi_inventario) # Quitar 1 unidad del producto con código 1 al carrito
# # Listar todos los productos del carrito
# mi_carrito.mostrar()
# # Quitar 1 producto al carrito
# mi_carrito.quitar (1, 1, mi_inventario) # Quitar 1 unidad del producto con código 1 al carrito
# # Listar todos los productos del cgarrito
# mi_carrito.mostrar()
# # Mostramos el inventario
# mi_inventario.listar_productos()

# # Programa principal(test de la base de datos )
# # Crear la base de datos y la tabla si no existen
# create_database()

# # Crear una instancia de la clase Inventario
# mi_inventario = Inventario()

# # Agregar productos al inventario
# inventario.agregar_producto(1, 'Teclado mecanico', 10, 4500,'k552','tkl','URL','Red Dragon')
# inventario.agregar_producto(2, 'Teclado dividido', 20, 4800,'moonlander','linear','url','asd')
# inventario.agregar_producto(3, 'Teclado Mecánico USB', 2000, 4800,'moonlander','split','url','zkl')
# inventario.agregar_producto(4, 'Teclado mecanico', 10, 4500,'k552','tkl','URL','Red Dragon')
# inventario.agregar_producto(5, 'Teclado dividido', 20, 4800,'moonlander','linear','url','asd')

# # Consultar algún producto del inventario
# print(mi_inventario.consultar_producto(1)) #Existe, se muestra la dirección de memoria
# print(mi_inventario.consultar_producto(6)) #No existe, se muestra False

# # Listar los productos del inventario
# mi_inventario.listar_productos()

# # Modificar un producto del inventario
# mi_inventario.modificar_producto(2, "Mouse Rojo", 10, 19.99, "ergonomico", "gamer", "url", "logitech")

# # Listar nuevamente los productos del inventario para ver la modificación
# mi_inventario.listar_productos()

# # Eliminar un producto
# mi_inventario.eliminar_producto(3)

# # Listar nuevamente los productos del inventario para ver la eliminación
# mi_inventario.listar_productos()


# # Crear una instancia de la clase Carrito
# mi_carrito = Carrito()
# # Agregar 2 unidades del producto con código 1 al carrito
# mi_carrito.agregar(1, 2, mi_inventario)  
# # Agregar 1 unidad del producto con código 2 al carrito
# mi_carrito.agregar(2, 1, mi_inventario)  

# # Mostrar el contenido del carrito y del inventario
# mi_carrito.mostrar()
# mi_inventario.listar_productos()

# # Quitar 1 unidad del producto con código 1 al carrito y 1 unidad del producto con código 2 al carrito
# mi_carrito.quitar(1, 1, mi_inventario)
# mi_carrito.quitar(2, 1, mi_inventario)

# # Mostrar el contenido del carrito y del inventario
# mi_carrito.mostrar()
# mi_inventario.listar_productos()


# Finalmente, si estamos ejecutando este archivo, lanzamos app.
if __name__ == '__main__':
    app.run()
