# --------------------------------------Importamos librerias--------------------------------------------

from tkinter import *
import os
import cv2
from matplotlib import pyplot
from mtcnn.mtcnn import MTCNN
import numpy as np
import mysql.connector
from mysql.connector import Error
from datetime import datetime
from PIL import Image, ImageTk


# ------------------------------------Base de datos-----------------------------------------------------


def guardar_registro_en_base_de_datos(usuario, tipo_registro):
    try:
        # Establecer conexión con la base de datos
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="base_Datos"
        )

        # Crear un cursor para ejecutar las consultas
        cursor = conexion.cursor()

        # Obtener la fecha y hora actual
        fecha_actual = datetime.now().date()
        hora_actual = datetime.now().time()

        # Insertar los datos en la tabla correspondiente
        consulta = "INSERT INTO registros (nombre_usuario, fecha, hora, tipo_registro) VALUES (%s, %s, %s, %s)"
        valores = (usuario, fecha_actual, hora_actual, tipo_registro)
        cursor.execute(consulta, valores)

        # Confirmar los cambios y cerrar la conexión
        conexion.commit()
        cursor.close()
        conexion.close()

        print("Registro guardado en la base de datos")
    except Error as e:
        print("Error al guardar en la base de datos:", str(e))


def guardar_en_base_de_datos(usuario, imagen):
    # Establecer conexión con la base de datos
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="base_Datos"
    )

    # Crear un cursor para ejecutar las consultas
    cursor = conexion.cursor()

    # Insertar los datos en la tabla correspondiente
    consulta = "INSERT INTO usuario (nombre_usuario, imagen) VALUES (%s, %s)"
    valores = (usuario, imagen)
    cursor.execute(consulta, valores)

    # Confirmar los cambios y cerrar la conexión
    conexion.commit()
    conexion.close()

# --------------------------- Funcion para almacenar el registro facial --------------------------------------


def registro_facial():
    usuario = usuario_entrada.get()

    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        cv2.imshow('Registro Facial', frame)
        if cv2.waitKey(1) == 27:
            break

    imagen_registro = usuario + "_registro.jpg"
    cv2.imwrite(imagen_registro, frame)
    cap.release()
    cv2.destroyAllWindows()

    # Guardar los datos en la base de datos
    guardar_en_base_de_datos(usuario, imagen_registro)

    usuario_entrada.delete(0, END)

    Label(pantalla1, text="Registro facial exitoso",
          fg="green", font=("Calibri", 11)).pack()
    

# ------------------------Crearemos una funcion para asignar al boton registro --------------------------------
def registro():
    global usuario
    global contra  # Globalizamos las variables para usarlas en otras funciones
    global usuario_entrada
    global pantalla1
    # Esta pantalla es de un nivel superior a la principal
    pantalla1 = Toplevel(pantalla)
    pantalla1.title("Registro")
    pantalla1.state('zoomed')  # Ampliar la ventana al máximo
    contenedor_principal1 = Frame(pantalla1)
    contenedor_principal1.pack(pady=20)
  # Agregar la imagen encima de los botones
    imagen1 = PhotoImage(file="C:/Users/robin/Downloads/9+CodigoFuente/reconocimientofacial1/logo.png")
    imagen1 = imagen1.subsample(4)  # Puedes ajustar el factor de submuestreo según tus necesidades
    etiqueta_imagen = Label(contenedor_principal1, image=imagen1)
    etiqueta_imagen.pack()

    # --------- Empezaremos a crear las entradas ----------------------------------------

    usuario = StringVar()
    contra = StringVar()

    Label(pantalla1, text="Registro facial: debe de asignar un usuario:").pack()
    # Label(pantalla1, text = "").pack()  #Dejamos un poco de espacio
    Label(pantalla1, text="").pack()  # Dejamos un poco de espacio
    # Mostramos en la pantalla 1 el usuario
    Label(pantalla1, text="Usuario * ").pack()
    # Creamos un text variable para que el usuario ingrese la info
    usuario_entrada = Entry(pantalla1, textvariable=usuario)
    usuario_entrada.pack()
 

    # ------------ Vamos a crear el boton para hacer el registro facial --------------------
    Label(pantalla1, text="").pack()
    Button(pantalla1, text="Registro Facial", width=60,
           height=4, command=registro_facial).pack()

# --------------------------Funcion para el Login Facial --------------------------------------------------------


def login_facial():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        cv2.imshow('Login Facial', frame)
        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

    # Realizar la verificación facial y obtener el usuario
    usuario = verificar_rostro(frame)

    if usuario:
        # Guardar el registro de entrada en la base de datos
        Label(pantalla2, text="Inicio de Sesión Exitoso", fg="green", font=("Calibri", 11)).pack()
        print("Bienvenido al sistema usuario:", usuario)
        Label(text="").pack()  # Creamos el espacio entre el titulo y el primer boton

        entrada_btn = Button(pantalla2, text="Entrada", width=20, height=1, command=marcar_entrada)
        entrada_btn.pack()
        Label(text="").pack()  # Creamos el espacio entre el titulo y el primer boton

        salida_btn = Button(pantalla2, text="Salida", width=20, height=1, command=marcar_salida)
        salida_btn.pack()
    else:
        print("Rostro incorrecto, verifique su usuario")
        Label(pantalla2, text="Rostro incorrecto, verifique su usuario",
              fg="red", font=("Calibri", 11)).pack()


