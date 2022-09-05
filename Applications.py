#!/usr/bin/python3

from Engine import Engine
import os
import wikipedia 
import random
import webbrowser 
import urllib.request
import re
import tools as t
import threading
import subprocess as sp
from datetime import datetime, timedelta
from numpy import sqrt, cbrt
import telegram_send
import base64
from pydub import AudioSegment
from pydub.playback import play
from io import BytesIO
from time import sleep


class Applications(Engine):

    """ Clase Applications.

    Clase que contiene las funcionalidades:
        - Control de Spotify del usuario:
            > Estado de Spotify.
            > Reanudar la reproducción.
            > Pausar la reproducción.
            > Parar la reproducción.
            > Pasar a la siguiente canción.
            > Retroceder a la canción anterior.
            > Mostrar la información de la canción actual:
                * Nombre.
                * Álbum.
                * Artista.
        - Búsquedas web:
            > Google.
            > Wikipedia.
            > Youtube.
        - Información meteorológica.
        - Lógica de la puesta y finalización de alarmas.
        - Lógica de la puesta y finalización de recordatorios.
        - Operaciones matemáticas.
        - Funcionalidades del teléfono móvil:
            > Inicio.
            > Batería baja.
            > Carga completa.
            > Encontrar el teléfono.

    Args:
            - Engine (class): Superclase que contiene las funcionalidades relacionadas con el control del reconocimiento y
            la emisión de voz, la comprobación de la conexión a Internet del usuario, cambio de voz del asistente y la interfaz
            gráfica de usuario (GUI) 
    """

#   ******************  __init__  ******************

    def __init__(self, SpotifyActions, MathOperations, Numbers):
        """
        Función de inicialización todos los atributos y parámetros de la clase Applications. Además se instancia la superclase 
        Engine, de la que se heredan todos sus atributos y métodos.

        Args:
            SpotifyActions (dict): Diccionario de los comandos necesarios para realizar el control de Spotify.
            MathOperations (dict): Diccionario que contiene la información necesaria para la lógica de las operaciones matemáticas.
            Numbers (dict): Diccionario que contiene la transcripción de algunos números para el correcto funcionamiento del sistema.
        """
        # Recepción argumentos
        self.SpotifyActions = SpotifyActions
        self.MathOperations = MathOperations
        self.Numbers = Numbers
        
        # Atributos de las funcionalidades del teléfono móvil
        self.macroPhone = None

        # Atributo de localización por defecto
        self.defaultLocation = "Madrid"

        # Inicialización del módulo de wikipedia
        wikipedia.set_lang("es")

        # Inicialización del comando Switch propio para unidades del tiempo
        self.s_time_unit = t.Tools(3)	        #Instancia objeto Switch
        self.s_time_unit.setSwitch_time_unit()	#Creador del switch

        # Instanciación de la superclase Engine de la que hereda la clase Applications
        Engine.__init__(self, self.Names)


#   ******************  Spotify  ******************

    def spotify(self, action, window = None):
        """
        Función que realiza la lógica de control del Spotify del usuario. Utiliza el sistema de comunicación D-Bus
        para poder realizar las acciones sobre el programa Spotify.

        Args:
            action (str): Acción a realizar sobre Spotify:
                - "status": Estado de Spotify.
                - "play":  Reanudar la reproducción.
                - "pause":  Pausar la reproducción.
                - "stop":  Parar la reproducción.
                - "next":  Pasar a la siguiente canción.
                - "previous":  Retroceder a la canción anterior.
                - "song":  Mostrar la información de la canción actual:
                    * Nombre.
                    * Álbum.
                    * Artista.
            window (tkinter.Tk, optional): Ventana de la interfaz de usuario. Defaults to None.

        Returns:
            speech (str): Cadena de texto que contiene la frase que debe pronunciar el sistema.
            text (str): Cadena de texto que contiene la frase que debe mostrar el sistema.
            status (int): Variable respuesta del sistema. 256 significa que ha habiado algún error.
        """
        if window is not None:
            self.GUI("Close", prev_window=window)                                                   # Cierre ventana anterior
        if action == "status":                                                                      # *status*
            return sp.getoutput(self.SpotifyActions[action])                                        
        elif action == "song":                                                                      # *song*
            title = sp.getoutput(self.SpotifyActions["title"])                                      
            album = sp.getoutput(self.SpotifyActions["album"])                                      
            artist = sp.getoutput(self.SpotifyActions["artist"])                                    
            speech = "Es " + title + ", del album " + album + ", de " + artist                      
            text = "Canción: " + title + "\n" + "Album: " + album + "\n" + "Artista: " + artist     
            return speech, text                                                                     
        else:                                                                                       # *play*, *pause*, *stop*, *next* y *previous*
            status = os.system(self.SpotifyActions[action])                                         
            if action == "previous":                                                                
                status = os.system(self.SpotifyActions[action])                                     
            return status                                                                           


