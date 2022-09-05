#!/usr/bin/python3

import speech_recognition as sr 
import pyttsx3 
from tkinter import *
from tkinter import scrolledtext
from tkinter import font
from tkcalendar import Calendar
from datetime import datetime
import requests
import re


class Engine():

    """ Clase Engine.

    Superclase del sistema Teodoro. Esta clase contiene los métodos que hacen funcionar al sistema en cuanto a la lógica 
    de reconocimiento, emisión y cambio de voz del asistente. Además, implementa el método para la creación de interfaces
    gráficas de usuario (GUIs) para ser utilizadas a lo largo de la ejecución de programa. Por último, contiene la comprobación
    de la conexión a Internet del usuario.
    """

#   ******************  __init__  ******************

    def __init__(self, Names):
        """
        Función de inicialización todos los atributos y parámetros de la clase Engine. En esta función se definen los nombres
        que el asistente debe reconocer como triggers para atender al usuario. Se define los parámetros necesarios para la
        inicialización del motor de reconocimiento de voz y de la emisión de audio por parte del sistema. 

        Args:
            Names (list): Lista de nombres reconocidos por el asistente para su invocación.
        """
        # Recepción argumentos
        self.Names = Names

        # Inicialización reconocimient de voz
        self.__r = sr.Recognizer()
        self.__r.pause_threshold = 1
        # r.energy_threshold = 4000
        # r.dynamic_energy_adjustment_ratio = 1
        # with sr.Microphone() as source:
        #     r.adjust_for_ambient_noise(source)

        # Atributos reconocimiento y emisión de voz
        self.voiceEngine = pyttsx3.init()
        self.defaultVoice = 'spanish+m3'
        self.currentVoice = 'spanish+m3'
        self.defaultWisperVoice = 'spanish+whisper'
        self.defaultRate = 180
        self.maxVoices = 7
        self.voiceEngine.setProperty('voice', self.defaultVoice)
        self.voiceEngine.setProperty('rate', self.defaultRate)
    
    
#   ******************  Comprobación de conexión a Internet  ******************

    def internetCheck(self):
        """
        Función de comprobación de la conexión a Internet del usuario. Sin conexión a Internet, el sistema no puede iniciarse
        debido a la imposibilidad de utilizar el reconocimiento de voz y la base de conocimiento.

        Returns:
            response, text (int, str): En caso de éxito se devuelve un 0, sino, se devuelve la cadena de texto del mensaje de error
            que debe mostrarse por pantalla al usuario.
        """
        url = "http://www.google.com"
        timeout = 5
        try:
            requests.get(url, timeout = timeout)
            return 0
        except (requests.ConnectionError, requests.Timeout) as exception:
            text = "No tiene acceso \na Internet"
            return text