def verificar_rostro(frame):
    def orb_sim(img1, img2):
        orb = cv2.ORB_create()  # Creamos el objeto de comparacion

        # Creamos descriptor 1 y extraemos puntos claves
        kpa, descr_a = orb.detectAndCompute(img1, None)
        # Creamos descriptor 2 y extraemos puntos claves
        kpb, descr_b = orb.detectAndCompute(img2, None)

        # Creamos comparador de fuerza
        comp = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

        # Aplicamos el comparador a los descriptores
        matches = comp.match(descr_a, descr_b)

        # Extraemos las regiones similares en base a los puntos claves
        regiones_similares = [i for i in matches if i.distance < 70]
        if len(matches) == 0:
            return 0
        # Exportamos el porcentaje de similitud
        return len(regiones_similares)/len(matches)
    
    usuario_encontrado = None

    # Obtener los archivos de imágenes registradas
    archivos = os.listdir()

    detector = MTCNN()
    caras = detector.detect_faces(frame)

    for resultado in caras:
        x1, y1, ancho, alto = resultado['box']
        x2, y2 = x1 + ancho, y1 + alto

        cara_verificar = frame[y1:y2, x1:x2]
        cara_verificar = cv2.resize(
            cara_verificar, (150, 200), interpolation=cv2.INTER_CUBIC)

        # Comparar la cara verificada con las imágenes registradas
        for archivo in archivos:
            if archivo.endswith(".jpg"):
                usuario = archivo.split(".")[0]
                rostro_reg = cv2.imread(archivo, 0)
                try:
                    similitud = orb_sim(rostro_reg, cara_verificar)

                    if similitud >= 0.98:
                        usuario_encontrado = usuario
                        break
                except cv2.error:
                    mensaje_error = "Ocurrió un error al comparar los rostros. Vuelve a tomar la foto."
                    Label(pantalla2, text=mensaje_error, fg="red", font=("Calibri", 11)).pack()


    return usuario_encontrado

# ------------------------- Función para marcar entrada o salida ----------------------------------------------


def marcar_entrada():
    usuario = usuario_entrada2.get()

    # Guardar el registro de entrada en la base de datos
    guardar_registro_en_base_de_datos(usuario, "entrada")

    print("Marca de entrada registrada")
    Label(pantalla2, text="Marca de entrada registrada",
          fg="green", font=("Calibri", 11)).pack()


def marcar_salida():
    usuario = usuario_entrada2.get()

    # Guardar el registro de salida en la base de datos
    guardar_registro_en_base_de_datos(usuario, "salida")

    print("Marca de salida registrada")
    Label(pantalla2, text="Marca de salida registrada",
          fg="green", font=("Calibri", 11)).pack()

    # -------------------------- Funcion para comparar los rostros --------------------------------------------
    


# ------------------------Funcion que asignaremos al boton login -------------------------------------------------


def login():
    global pantalla2
    global usuario_entrada2

    pantalla2 = Toplevel(pantalla)
    pantalla2.title("Login")
    pantalla2.state('zoomed')  # Ampliar la ventana al máximo
    contenedor_principal2 = Frame(pantalla2)
    contenedor_principal2.pack(pady=20)
  # Agregar la imagen encima de los botones
    imagen2 = PhotoImage(file="logo.png")
    imagen2 = imagen2.subsample(4)  # Puedes ajustar el factor de submuestreo según tus necesidades
    etiqueta_imagen = Label(contenedor_principal2, image=imagen2)
    etiqueta_imagen.pack()
    Label(pantalla2, text="Login Facial").pack()
    Label(pantalla2, text="").pack()  # Dejamos un poco de espacio
    Label(pantalla2, text="Ingrese su nombre de usuario:").pack()

    usuario_entrada2 = Entry(pantalla2)
    usuario_entrada2.pack()
    Label(pantalla2, text="").pack()  # Dejamos un poco de espacio
    Button(pantalla2, text="Inicio de Sesión Facial", width=60, height=4, command=login_facial).pack()


# ------------------------- Funcion de nuestra pantalla principal ------------------------------------------------


def pantalla_principal():
    global pantalla
    pantalla = Tk()
    pantalla.state('zoomed')  # Ampliar la ventana al máximo
    pantalla.title("Berriondo Hamburgueseria")

    # Crear el contenedor principal
    contenedor_principal = Frame(pantalla)
    contenedor_principal.pack(pady=20)

    # Agregar la imagen encima de los botones
    imagen = PhotoImage(file="C:/Users/robin/Downloads/9+CodigoFuente/reconocimientofacial1/logo.png")
    imagen = imagen.subsample(4)  # Puedes ajustar el factor de submuestreo según tus necesidades
    etiqueta_imagen = Label(contenedor_principal, image=imagen)
    etiqueta_imagen.pack()

    # Espacio entre la imagen y los botones
    Label(contenedor_principal, text="").pack()

    # Botones
    boton_inicio_sesion = Button(contenedor_principal, text="Inicio de Sesión", height=4, width=60, command=login)
    boton_inicio_sesion.pack()

    Label(contenedor_principal, text="").pack()

    boton_registro = Button(contenedor_principal, text="Registro", height=4, width=60, command=registro)
    boton_registro.pack()

    pantalla.mainloop()

pantalla_principal()


