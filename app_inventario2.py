import sqlite3

# Configurar la conexión a la base de datos SQLite
DATABASE = 'inventario.db'

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
        self.productos = []  # Lista de productos en el inventario (variable de clase)

    # Este método permite crear objetos de la clase "Producto" y agregarlos al inventario.
    def agregar_producto(self, codigo, descripcion, cantidad, precio,modelo,formato,imagen,marca):
        nuevo_producto = Producto(codigo, descripcion, cantidad, precio,modelo,formato,imagen,marca)
        self.productos.append(nuevo_producto)  # Agrega un nuevo producto a la lista

    # Este método permite consultar datos de productos que están en el inventario
    # Devuelve el producto correspondiente al código proporcionado o False si no existe.
    def consultar_producto(self, codigo):
        for producto in self.productos:
            if producto.codigo == codigo:
                return producto # Retorna un objeto
        return False

    # Este método permite modificar datos de productos que están en el inventario
    # Utiliza el método consultar_producto del inventario y modificar del producto.
    def modificar_producto(self, codigo, nueva_descripcion, nueva_cantidad, nuevo_precio, nuevo_modelo, nuevo_formato, nueva_imagen, nueva_marca):
        producto = self.consultar_producto(codigo)
        if producto:
            producto.modificar(nueva_descripcion, nueva_cantidad, nuevo_precio, nuevo_modelo, nuevo_formato, nueva_imagen, nueva_marca)

    # Este método elimina el producto indicado por codigo de la lista mantenida en el inventario.
    def eliminar_producto(self, codigo):
        eliminar = False
        for producto in self.productos:
            if producto.codigo == codigo:
                eliminar = True
                producto_eliminar = producto       
        if eliminar == True:
            self.productos.remove(producto_eliminar)
            print(f'Producto {codigo} eliminado.')
        else:
            print(f'Producto {codigo} no encontrado.')

    # Este método imprime en la terminal una lista con los datos de los productos que figuran en el inventario.
    def listar_productos(self):
        print("-"*50)
        print("Lista de productos en el inventario:")
        print("Código\tDescripción\t\tCant\tPrecio\tmodelo\tformato\timagen\tmarca")
        for producto in self.productos:
            print(f'{producto.codigo}\t{producto.descripcion}\t{producto.cantidad}\t{producto.precio}\t{producto.modelo}\t{producto.formato}\t{producto.imagen}\t{producto.marca}')
        print("-"*50)

class Carrito:
    # Definimos el constructor e inicializamos los atributos de instancia
    def __init__(self):
        self.items = []  # Lista de items en el carrito (variable de clase)

    # Este método permite agregar productos del inventario al carrito.
    def agregar(self, codigo, cantidad, inventario):
        # Nos aseguramos que el producto esté en el inventario
        producto = inventario.consultar_producto(codigo)
        if producto is False: 
            print("El producto no existe.")
            return False

        # Verificamos que la cantidad en stock sea suficiente
        if producto.cantidad < cantidad:
            print("Cantidad en stock insuficiente.")
            return False

        # Si existe y hay stock, vemos si ya existe en el carrito.
        for item in self.items:
            if item.codigo == codigo:
                item.cantidad += cantidad
                # Actualizamos la cantidad en el inventario
                producto = inventario.consultar_producto(codigo)
                producto.modificar(producto.descripcion, producto.cantidad - cantidad, producto.precio,producto.modelo,producto.formato,producto.imagen,producto.marca)
                return True

        # Si no existe en el carrito, lo agregamos como un nuevo item.
        nuevo_item = Producto(codigo, producto.descripcion, cantidad, producto.precio,producto.modelo,producto.formato,producto.imagen,producto.marca)
        self.items.append(nuevo_item)
        # Actualizamos la cantidad en el inventario
        producto = inventario.consultar_producto(codigo)
        producto.modificar(producto.descripcion, producto.cantidad - cantidad, producto.precio,producto.modelo,producto.formato,producto.imagen,producto.marca)
        return True

    # Este método quita unidades de un elemento del carrito, o lo elimina.
    def quitar(self, codigo, cantidad, inventario):
        for item in self.items:
            if item.codigo == codigo:
                if cantidad > item.cantidad:
                    print("Cantidad a quitar mayor a la cantidad en el carrito.")
                    return False
                item.cantidad -= cantidad
                if item.cantidad == 0:
                    self.items.remove(item)
                # Actualizamos la cantidad en el inventario
                producto = inventario.consultar_producto(codigo)
                producto.modificar(producto.descripcion, producto.cantidad + cantidad, producto.precio,producto.modelo,producto.formato,producto.imagen,producto.marca)
                return True

        # Si el bucle finaliza sin novedad, es que ese producto NO ESTA en el carrito.
        print("El producto no se encuentra en el carrito.")
        return False

    def mostrar(self):
        print("-"*50)
        print("Lista de productos en el carrito:")
        print("Código\tDescripción\t\tCant\timagen\tPrecio")
        for item in self.items:
            print(f'{item.codigo}\t{item.descripcion}\t{item.cantidad}\t{item.imagen}\t{item.precio}')
        print("-"*50)



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


# Programa principal (test de la clase carrito)

# Crear una instancia de la clase Inventario
mi_inventario = Inventario()

# Crear una instancia de la clase Carrito
mi_carrito = Carrito()

# Crear 5 productos y agregarlos al inventario
mi_inventario.agregar_producto(1, 'Teclado mecanico', 10, 4500,'k552','tkl','URL','Red Dragon')
mi_inventario.agregar_producto(2, 'Teclado dividido', 20, 4800,'moonlander','linear','url','asd')
mi_inventario.agregar_producto(3, 'Teclado Mecánico USB', 2000, 4800,'moonlander','split','url','zkl')
mi_inventario.agregar_producto(4, 'Teclado mecanico', 10, 4500,'k552','tkl','URL','Red Dragon')
mi_inventario.agregar_producto(5, 'Teclado dividido', 20, 4800,'moonlander','linear','url','asd')

# Listar todos los productos del inventario
mi_inventario.listar_productos()

# Agregar 2 productos al carrito
mi_carrito.agregar(1, 2, mi_inventario) # Agregar 2 unidades del producto con código 1 al carrito
mi_carrito.agregar(3, 4, mi_inventario) # Agregar 1 unidad del producto con código 3 al carrito
mi_carrito.quitar (1, 1, mi_inventario) # Quitar 1 unidad del producto con código 1 al carrito
# Listar todos los productos del carrito
mi_carrito.mostrar()
# Quitar 1 producto al carrito
mi_carrito.quitar (1, 1, mi_inventario) # Quitar 1 unidad del producto con código 1 al carrito
# Listar todos los productos del carrito
mi_carrito.mostrar()
# Mostramos el inventario
mi_inventario.listar_productos()