#   ******************  Búsquedas web  ******************

    def google(self, query):
        """
        Función que realiza búsquedas web en el buscador www.google.es

        Args:
            query (str): palabras clave.
        """
        if "búsqueda" in query:
            request = self.GUI("Text", text="Introduce tu búsqueda")
        else:
            request = query.replace("busca", "").replace ("en", "").replace("google", "")
        webbrowser.open("https://www.google.es/search?q=" + request)

    def wikipedia(self, query):
        """
        Función que realiza búsquedas en la Wikipedia.

        Args:
            query (str): palabras clave.

        """
        if "búsqueda" in query:
            request = self.GUI("Text", text="Introduce tu búsqueda")
        else:
            request = query.replace("busca", "").replace ("en", "").replace("wikipedia", "")
        try:
            page = wikipedia.page(request)
            webbrowser.open(page.url)
        except wikipedia.DisambiguationError as e:
            s = random.choice(e.options)
            page = wikipedia.page(s)
            webbrowser.open(page.url)
            os.system("clear") 

    def youtube(self, query): 
        """
        Función que realiza búsquedas web en la página www.youtube.es. Puede mostrar la página de búsqueda con las palabras clave
        o, directamente, abrir la página del primer vídeo resultante de la búsqueda con las palabras clave.

        Args:
            query (str): palabras clave.
        """   
        if "búsqueda" in query or "vídeo" in query:
            request = self.GUI("Text", text="Introduce tu búsqueda")
        else:
            request = query.replace("busca", "").replace ("en", "").replace("youtube", "")
        if "búsqueda" in query or "busca" in query:                                                                                            # Búsqueda web Youtube
            webbrowser.open("https://www.youtube.com/results?search_query=" + request.replace(" ", "+"))
        else:                                                                                                           # Reproducción de vídeo youtube    
            html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + request.replace(" ", "+"))
            video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
            webbrowser.open("https://www.youtube.com/watch?v=" + video_ids[0])


#   ******************  Tiempo meteorológico  ******************

    def weather(self, query):
        """
        Función que realiza una búsqueda sobre las condiciones meterológicas de una determinada zona. El resultado es
        expuesto al usuario a través de una imagen.

        Args:
            query (str): palabras clave.

        Returns:
            speech (str): Cadena de texto que contiene la frase que debe pronunciar el sistema.
            place (str): Nombre del lugar de la búsqueda.
        """
        # Obtenición del lugar
        if "en" in query:
            query = query.partition("en")
            place = str(query[2]).replace(" ","")
        else:
            place = self.GUI("Text", text="Introduce la localización", default_text=self.defaultLocation)

        # Obtención información meteorológica
        os.system("curl http://es.wttr.in/" + place + ".png --output '" + place + ".png'")
        weather = os.popen("curl 'wttr.in/"+ place + "?format=%C%t&lang=es'").read()

        # Obtención temperatura y descripción
        if "+" in weather:
            weather = weather.partition("+")
            desc = weather[0]
            temp = weather[2].replace("°C", "")
        elif "-" in weather:
            weather = weather.partition("-")
            desc = weather[0]
            temp = "-" + weather[2].replace("°C", "")
        else:
            weather = weather.replace("0", "")
            desc = weather
            temp = "0"   

        speech = "En " + place + ",  está " + desc + " y hace " + str(temp) + " grados."
        return speech, place