#   ******************  Motor de reconocimiento, emisión y cambio de voz  ******************

    def speak(self, audio): 
        """
        Función para la emisisón de audio del asistente.

        Args:
            audio (str): texto a enunciar por parte del asistente.
        """
        self.voiceEngine.say(audio)
        self.voiceEngine.runAndWait() 

    def takeCommand(self):
        """
        Función que contiene la lógica de recepción de peticiones del usuario. En este método se recoge el audio y
        se comprueba si el usuario a invocado al asistente. Si es así, se procede a la recepción de la petición y 
        a su reconocimiento para devolverlo en forma de texto al bucle principal.

        Returns:
            request (str): texto de la petición del usuario transcrita.
            window (tkinter.Tk): Ventana de la interfaz de usuario.
        """
        # r = sr.Recognizer()

        while 1:
            with sr.Microphone() as source:
                audio = self.__r.listen(source, phrase_time_limit = 5)
                try:
                    query = self.__r.recognize_google(audio, language='es-ES')
                    for name in self.Names:
                        if (query.find(name)) != -1:
                            self.speak("¿Si?")
                            window = self.GUI("Status", "Reconociendo...")
                            audio = self.__r.record(source, 10)
                            # audio = r.listen(source, phrase_time_limit = 10) 
                            try:
                                request = self.__r.recognize_google(audio, language='es-ES')
                                return request, window
                            except:
                                self.GUI("Close", prev_window = window)
                                return None, None		
                    return None, None
                except: 
                    return None, None

    def repeat(self):
        """
        Función análoga a *takeCommand* para la repetición de peticiones del usuario tras un reconocimiento erróneo.

        Returns:
            request (str): texto de la petición del usuario transcrita.
            window (tkinter.Tk): Ventana de la interfaz de usuario.
        """
        # r = sr.Recognizer()
        with sr.Microphone() as source:
            try:
                window = self.GUI("Status", "Reconociendo...")
                audio = self.__r.record(source, 10)
                try: 
                    request = self.__r.recognize_google(audio, language='es-ES')
                    return request, window
                except:
                    self.GUI("Close", prev_window = window)
                    return None, None
            except:
                return None, None

    def changeVoice(self):
        """
        Función para cambiar la voz del asistente. Este método irá pasando por las voces disponibles en el sistema
        para que el usuario pueda realizar esta funcionalidad completamente por voz. Si no se elige ninguna voz nueva,
        se mantiene la voz que tenía el asistente antes de ejecutar esta funcionalidad. También se puede elegir la voz
        por defecto en cualquier momento si el usuario expresa algo distinto a un "si" ni "no" a cualquiera de las
        posibilidades.

        Returns:
            speech (str): Cadena de texto que contiene la frase que debe pronunciar el sistema.
            text (str): Cadena de texto que contiene la frase que debe mostrar el sistema.
        """
        # Inicialización
        # r = sr.Recognizer()                                                 
        window = self.GUI("Status", "Sí -> confirmar \n No -> siguiente voz \n Cualquier cosa \n -> voz por defecto")
        i = 1
        change = False
        self.currentVoice = self.voiceEngine.getProperty('voice')

        # Bucle de búsqueda de voz
        while i <= self.maxVoices:
            newVoice = "spanish+m" + str(i)
            self.voiceEngine.setProperty('voice', newVoice)
            self.speak("Esta es una prueba de voz. ¿Le gusta?")

            # Recepción de respuesta del usuario
            with sr.Microphone() as source:
                audio = self.__r.listen(source, phrase_time_limit = 3)
                try:
                    query = self.__r.recognize_google(audio, language='es-ES')
                    if query == "si":
                        change = True
                        break
                    elif query == "no":
                        i = i+1
                        continue
                    else:
                        self.voiceEngine.setProperty('voice', self.defaultVoice)
                        break
                except:
                    self.speak = "Por favor, pruebe otra vez"
                    continue

        # Casos posibles
        if i > self.maxVoices:  # No se ha elegido ninguna voz
            self.voiceEngine.setProperty('voice', self.currentVoice)
            text = "Se mantiene la voz anterior"
            speech = "No ha seleccionado niguna de las voces disponibles. Se mantiene la voz anterior"
        elif change:            # Se ha cambiado la voz
            text = "Voz cambiada"
            speech = "Ha cambiado la voz correctamente"
        else:                   # Se ha elegido la voz por defecto
            text = "Voz por defecto"
            speech = "Ha elegido al voz por defecto"

        # Cierre ventana anterior
        self.GUI("Close", prev_window = window)         

        return speech, text


