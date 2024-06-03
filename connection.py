

#clase connetion.py
# Librerías importadas
import psycopg2  # Para conectarse a la base de datos PostgreSQL
from tabulate import tabulate  # Para mostrar datos tabulados
from jinja2 import Template  # Para generar desprendibles de pago en formato HTML
import datetime  # Para manejar fechas y horas actuales
import matplotlib.pyplot as plt  # Para generar gráficas

# Clase para manejar la conexión a la base de datos
class DatabaseConnection:
    def __init__(self):
        # Configuración de la conexión a la base de datos
        self.dbname = "nomina_q32c"
        self.user = "postgres_user"
        self.password = "SoME4ts1YFNDgyR1nGnbqutHQrbkyNRA"
        self.host = "dpg-cokl1docmk4c739h7up0-a.ohio-postgres.render.com"
        self.port = 5432
        self.connection = None

    # Método para establecer conexión
    def connect(self):
        try:
            self.connection = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            print("Conexión exitosa a la base de datos.")
        except psycopg2.Error as e:
            print("Error al conectar a la base de datos:", e)

    # Método para cerrar conexión
    def disconnect(self):
        if self.connection:
            self.connection.close()
            print("Conexión cerrada.")

    # Método para ejecutar consultas SELECT
    def execute_query(self, query, params=None):
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
        except psycopg2.Error as e:
            print("Error al ejecutar la consulta:", e)
            return []

    # Método para ejecutar consultas INSERT, UPDATE, DELETE
    def execute_insert(self, query, params=None):
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            print("Inserción de datos exitosa.")
        except psycopg2.Error as e:
            self.connection.rollback()
            print("Error al insertar datos:", e)

    # Método para establecer la conexión al usar 'with'
    def __enter__(self):
        self.connect()
        return self

    # Método para cerrar la conexión al usar 'with'
    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.disconnect()