#   ******************  Alarmas  ******************

    def setAlarm(self, query):
        """
        Función que realiza la puesta de alarmas. Se creará una alarma no bloqueante del sistema a través de un thread.

        Args:
            query (str): palabras clave.

        Returns:
            t (int): tiempo en segundos para la finalización de la alarma.
            speech (str): Cadena de texto que contiene la frase que debe pronunciar el sistema.
            text (str): Cadena de texto que contiene la frase que debe mostrar el sistema.
        """
        # Obtención de duración
        list_of_words = query.split()
        try:
            t = int(list_of_words[list_of_words.index("de") + 1])
            unit = list_of_words[list_of_words.index("de") + 2]
            m = self.s_time_unit.switch(unit)
        except:
            t, m = self.GUI("Alarm", text="Introduce duración", default_text="5")
        t *= m # Duración en segundos

        # Obtención de nombre
        try:
            name = ' '.join(list_of_words[list_of_words.index("nombre")+1:])
        except:
            name = self.GUI("Text", text="Introduce nombre", default_text="Alarma")

        speech = "Riiiiiiiiiing riiiiiiiiiing. Fin de la alarma de nombre " + name
        text = "Fin de la alarma \n " + name
        return t, speech, text

    def alarm(self, speech, text):
        """
        Función de finalización de una alarma. Comprueba el estado de Spotify, si está sonando una canción, la para momentáneamente
        para enunciar el fin de la alarma y, a continuación, vuelve a reanudar la reproducción.

        Args:
            speech (str): Cadena de texto que contiene la frase que debe pronunciar el sistema.
            text (str): Cadena de texto que contiene la frase que debe mostrar el sistema.
        """
        if self.spotify("status") == "Playing": # Comprobación del status de Spotify
            self.spotify("pause")               # Pausar reproducción
            self.speak(speech)                  # Enunciar *speech*
            self.spotify("play")                # Reanudar reproducción
        else:
            self.speak(speech)                  # Enunciar *speech*     
        self.GUI("Show", text = text)           # Mostrar *text*
    
#   ******************  Recordatorios  ******************

    def setReminder(self, query, user):
        """
        Función que realiza la creación de recordatorios. Estos son guardados en la base de conocimientos.

        Args:
            query (str): palabras clave.
            user (str): usuario creador del recordatorio.

        Returns:
            speech (str): Cadena de texto que contiene la frase que debe pronunciar el sistema.
            text (str): Cadena de texto que contiene la frase que debe mostrar el sistema.
        """
        list_of_words = query.split()
        
        # Obtención del nombre
        try:
            name = ' '.join(list_of_words[list_of_words.index("nombre")+1:])
        except:
            name = self.GUI("Text", text="Introduce el nombre del recordatorio", default_text="Recordatorio")
       
        # Obtención de la hora
        hour = self.GUI("Hour", text="Introduce la hora del recordatorio")

        # Obtención de la fecha
        try:
            day = list_of_words[list_of_words.index("para") + 1]
            today = datetime.today().date()
            if day == "hoy":
                day = str(today)
            elif day == "mañana":
                day = str(today + timedelta(days=1))
            elif day == "pasado mañana":
                day = str(today + timedelta(days=2))
            else:
                day = list_of_words[list_of_words.index("para") + 2]
                key_list = list(self.Numbers.keys())
                val_list = list(self.Numbers.values())
                position = val_list.index(day)
                day = key_list[position]
        except:
            day = self.GUI("Date", text="Introduce la fecha del recordatorio",  geometry = "400x300")
        
        new_rem = {"usuario": user, "nombre": name, "día": day, "hora": hour}
        self.db["Reminders"].insert_one(new_rem)

        speech = "Recordatorio creado"
        text = "Recordatorio de nombre: " + name + "\ncreado correctamente"
        return speech, text

    def checkReminder(self, user):
        """
        Función que comprueba si se ha de enunciar algún recordatorio. Se la llama periódicamente a través del 
        bucle principal.

        Args:
            user (str): usuario actual del sistema.

        Returns:
            speech (str): Cadena de texto que contiene la frase que debe pronunciar el sistema.
            text (str): Cadena de texto que contiene la frase que debe mostrar el sistema.
        """
        
        # Obtención día y hora actuales
        t = datetime.now() 
        hour = t.strftime('%H:%M')
        today = datetime.today()
        number = str(today.date())

        # Obtención de recordatorios de la colección Reminders
        reminders = []
        for collection in self.db.list_collection_names():
            if collection == "Reminders":
                for element in self.db[collection].find({}):
                    reminders.append(element)
        
        # Obtención *speech* y *text*
        if not len(reminders):                                                                       
            speech = None
            text = None
        else:
            for rem in range(len(reminders)):
                if reminders[rem]["usuario"] == user:
                    if reminders[rem]["día"] == number and reminders[rem]["hora"] <= hour:                          # Comprobación del recordatorio
                        speech = "Tienes un recordatorio para esta hora de nombre " + reminders[rem]["nombre"]
                        text = "Recordatorio " + reminders[rem]["nombre"]
                        del_rem = {"hora" : reminders[rem]["hora"]}
                        self.db["Reminders"].delete_one(del_rem)                                                    # Borrado del recordatorio
                    elif reminders[rem]["día"] > number:
                        del_rem = {"hora" : reminders[rem]["hora"]}
                        self.db["Reminders"].delete_one(del_rem)                                                    # Borrado del recordatorio
                    else:
                        speech = None
                        text = None
        
        return speech, text


