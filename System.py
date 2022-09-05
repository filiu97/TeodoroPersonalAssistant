#!/usr/bin/python3

from Engine import Engine

import os
import webbrowser

class System(Engine):
    
    """ Clase System.

    Clase que contiene las funcionalidades:
        - Control de ordenador:
            > Suspender.
            > Apagar.
            > Reiniciar.

    Args:
            - Engine (class): Superclase que contiene las funcionalidades relacionadas con el control del reconocimiento y
            la emisión de voz, la comprobación de la conexión a Internet del usuario, cambio de voz del asistente y la interfaz
            gráfica de usuario (GUI) 
    """

#   ******************  __init__  ******************

    def __init__(self):
        """
        Función de inicialización de la clase System. Se instancia la superclase Engine, de la que se heredan todos sus atributos 
        y métodos.
        """
        Engine.__init__(self, self.Names)


#   ******************  Funcionalidades para el control del ordenador  ******************

    def shutdown(self):
        """
        Función que realiza el apagado del ordenador.
        """
        self.speak("Perfecto, que tengas un buen día")  # Enunciar frase
        if self.PhoneFunctions:
            webbrowser.open(self.OffMacro)
        os.system("shutdown now -h")

    def suspend(self):
        """
        Función que realiza el apagado del ordenador.
        """
        self.speak("Perfecto, suspendiendo el equipo")  # Enunciar frase
        os.system("sudo pm-suspend")

    def restart(self):
        """
        Función que realiza el apagado del ordenador.
        """
        self.speak("Perfecto, reiniciando el equipo")   # Enunciar frase
        if self.PhoneFunctions:
            webbrowser.open(self.OffMacro)
        os.system("shutdown now -r")               