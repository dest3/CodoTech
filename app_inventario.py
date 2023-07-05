import sqlite3

from flask import Flask, jsonify, request

from flask_cors import CORS


# Configurar la conexión a la base de datos SQLite
DATABASE = "inventario.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# Crear la tabla 'productos' si no existe
def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS productos (
            codigo INTEGER PRIMARY KEY,
            descripcion TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            precio REAL NOT NULL
        ) """
    )
    conn.commit()
    cursor.close()
    conn.close()


# Verificar si la base de datos existe, si no, crearla y crear la tabla
def create_database():
    conn = sqlite3.connect(DATABASE)
    conn.close()
    create_table()


# Programa principal
# Crear la base de datos y la tabla si no existen
create_database()


class Producto:
    # Definimos el constructor e inicializamos los atributos de instancia
    def __init__(
        self,
        codigo,
        descripcion,
        cantidad,
        precio,
    ):
        self.codigo = codigo  # Código
        self.descripcion = descripcion  # Descripción
        self.cantidad = cantidad  # Cantidad disponible (stock)
        self.precio = precio  # Precio

    # Este método permite modificar un producto.
    def modificar(self, nueva_descripcion, nueva_cantidad, nuevo_precio):
        self.descripcion = nueva_descripcion  # Modifica la descripción
        self.cantidad = nueva_cantidad  # Modifica la cantidad
        self.precio = nuevo_precio  # Modifica el precio


class Inventario:
    def __init__(self):
        self.conexion = get_db_connection()
        self.cursor = self.conexion.cursor()
    
    
    def agregar_producto(self, codigo, descripcion, cantidad, precio, imagen):
        producto_existente = self.consultar_producto(codigo)
        if producto_existente:
            return jsonify({'message': 'Ya existe un producto con ese código.'}), 400
        sql = f'INSERT INTO productos VALUES ({codigo}, "{descripcion}", {cantidad}, {precio}, {imagen});'
        self.cursor.execute(sql)
        self.conexion.commit()
        return jsonify({"message": "Producto agregado correctamente."}), 200

    def consultar_producto(self, codigo):
        sql = f"SELECT * FROM productos WHERE codigo = {codigo};"
        self.cursor.execute(sql)
        row = self.cursor.fetchone()
        if row:
            codigo, descripcion, cantidad, precio, imagen = row
            return Producto(codigo, descripcion, cantidad, precio, imagen)
        return None

    def modificar_producto(
        self, codigo, nueva_descripcion, nueva_cantidad, nuevo_precio
    ):
        producto = self.consultar_producto(codigo)
        if producto:
            producto.modificar(nueva_descripcion, nueva_cantidad, nuevo_precio)
            sql = f'UPDATE productos SET descripcion = "{nueva_descripcion}", cantidad = {nueva_cantidad}, precio = {nuevo_precio} WHERE codigo = {codigo};'
            self.cursor.execute(sql)
            self.conexion.commit()
            return jsonify({"message": "Producto modificado correctamente."}), 200
        return jsonify({"message": "Producto no encontrado."}), 404

    def eliminar_producto(self, codigo):
        sql = f"DELETE FROM productos WHERE codigo = {codigo};"
        self.cursor.execute(sql)
        if self.cursor.rowcount > 0:
            self.conexion.commit()
            return jsonify({"message": "Producto eliminado correctamente."}), 200
        return jsonify({"message": "Producto no encontrado."}), 404

    def listar_productos(self):
        self.cursor.execute("SELECT * FROM productos")
        rows = self.cursor.fetchall()
        productos = []
        for row in rows:
            codigo, descripcion, cantidad, precio = row
            producto = {
                "codigo": codigo,
                "descripcion": descripcion,
                "cantidad": cantidad,
                "precio": precio,
            }
            productos.append(producto)
        return jsonify(productos), 200


class Carrito:
    def __init__(self):
        self.conexion = get_db_connection()
        self.cursor = self.conexion.cursor()
        self.items = []

    def agregar(self, codigo, cantidad, inventario):
        producto = inventario.consultar_producto(codigo)
        if producto is None:
            return jsonify({"message": "El producto no existe."}), 404
        if producto.cantidad < cantidad:
            return jsonify({"message": "Cantidad en stock insuficiente."}), 400

        for item in self.items:
            if item.codigo == codigo:
                item.cantidad += cantidad
                sql = f"UPDATE productos SET cantidad = cantidad - {cantidad}  WHERE codigo = {codigo};"
                self.cursor.execute(sql)
                self.conexion.commit()
                return (
                    jsonify({"message": "Producto agregado al carrito correctamente."}),
                    200,
                )

        nuevo_item = Producto(codigo, producto.descripcion, cantidad, producto.precio)
        self.items.append(nuevo_item)
        sql = f"UPDATE productos SET cantidad = cantidad - {cantidad}  WHERE codigo = {codigo};"
        self.cursor.execute(sql)
        self.conexion.commit()
        return jsonify({"message": "Producto agregado al carrito correctamente."}), 200

    def quitar(self, codigo, cantidad, inventario):
        for item in self.items:
            if item.codigo == codigo:
                if cantidad > item.cantidad:
                    return (
                        jsonify(
                            {
                                "message": "Cantidad a quitar mayor a la cantidad en el carrito."
                            }
                        ),
                        400,
                    )
                item.cantidad -= cantidad
                if item.cantidad == 0:
                    self.items.remove(item)
                sql = f"UPDATE productos SET cantidad = cantidad + {cantidad} WHERE codigo = {codigo};"
                self.cursor.execute(sql)
                self.conexion.commit()
                return (
                    jsonify({"message": "Producto quitado del carrito correctamente."}),
                    200,
                )
        return jsonify({"message": "El producto no se encuentra en el carrito."}), 404

    def mostrar(self):
        productos_carrito = []
        for item in self.items:
            producto = {
                "codigo": item.codigo,
                "descripcion": item.descripcion,
                "cantidad": item.cantidad,
                "precio": item.precio,
            }
            productos_carrito.append(producto)
        return jsonify(productos_carrito), 200


app = Flask(__name__)
CORS(app)


carrito = Carrito()  # Instanciamos un carrito
inventario = Inventario()  # Instanciamos un inventario


# Ruta para obtener los datos de un producto según su código
@app.route("/productos/<int:codigo>", methods=["GET"])
def obtener_producto(codigo):
    producto = inventario.consultar_producto(codigo)
    if producto:
        return (
            jsonify(
                {
                    "codigo": producto.codigo,
                    "descripcion": producto.descripcion,
                    "cantidad": producto.cantidad,
                    "precio": producto.precio,
                }
            ),
            200,
        )
    return jsonify({"message": "Producto no encontrado."}), 404


# Ruta para obtener el index
@app.route("/")
def index():
    return "API de Inventario"


# Ruta para obtener la lista de productos del inventario
@app.route("/productos", methods=["GET"])
def obtener_productos():
    return inventario.listar_productos()


# Ruta para agregar un producto al inventario
@app.route("/productos", methods=["POST"])
def agregar_producto():
    codigo = request.json.get("codigo")
    descripcion = request.json.get("descripcion")
    cantidad = request.json.get("cantidad")
    precio = request.json.get("precio")
    imagen = request.json.get("imagen")
    return inventario.agregar_producto(codigo, descripcion, cantidad, precio, imagen)


# Ruta para modificar un producto del inventario
@app.route("/productos/<int:codigo>", methods=["PUT"])
def modificar_producto(codigo):
    nueva_descripcion = request.json.get("descripcion")
    nueva_descripcion = request.json.get("descripcion")
    nueva_cantidad = request.json.get("cantidad")
    nuevo_precio = request.json.get("precio")
    return inventario.modificar_producto(
        codigo, nueva_descripcion, nueva_cantidad, nuevo_precio
    )


# Ruta para eliminar un producto del inventario
@app.route("/productos/<int:codigo>", methods=["DELETE"])
def eliminar_producto(codigo):
    return inventario.eliminar_producto(codigo)


# Ruta para agregar un producto al carrito
@app.route("/carrito", methods=["POST"])
def agregar_carrito():
    codigo = request.json.get("codigo")
    cantidad = request.json.get("cantidad")
    inventario = Inventario()
    return carrito.agregar(codigo, cantidad, inventario)


# Ruta para quitar un producto del carrito
@app.route("/carrito", methods=["DELETE"])
def quitar_carrito():
    codigo = request.json.get("codigo")
    cantidad = request.json.get("cantidad")
    inventario = Inventario()
    return carrito.quitar(codigo, cantidad, inventario)


# Ruta para obtener el contenido del carrito
@app.route("/carrito", methods=["GET"])
def obtener_carrito():
    return carrito.mostrar()
