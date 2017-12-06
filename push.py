from selenium import webdriver
import subprocess
import time
#import geograpy

def get_article():
    driver = webdriver.Firefox()
    driver.set_window_size(1366, 728)
    driver.get("http://www.secretflying.com/euro-deals/")
    time.sleep(5)
    article_id = driver.find_element_by_xpath("//article").get_attribute("id")
    article_title = driver.find_element_by_xpath("//h2[@class='entry-title']/a").get_attribute("title")
    driver.quit()
    return {'idt':article_id,'text':article_title}



def sendmessage(title,message):
    subprocess.Popen(['notify-send','-a','DEAL!',title, message])
    return

recent_article = 0
while(1):
    article = get_article()
    if (recent_article != article['idt']):
        #summary = extraction.Extractor(article['text'])
        #summary.find_entities()
        #print summary.places
        #price = int(filter(str.isdigit,str(article['text']))) +"$"
        sendmessage(article['text'],price)
    print "Check done!"
    time.sleep(120)
