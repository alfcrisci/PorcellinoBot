#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from datetime import datetime, timedelta, time, date
import sys
import json
import xmltodict
import logging
import nominatim
from BeautifulSoup import BeautifulSoup
import requests
import ConfigParser

import telebot
from telebot import types

import pymeteosalute

reload(sys) 
sys.setdefaultencoding("utf-8")

#############################################################################
# read config

Config = ConfigParser.ConfigParser()
Config.read("porcellino_data.conf")

TOKEN=str(Config.get('porcellino_id','telegram_token'))
wikicommons_target=str(Config.get('porcellino_id','wikicommons_target'))
osm_loc=str(Config.get('porcellino_id','osm_loc'))
meteo=str(Config.get('porcellino_datasource','meteo_IFIRENZE35')) 

#############################################################################

def utci_class_7_stick(utci_v):
	try:
		utci_v=float(utci_v)
	except:
		return 8.0
	if utci_v<-60.0:
		return 8.0
	if utci_v>60.0:
		return 8.0
	if utci_v > 38.0:
		return 7.0
	elif utci_v>32.0 and utci_v<=38.0:
		return 6.0
	elif utci_v>26.0 and utci_v<=32.0:
		return 5.0
	elif utci_v >16.0 and utci_v<=26.0:
		return 4.0
	elif utci_v>5.0 and utci_v<=16.0:
		return 3.0
	elif utci_v>-2.0 and utci_v<=5.0:
		return 2.0
	elif utci_v<=-2.0:
		return 1.0



#########################################################################################################
# Define global variables

knownUsers = []  # todo: save these in a file,
userStep = {}  # so they won't reset every time the bot restarts

#########################################################################################################

commands = {  'start': 'avvia il PorcellinoBot e traduce i dati di un sensore di Firenze Centro\n',
                       'help': 'un riassunto dei comandi e i dei crediti\n',
                       'mappa': 'dove sta il Porcellino su OpenStreetMap!\n',
                       'wikime': 'vuoi sapere di me davvero?\n',
           }

credits = {'PorcellinoBot': 'Sviluppato da opensensorsdata http://www.opensensorsdata.it',
               'Porcellino' : 'Il Porcellino sta presso il http://www.mercatodelporcellino.it/',
               'Wikimedia_Commons' : 'https://commons.wikimedia.org/wiki/File:Porcellino_di_pietro_tacca,_originale_02.JPG',
               'Wikimedia_Commons' : 'https://commons.wikimedia.org/wiki/File:PorcellinoFlorence.jpg', 
               'Source meteo' : ' dati di base sono recuperati da: http://www.wunderground.com/ IFIRENZE35 '
           }


#############################################################################
# Define bot structure


bot = telebot.TeleBot('insert token of telegram bot') 
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

def listener(messages):
    """
    When new messages arrive TeleBot will call this function.
    """
    for m in messages:
        if m.content_type == 'text':
            # print the sent message to the console
            print str(m.chat.first_name) + " [" + str(m.chat.id) + "]: " 

#######################################################################################

bot.set_update_listener(listener)  # register listener

#######################################################################################

markup = types.ReplyKeyboardMarkup(row_width=2)
markup.row('/help', '/start')
markup.row('/wikime', '/mappa')
             
hideBoard = types.ReplyKeyboardHide()

#######################################################################################

@bot.message_handler(commands=['help'])
def command_help(m):
	cid = m.chat.id
	sti = open('stickers/porcellino/webp/porcellino_about.webp', 'rb')
	bot.send_sticker(cid, sti)
	help_text = "Rispondo a questi comandi : \n\n"
	for key in commands:  
		help_text += "/" + key + ": "
		help_text += commands[key] + "\n"
	bot.send_message(cid, help_text) 
	credits_text = "\n I Crediti sono : \n\n"
	for key in credits:  
		credits_text += "/" + key + ": "
		credits_text += credits[key] + "\n"
	bot.send_message(cid, credits_text,reply_markup=markup) 

