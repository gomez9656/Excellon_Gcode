import os                        #Para manejar el path
from tkinter import *            #Para la interfaz grafica
from tkinter import messagebox   #Para crear el aviso al final del programa
from tkinter import filedialog   #Para usar el explorador de archivos
from io import open              #Importa el metodo open del modulo io
import re                        #Importa el modulo re para expresiones regulares

fichero = False
path = False

def abreFichero(): #Función para buscar el archivo de Eagle
    global fichero
    fichero = filedialog.askopenfilename(title = "abrir") #Abre el explorador de archivos y
                                                            #guarda el archivo escodigo en fichero

def abrePath(): #Función para guardar la dirección donde se quieren guardar los archivos Gcode
    global path
    path = filedialog.askdirectory() #Abre el explorador de archivos para guardar el path

def ejecutar(): #Al pulsar el boton ejecutar se va a la función principal
    principal()

def infoFinal():
    messagebox.showinfo("Excellon to Gcode",
            "Revisa la carpeta donde decidiste guardar los archivos") #Aviso al finalizar el programa

def crear_archivos(total_brocas):       #Función para crear todos los archivos de GCODE
    archivos = []
    global path
    for i in range(1, total_brocas + 1):
        filepath = os.path.join('%s'%path, 'GCODE%s.txt'%i)#Crea los archivos dependiendo del numero de brocas
        open(filepath,"a")

def leer_archivo_eagle(archivo_a_leer):
    excellon = open(archivo_a_leer, "r") #Abre el archivo generado por Eagle en modo lectura
    contenido = excellon.read() #Lee todo el archivo y lo guarda en contenido
    excellon.close()    #Cierra el archivo
    return contenido

def cantidad_brocas(contenido):          #Función para calcular el número de brocas
    suma = len(re.findall(r"T\d\d*C", contenido))    #Busca T[0-9][0-9]C y los cuenta
    return suma

def crear_posicion_inicio(total_brocas, contenido):
    posicion_inicio = [] #Lista para guardar los inicios de las posiciones de las brocas
    for i in range(1, total_brocas + 1):
        posicion_inicio.append(re.search(r"T%s\n"%i,contenido)) #Busca el inicio de las posiciones de cada broca y las guarda en un vector
        posicion_inicio[i - 1] = posicion_inicio[i - 1].start()  #Convierte el inicio de la posición en entero

    final = re.search(r"M30",contenido)
    posicion_final = final.start()
    posicion_inicio.append(posicion_final)
    return posicion_inicio

def posiciones_dependiendo_broca(posicion_inicio,contenido):
    for i in range(0,len(posicion_inicio)-1):
        mensaje = ''
        for j in range(posicion_inicio[i],posicion_inicio[i+1]):
            mensaje += contenido[j] #Guarda el valor de las posiciones dependiendo de la broca
        escalar_mensaje(mensaje,i)

def escalar_mensaje(mensaje,k): #k indica el numero de archivo en que vamos
    coordenadas = re.findall(r"\d\d*.\d\d*\n",mensaje) #Busca las coordenadas en el mensaje
    m = 0                                                # y va guardando cada una en coordenadas
    for i in range(0, len(coordenadas)):        #Guarda cada par ordenado en un vector para
        vector = coordenadas[i]                 #poder usar cada par por separado
        [x,y] = escalar_coordenada(vector)
        if i == len(coordenadas) - 1:        #Si m=0 indica que es la primera vez que se
            m = 1                            #usa ese archivo. si m=1 indica que es la ultima
        abrir_archivo(k,x,y,i,m)             #vez que se usara ese archivo

def abrir_archivo(i,x,y,j,m):           #i indica el numero de archivo en que vamos
    b = i + 1
    global path
    archivo = os.path.join('%s'%path, 'GCODE%s.txt'%b) #Concatena el path y GCODE%S.txt
    archivo = open(archivo,"a")#Crea un archivo en modo append
    escribir_en_archivo(archivo,x,y,j,m)
    archivo.close()

def escribir_en_archivo(archivo,x,y,j,m):#Si j=0 indica que es la primera vez
        if j == 0:                       #que se va a escribir en ese archivo
            archivo.write('%\nG90\nG21\nF300.0S6000M03\n')
        archivo.write("G99 G83 X")
        archivo.write(str(x))   #Escribe la coordenada de x en formato str
        archivo.write('Y')
        archivo.write(str(y))   #Escribe la coordenada de y en formato str
        archivo.write(" Z-2.0 R1.0 Q1.0")
        archivo.write("\n")
        if m == 1:                              #Si m=1 indica que es la ultima vez que se
            archivo.write("G80\nM05\nM02\n%")   #escribira en ese archivo

def escalar_coordenada(vector):
    coordenadaX_sin_escalar = []
    coordenadaY_sin_escalar = []
    posicionY = (re.search(r"Y",vector)).start() #Busca la posición de la letra Y en el vector

    for i in range(0,posicionY):
        coordenadaX_sin_escalar.append(vector[i]) #Guarda el valor de la coordenada X
    coordenadaX_en_str= ''.join(coordenadaX_sin_escalar) #Junta toda la lista en un str
    coordenadaX_en_float = float(coordenadaX_en_str)    #Convierte el str en un float
    coordenadaX_escalada = (coordenadaX_en_float/1000) #Convierte la coordenada en mm
    coordenadaX_escalada = coordenadaX_escalada + 1     #Le suma 1mm a la coordenada de X

    for i in range(posicionY + 1,len(vector) - 1):
        coordenadaY_sin_escalar.append(vector[i])
    coordenadaY_en_str= ''.join(coordenadaY_sin_escalar)
    coordenadaY_en_float = float(coordenadaY_en_str)
    coordenadaY_escalada = (coordenadaY_en_float/1000)
    coordenadaY_escalada = coordenadaY_escalada + 1

    return coordenadaX_escalada,coordenadaY_escalada

def principal(): #Función main
    global fichero, path
    contenido = leer_archivo_eagle(fichero) #Lee el archivo de Eagle y lo guarda en contenido
    total_brocas = cantidad_brocas(contenido) #Cuenta la cantidad de brocas
    crear_archivos(total_brocas)                #Crea los archivos en base al total de brocas
    posicion_inicio = crear_posicion_inicio(total_brocas, contenido)
    posiciones_dependiendo_broca(posicion_inicio, contenido)
    infoFinal()

raiz = Tk()

miFrame = Frame(raiz)
miFrame.pack()

raiz.title("Excellon to Gcode")

instruccion_1 = Label(miFrame, text = "Seleccione el archivo de Eagle")
instruccion_1.grid(row = 0, column = 0, padx = 10, pady = 10)
instruccion_2 = Label(miFrame, text = "Ingrese la ubicación donde quiere guardar los archivos generados")
instruccion_2.grid(row = 1, column = 0, padx = 10, pady = 10)
instruccion_3 = Label(miFrame, text = "Generar los archivos en codigo G")
instruccion_3.grid(row = 2, column = 0, padx = 10, pady = 10)

boton_Ubicacion = Button(miFrame, text = "Archivo", command = abreFichero)
boton_Ubicacion.grid(row = 0, column = 1, padx = 10, pady = 10)
boton_path = Button(miFrame, text = "Dirección", command = abrePath)
boton_path.grid(row = 1, column = 1, padx = 10, pady = 10)
boton_ejecutar = Button(miFrame, text = "Ejecutar", command = ejecutar)
boton_ejecutar.grid(row = 2, column = 1, padx = 10, pady = 10)

raiz.mainloop()
