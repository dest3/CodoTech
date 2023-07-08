import sqlite3

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
            print("Ya existe un producto con ese código.")
            return False
        sql = f'INSERT INTO productos VALUES ({codigo}, "{descripcion}", {cantidad}, {precio}, "{modelo}", "{formato}", "{imagen}", "{marca}");'#genera interaccion sql carga 
        self.cursor.execute(sql) #insertar una nueva fila en la tabla "productos"
        self.conexion.commit()#guarda el cambio
        return True

    # Este método permite consultar datos de productos que están en el inventario
    # Devuelve el producto correspondiente al código proporcionado o False si no existe.

    def consultar_producto(self, codigo):
        sql = f'SELECT * FROM productos WHERE codigo = {codigo};'#crea un string con el id codigo del producto
        self.cursor.execute(sql) #busca el codigo
        row = self.cursor.fetchone()#trae la primer linea de los resultados
        if row:#si encuentra el codigo
            codigo, descripcion, cantidad, precio, modelo, formato, imagen, marca = row #crea tula row
            return Producto(codigo, descripcion, cantidad, precio, modelo, formato, imagen, marca)
        return False


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

    # Este método elimina el producto indicado por codigo de la lista mantenida en el inventario.
    def eliminar_producto(self, codigo):
        sql = f'DELETE FROM productos WHERE codigo = {codigo};' #genera el fstring con la sentencia slq que eliminara el producto con el id codigo
        self.cursor.execute(sql)#ejecuta la sentencia sql
        if self.cursor.rowcount > 0:#veridica si se elimino al menos una fila de la bd
            print(f'Producto {codigo} eliminado.')
            self.conexion.commit()#confirma 
        else:#en caso de que no encuentre codigo
            print(f'Producto {codigo} no encontrado.')


    # Este método imprime en la terminal una lista con los datos de los productos que figuran en el inventario.
    def listar_productos(self):
        print("-"*50)
        print("Lista de productos en el inventario:")
        print("Código\tDescripción\t\tCant\tPrecio\tmodelo\tformato\timagen\tmarca")
        self.cursor.execute("SELECT * FROM productos")#selecciona todos los productos de la tabla productos
        rows = self.cursor.fetchall()#recupera todas las filas de la respuesta slq
        for row in rows:#recorre las cuplas para imprimir el resultado 
            codigo, descripcion, cantidad, precio, modelo, formato, imagen, marca = row
            print(f'{codigo}\t{descripcion}\t{cantidad}\t{precio}\t{modelo}\t{formato}\t{imagen}\t{marca}')
        print("-"*50)

class Carrito:
    # Definimos el constructor e inicializamos los atributos de instancia
    def __init__(self):
        self.conexion = sqlite3.connect('inventario.db')  # Conexión a la BD
        self.cursor = self.conexion.cursor()#crea cursor para ejecutar consultas sql
        self.items = []#inicia una lista vacia

    # Este método permite agregar productos del inventario al carrito.
    def agregar(self, codigo, cantidad, inventario):
        producto = inventario.consultar_producto(codigo)#obtiene el codigo mediante el metodo consultar_producto
        
        if producto is False:#si no encuentra producto
            print("El producto no existe.")
            return False
        if producto.cantidad < cantidad:#si producto.cantidad es menor a la cantidad solicitada
            print("Cantidad en stock insuficiente.")
            return False

        for item in self.items:#recorre los items del carrito
            if item.codigo == codigo:#si encuentra un itep con el mismo codigo lo acumula
                item.cantidad += cantidad
                sql = f'UPDATE productos SET cantidad = cantidad - {cantidad}  WHERE codigo = {codigo};'#crea el fstring con la sentencia sql 
                self.cursor.execute(sql)#ejecuta la sentencia
                self.conexion.commit()#actualiza 
                return True

        nuevo_item = Producto(codigo, producto.descripcion, cantidad, producto.precio, producto.modelo, producto.formato, producto.imagen, producto.marca)#crea nuevo producto
        self.items.append(nuevo_item)#actualiza el item nuevo en la lista
        sql = f'UPDATE productos SET cantidad = cantidad - {cantidad}  WHERE codigo = {codigo};'#crea el fstring con el comando sql
        self.cursor.execute(sql)#ejecuta la sentencia
        self.conexion.commit()#actualza
        return True

    # Este método quita unidades de un elemento del carrito, o lo elimina.
    
    def quitar(self, codigo, cantidad, inventario):
        for item in self.items:#recorre los items en inventario
            if item.codigo == codigo:#si encuentra el codigo dado 
                if cantidad > item.cantidad:#prueba que la cantidad que se quiere sacar sea menor a la cantidad del carrito 
                    print("Cantidad a quitar mayor a la cantidad en el carrito.")
                    return False
                item.cantidad -= cantidad#resta la cantidad del producto solicitado
                if item.cantidad == 0:#si el item queda en 0
                    self.items.remove(item)#se elimina el item de la lista
                sql = f'UPDATE productos SET cantidad = cantidad + {cantidad} WHERE codigo = {codigo};'#se crea el fstring para ejecutar la sentencia sql
                self.cursor.execute(sql)#ejecuta la sentencia
                self.conexion.commit()#actualiza
                return True

    #este metodo lista los objetos en del carrito
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
# # Listar todos los productos del carrito
# mi_carrito.mostrar()
# # Mostramos el inventario
# mi_inventario.listar_productos()



# # Programa principal(test de la base de datos )
# # Crear la base de datos y la tabla si no existen
# create_database()

# # Crear una instancia de la clase Inventario
# mi_inventario = Inventario()

# # Agregar productos al inventario
# mi_inventario.agregar_producto(1, 'Teclado mecanico', 10, 4500,'k552','tkl','URL','Red Dragon')
# mi_inventario.agregar_producto(2, 'Teclado dividido', 20, 4800,'moonlander','linear','url','asd')
# mi_inventario.agregar_producto(3, 'Teclado Mecánico USB', 2000, 4800,'moonlander','split','url','zkl')
# mi_inventario.agregar_producto(4, 'Teclado mecanico', 10, 4500,'k552','tkl','URL','Red Dragon')
# mi_inventario.agregar_producto(5, 'Teclado dividido', 20, 4800,'moonlander','linear','url','asd')

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