@bot.message_handler(commands=['start'])
def command_start(m):
	cid = m.chat.id
	if cid not in knownUsers:  
		knownUsers.append(cid) 
		userStep[cid] = 0  
		bot.send_message(cid, "Eccoci...")
	else:
		bot.send_message(cid, "Arieccoci....ci siam bell' visti!")   
	r = requests.get(meteo)
	try:
		meteo_data=xmltodict.parse(r.content)		
		t_meteo_centro=float(meteo_data['current_observation']['temp_c'])
		rh_meteo_centro=float(meteo_data['current_observation']['relative_humidity'])
		utci_centro=pymeteosalute.utci(t_meteo_centro,rh_meteo_centro,1.0,t_meteo_centro) 
		utci_class_centro_stick=str(int(utci_class_7_stick(utci_centro)))
		sti = open(str('stickers/porcellino/webp/porcellino_'+utci_class_centro_stick + '.webp'), 'rb')
		bot.send_sticker(cid, sti)
		bot.send_message(cid, str('Temperatura aria (gradiC) : ' + str(t_meteo_centro) +' Umidita\' relativa ( % ) :'+ str(rh_meteo_centro)+'\n'))
		bot.send_message(cid, str('Universal Thermal Comfort Index (o Temperatura aria percepita ): '+ str(round(utci_centro,1)) +' gradiC \n'))
		bot.send_message(cid, str('Alla prossima! Prova a scrivere grazie se vuoi'),reply_markup=markup)
	except:
		utci_class_centro_stick=str(int(8.0))
		sti = open(str('stickers/porcellino/webp/porcellino_'+utci_class_centro_stick + '.webp'), 'rb')
		bot.send_sticker(cid, sti)
		bot.send_message(cid, str('Mi dispiace non riesco a leggere il sensore. Scusa.'))


@bot.message_handler(commands=['wikime'])
def command_wikime(m):
	cid = m.chat.id
	sti = open('stickers/porcellino/webp/porcellino_wiki.webp', 'rb')
	bot.send_message(cid, "Mi garba Wikipedia!")
	bot.send_sticker(cid, sti)
	bot.send_message(cid,str('https://it.wikipedia.org/wiki/Fontana_del_Porcellino'),reply_markup=markup) 

          

@bot.message_handler(commands=['mappa'])
def command_mappa(m):
	cid = m.chat.id
	sti = open('stickers/porcellino/webp/porcellino_osm.webp', 'rb')
	bot.send_sticker(cid, sti)
 	bot.send_message(cid, "Mi garba OpenStreetMap!")
	bot.send_message(cid,str("http://www.openstreetmap.org/node/3391028134#map=19/43.76987/11.25421"),reply_markup=markup)


	
@bot.message_handler(func=lambda message: message.text == "grazie")
def command_text_hi(m):
	cid = m.chat.id
	sti = open('stickers/porcellino/webp/porcellino_grazie.webp', 'rb')
	bot.send_sticker(cid, sti,reply_markup=markup)	

@bot.message_handler(func=lambda message: message.text == "Grazie")
def command_text_hi(m):
	cid = m.chat.id
	sti = open('stickers/porcellino/webp/porcellino_grazie.webp', 'rb')
	bot.send_sticker(cid, sti,reply_markup=markup)	

@bot.message_handler(func=lambda message: message.text == "chi sono le tue amiche?")
def command_text_hi(m):
	cid = m.chat.id
	sti = open('stickers/porcellino/webp/23_archeognock.webp', 'rb')
	bot.send_sticker(cid, sti)
	bot.send_message(cid, "Le Signore dei Reperti Antonia Astrid Domenica e Paola")

@bot.message_handler(func=lambda message: message.text == "Chi sono le tue amiche?")
def command_text_hi(m):
	cid = m.chat.id
	sti = open('stickers/porcellino/webp/23_archeognock.webp', 'rb')
	bot.send_sticker(cid, sti)
	bot.send_message(cid, "Le Signore dei Reperti Antonia Astrid Domenica e Paola")

@bot.message_handler(func=lambda message: message.text == "A chi vuoi bene?")
def command_text_hi(m):
	cid = m.chat.id
	sti = open('stickers/porcellino/webp/prof-puppala.webp', 'rb')
	bot.send_sticker(cid, sti)
	bot.send_message(cid, "Al prof. Alfonso Puppala!")

@bot.message_handler(func=lambda message: message.text == "a chi vuoi bene?")
def command_text_hi(m):
	cid = m.chat.id
	sti = open('stickers/porcellino/webp/prof-puppala.webp', 'rb')
	bot.send_sticker(cid, sti)
	bot.send_message(cid, "Al prof. Alfonso Puppala!")





 

	

#############################################################################
# Lancia il bot

bot.polling(none_stop=True,timeout=120)

#############################################################################



