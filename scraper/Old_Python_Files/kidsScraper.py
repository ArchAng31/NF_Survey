import httplib
from gzip import GzipFile
from StringIO import StringIO
from bs4 import BeautifulSoup
import time
import os


# this will spoof a Firefox browser
headerDict = {"Host": "www.netflix.com",
              "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0",
              "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
              "Accept-Language": "en-US,en;q=0.5",
              "Accept-Encoding": "gzip, deflate, br",
              "Referer": "http://www.netflix.com/kids",
              "Cookie": "memclid=a528c842-86b0-4d9d-9fd8-74d747e0139c; NetflixId=v%3D2%26ct%3DBQAOAAEBEK2Y578B940dcDKwrF1IO2O" \
                        "BoNuae-81gukWKINeb_lnxJtqOcXtTV9qjgwHDdQmQLPT1KplyBKMsyDr3xGk3d1Nsm3ErTaabORVsl30rWP_szDvZkx-1LDuReu" \
                        "Xfr5zZxnC57R0VteuagKf4I1PCmTA7KASvyTsaw3z8bX1_eiRxwKZH7z4WzM8yT6Ereo8OgbNQm4IawLZH441W8GyFPUEXZJ3LBz" \
                        "9B4yAM2z7QwOz_khjuR61XVq4tSEjCOYIKRnYSJ342Yl4yFUYBCYc-IQgAJWjCxIumAikGZwmY0Q5K5STlvrdMrh9Lss8_blrnkg" \
                        "QyL7Ak957ZCB1vW150fq5Bl6hOBYgtxt8HJ95zlwjKZffx4WxqYjcwD3z-ynrKz60-UojeKvfQC3pfIniOE9s9HDcRNt6M8OEumo" \
                        "1RzvvvwGSHjgOxyx7n_qRDV_1heofZ-Oir0UhNfnf8SLYW-eBEx_Y4v9OUcr-Zm6jCa1sCufbMA8U9WU_EwSM9MyEnTZKD7_MM90-qRSHmLGuKzfRdOmTwfpYQ5uBtuwRobhG5CBEEEJ_M4sJSEH-aXX3JMo4" \
                        "%26bt%3Ddbl%26ch%3DAQEAEAABABQAV74vJcFM-86tIr-n2F9X6IHeBsscR_0.%26mac%3DAQEAEAABABT1BkSyi3_vqI3DUFXUZPvDjny0FUbKMOA" \
                        ".; SecureNetflixId=v%3D2%26mac%3DAQEAEQABABTn2DcmTzkMq0x2Lg2qw2vtBrSUc9rePF4.%26dt%3D1458587831757; nmab" \
                        "=MDAxLTY1NDM6Mg%3D%3D; cL=1458587827840%7C145858686293632152%7C145858686211746564%7C%7C48%7C3HAZXSFPVNBFLAOWA6FX5VACAA" \
                        "; profilesNewSession=0; profilesNewUser=0; lhpuuidh-browse-3HAZXSFPVNBFLAOWA6FX5VACAA=US%3AEN-US%3A05309c63-0184-45b3-b0b2-8e43fc81b797_ROOT" \
                        "; lhpuuid-kid-FEKOSOZ7WJFKVDHKPYE7NVMESQ=US%3AEN-US%3A4902eb29-c36b-4ace-bf9b-3710a6ffe50d_ROOT",
              "Connection": "keep-alive"}

### Generate Sources
def generateSources():
  sourceList = []

  conn = httplib.HTTPSConnection("www.netflix.com")
  conn.request(method="GET", url="/Kids", headers=headerDict)
  response = conn.getresponse()
  data = response.read()
  kidsHTM = GzipFile(fileobj=StringIO(data)).read()

  file = open("kids_htm_sources/Kids", 'wt')
  file.write(kidsHTM)
  file.close()

  sourceList.append("Kids")

  kidsParsed = BeautifulSoup(kidsHTM, 'lxml')

  navigation = kidsParsed.find('div', 'subnav-wrap col-5')

  for link in navigation.find_all('a'):
    address = link.get('href')
    if "category" in address:
      conn = httplib.HTTPSConnection("www.netflix.com")
      conn.request(method="GET", url=address, headers=headerDict)
      response = conn.getresponse()
      data = response.read()
      categoryHTM = GzipFile(fileobj=StringIO(data)).read()
      categoryNum = address[15:]

      file = open("kids_htm_sources/" + categoryNum, 'wt')
      file.write(categoryHTM)
      file.close()

      sourceList.append(categoryNum)

  return sourceList

