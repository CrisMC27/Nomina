#clase main.py
import datetime
from connection import DatabaseConnection
from tabulate import tabulate 
import matplotlib.pyplot as plt 

# Lista para almacenar los empleados registrados
empleados = []

# Función para mostrar el menú principal y obtener la opción del usuario
def mostrar_menu_principal():
    print("\nBienvenido al Sistema de Informes:")
    print("\n1. Registro de Personal")
    print("2. Desprendible de Pago")
    print("3. Informe de Devengados y Descuentos")
    print("4. Generar Horas Extras")
    print("5. Generar prima legal")
    print("6. Estadísticas")
    print("7. Generar Gráficas")
    print("8. Mostrar Base de Empleados")
    print("9. Salir")
    opcion = input("\nPor favor, seleccione una opción: ")
    return opcion

# Función para manejar la opción del menú principal
def manejar_opcion_principal(opcion):
    if opcion == "1":
        registro_personal()
    elif opcion == "2":
        #cedula = input("Ingrese la cédula del empleado para mostrar el desprendible de pago: ")
        #mostrar_desprendible_pago(cedula)
        generar_desprendible_pago()
    elif opcion == "3":
        cedula = input("Ingrese la cédula del empleado: ")
        aplicar_subsidio_transporte(cedula)
        aplicar_descuento_salud_pension() 
    elif opcion == "4":
        mostrar_menu_horas_extras() 
    elif opcion == "5":
        generar_prima_legal()
    elif opcion == "6":
        generar_estadisticas()
    elif opcion == "7":
        generar_graficas()
    elif opcion == "8":
        mostrar_base_empleados()
    elif opcion == "9":
        print("Gracias por usar el Sistema de Informes. ¡Hasta luego!")
        exit()
    else:
        print("Opción inválida. Por favor, seleccione una opción válida.")

#------------------------------------------------------------------------------------------------------------        

"""
    Función para el registro de personal en la base de datos.

    Solicita al usuario ingresar los datos del empleado, incluyendo cédula, nombres, apellidos, cargo, centro de costo,
    sueldo, subsidio de transporte, EPS, fondo de pensiones y fecha de ingreso. Luego, inserta estos datos en la tabla
    'Empleado' de la base de datos.

    Nota: Esta función utiliza la clase 'DatabaseConnection' para realizar la conexión y la inserción de datos en la
    base de datos.
"""

