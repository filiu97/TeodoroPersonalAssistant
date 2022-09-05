#!/usr/bin/python3

from Engine import Engine
from dateutil.relativedelta import relativedelta
import datefinder
from datetime import datetime, timedelta
from apiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import pickle
import iso8601
import os
import json



class Calendar(Engine):

    """ Clase Calendar.

    Clase de gestión del calendario de Google del usuario. En ella se establece la conexión con la API creada y configurada 
    anteriormente para su utilización. Contiene las funcionalidades:
        - Mostrar los eventos del calendario de Google y del Trello del usuario.
        - Creación de eventos en el calendario de Google del usuario.

    Args:
        - Engine (class): Superclase que contiene las funcionalidades relacionadas con el control del reconocimiento y
        la emisión de voz, la comprobación de la conexión a Internet del usuario, cambio de voz del asistente y la interfaz
        gráfica de usuario (GUI).

    """

#   ******************  __init__  ******************

    def __init__(self, CalendarsID, CalendarsAPI, Numbers, Months):
        """
        Función de inicialización todos los atributos y parámetros de la clase Calendar. Se inicializa el calendario y
        se instancia la superclase Engine, de la que se heredan todos sus atributos y métodos.

        Args:
            CalendarsID (dict): ID's del calendarios de Google y la conexión con las tareas de Trello en el mismo calendario Google.
            CalendarsAPI (dict): JSON para el acceso a la API de Google Calendar.
            Numbers (dict): Diccionario que contiene la transcripción de algunos números para el correcto funcionamiento del sistema.
            Months (dict): Diccionario que contiene la transcripción de los meses para el correcto funcionamiento del sistema.
        """
        # Recepción de argumentos
        self.CalendarsID = CalendarsID
        self.CalendarsAPI = CalendarsAPI
        self.Numbers = Numbers
        self.Months = Months
        
        # Inicialización del calendario
        if os.path.isfile('.tokenCalendar.pkl'):
            self.__credentials = pickle.load(open(".tokenCalendar.pkl", "rb"))  
            self.service = build("calendar", "v3", credentials = self.__credentials)
        if self.CalendarsAPI:
            with open(".client_secret.json", "w") as outfile:
                json.dump(self.CalendarsAPI, outfile)
            scopes = ['https://www.googleapis.com/auth/calendar']
            flow = InstalledAppFlow.from_client_secrets_file(".client_secret.json", scopes=scopes)
            self.__credentials = flow.run_local_server()
            pickle.dump(self.__credentials, open(".tokenCalendar.pkl", "wb")) 
            os.remove(".client_secret.json")

        # Instanciación de la superclase Enigne de la que hereda la clase Calendar
        Engine.__init__(self, self.Names)
        