#   ******************  Operaciones matemáticas  ******************

    def mathOperation(self, query):
        """
        Función que realiza las operaciones matemáticas programadas en la base de conocimiento.

        Args:
            query (str): palabras clave.

        Returns:
            speech (str): Cadena de texto que contiene la frase que debe pronunciar el sistema.
            text (str): Cadena de texto que contiene la frase que debe mostrar el sistema.
        """
        list_of_words = query.split()

        # Obtención de la operación
        operation = None
        for key in self.MathOperations.keys():
            if self.MathOperations[key]["keyword"] in query:
                operation = self.MathOperations[key]["operation"]
                if self.MathOperations[key]["keyword"] == "elevado":
                    number_1 = list_of_words[list_of_words.index(
                        "elevado") - 1]
                    if list_of_words[list_of_words.index("elevado") + 2] == "cuadrado":
                        number_2 = "2"
                    elif list_of_words[list_of_words.index("elevado") + 2] == "cubo":
                        number_2 = "3"
                    else:
                        number_2 = list_of_words[list_of_words.index(
                            "elevado") + 2]
                elif self.MathOperations[key]["keyword"] == "raíz cuadrada" or self.MathOperations[key]["keyword"] == "raíz cúbica":
                    number_1 = list_of_words[list_of_words.index(
                        "raíz") + 3]
                    number_2 = "-1"
                else:
                    number_1 = list_of_words[list_of_words.index(
                        self.MathOperations[key]["keyword"]) - 1]
                    number_2 = list_of_words[list_of_words.index(
                        self.MathOperations[key]["keyword"]) + 1]
        if operation == None:
            speech = "Lo siento, no puedo realizar esa operación"
            text = "Operación no recogida"
            return speech, text

        # Obtención de los dos números
        key_list = list(self.Numbers.keys())
        val_list = list(self.Numbers.values())
        try:
            position = val_list.index(number_1)
            number_1 = int(key_list[position])
        except:
            number_1 = int(number_1)
        try:
            position = val_list.index(number_2)
            number_2 = int(key_list[position])
        except:
            number_2 = int(number_2)

        # Obtención del resultado
        result = eval(operation)
        speech = str(result)
        text = str(result)
        return speech, text


#   ******************  Funcionalidades del teléfono móvil  ******************

    def checkPhone(self):
        """
        Función que realiza la comprobación del teléfono móvil. La función intenta obtener datos a través de comandos UDP
        enviados desde el teléfono móvil. Si recibe ciertos caracteres clave, estos desbloquean la funcionalidad deseada.
        Estas funcionalidades son:
            > Inicio ('on*unlock_key*').
            > Batería baja ('b').
            > Carga completa ('f').
        """
        try:
            data, _ = self.sock.recvfrom(1024)                                  # Recepción de infromación UDP
            code = data.decode("utf-8") 
            if code.startswith('on'):                                           # Inicio Teodoro en el teléfono móvil
                self.macroPhone = code[2:]
            elif code == 'c':                                                   # Reproducción audio de llamada de emergencia
                audio = self.fs.find_one({"filename":"EmergencyCall"})          # Reproducción del audio
                bytedata = audio.read()
                aud_IO = BytesIO(base64.b64decode(bytedata))
                song = AudioSegment.from_file(aud_IO, format="mp3")
                play(song)
                return 1
            elif code == 'b':                                                   # Batería baja
                self.speak(self.User + ", te queda poca batería en el móvil")   
            elif code == 'f':                                                   # Carga llena
                self.speak(self.User + ", tu móvil ya está cargado")
        except:
            return None
        
    def findPhone(self):
        """
        Función que realiza la funcionalidad de encontrar el teléfono móvil de usuario. Se envía a un bot de telegram
        previamente iniciado y configurado la clave para el desbloqueo del teléfono, desencadenando la macro creada en 
        el mismo para esta funcionalidad.

        Returns:
            speech (str): Cadena de texto que contiene la frase que debe pronunciar el sistema.
        """
        telegram_send.send(messages=[self.macroPhone])  # Trigger a través de bot en Telegram
        speech = "Voy a ello"
        return speech

    def EmergencyCall(self):
        """
        Función que realiza la funcionalidad de llamada de emergencia con el teléfono móvil de usuario. 
        Debe estar configurado la macro para poder realizarlo, al igual que existir un audio en la base de conocimiento.

        Returns:
            speech (str): Cadena de texto que contiene la frase que debe pronunciar el sistema.
        """
        webbrowser.open(self.EmergencyMacro)
        speech = "Llamando a emergencias"
        return speech