# Función para el registro de personal
def registro_personal():
    # Solicitar información del empleado al usuario

    cedula = input("Ingrese la cédula del empleado: ")
    nombres = input("Ingrese los nombres del empleado: ")
    apellidos = input("Ingrese los apellidos del empleado: ")
    cargo = input("Ingrese el cargo del empleado: ")
    centro_costo = input("Ingrese el centro de costo del empleado: ")
    sueldo = Decimal(input("Ingrese el sueldo del empleado: "))
    subsidio_transporte = Decimal(input("Ingrese el subsidio de transporte del empleado: "))
    eps = input("Ingrese la EPS del empleado: ")
    pension = input("Ingrese el fondo de pensiones del empleado: ")
    fecha_ingreso = input("Ingrese la fecha de ingreso del empleado (AAAA-MM-DD): ")
    
    # Insertar los datos del empleado en la base de datos
    with DatabaseConnection() as connection:
        query = """
        INSERT INTO Empleado (cedula, nombres, apellidos, cargo, centro_costo, sueldo, subsidio_transporte, eps, pension, fecha_ingreso)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        connection.execute_query(query, (cedula, nombres, apellidos, cargo, centro_costo, sueldo, subsidio_transporte, eps, pension, fecha_ingreso))
    
    # Confirmar que el empleado ha sido registrado exitosamente
    print("Empleado registrado exitosamente.")

#------------------------------------------------------------------------------------------------------------
# Función para buscar empleado por cédula
def buscar_empleado_por_cedula(cedula):
    
    # Establecer conexión con la base de datos
    with DatabaseConnection() as connection:
                
        # Consultar la base de datos para obtener el empleado con la cédula especificada

        query = "SELECT * FROM Empleado WHERE cedula = %s"
        params = (cedula,)
        result = connection.execute_query(query, params)

        # Verificar si se encontró un empleado con la cédula especificada
        if result:

            # Extraer los datos del primer resultado (asumiendo que la cédula es única)
            empleado = result[0]

            # Crear un diccionario con los datos del empleado y devolverlo

            return {
                "cedula": empleado[0],
                "nombres": empleado[1],
                "apellidos": empleado[2],
                "cargo": empleado[3],
                "centro_costo": empleado[4],
                "sueldo": empleado[5],
                "subsidio_transporte": empleado[6],
                "eps": empleado[7],
                "pension": empleado[8],
                "fecha_ingreso": empleado[9]
            }
        
        # Si no se encontró ningún empleado con la cédula especificada, devolver None
        return None
    
#------------------------------------------------------------------------------------------------------------
# Función para generar desprendible de pago

from jinja2 import Template
import datetime
from decimal import Decimal

# Función para generar desprendible de pago
def generar_desprendible_pago():
    cedula = input("Ingrese la cédula del empleado: ")

    with DatabaseConnection() as connection:
        # Obtener datos del empleado
        query_empleado = "SELECT nombres, apellidos, cargo, sueldo, subsidio_transporte FROM Empleado WHERE cedula = %s"
        empleado = connection.execute_query(query_empleado, (cedula,))
        if not empleado:
            print("Empleado no encontrado.")
            return
        
        nombres, apellidos, cargo, sueldo, subsidio_transporte = empleado[0]

        # Convertir valores a float para cálculos
        sueldo = float(sueldo)
        subsidio_transporte = float(subsidio_transporte)

        # Obtener datos de horas extras
        query_horas_extras = """
        SELECT SUM(hed), SUM(hen), SUM(heddf), SUM(hendf)
        FROM HorasExtras
        WHERE cedula = %s
        """
        horas_extras = connection.execute_query(query_horas_extras, (cedula,))
        if horas_extras:
            hed, hen, heddf, hendf = horas_extras[0]
            if hed is None: hed = 0
            if hen is None: hen = 0
            if heddf is None: heddf = 0
            if hendf is None: hendf = 0
        else:
            hed, hen, heddf, hendf = 0, 0, 0, 0

        # Calcular valor de horas extras
        valor_horas_extras = (float(hed) * (sueldo / 240) * 1.25) + (float(hen) * (sueldo / 240) * 1.75) + (float(heddf) * (sueldo / 240) * 2) + (float(hendf) * (sueldo / 240) * 2.5)

        # Calcular descuentos
        descuento_pension = sueldo * 0.04  # 4% para pensión
        descuento_salud = sueldo * 0.04  # 4% para salud
        total_descuentos = descuento_pension + descuento_salud

        # Calcular total devengados y total neto
        total_devengados = sueldo + subsidio_transporte + valor_horas_extras
        total_neto = total_devengados - total_descuentos

        # Plantilla del desprendible de pago
        template = Template("""
=========================================================================
                             
                            Desprendible de Pago
                            
=========================================================================
                            
Nombre del Empleado: {{ nombres }} {{ apellidos }}
Documento de Identidad: {{ cedula }}
Cargo: {{ cargo }}
Fecha de Proceso: {{ fecha_proceso }}
                            
=========================================================================
                             
                            Devengados
                            
=========================================================================
                            
Descripción                         Valor
              
Sueldo Base:                        $ {{ sueldo }}
Subsidio Transporte:                $ {{ subsidio_transporte }}
{% if valor_horas_extras > 0 %}
Total Horas Extras:                 $ {{ valor_horas_extras }}
{% else %}
Total Horas Extras:         El empleado no tiene horas extras realizadas
{% endif %}
                            
=========================================================================
                             
                            Descuentos

=========================================================================
                            
Descripción                         Valor
              
Pensión:                            $ {{ descuento_pension }}
Salud:                              $ {{ descuento_salud }}
                            
=========================================================================
                            
              Total Devengados:          $ {{ total_devengados }}
              Total Descuentos:          $ {{ total_descuentos }}
              Total Neto:                $ {{ total_neto }}
                            
