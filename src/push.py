#!/usr/bin/python
# -*- coding: latin-1 -*-
import subprocess, os
from bs4 import BeautifulSoup
from geotext import GeoText
import datetime
import requests
import sched, time
import pyaudio
import wave
import re


def get_articles():
    """Requests newest articles from server"""
    try:
        # Edit this line for other regions
        response = requests.get("http://www.secretflying.com/euro-deals/", timeout=5)
        html = response.text
        soup = BeautifulSoup(html,'html.parser')
        output = []
        articles = soup.findAll('article')
        # Interates over all articles
        for item in articles:
            if item.has_attr('id'):
                date_list = []
                date = str(item.find('time')['datetime']).replace("-",",").replace("T",",").replace(":",",")
                date = date[:len(date)-6]
                date_list = date.split(",")
                # 2017-12-19T19:22:03+00:00              Year          Month             Day                 Hour            Minute           Secound
                article_time = datetime.datetime(int(date_list[0]),int(date_list[1]),int(date_list[2]),int(date_list[3]),int(date_list[4]),int(date_list[5]))
                description = item.find('a')['title']
                places = GeoText(description)
                output.insert(0,{'time':article_time,'text':description,'cities':places.cities,'price':find_Price_in_String(description),'type':find_type_in_String(description)})
        return output
    except:
        return []

def find_Price_in_String(sinput):
    """Searches for Price signiture and returns price as string"""
    if u'$' or u'€' or u'£'in sinput:
        symbol_pos = max([unicode(sinput).find(u"\u0024"),unicode(sinput).find(u"\u20AC"),unicode(sinput).find(u"\u00A3")])
        offset = 1
        while (sinput[symbol_pos+offset].isdigit()):
            offset += 1
        return sinput[symbol_pos:symbol_pos+offset]
    else:
        return "No price :("

def find_type_in_String(sinput):
    """Returns trip type"""
    if "roundtrip" in sinput:
        return "roundtrip"
    if "one-way" in sinput:
        return "one-way"
    else:
        return ""

def playsound():
    """Plays notification sound"""
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
    """Sends notification to user"""
    playsound()
    subprocess.Popen(['notify-send','-i',os.getcwd() +os.path.dirname(__file__)[1:]+ "/../res/airplane.svg",'-a','DEAL!',title, message])
    return

def describe_trip(cities):
    """Prepares short notification Text"""
    if len(cities) == 1:
        trip = "from " + cities[0]
    else:
        if len(cities) == 2:
            trip = "from " +cities[0] + " to "+ cities[1]
        else:
            trip = "between "
            for item in cities:
                trip.append(" "+item)
    return trip

def check(inner_loop):
    """Checks for new articles"""
    global article_id_cout
    articles = get_articles()
    if (len(articles) == 0):
        print "Error"
    else:
        for item in articles:
            article = item
            if (article_id_cout < article['time']):
                article_id_cout = article['time']
                sendmessage("For " + article['price'] + " " + describe_trip(article['cities'])+ "  ("+article['type']+")", article['text'])
    loop.enter(120, 1, check, (inner_loop,))

# Saves last article ID
article_id_cout = datetime.datetime(2017,01,01)

# Creates schedular for executing the script every two minutes
loop = sched.scheduler(time.time, time.sleep)

# Start loop
loop.enter(0, 1, check, (loop,))
loop.run()
