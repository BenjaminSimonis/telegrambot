#Assistant Bot for Telegram
#Author: Benjamin Simonis
#Date: January/2018
#Version: 0.8 Beta

import telegram, json, requests, os, subprocess, time
from time import sleep 
from urllib2 import URLError
from random import randint
import subprocess

#global variables
PiFactsCollection = []
#AuthList are Telegram IDs, which are allowed to talk with the Bot
AuthList = [12345678,98754321]
EditList = False
ListFile = "/home/bot/TelegramBot/list.txt"
AccessList = "/home/bot/TelegramBot/tried.txt"
emojis = {
        "Rain":"\U0001F327",
        "Thunderstorm":"\U000026C8",
        "Sun":"\U00002600",
        "Clouds":"\U00002601",
        "Cloudy":"\U000026C5",
        "Foggy":"\U0001F32B",
        "Snow":"\U0001F328",
	"Temperatur":"\U0001F321",
	"Wind":"\U0001F32C",
	"Grad":"\U00002103"
}

#Function: manages PI Telegram bot
#Params: bot object and update ID
#Return: update ID
def PIBot(bot, update_id):
	for update in bot.getUpdates(offset=update_id, timeout=10):
        	chat_id = update.message.chat_id
        	update_id = update.update_id + 1
        	message = update.message.text
        	if message and (chat_id in AuthList):
        		CheckAndAnswer(message, bot, chat_id)
		else: 
			bot.sendMessage(chat_id=chat_id, text="Please don't talk to me or ask my Admin first, if you want to talk with me!")
			f = open(AccessList, 'a')
                	f.write(str(chat_id) + " - " + time.strftime("%d.%m.%Y %H:%M:%S") + "\n")
                	f.close
	return update_id

#Function: check message rec. and answer it (if it's needed)
#Params: message, bot telegram object and Telegram chat ID
#Return: none
def CheckAndAnswer(Msg,BotObj,ChatID):
	MsgLowerCase = Msg.lower()
	global EditList
	global ListFile
	if (EditList == True):
		EditTheList(MsgLowerCase, BotObj, ChatID)
		return
	elif (MsgLowerCase == "hi" or MsgLowerCase == "hallo" or MsgLowerCase == "hey"):
		BotObj.sendMessage(chat_id=ChatID, text="Hallo, ich bin dein persönlicher Assistent und bin zu deinen Diensten. Siehe auch /help " )
		return
	elif ((MsgLowerCase == "/facts")):
		RandomFact = ChuckNorrisJokes()
		BotObj.sendMessage(chat_id=ChatID, text=RandomFact)
		return
	elif ((MsgLowerCase == "/help")):
                BotObj.sendMessage(chat_id=ChatID, text="Es gibt zur Zeit folgende Commands:\nhi\n/facts\n/help\n/additems\n/stop\n/deleteall\n/givelist\nWeitere Commands wird es in Zukunft geben.")
                return
	elif ((MsgLowerCase == "/additems")):
		BotObj.sendMessage(chat_id=ChatID, text="Was moechtest du der Einkaufsliste hinzufuegen? Bitte trenne die einzelnen Elemente mit einem Komma! Wenn du fertig bist, nutze /stop")
                EditList = True
		return	
	elif ((MsgLowerCase == "/deleteall")):
                BotObj.sendMessage(chat_id=ChatID, text="Ok, Liste ist geloescht.")
                f = open(ListFile, 'w')
		f.write("=== Einkaufsliste ===\n")
		f.close()
		return
	elif ((MsgLowerCase == "/givelist")):
		f = open(ListFile, 'r')
		listContent = f.read()
                BotObj.sendMessage(chat_id=ChatID, text=listContent)
		f.close()
                return
	elif (( "/weather" in MsgLowerCase)):
		town = Msg.split()
		test=Weather(town)
		BotObj.sendMessage(chat_id=ChatID, text=test)
		return
	elif ((MsgLowerCase == "/temp")):
                text = Temp()
                BotObj.sendMessage(chat_id=ChatID, text=text)
                return
	elif ((MsgLowerCase == "/disk")):
                text = Disk()
                BotObj.sendMessage(chat_id=ChatID, text=text)
                return
	else:
		BotObj.sendMessage(chat_id=ChatID, text="Ich verstehe den Befehl nicht. Nutze /help fuer mehr Informationen.")
		return