#   ******************  Funciones auxiliares de Calendar  ******************

    def __get_date_hours(self, date_input, time_format = "date"):
        """
        Función que devuelve la fecha de un evento en diversos formatos:
            - Fecha completa ("date").
            - Hora ("hours").
            - Día ("day_complete").

        Args:
            date_input (???): _description_
            time_format (str, optional): Variable de texto que diferencia entre los formatos disponibles. Defaults to "date".

        Returns:
            date_obj: La fecha en el formato deseado.
        """
        date_obj = iso8601.parse_date(date_input)
        if time_format == "date":
            return date_obj.strftime('%H:%M del %d-%m-%Y ')
        elif time_format == "hours":
            return date_obj.strftime('%H:%M')
        elif time_format == "day_complete":
            return date_obj.strftime('%d-%m-%Y ')

    def __get_relative_events(self, calendarID, duration, offset = 0, maxResults = 50):
        """
        Función que devuelve los eventos que tienen lugar en un tiempo relativo respecto a hoy. Por ejemplo, los eventos
        de esta semana, o del próximo mes.

        Args:
            calendarID (str): ID del calendarios de Google.
            duration (int): Número de días del intervalo buscado.
            offset (int, optional): Desplazamiento en días desde el día actual al primero del intervalo buscado. Defaults to 0.
            maxResults (int, optional): Número máximo de resultados que se devuelven. Defaults to 50.

        Returns:
            eventsResult(???): Listado de eventos.
        """
        today = datetime.today()
        today = datetime.combine(today, datetime.min.time())
        today = today + relativedelta(days = offset)
        diff = today + relativedelta(days = duration)
        tmin = today.isoformat('T') + "Z"
        tmax = diff.isoformat('T') + "Z"
        eventsResult = self.service.events().list(
            calendarId = calendarID,
            timeMin = tmin,
            timeMax = tmax,
            maxResults = maxResults,
            singleEvents = True,
            orderBy = 'startTime',
        ).execute()
        return eventsResult

    def __get_absolute_events(self, calendarID, day_str, maxResults = 50):
        """
        Función que devuelve los eventos que tienen lugar en una fecha concreta. Por ejemplo, hoy, mañana, pasado mañana o 
        un día concreto.

        Args:
            calendarID (str): ID del calendarios de Google.
            day_str (???): La fecha del día solicitado.
            maxResults (int, optional): Número máximo de resultados que se devuelven. Defaults to 50.

        Returns:
            eventsResult(???): Listado de eventos.
        """
        matches = list(datefinder.find_dates(day_str))
        day = matches[0]
        diff = day + relativedelta(days = 1)
        tmin = day.isoformat('T') + "Z"
        tmax = diff.isoformat('T') + "Z"
        eventsResult = self.service.events().list(
            calendarId = calendarID,
            timeMin = tmin,
            timeMax = tmax,
            maxResults = maxResults,
            singleEvents = True,
            orderBy = 'startTime',
        ).execute()
        return eventsResult

    def __create_event(self, start_time_str, summary, duration = 1, description = None, location = None):
        """
        Función que crea un evento en el calendario.

        Args:
            start_time_str (???): Día de comienzo del evento.
            summary (str): Título del evento.
            duration (int, optional): Duración en horas del evento. Defaults to 1.
            description (str, optional): Descripción del evento. Defaults to None.
            location (str, optional): Localización del evento. Defaults to None.

        Returns:
            Respuesta de la petición a la API para la creación del evento.
        """
        matches = list(datefinder.find_dates(start_time_str))
        if len(matches):
            start_time = matches[0]
            end_time = start_time + timedelta(hours = duration)
                    
        event = {
            'summary': summary,
            'location': location,
            'description': description,
            'start': {
                'dateTime': start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                'timeZone': 'Europe/Madrid',
            },
            'end': {
                'dateTime': end_time.strftime("%Y-%m-%dT%H:%M:%S"),
                'timeZone': 'Europe/Madrid',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }
            
        return self.service.events().insert(calendarId = self.CalendarsID['personal'], body = event, sendNotifications = True).execute()


#   ******************  getCalendar y setCalendar  ******************

    def getCalendar(self, query):
        """
        Función que implementa toda la lógica de recepción de peticiones para mostrar eventos del calendario. Otorga muchas posibilidades:
            - Hoy.
            - Mañana.
            - Pasado mañana.
            - Fecha concreta.
            - X semanas.
            - X meses.

        Args:
            query (str): Cadena de texto de la frase que define el tiempo de los eventos buscados.

        Returns:
            speech (str): Cadena de texto que contiene la frase que debe pronunciar el sistema.
            text (str): Cadena de texto que contiene la frase que debe mostrar el sistema.
        """
        try:
            # Inicialización calendario
            self.service = build("calendar", "v3", credentials=self.__credentials)

            # Elección del calendario a enseñar
            list_of_words = query.split()
            if ("eventos" in query) or ("calendario" in query):
                calendarID = self.CalendarsID['personal']
                event_type = "eventos"
            else:
                calendarID = self.CalendarsID['trello']
                event_type = "tareas"

            date_format = "%d/%m/%Y"
            
            # "X" semanas
            if "semanas" in query:
                number = list_of_words[list_of_words.index("semanas") - 1]
                time_str = "las próximas " + number + " semanas"
                time_format = "date"
                key_list = list(self.Numbers.keys())
                val_list = list(self.Numbers.values())
                position = val_list.index(number)
                number = int(key_list[position])
                duration = 7*number
                eventsResult = self.__get_relative_events(calendarID, duration)

            # Esta o próxima semana
            elif "semana" in query:
                time_unit = list_of_words[list_of_words.index("semana") - 1]
                if time_unit == "esta":
                    time_str = "esta semana"
                    time_format = "date"
                    duration = 7
                    eventsResult = self.__get_relative_events(calendarID, duration)
                elif time_unit == "próxima" or time_unit == "siguiente":
                    time_str = "la próxima semana"
                    time_format = "date"
                    duration = 7
                    offset = 7
                    eventsResult = self.__get_relative_events(calendarID, duration, offset)
            
            # "X" meses
            elif "meses" in query:
                number = list_of_words[list_of_words.index("meses") - 1]
                time_str = "los próximos " + number + " meses"
                time_format = "date"
                key_list = list(self.Numbers.keys())
                val_list = list(self.Numbers.values())
                position = val_list.index(number)
                number = int(key_list[position])
                duration = 30*number
                eventsResult = self.__get_relative_events(calendarID, duration)

            # Este o próximo mes
            elif "mes" in query:
                time_unit = list_of_words[list_of_words.index("mes") - 1]
                if time_unit == "este":
                    time_str = "este mes"
                    time_format = "date"
                    duration = 30
                    eventsResult = self.__get_relative_events(calendarID, duration)
                elif time_unit == "próximo" or time_unit == "siguiente":
                    time_str = "la próximo mes"
                    time_format = "date"
                    duration = 30
                    offset = 30
                    eventsResult = self.__get_relative_events(calendarID, duration, offset)

            # Día
            else:
                if "para" in query:
                    time_unit = "para"
                elif "de" in query:
                    time_unit = "de"
                else:
                    return -1, -1
                # Hoy
                if list_of_words[list_of_words.index(time_unit) + 1] == "hoy":
                    time_str = "hoy"
                    time_format = "hours"
                    today = datetime.today()
                    day_str = today.strftime(date_format)
                    eventsResult = self.__get_absolute_events(calendarID, day_str)
                # Mañana
                elif list_of_words[list_of_words.index(time_unit) + 1] == "mañana":
                    time_str = "mañana"
                    time_format = "hours"
                    today = datetime.today()
                    day_str = today + timedelta(days=1)
                    day_str = day_str.strftime(date_format)
                    eventsResult = self.__get_absolute_events(calendarID, day_str)
                # Pasado mañana
                elif list_of_words[list_of_words.index(time_unit) + 1] == "pasado":
                    time_str = "pasado mañana"
                    time_format = "hours"
                    today = datetime.today()
                    day_str = today + timedelta(days=2)
                    day_str = day_str.strftime(date_format)
                    eventsResult = self.__get_absolute_events(calendarID, day_str)
                # Día concreto
                else:
                    try:
                        day = list_of_words[list_of_words.index(time_unit) + 2]
                        key_list = list(self.Numbers.keys())
                        val_list = list(self.Numbers.values())
                        position = val_list.index(day)
                        day = key_list[position]
                    except:
                        day = list_of_words[list_of_words.index(time_unit) + 2]
                    try:
                        month = list_of_words[list_of_words.index(time_unit) + 4]
                        key_list = list(self.Months.keys())
                        val_list = list(self.Months.values())
                        position = val_list.index(month)
                        month = key_list[position]
                    except:
                        today = datetime.today()
                        month = today.month
                    try:
                        year = int(list_of_words[list_of_words.index(time_unit) + 6])
                    except:
                        today = datetime.today()
                        year = today.year
                    time_str = "el día " + str(day) + " de " +  str(month) + " de " + str(year)
                    time_format = "hours"
                    day_str = str(day) + "/" + str(month) + "/" + str(year)
                    eventsResult = self.__get_absolute_events(calendarID, day_str)

            # Obtener resultados
            if eventsResult['items']:
                speech = "Tus " + event_type + "  para " + time_str + " son:"
                text = str()
                for event in eventsResult['items']:
                    if 'dateTime' in event['start'].keys():
                        text += "   -" + event['summary'] + " a las " + self.__get_date_hours(event['start']['dateTime'], time_format) + "\n"
                    else:
                        text += "   -" + event['summary'] + " el día " + self.__get_date_hours(event['start']['date'], 'day_complete') + "\n"
            else:
                speech = "No tienes nada para " + time_str
                text = "No tienes nada para " + time_str
        
            return speech, text

        # Error de credenciales
        except:
            # if os.path.isfile('.client_secret.json'):
            if self.CalendarsAPI:
                with open(".client_secret.json", "w") as outfile:
                    json.dump(self.CalendarsAPI, outfile)
                self.speak("Parece que ha habido un error. Por favor, vuelve a actualizar sus credenciales.")
                scopes = ['https://www.googleapis.com/auth/calendar']
                flow = InstalledAppFlow.from_client_secrets_file(".client_secret.json", scopes=scopes)
                self.__credentials = flow.run_local_server()
                pickle.dump(self.__credentials, open(".tokenCalendar.pkl", "wb")) 
                os.remove(".client_secret.json")
                speech = "Se han actualizado las credenciales"
                text = "Credenciales actualizadas.\nVuelva a intentar su petición"
            else:
                speech = "Usted no tiene acceso a la API de Google Calendar"
                text = "Gestione su acceso a la\nAPI de Google Calendar"

            return speech, text

    def setCalendar(self, query):
        """
        Función que implementa toda la lógica de recepción de peticiones para crear un evento en el calendario. Otorga muchas posibilidades:
            - Hoy.
            - Mañana.
            - Pasado mañana.
            - Fecha concreta.
        Args:
            query (str): Cadena de texto de la frase que define el tiempo de los eventos buscados.

        Returns:
            speech (str): Cadena de texto que contiene la frase que debe pronunciar el sistema.
            text (str): Cadena de texto que contiene la frase que debe mostrar el sistema.
        """
        try:
            # Inicialización calendario
            self.service = build("calendar", "v3", credentials=self.__credentials)

            # Obtención de la fecha
            list_of_words = query.split()
            time_unit = "para"
            date_format = "%d/%m/%Y"
            if time_unit not in list_of_words:
                day_str = self.GUI("Date", text="Introduce la fecha del evento",  geometry = "400x300")
            else:
                if list_of_words[list_of_words.index(time_unit) + 1] == "hoy":
                    time_str = "hoy"
                    today = datetime.today()
                    time_str = today.strftime(date_format)
                elif list_of_words[list_of_words.index(time_unit) + 1] == "mañana":
                    day_str = "mañana"
                    today = datetime.today()
                    day_str = today + timedelta(days=1)
                    day_str = day_str.strftime(date_format)
                elif list_of_words[list_of_words.index(time_unit) + 1] == "pasado":
                    time_str = "pasado mañana"
                    today = datetime.today()
                    day_str = today + timedelta(days=2)
                    day_str = day_str.strftime(date_format)
                else:
                    try:
                        day = list_of_words[list_of_words.index(time_unit) + 2]
                        key_list = list(self.Numbers.keys())
                        val_list = list(self.Numbers.values())
                        position = val_list.index(day)
                        day = key_list[position]
                    except:
                        day = list_of_words[list_of_words.index(time_unit) + 2]
                    try:
                        month = list_of_words[list_of_words.index(time_unit) + 4]
                        key_list = list(self.Months.keys())
                        val_list = list(self.Months.values())
                        position = val_list.index(month)
                        month = key_list[position]
                    except:
                        today = datetime.today()
                        month = today.month
                    try:
                        year = int(list_of_words[list_of_words.index(time_unit) + 6])
                    except:
                        today = datetime.today()
                        year = today.year

                    day_str = str(day) + "/" +  str(month) + "/" + str(year)
            
            # Obtención de la hora
            hours_str = self.GUI("Hour", text="Introduce la hora del evento")

            # Obtención del tiempo del evento
            time_str = day_str + " " + hours_str

            # Obtención del título
            try:
                summary = ' '.join(list_of_words[list_of_words.index("nombre")+1:])
            except:
                summary = self.GUI("Text", text="Introduce el nombre del evento", default_text="Evento")

            # Obtención de la descripción y localización
            description, location = self.GUI("SetCalendar", geometry="800x400")

            # Creación del evento
            self.__create_event(time_str, summary.title(), description=description, location=location)

            speech = "Evento creado correctamente"
            text = "Evento creado"

            return speech, text

        # Error de credenciales
        except:
            # if os.path.isfile('.client_secret.json'):
            if self.CalendarsAPI:
                with open(".client_secret.json", "w") as outfile:
                    json.dump(self.CalendarsAPI, outfile)
                self.speak("Parece que ha habido un error. Por favor, vuelve a actualizar sus credenciales.")
                scopes = ['https://www.googleapis.com/auth/calendar']
                flow = InstalledAppFlow.from_client_secrets_file(".client_secret.json", scopes=scopes)
                self.__credentials = flow.run_local_server()
                pickle.dump(self.__credentials, open(".tokenCalendar.pkl", "wb")) 
                os.remove(".client_secret.json")
                speech = "Se han actualizado las credenciales"
                text = "Credenciales actualizadas.\nVuelva a intentar su petición"
            else:
                speech = "Usted no tiene acceso a la API de Google Calendar"
                text = "Gestione su acceso a la\nAPI de Google Calendar"

            return speech, text