=========================================================================
        """)

        fecha_proceso = datetime.datetime.now().strftime("%Y-%m-%d")

        # Renderizar la plantilla con los datos
        desprendible = template.render(
            nombres=nombres,
            apellidos=apellidos,
            cedula=cedula,
            cargo=cargo,
            fecha_proceso=fecha_proceso,
            sueldo=sueldo,
            subsidio_transporte=subsidio_transporte,
            valor_horas_extras=valor_horas_extras,
            descuento_pension=descuento_pension,
            descuento_salud=descuento_salud,
            total_devengados=total_devengados,
            total_descuentos=total_descuentos,
            total_neto=total_neto
        )

        # Mostrar el desprendible de pago
        print(desprendible)

        # Guardar el desprendible de pago en un archivo HTML (opcional)
        with open(f"desprendible_{cedula}.html", "w") as file:
            file.write(desprendible)


#------------------------------------------------------------------------------------------------------------


# Función para aplicar el auxilio de transporte
def aplicar_subsidio_transporte(cedula):
    SMMLV = 1300000
    subsidio_transporte = 140606  # Valor actual del subsidio de transporte en Colombia
    
    with DatabaseConnection() as connection:
        # Obtener datos del empleado
        query_empleado = "SELECT cedula, nombres, apellidos, sueldo FROM Empleado WHERE cedula = %s"
        empleado = connection.execute_query(query_empleado, (cedula,))
        if empleado:
            empleado = empleado[0]
            cedula_empleado, nombres_empleado, apellidos_empleado, sueldo_empleado = empleado

            # Convertir sueldo_empleado a float
            sueldo_empleado = float(sueldo_empleado)
            
            # Determinar si el empleado tiene derecho al subsidio de transporte
            if sueldo_empleado <= 2 * SMMLV:
                subsidio = subsidio_transporte
            else:
                subsidio = 0

            # Actualizar la base de datos con el subsidio de transporte
            query_update = "UPDATE Empleado SET subsidio_transporte = %s WHERE cedula = %s"
            connection.execute_insert(query_update, (subsidio, cedula))

            print(f"Subsidio de transporte aplicado correctamente para {nombres_empleado} {apellidos_empleado}.")
        else:
            print("Empleado no encontrado.")


# Función para aplicar descuentos de salud y pensión
def aplicar_descuento_salud_pension():
    cedula = input("Ingrese la cédula del empleado: ")

    with DatabaseConnection() as connection:
        # Obtener datos del empleado
        query_empleado = "SELECT cedula, nombres, apellidos, sueldo, subsidio_transporte FROM Empleado WHERE cedula = %s"
        empleado = connection.execute_query(query_empleado, (cedula,))
        if empleado:
            empleado = empleado[0]
            cedula_empleado, nombres_empleado, apellidos_empleado, sueldo_empleado, subsidio_transporte = empleado

            # Convertir sueldo_empleado a float
            sueldo_empleado = float(sueldo_empleado)

            # Calcular descuentos de salud y pensión
            descuento_salud = sueldo_empleado * 0.04  # 4% del sueldo para salud en Colombia
            descuento_pension = sueldo_empleado * 0.04  # 4% del sueldo para pensión en Colombia
            descuento_total = descuento_salud + descuento_pension

            # Calcular el salario total
            salario_total = sueldo_empleado - descuento_total + float(subsidio_transporte)

            # Mostrar tabla con los datos del empleado y los descuentos aplicados
            tabla = [
                ["Documento de Identidad", cedula_empleado],
                ["Nombre", f"{nombres_empleado} {apellidos_empleado}"],
                ["Descuento Salud", descuento_salud],
                ["Descuento Pensión", descuento_pension],
                ["Descuento Total", descuento_total],
                ["Subsidio Transporte", subsidio_transporte],
                ["Salario Total", salario_total]
            ]
            print(tabulate(tabla, headers=["Descripción", "Valor"]))
        else:
            print("Empleado no encontrado.")




#------------------------------------------------------------------------------------------------------------
# Funciones para manejar horas extras

def mostrar_menu_horas_extras():
    while True:

        # Mostrar las opciones del menú

        print("\nMenú de Horas Extras:")
        print("1. Ingresar Horas Extras del Empleado")
        print("2. Mostrar Total de Horas Extras por Empleado")
        print("3. Volver al Menú Principal")
        
        # Solicitar al usuario que seleccione una opción

        opcion = input("Seleccione una opción: ")


        # Evaluar la opción seleccionada por el usuario y llamar a la función correspondiente
        if opcion == "1":
            ingresar_horas_extras_empleado()# Llamar a la función para ingresar horas extras de un empleado
        elif opcion == "2":
            mostrar_total_horas_extras()# Llamar a la función para mostrar el total de horas extras por empleado
        elif opcion == "3":
            break# Salir del bucle y volver al menú principal
        else:
            print("Opción inválida. Por favor, seleccione una opción válida.")


def manejar_menu_horas_extras():
    while True:
        opcion = mostrar_menu_horas_extras()
        if mostrar_menu_horas_extras(opcion):
            break  # Salir del bucle y regresar al menú principal


import matplotlib.pyplot as plt

def ingresar_horas_extras_empleado():

        # Solicitar al usuario que ingrese los datos del empleado y las horas extras

    cedula = input("Ingrese la cédula del empleado: ")
    nombres = input("Ingrese los nombres del empleado: ")
    apellidos = input("Ingrese los apellidos del empleado: ")
    salario = float(input("Ingrese el salario del empleado: "))
    HEDO = int(input("Ingrese la cantidad de horas extras diurnas ordinarias: "))
    HENO = int(input("Ingrese la cantidad de horas extras nocturnas ordinarias: "))
    HEDDF = int(input("Ingrese la cantidad de horas extras diurnas dominicales y festivas: "))
    HENDF = int(input("Ingrese la cantidad de horas extras nocturnas dominicales y festivas: "))

    
        # Calcular el valor de las horas extras según las tarifas establecidas

    CHEDO = salario / 240 * HEDO * 1.25
    CHENO = salario / 240 * HENO * 1.75
    CHEDDF = salario / 240 * HEDDF * 2
    CHENDF = salario / 240 * HENDF * 2.5


    # Calcular el salario total incluyendo las horas extras

    total_salario = salario + CHEDO + CHENO + CHEDDF + CHENDF


    # Mostrar los resultados en forma tabular

    print("\n========================================")
    resultados = [
        ['Tipo de dato', 'Dato'],
        ['Nombre de Empleado', f"{nombres} {apellidos}"],
        ['Salario del Empleado', salario],
        ['Número de horas diurnas ordinarias:', HEDO],
        ['Valor de horas diurnas ordinarias:', CHEDO],
        ['Número de horas diurnas dominicales y festivas:', HEDDF],
        ['Valor de horas diurnas dominicales y festivas:', CHEDDF],
        ['Número de horas nocturnas dominicales y festivas:', HENDF],
        ['Valor de horas nocturnas dominicales y festivas:', CHENDF],
        ['Salario Total:', total_salario]
    ]


        # Imprimir la tabla de resultados usando la función tabulate

    print(tabulate(resultados, headers='firstrow'))


    # Insertar los datos de las horas extras en la base de datos

    with DatabaseConnection() as connection:
        query = """
        INSERT INTO HorasExtras (cedula, hed, hen, heddf, hendf, fecha)
        VALUES (%s, %s, %s, %s, %s, CURRENT_DATE)
        """
        params = (cedula, HEDO, HENO, HEDDF, HENDF)
        connection.execute_query(query, params)

    print("Datos de horas extras guardados en la base de datos.\n")


    # Mostrar un gráfico de barras con el valor de las horas extras por categoría

    categorias = ['Horas diurnas ordinarias', 'Horas nocturnas ordinarias', 'Horas diurnas dominicales y festivas', 'Horas nocturnas dominicales y festivas']
    valores = [CHEDO, CHENO, CHEDDF, CHENDF]

    plt.figure(figsize=(10, 6))
    plt.bar(categorias, valores, color='blue')

    plt.xlabel('Tipo de Horas Extras')
    plt.ylabel('Valor a Pagar')
    plt.title('Valor de Horas Extras por Categoría')
    plt.show()


from decimal import Decimal
def mostrar_total_horas_extras():

        # Conexión a la base de datos

    with DatabaseConnection() as connection:

                # Consulta para obtener el total de horas extras por empleado

        query = """
        SELECT e.cedula, e.nombres, e.apellidos, TO_CHAR(e.sueldo::numeric, 'FM9999999999.99') AS sueldo,
               COALESCE(SUM(he.hed), 0) AS total_hed,
               COALESCE(SUM(he.hen), 0) AS total_hen,
               COALESCE(SUM(he.heddf), 0) AS total_heddf,
               COALESCE(SUM(he.hendf), 0) AS total_hendf,
               COALESCE(SUM(he.hed * (e.sueldo / 240) * 1.25 + he.hen * (e.sueldo / 240) * 1.75 + he.heddf * (e.sueldo / 240) * 2 + he.hendf * (e.sueldo / 240) * 2.5), 0) AS total_valor_horas_extras,
               MAX(he.fecha) AS fecha_ingreso_horas_extras
        FROM Empleado e
        LEFT JOIN HorasExtras he ON e.cedula = he.cedula
        GROUP BY e.cedula, e.nombres, e.apellidos, e.sueldo
        """

                # Ejecutar la consulta

        resultado = connection.execute_query(query)
        

                # Verificar si hay resultados

        if resultado:
            tabla = [
                ["Documento de Identidad", "Nombres", "Apellidos", "Salario", "Total HED", "Total HEN", "Total HEDDF", "Total HENDF", "Total Valor Horas Extras (COP)", "Fecha Ingreso Horas Extras"]
           
            ]

                        # Iterar sobre los resultados y agregarlos a la tabla

            for row in resultado:
                row_list = list(row)

                                # Formatear el salario y el total de valor de horas extras como moneda colombiana

                row_list[3] = f"${row_list[3]}"
                row_list[8] = f"${row_list[8]}"
                tabla.append(row_list)

                            # Mostrar la tabla usando la función tabulate

            print(tabulate(tabla, headers="firstrow"))
        else:

                        # Si no hay resultados, mostrar un mensaje indicando que no se encontraron horas extras

            print("No se encontraron horas extras para ningún empleado.")




# mostrar_total_horas_extras()

#------------------------------------------------------------------------------------------------------------
# Función para generar prima legal
def generar_prima_legal():
    cedula = input("Ingrese la cédula del empleado para generar la prima: ")

    with DatabaseConnection() as connection:
        try:
            # Consultar datos necesarios para el cálculo de la prima
            query = """
            SELECT e.cedula, e.nombres, e.apellidos, e.sueldo, e.subsidio_transporte, COALESCE(SUM(he.hed + he.hen + he.heddf + he.hendf), 0) AS total_hextras
            FROM Empleado e
            LEFT JOIN HorasExtras he ON e.cedula = he.cedula
            WHERE e.cedula = %s
            GROUP BY e.cedula, e.nombres, e.apellidos, e.sueldo, e.subsidio_transporte;
            """
            empleado_data = connection.execute_query(query, (cedula,))
            if empleado_data:
                cedula, nombres, apellidos, sueldo, subsidio, total_hextras = empleado_data[0]

                # Calcular el total a pagar
                total_a_pagar = sueldo + total_hextras

                # Calcular la prima
                prima = ((total_a_pagar + subsidio) * 180) / 360

                # Insertar la prima en la tabla DesprendiblePago
                insert_query = """
                INSERT INTO DesprendiblePago (cedula, total_devengados)
                VALUES (%s, %s);
                """
                connection.execute_insert(insert_query, (cedula, prima))

                # Formatear la prima como decimal en lugar de notación científica
                prima_decimal = "{:.2f}".format(prima)

                print("\nTabla de Prima Generada:")
                tabla_prima = [
                    ["Número de Identidad", "Nombre", "Prima Generada"],
                    [cedula, f"{nombres} {apellidos}", prima_decimal]
                ]
                print(tabulate(tabla_prima, headers="firstrow"))
            else:
                print("No se encontraron datos del empleado para calcular la prima.")
        except Exception as e:
            print("Error al generar la prima:", e)


#------------------------------------------------------------------------------------------------------------

# Función para generar estadísticas
def generar_estadisticas():
    with DatabaseConnection() as connection:
        query = "SELECT cargo, AVG(sueldo) FROM Empleado GROUP BY cargo"
        result = connection.execute_query(query)
        if result:
            formatted_result = [(cargo, "{:,.0f}".format(sueldo)) for cargo, sueldo in result]
            print("\nEstadísticas de Sueldos Promedio por Cargo:")
            print(tabulate(formatted_result, headers=["Cargo", "Sueldo Promedio"]))
        else:
            print("No se encontraron datos para generar estadísticas.")

# Función para generar gráficas
def generar_graficas():
    with DatabaseConnection() as connection:
        query = "SELECT cargo, COUNT(*) FROM Empleado GROUP BY cargo"
        result = connection.execute_query(query)
        if result:
            cargos, cantidades = zip(*result)
            plt.pie(cantidades, labels=cargos, autopct='%1.1f%%')
            plt.title('Distribución de Empleados por Cargo')
            plt.show()
        else:
            print("No se encontraron datos para generar gráficas.")

from tabulate import tabulate

def mostrar_base_empleados():
    with DatabaseConnection() as connection:
        query = """
        SELECT e.cedula, e.nombres, e.apellidos, TO_CHAR(e.sueldo::numeric, 'FM9999999999.99') AS sueldo,
               COALESCE(e.subsidio_transporte, 0) AS subsidio_transporte,
               COALESCE(e.eps, 'No especificado') AS eps,
               COALESCE(e.pension, 'No especificado') AS pension,
               TO_CHAR(e.fecha_ingreso, 'YYYY-MM-DD') AS fecha_ingreso
        FROM Empleado e
        """
        result = connection.execute_query(query)
        if result:
            print("\nBase de Empleados Registrados:")
            headers = ["Documento de Identidad", "Nombres", "Apellidos", "Salario", "Subsidio de Transporte", "EPS", "Pensión", "Fecha de Ingreso"]
            formatted_result = [[row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]] for row in result]
            print(tabulate(formatted_result, headers=headers, tablefmt="pretty"))
        else:
            print("No hay empleados registrados.")

# Loop principal del programa
def main():
    while True:
        opcion = mostrar_menu_principal()
        manejar_opcion_principal(opcion)

if __name__ == "__main__":
    main()
