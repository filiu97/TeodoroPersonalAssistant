#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 12:49:28 2019

@author: filiu
"""

class Tools:
	
	def __init__(self, Nelem):
		self.Nelem = Nelem
		self.switcher = {}
		
	def switch(self, argument):	#Comando switch
		return self.switcher.get(argument, "Invalid key")
	
	def setSwitch(self):	#Creador del switch de forma manual
		print("Enter", self.Nelem, "arguments (separates with intros)")
		for i in range(self.Nelem):
			self.switcher[i] = input()
	
	def setSwitch_color(self):	#Creador del switch para color (color.py)
		self.switcher = {
				"black": "30",
				"red": "31",
				"green": "32",
				"yellow": "33",
				"blue": "34",
				"purple": "35",
				"cyan": "36",
				"white": "37",
				}
		
			
	def setSwitch_style(self):	#Creador del switch para style (color.py)
		self.switcher = {
				"normal": "0",
				"bold": "1",
				"underlined": "2",
				"negative1": "3",
				"negative2": "5",
				}
		
	def setSwitch_time_unit(self): #Creador del switch para horas alarma (Teodoro.py)
		self.switcher = {
				"horas": 3600,
				"hora": 3600,
				"minutos": 60,
				"minuto": 60,
				"segundos": 1,
				"segundo": 1,
				}
		
		
	
	def sign(self):
		print("\n\n\t\t\t\t\t\t\t\t Made by Carlos Filiu")