import os, sys
import requests
from bs4 import BeautifulSoup
import re
import html

headers={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:107.0) Gecko/20100101 Firefox/107.0"}
url = 'https://www.ivoox.com/en/podcast-orbita-de-endor-podcast_sq_f113302_1.html'

def get_episodes():
    _eps = []
    content = requests.get(url, headers=headers)
    soup = BeautifulSoup(content.text, 'html.parser')

    divs = soup.select("div.play > a")
    for i in divs:
        _title = html.unescape(i['title'][13:])
        #print(_title)
        _result = i['onclick'].split('"')[1]
        _eps.append([_title, _result])
        #print(_result)
    return _eps
            
def get_audio_link(_data):
    _url = _data[1]
    _title = _data[0]
    global headers
    #print(_url)
    proxies= {  'http':'127.0.0.1:8080' ,'https':'192.168.1.147:8080' }
    #test forfan title
    #class="fan-title" marca de sponsored
    #content = requests.get(_url, headers=headers, proxies=proxies, verify=False)
    content = requests.get(_url, headers=headers)
    divs = re.search(r"\.downloadlink'\).load\((.*')" , content.text)
    mp3_url = 'https://www.ivoox.com/' + (divs[1].replace("\'",""))
    # get mp3
    content = requests.get(mp3_url, headers)
    soup = BeautifulSoup(content.text, 'html.parser')
    divs = soup.select("div.text-center > a")
    mp3_new_url = (divs[0]['href'])
    headers = { 'Referer' : mp3_new_url, 'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:107.0) Gecko/20100101 Firefox/107.0'}
    content_mp3 = requests.get(mp3_new_url, headers=headers)# ,proxies=proxies, verify=False) #, allow_redirects=False)
    if content_mp3.status_code != 401:
        #save mp3
        with open( '/srv/http/mp3/' + (_title[:30].replace(" ","_")) +'.mp3', 'wb') as f:
            f.write(content_mp3.content)
    # save as latest title
    with open( 'ivoorip.txt', 'w' ) as f:
        f.write(_title)

    
episode_arr = get_episodes()
# read latest title
latest_title = ''
with open ('ivoorip.txt','r') as f:
    latest_title = f.read()
# get only the newest episode
new_ep = []
for ep in episode_arr:
    if latest_title == ep[0]:
        break
    else:
        print(ep[0])
        new_ep.append(ep) 
# get episodes     
for eps in reversed(new_ep):
    print("Getting %s" % eps[0])
    get_audio_link(eps)


