#!/usr/bin/python
# -*- coding: latin-1 -*-
import subprocess, os
from bs4 import BeautifulSoup
from geotext import GeoText
import requests
import time
import pyaudio
import wave


def get_article():
    # Edit this line for other regions
    response = requests.get("http://www.secretflying.com/euro-deals/", timeout=5)
    html = response.text
    soup = BeautifulSoup(html,'html.parser')
    article_id = soup.find('article')['id']
    description = soup.find('article').find('a')['title']
    places = GeoText(description)
    return {'idt':article_id,'text':description,'cities':places.cities,'price':find_Price_in_String(description),'type':find_type_in_String(description)}

def find_Price_in_String(sinput):
    if u'$' or u'€' or u'£'in sinput:
        symbol_pos = max([unicode(sinput).find(u"\u0024"),unicode(sinput).find(u"\u20AC"),unicode(sinput).find(u"\u00A3")])
        offset = 1
        while (sinput[symbol_pos+offset].isdigit()):
            offset += 1
        return sinput[symbol_pos:symbol_pos+offset]
    else:
        return "No price :("

def find_type_in_String(sinput):
    if "roundtrip" in sinput:
        return "roundtrip"
    if "one-way" in sinput:
        return "one-way"
    else:
        return ""

def playsound():
    chunk = 1024
    wf = wave.open(os.path.dirname(__file__)+'/../res/Beeper.wav', 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(
        format = p.get_format_from_width(wf.getsampwidth()),
        channels = wf.getnchannels(),
        rate = wf.getframerate(),
        output = True)
    data = wf.readframes(chunk)
    while data != '':
        stream.write(data)
        data = wf.readframes(chunk)
    stream.close()
    p.terminate()

def sendmessage(title,message):
    playsound()
    subprocess.Popen(['notify-send','-i',os.getcwd() +os.path.dirname(__file__)[1:]+ "/../res/airplane.svg",'-a','DEAL!',title, message])
    print os.getcwd() +os.path.dirname(__file__)[1:]+"/../res/airplane.svg"
    return

def describe_trip(cities):
    if len(cities) == 1:
        trip = "in" + article['cities'][0]
    else:
        if len(cities) == 2:
            trip = "from " +cities[0] + " to "+ cities[1]
        else:
            trip = "between "
            for item in cities:
                trip.append(" "+item)
    return trip

#Saves last article id
recent_article = 0
while(1):
    article = get_article()
    if (recent_article != article['idt']):
        recent_article = article['idt']
        sendmessage("For " + article['price'] + " " + describe_trip(article['cities'])+ "  ("+article['type']+")", article['text'])
        break
        time.sleep(120) #Refresh delay