#   ******************  GUI  ******************

    def __get_SetCalendar_entry(self, desc_entry, loc_entry):
        """
        Función para recoger la entrada de texto de la GUI *SetCalendar*

        Args:
            desc_entry (tkinter.Tk.Entry): Caja de texto para la descripción del evento.
            loc_entry (tkinter.Tk.Entry): Caja de texto para la localización del evento.
        """
        global description, location
        description = desc_entry.get("1.0", "1000.1000")
        location = str(loc_entry.get())

    def __get_Login_entry(self, name_entry, pwd_entry):
        """
        Función para recoger la entrada de texto de la GUI *Login*

        Args:
            name_entry (tkinter.Tk.Entry): Caja de texto para el nombre del usuario.
            pwd_entry (tkinter.Tk.Entry): Caja de texto para la contraseña del usuario.

        """
        global name, password
        name = str(name_entry.get())
        password = str(pwd_entry.get())

    def __get_Text_entry(self, text_entry):
        """
        Función para recoger la entrada de texto de la GUI *Text*.

        Args:
            text_entry (tkinter.Tk.Entry): Caja de texto para el texto introducido por el usuario.
        """
        global info
        info = str(text_entry.get())  

    def __get_Alarm_radiobutton(self, var):
        """
        Función para recoger el valor de los botones de la GUI *Alarm*.

        Args:
            var (IntVar): Variable de recogida de unidad de tiempo.
        """
        global unit
        unit = var.get()

    def __get_Hour_entry(self, hour, minute):
        global alarm_time 
        h = hour.get()
        m = minute.get()
        alarm_time = h + ":" + m

    def __get_Date_calendar(self, cal):
        global date
        date = cal.get_date()

    def __isValidTime(self, time):
        regex = "^([01]?[0-9]|2[0-3]):[0-5][0-9]$"
        p = re.compile(regex)
        if (time == "") :
            return False
        m = re.search(p, time)
        if m is None :
            return False
        else :
            return True

    # REVISAR
    def GUI(self, action, text = None, default_text = None,
            size = 16, geometry = "400x200", prev_window = None):        
        """
        Función generadora de GUIs. En este método están definidas todas las interfaces necesarias para la ejecución
        del sistema. Son GUIs personalizadas para cada funcionalidad concreta.

        Args:
            action (str): Variable que diferencia qué tipo de GUI se desea usar.
            text (str, optional): Variable para pasar un determinado texto. Defaults to None.
            size (int, optional): Variable para cambiar el tamaño de letra en las interfaces. Defaults to 16.
            geometry (str, optional): Variable de texto que define el tamaño de la ventana que se genera. Defaults to "400x200".
            prev_window (tkinter.Tk, optional): Ventana de la interfaz de usuario. Defaults to None.

        Returns:
            En algunas GUIs se devuelven cadenas de texto para la ejecución de la funcionalidad a la que sirve la interfaz.
        """
        # Cierre de ventana anterior o acción *Close*
        if prev_window is not None or action == "Close":
            prev_window.destroy()
            if action == "Close":
                return

        # Inicialización de ventana de GUI
        window = Tk()
        window.geometry(geometry)
        bg = "gainsboro"
        window.configure(bg = bg)
        window.title("Teodoro " + action)
        window.resizable(False, False)
        font1 = "bitstream charter"
        font2 = "Helvetica"
        close_label = "Cierre esta ventana para continuar"
        ok_button = "ok.png"

        # Opciones de GUI
        if action == "Login":           # GUI Login
            
            label = Label(
                window,
                text = text,
                font = (font1, size, "bold"),
                padx = 0,
                pady = 10,
                bg = bg
                )
            label.pack()

            frame1 = Frame(
                window,
                bg = bg
            )
            frame1.pack()

            Label(
                frame1, 
                text = "Nombre de usuario", 
                font = (font1, size-4, "bold"),
                padx = 10,
                pady = 5,
                bg=bg).grid(row=0, column=0, sticky=W)

            name_entry = Entry(
                frame1,
                font = (font1, size-6),
                width = 30)
            name_entry.grid(
                row = 0, 
                column = 1,
                sticky = W)
            if text:
                name_entry.insert(0, default_text)

            Label(
                frame1, 
                text = "Contraseña", 
                font = (font1, size-4, "bold"),
                padx = 10,
                pady = 5,
                bg=bg).grid(row=1, column=0, sticky=W)
        
            pwd_entry = Entry(
                frame1,
                font = (font1, size-6),
                show = "*",
                width = 30)
            pwd_entry.grid(
                row = 1, 
                column = 1,
                sticky = W)

            phone = IntVar()
            Checkbutton(
                frame1,
                text = " Usar funcionalidades móvil", 
                pady = 10,
                variable = phone).grid(row = 2, column = 1, sticky = W)

            frame2 = Frame(
                window,
                bg = bg
            )
            frame2.pack()
            b1 = Button(
                frame2,
                command = lambda: [self.__get_Login_entry(name_entry, pwd_entry), window.destroy()])
            img = PhotoImage(file = ok_button)
            b1.config(image = img)
            b1.pack()

            window.mainloop()

            return name, password, phone

        elif action == "Status":        # GUI Status
            label = Label(
                window,
                text = text,
                font = (font1, size, "bold"),
                padx = 0,
                pady = 0,
                bg = bg
                )
            label.pack(expand = True)
            window.update()
            return window
            
        elif action == "Show":          # GUI Show

            label = Label(
                window,
                text = text,
                font = (font1, size, "bold"),
                padx = 0,
                pady = 25,
                bg = bg
            )

            cls_label = Label(
                window,
                text = close_label,
                font = (font2, 10, "bold"),
                padx = 0,
                pady = 0,
                bg = bg
                )

            b1 = Button(
                window,
                command = lambda: window.destroy())
            img = PhotoImage(file = ok_button)
            b1.config(image = img)

            label.pack(expand = True)
            cls_label.pack(expand = True)
            b1.pack(expand = True)

            window.mainloop()

        elif action == "Error":         # GUI Error

            Label(
                window,
                text = text,
                font = (font1, size, "bold"),
                padx = 0,
                pady = 15,
                bg = bg
            ).pack()

            Label(
                window,
                text = default_text,
                font = (font1, size-2),
                padx = 0,
                pady = 20,
                bg = bg
            ).pack()

            cls_label = Label(
                window,
                text = close_label,
                font = (font2, 10, "bold"),
                padx = 0,
                pady = 0,
                bg = bg
                )

            b1 = Button(
                window,
                command = lambda: window.destroy())
            img = PhotoImage(file = ok_button)
            b1.config(image = img)

            cls_label.pack(expand = True)
            b1.pack(expand = True)

            window.mainloop()

        elif action == "GetCalendar":   # GUI GetCalendar
            
            label = Label(
                window,
                text = "Estos son sus eventos",
                font = (font1, size, "bold"),
                padx = 0,
                pady = 20,
                bg = bg
            )
            label.pack()

            frame1 = Frame(
                window,
                bg = bg
            )
            frame1.pack()
        
            text_area = scrolledtext.ScrolledText( 
                frame1,
                font = (font1, size-1),
                width = 75, 
                height = 22,
                wrap = WORD)
                
            text_area.grid(column = 0)
            text_area.insert(INSERT, text)
            text_area.configure(state ='disabled')

            frame2 = Frame(
                window,
                bg = bg
            )
            frame2.pack()

            Label(
                frame2,
                text = close_label,
                font = (font2, 10, "bold"),
                padx = 0,
                pady = 20,
                bg = bg).grid(column = 0, row = 1)

            frame3 = Frame(
                window,
                bg = bg
            )
            frame3.pack()
            b1 = Button(
                frame3,
                command = lambda: window.destroy())
            img = PhotoImage(file = ok_button)
            b1.config(image = img)
            b1.pack()

            window.mainloop()

        elif action == "SetCalendar":   # GUI SetCalendar

            Label(
                window,
                text = "¿Quieres añadir una descripción y localización a tu evento?",
                font = (font1, size, "bold"),
                padx = 10,
                pady = 30,
                bg = bg).pack()

            frame1 = Frame(
                window,
                bg = bg)
            frame1.pack()

            Label(
                frame1, 
                text = "Descripción", 
                font = (font1, size, "bold"),
                padx = 10,
                pady = 20,
                bg = bg).grid(row = 0, column = 0, sticky = W)
            
            desc_entry = scrolledtext.ScrolledText( 
                frame1,
                font = (font1, size-6),
                width = 50, 
                height = 10,
                wrap = WORD)

            desc_entry.grid(
                row = 0, 
                column = 1,
                sticky = W)

            Label(
                frame1, 
                text = "Localización", 
                font = (font1, size, "bold"),
                padx = 10,
                pady = 20,
                bg = bg).grid(row = 1, column = 0, sticky = W)
        
            loc_entry = Entry(
                frame1,
                font = (font1, size-6),
                width = 50)
            loc_entry.grid(
                row = 1, 
                column = 1,
                sticky = W)

            frame2 = Frame(
                window,
                bg = bg
            )
            frame2.pack()

            Label(
                frame2,
                text = close_label,
                font = (font2, 10, "bold"),
                padx = 0,
                pady = 5,
                bg = bg).grid(column = 0, row = 1)

            frame3 = Frame(
                window,
                pady = 0,
                bg = bg).pack()
            b1 = Button(
                frame3,
                command = lambda: [self.__get_SetCalendar_entry(desc_entry, loc_entry), window.destroy()])
            img = PhotoImage(file = ok_button)
            b1.config(image=img)
            b1.pack(expand = True)

            window.mainloop()

            return description, location

        elif action == "Text":          # GUI Text
            
            if text == None:
                text = "Introduce aquí el texto"

            label = Label(
                window,
                text = text,
                font = (font1, size, "bold"),
                padx = 0,
                pady = 10,
                bg = bg
                )
            label.pack()

            frame1 = Frame(
                window,
                bg = bg,
                pady = 15
            )
            frame1.pack()

            if text == "secret":
                text_entry = Entry(
                    frame1,
                    font = (font1, size-6),
                    show = "*",
                    width = 50)
            else:
                text_entry = Entry(
                    frame1,
                    font = (font1, size-6),
                    width = 50)
            text_entry.grid(
                row = 1, 
                column = 0,
                sticky = W)

            if default_text:
                text_entry.insert(0, default_text)

            frame2 = Frame(
                window,
                bg = bg,
            )
            frame2.pack()

            Label(
                frame2,
                text = close_label,
                font = (font2, size-6, "bold"),
                padx = 0,
                pady = 10,
                bg = bg).grid(column=0, row=2)

            frame3 = Frame(
                window,
                bg = bg
            )
            frame3.pack()
            b1 = Button(
                frame3,
                command = lambda: [self.__get_Text_entry(text_entry), window.destroy()])
            img = PhotoImage(file = ok_button)
            b1.config(image = img)
            b1.pack()

            window.mainloop()

            return info

        elif action == "Alarm":         # GUI Alarm

            label = Label(
                window,
                text = "Introduce aquí el texto",
                font = (font1, size, "bold"),
                padx = 0,
                pady = 10,
                bg = bg
                )
            label.pack()

            frame1 = LabelFrame(
                window,
                text = "Tiempo",
                padx = 10, 
                pady = 10,
                bg = bg,
            )
            frame1.pack()

            text_entry = Entry(
                frame1,
                font = (font1, size-6),
                width = 10)
            text_entry.grid(
                row = 0, 
                column = 0,
                sticky = W)

            if default_text:
                text_entry.insert(0, default_text)

            var = IntVar()
            var.set(60)
            self.__get_Alarm_radiobutton(var)
            Radiobutton(frame1, text="Segundos", variable=var, value=1, command=lambda: self.__get_Alarm_radiobutton(var)).grid(row=0, column=1)
            Radiobutton(frame1, text="Minutos", variable=var, value=60, command=lambda: self.__get_Alarm_radiobutton(var)).grid(row=0, column=2)
            Radiobutton(frame1, text="Horas", variable=var, value=3600, command=lambda: self.__get_Alarm_radiobutton(var)).grid(row=0, column=3)

            frame2 = Frame(
                window,
                bg = bg,
            )
            frame2.pack()

            Label(
                frame2,
                text = close_label,
                font = (font2, size-6, "bold"),
                padx = 0,
                pady = 10,
                bg = bg).grid(column=0, row=2)

            frame3 = Frame(
                window,
                bg = bg
            )
            frame3.pack()
            b1 = Button(
                frame3,
                command = lambda: [self.__get_Text_entry(text_entry), window.destroy()])
            img = PhotoImage(file = ok_button)
            b1.config(image = img)
            b1.pack()

            window.mainloop()

            return int(info), int(unit)

        elif action == "Hour":          # GUI Hour
            
            if text == None:
                text = "Introduce la hora"

            label = Label(
                window,
                text = text,
                font = (font1, size, "bold"),
                padx = 0,
                pady = 10,
                bg = bg
                )
            label.pack()

            frame1 = Frame(
                window,
                bg = bg,
                pady = 5
            )
            frame1.pack()

            Label(
                frame1,
                text = "Horas",
                padx = 10,
                pady = 2,
                font = (font1, size-5)
            ).grid(row = 1, column = 1)

            Label(
                frame1,
                text = "Minutos",
                padx = 5,
                pady = 2,
                font = (font1, size-5)
            ).grid(row = 1, column = 2)
            
            hour = StringVar()
            minute = StringVar()
            
            Entry(
                frame1,
                textvariable = hour, 
                bg = "#48C9B0", 
                width = 5, 
                font = (font1, size-6)
                ).grid(row = 2, column = 1)
            Entry(
                frame1, 
                textvariable = minute, 
                bg = "#48C9B0", 
                width = 5, 
                font = (font1, size-6)
                ).grid(row = 2, column = 2)

            frame2 = Frame(
                window,
                pady = 5,
                bg = bg,
            )
            frame2.pack()

            Label(
                frame2,
                text = close_label,
                font = (font2, size-6, "bold"),
                padx = 0,
                pady = 10,
                bg = bg).grid(column=0, row=2)

            frame3 = Frame(
                window,
                bg = bg
            )
            frame3.pack()
            b1 = Button(
                frame3,
                command = lambda: [self.__get_Hour_entry(hour, minute), window.destroy()])
            img = PhotoImage(file = ok_button)
            b1.config(image = img)
            b1.pack()

            window.mainloop()

            if(self.__isValidTime(alarm_time)):
                return alarm_time
            else:
                self.GUI("Show", text="Por favor, introduce una\n hora en el formato correcto")
                alarm_time_correct = self.GUI("Hour", text="Introduce la hora")
                return alarm_time_correct

        elif action == "Date":          # GUI Date
            
            label = Label(
                window,
                text = text,
                font = (font1, size, "bold"),
                padx = 0,
                pady = 10,
                bg = bg
                )
            label.pack()

            frame1 = Frame(
                window,
                bg = bg,
                pady = 5
            )
            frame1.pack()
            
            cal = Calendar(
                window, 
                selectmode = 'day')
            cal.pack()
            
            frame2 = Frame(
                window,
                pady = 5,
                bg = bg,
            )
            frame2.pack()

            Label(
                frame2,
                text = close_label,
                font = (font2, size-6, "bold"),
                padx = 0,
                pady = 10,
                bg = bg).grid(column=0, row=2)

            frame3 = Frame(
                window,
                bg = bg
            )
            frame3.pack()
            b1 = Button(
                frame3,
                command = lambda: [self.__get_Date_calendar(cal), window.destroy()])
            img = PhotoImage(file = ok_button)
            b1.config(image = img)
            b1.pack()

            window.mainloop()

            return str(datetime.strptime(date, '%d/%m/%y').date())