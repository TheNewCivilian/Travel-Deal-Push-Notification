#!/usr/bin/python
# -*- coding: latin-1 -*-
import subprocess, os
from bs4 import BeautifulSoup
from geotext import GeoText
from gi.repository import Gtk
import notify2
import datetime
import requests
import sched, time
import pyaudio
import wave
import re
import webbrowser

class TDNotifiyer():

    def __init__(self):
        notify2.init('Traveldeal alert',mainloop='glib')

        # Saves last article ID
        self.article_id_cout = datetime.datetime(2017,01,01)

        # Creates schedular for executing the script every two minutes
        self.loop = sched.scheduler(time.time, time.sleep)
        # Start loop
        self.loop.enter(0, 1, self.check, (self.loop,))
        self.loop.run()


    def get_articles(self):
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
                    output.insert(0,{'time':article_time,'text':description,'link': item.find('a')['href'],'cities':places.cities,'price':self.find_Price_in_String(description),'type':self.find_type_in_String(description)})
            return output
        except:
            return []

    def find_Price_in_String(self,sinput):
        """Searches for Price signiture and returns price as string"""
        if u'$' or u'€' or u'£'in sinput:
            symbol_pos = max([unicode(sinput).find(u"\u0024"),unicode(sinput).find(u"\u20AC"),unicode(sinput).find(u"\u00A3")])
            offset = 1
            while (sinput[symbol_pos+offset].isdigit()):
                offset += 1
            return sinput[symbol_pos:symbol_pos+offset]
        else:
            return "No price :("

    def find_type_in_String(self,sinput):
        """Returns trip type"""
        if "roundtrip" in sinput:
            return "roundtrip"
        if "one-way" in sinput:
            return "one-way"
        else:
            return ""

    def playsound(self):
        """Plays notification sound"""
        chunk = 1024
        # wf = wave.open('../res/Beeper.wav', 'rb')
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

    def openLink(self,n, action):
        assert action == "default"
        print 'test'
        # webbrowser.open(link)
        n.close()

    def sendmessage(self,article):
        """Sends notification to user"""
        title = "For " + article['price'] + " " + self.describe_trip(article['cities'])+ "  ("+article['type']+")"
        message = article['text']
        link = article['link']
        self.playsound()
        n = notify2.Notification(title,message,"../res/airplane.svg")
        n.add_action("default","Open", self.openLink)
        n.show()
        return



    def describe_trip(self,cities):
        """Prepares short notification Text"""
        if len(cities) == 1:
            trip = "from " + cities[0]
        else:
            if len(cities) == 2:
                trip = "from " +cities[0] + " to "+ cities[1]
            else:
                trip = "between "
                for item in cities:
                    trip += " " + item
        return trip

    def check(self,inner_loop):
        """Checks for new articles"""
        # global article_id_cout
        articles = self.get_articles()
        if (len(articles) == 0):
            print "Error"
        else:
            for item in articles:
                article = item
                if (self.article_id_cout < article['time']):
                    self.article_id_cout = article['time']
                    self.sendmessage(article)
        self.loop.enter(120, 1, self.check, (inner_loop,))

if __name__ == "__main__":
    TDNotifiyer()
    Gtk.main()