def EditTheList(Msg,Bot,ChatID):
        global EditList
	if ((Msg == "/stop")):
                Bot.sendMessage(chat_id=ChatID, text="Danke fuers eintragen!")
                EditList = False
                return
        elif (not Msg.startswith('/')):
                f = open(ListFile, 'a')
                f.write(Msg.replace(',', '\n').replace(' ', ''))
                f.close()
                return
	else:
		Bot.sendMessage(chat_id=ChatID, text="Bitte beende erst das Eintragen in die Liste mit /stop !")
		return

#Function: Request an Random Chuck Norris Joke from an API, process the Json and returns it
#Params: none
#Return: Random Chuck Norris Joke
def ChuckNorrisJokes():
	chuck_norris = "http://api.icndb.com/jokes/random"
	dict = {'&quot;':'"'}
	resp = requests.get(chuck_norris)
	joke = json.loads(resp.text)
	text = joke["value"]["joke"]
	text = replace_all(text, dict)
	return text

#Function: Replace words with other words
#Params: Words that should be replaced and the dictionary with what words the replacement should happen
#Return: Replaced String
def replace_all(text, dic):
	for i, j in dic.iteritems():
        	text = text.replace(i, j)
	return text

#Function: Get the Temperature of the Raspberry Pi and returns it
#Params: none
#Return: The Temperature of the Pi
def Temp():
	t=float(subprocess.check_output(["/opt/vc/bin/vcgencmd measure_temp | cut -c6-9"], shell=True)[:-1])
	ts=str(t)
	text="My temperature is "+ts+" C"
    	return text

#Function: Get Informations about the disk space of the Raspberry Pi
#Params: none
#Return: Informations about the disk space  
def Disk():
	result=subprocess.check_output("df -h .", shell=True)
	output=result.split()
     	text = "Disk space:\nTotal: "+output[8]+"\nUsed: "+output[9]+" ("+output[11]+")\nFree: "+output[10]
	return text

def Weather(town):
	w_api="http://api.openweathermap.org/data/2.5/forecast?q="
	api_code="&appid=API_KEY_FROM_OPENWEATHERMAP"
	country=",de"
	unit="&units=metric&lang=de"
	if len(town) > 2:
		country=town[2]
	town="Berlin"
	resp=requests.get(w_api+town+country+api_code+unit)
	loadedJson=json.loads(resp.text)
	actualWeather=loadedJson["list"][0]
	formattedWeather=FormatWeather(actualWeather)
	return formattedWeather

def FormatWeather(weatherText):
	#.decode('unicode-escape')
	resp = weatherText
	responseText=emojis[resp["weather"][0]["main"]].decode('unicode-escape') + " " + resp["weather"][0]["description"] + "\n"
	responseText=responseText + emojis["Temperatur"].decode('unicode-escape') + " " + str(resp["main"]["temp"]) + emojis["Grad"].decode('unicode-escape')  +  "\n"
	responseText=responseText + emojis["Wind"].decode('unicode-escape') + " " + str(resp["wind"]["speed"]) + " km/h"
	return responseText

#MAIN PROGRAM
update_id = None
InitFacts()

#Telegram API Token. Get yours with BotFather!
BotToken = 'TELEGRAM BOT API KEY'

bot = telegram.Bot(BotToken)
print 'PI TELEGRAM BOT READY TO GO!'

while True:
        try:
        	update_id = PIBot(bot, update_id)
        except telegram.TelegramError as e:
        	if e.message in ("Bad Gateway", "Timed out"):
                	sleep(1)
        	else: 
                	raise e
        except URLError as e:
            	sleep(1)
