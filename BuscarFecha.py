import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import mysql.connector
import openpyxl

# Función para buscar los registros según una fecha
def buscar_registros():
    fecha = entry_fecha.get()

    # Realizar la conexión a la base de datos
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="base_Datos"
        )

        cursor = connection.cursor()

        # Consulta SQL para buscar registros según la fecha
        query = "SELECT * FROM registros WHERE fecha = %s"
        cursor.execute(query, (fecha,))

        # Obtener los resultados de la consulta
        resultados = cursor.fetchall()

        # Mostrar los resultados en la tabla
        mostrar_resultados(resultados)

        cursor.close()
        connection.close()

    except mysql.connector.Error as error:
        messagebox.showerror("Error de conexión", str(error))


# Función para mostrar los resultados en la tabla
def mostrar_resultados(resultados):
    # Limpiar la tabla existente
    for i in treeview.get_children():
        treeview.delete(i)

    # Insertar los resultados en la tabla
    for resultado in resultados:
        treeview.insert("", "end", values=resultado)

# Función para exportar los resultados a Excel
def exportar_excel():
    # Obtener los datos de la tabla
    resultados = []
    for child in treeview.get_children():
        resultados.append(treeview.item(child)["values"])

  # Solicitar el nombre del archivo
    nombre_archivo = filedialog.asksaveasfile(defaultextension=".xlsx", filetypes=[("Archivos de Excel", "*.xlsx")])
    if not nombre_archivo:
        return
    
    # Obtener la ruta y el nombre de archivo seleccionados
    ruta_archivo = nombre_archivo.name
    # Crear un nuevo libro de Excel
    libro = openpyxl.Workbook()
    hoja = libro.active

    # Escribir los encabezados de las columnas
    encabezados = ["id", "Nombre", "Fecha", "Hora", "Registro"]  # Ajusta los encabezados según tu tabla
    hoja.append(encabezados)

    # Escribir los datos en las filas
    for resultado in resultados:
        hoja.append(resultado)

    # Guardar el archivo Excel
    nombre_archivo = "resultados.xlsx"  # Puedes ajustar el nombre y la ubicación del archivo según tu preferencia
    libro.save(ruta_archivo)
    messagebox.showinfo("Exportar a Excel", "Los resultados se han exportado correctamente.")

# Crear la ventana principal
window = tk.Tk()
window.title("Aplicación de búsqueda")
window.state('zoomed')  # Ampliar la ventana al máximo

# Etiqueta y campo de entrada para la fecha
label_fecha = tk.Label(window, text="Fecha (YYYY-MM-DD):")
label_fecha.pack()

entry_fecha = tk.Entry(window)
entry_fecha.pack()

tk.Label(window, text="").pack()  # Dejamos un poco de espacio
# Botón de búsqueda
btn_buscar = tk.Button(window, text="Buscar", width=60,
           height=4, command=buscar_registros)
btn_buscar.pack()
tk.Label(window, text="").pack()  # Dejamos un poco de espacio

# Botón de exportar a Excel
btn_exportar = tk.Button(window, text="Exportar a Excel", width=60,
           height=4, command=exportar_excel)
btn_exportar.pack()
tk.Label(window, text="").pack()  # Dejamos un poco de espacio

# Crear la tabla para mostrar los resultados
treeview = ttk.Treeview(window, columns=("id", "nombre", "fecha", "hora", "registro"))  # Ajusta las columnas según tu tabla
treeview.heading("id", text="Columna 1")
treeview.heading("nombre", text="Columna 2")
treeview.heading("fecha", text="Columna 3")
treeview.heading("hora", text="Columna 4")
treeview.heading("registro", text="Columna 5")
treeview.pack()

window.mainloop()