#### Crawl Sources
def crawlSource(source, videoDict, showDict):
  sourceParsed = BeautifulSoup(source, 'lxml')

  for div in sourceParsed.find_all('div', 'agMovie agMovie-lulg'):
    # the image's alt text is the name of the Movie/Series
    #image = div.find('img')
    #title = image.get('alt')
    span = div.find('span')
    spanClass = span.get('class')[0]
    if spanClass != "title":
        continue
    title = span.get_text()
    # if there is an "episodeBadge", then this is a link to a list of episodes...
    # ...otherwise, this is a direct link to a movie
    aList = div.find_all('a', 'episodeBadge')

    if (len(aList) == 0):
      link = div.find('a')
      videoDict[title] = 'https:' + link.get('href').split('?')[0].split(':')[1]
      #print (title + "\t" + link.get('href').split('?')[0]).encode('utf8') ### debugging line

    else:
      link = div.find('a', 'episodeBadge')
      showDict[link.get('href').split('?')[0]] = title

#### Crawl Show
def crawlShow(showName, showLink, videoDict):
  conn = httplib.HTTPSConnection("www.netflix.com")
  conn.request(method="GET", url=showLink, headers=headerDict)
  response = conn.getresponse()
  data = response.read()
  showHTM = GzipFile(fileobj=StringIO(data)).read()

  showParsed = BeautifulSoup(showHTM, 'lxml')

  titleToEpisode = {}

  for div in showParsed.find_all('div', 'ebob-content transp'):
    titleToEpisode[div.find('span', 'title').get_text()] = div.find('h3').get_text()

  for div in showParsed.find_all('div', 'agMovie agMovie-lulg'):
    image = div.find('img')
    title = image.get('alt')

    try:
      episodeNumber = titleToEpisode[title]
    except KeyError:
      continue

    link = div.find('a')
    videoDict[showName + "/" + episodeNumber] = 'https:' + link.get('href').split('?')[0].split(':')[1]
    #print (showName + "/" + episodeNumber + "\t" + link.get('href').split('?')[0]).encode('utf8') ### debugging line


#### MAIN PROGRAM ####
def runScrape(update_sources=False):
    videoDict = {}
    showDict = {}

    # start at www.netflix.com/Kids and enumerate all categories
    if update_sources:
        kidSources = generateSources()
    else:
        cur_directory = os.path.dirname(os.path.realpath(__file__))
        kids_dir = cur_directory + '/kids_htm_sources/'
        kidSources = []
        for filename in os.listdir(kids_dir):
            kidSources.append(filename)
        print(kidSources)
        time.sleep(30)

    print("Matching crawled URLs with movie names")
    date = time.strftime("%m_%d")
    final_results = open("results/kidsResults_" + date + ".txt", 'wt')

    # crawl each category
    for sourceID in kidSources:
      file = open("kids_htm_sources/" + sourceID, 'rt')
      source = file.read()
      file.close()
      crawlSource(source, videoDict)

    # deeper crawl over the pages for each show
    print("Total number of sites to visit is: " + str(len(showDict)))
    totalVisited = 0
    for key, value in showDict.iteritems():
      crawlShow(value, key, videoDict)
      totalVisited += 1
      if totalVisited % 25 == 0:
        print("Visited " + str(totalVisited) + " out of " + str(len(showDict)))

    # final dump of all individual videos



    for key, value in videoDict.iteritems():
      #print (key + "\t" + value).encode('utf8')
      final_results.write((key + "\t" + value + '\n').encode('utf8'))
    final_results.close()
    if __name__ != "__main__":
        return videoDict

if __name__ == "__main__":
    runScrape(update_sources=False)

