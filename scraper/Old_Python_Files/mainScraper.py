import httplib
from gzip import GzipFile
from StringIO import StringIO
from bs4 import BeautifulSoup
import time

# this will spoof a Firefox browser
kidHeaderDict = {"Host": "www.netflix.com",
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

headerDict = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
              "Accept-Encoding": "gzip, deflate, br",
              "Accept-Language": "en-US,en;q=0.5",
              "Connection": "keep-alive",
              "Cookie": "memclid=a528c842-86b0-4d9d-9fd8-74d747e0139c; NetflixId=v%3D2%26ct%3DBQAOAAEBEP-77ELQz_suTXqlEnFOjE6" \
                        "BoIfqRbR11e8xH70B3aBQ283GIinMpsDUdqU0hptZkTRFfh2RdLYsuglIIFvdiV7fewO90mdXOW8tbVwSDYL2srehfn1sD0AAFpu" \
                        "URmaKIuOikynf2NG8G4RCDoWxvNRbylBW-HM6Buv7w-PsiYp_t_9v_SPsvAFtbCi9Rtibr52IerlYLuZw7mmcFvmNdXl1ncLLfwd" \
                        "1MfzDsiRgqfulTiJIPdc6vj86tBJWX2b-aNf6ZCKxYTaSkvFoifubEsJXXI5J2tEu1rT5-daAHS27gpKGLeUF6lK8QuiROUk4Ugf" \
                        "DfHCPFLX4A69IYwU4sULup7bdtZjrZXBzP0ep1Ijr5EXY08o0-gkwkWejapItlnXOMqOV4n9lBzGx30_wDXA1LiYWmZtxsOefyz5" \
                        "n4exKsWOAzC3s5TuamBLyRIzShcx1zdCg9AD3l47bSN1NwbzE2HdL6uXkBFbAfOc4qQVauUS6QZQHHwFapfGR7PRtQb9FmvTyKKrRaY5X-Rb3nYz7bmJGuYroh0ceug_gqeqfFQywRZg1NohEN8Z4YRuZiouW" \
                        "%26bt%3Ddbl%26ch%3DAQEAEAABABTgz_w6oCAgAB33M_knRXckQMzRb4QxVqg.%26mac%3DAQEAEAABABQr5BgK3TxcY9_qTffJzvTPpSmUn-c0k5U" \
                        ".; SecureNetflixId=v%3D2%26mac%3DAQEAEQABABS-Ed_7VJoBQbjYxxdnhzoUlfhbvF5pURQ.%26dt%3D1458588306627; nmab" \
                        "=MDAxLTY1NDM6Mg%3D%3D; cL=1458588310394%7C145858686293632152%7C145858686211746564%7C%7C51%7C3HAZXSFPVNBFLAOWA6FX5VACAA" \
                        "; profilesNewSession=0; profilesNewUser=0; lhpuuidh-browse-3HAZXSFPVNBFLAOWA6FX5VACAA=US%3AEN-US%3A05309c63-0184-45b3-b0b2-8e43fc81b797_ROOT" \
                        "; lhpuuid-kid-FEKOSOZ7WJFKVDHKPYE7NVMESQ=US%3AEN-US%3Aaf44251e-388c-423c-ae9e-0f768ae09490_ROOT; docBytes" \
                        "=182285",
              "Host":"www.netflix.com",
              "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0"}

###Load Genre Files
def loadGenres():
    cat_file = open("neflixCategories.txt", 'rt')
    genreList = []
    genreDict = {}
    with cat_file as f:
      lines = f.read().split('\n')
      for line in lines:
        id = line.split(':')[1].strip()
        genreList.append(id)
        genreDict[id] = line.split(':')[0].strip()
    return genreList, genreDict

### Download Genres
def downloadGenres(genreList, genreDict):

  for genre in genreList:
    conn = httplib.HTTPSConnection("www.netflix.com")
    conn.request(method="GET", url="/browse/genre/" + genre,headers=headerDict)
    response = conn.getresponse()
    data = response.read()
    print("Getting " + genre + " - " + genreDict[genre] + "   "),
    print(response.status, response.reason)
    genreHTM = GzipFile(fileobj=StringIO(data)).read()

    file = open("main_htm_sources/" + genre, 'wt')
    file.write(genreHTM
    file.close()

#### Crawl Genres
def scrapeGenres(genreList, initialDict):
  for genre in genreList:
    file = open("main_htm_sources/" + genre, 'rb')
    data = file.read()
    file.close()
    page = BeautifulSoup(data, 'lxml')

    for div in page.find_all('div', 'smallTitleCard lockup title_card sliderRefocus '):
      title = div.get('aria-label')

      videoID = div.get('data-reactid').split('_')[1]

      initialDict[videoID] = title

### Download Searches
def downloadSearches():
  for x in range(97, 123):
    conn = httplib.HTTPSConnection("www.netflix.com")
    conn.request(method="GET", url="/search/" + chr(x),headers=headerDict)
    response = conn.getresponse()
    data = response.read()
    print("Getting " + chr(x))
    print(response.status, response.reason)
    searchHTM = GzipFile(fileobj=StringIO(data)).read()

    file = open("main_htm_sources/" + chr(x), 'wt')
    file.write(searchHTM)
    file.close()



#### Crawl Searches
def scrapeSearches(initialDict):
  for x in range(97,123):
    file = open("main_htm_sources/" + chr(x), 'rb')
    data = file.read()
    file.close()
    page = BeautifulSoup(data, 'lxml')

    for div in page.find_all('div', 'smallTitleCard lockup title_card sliderRefocus '):
      title = div.get('aria-label')

      videoID = div.get('data-reactid').split('_')[1]

      #initialDict[title] = videoID
      initialDict[videoID] = title

#### Crawl Show
def checkIfShowOrMovie(showName, showLink, videoDict):
  conn = httplib.HTTPSConnection("www.netflix.com")
  conn.request(method="GET", url="/Kids/title/" + showLink,headers=kidHeaderDict)
  response = conn.getresponse()
  print(response.code)
  data = response.read()
  showHTM = GzipFile(fileobj=StringIO(data)).read()

  if "<p>We were unable to process your request.</p>" in showHTM:
    videoDict[showName] = "https://www.netflix.com/watch/" + showLink
    #print (showName + "\thttp://www.netflix.com/watch/" + showLink).encode('utf8') ### debugging line
    return

  showParsed = BeautifulSoup(showHTM, 'lxml')

  titleToEpisode = {}

  for div in showParsed.find_all('div', 'ebob-content transp'):
    titleToEpisode[div.find('span', 'title').get_text()] = div.find('h3').get_text()

  #print ("Show: " + showName + "\t" + showLink.get('href').split('?')[0]).encode('utf8') ### debugging line
  for div in showParsed.find_all('div', 'agMovie agMovie-lulg'):
    #image = div.find('img')
    #title = image.get('alt')
    span = div.find('span')
    spanClass = span.get('class')[0]
    if spanClass != "title":
      continue
    title = span.get_text()

    try:
      episodeNumber = titleToEpisode[title]
    except KeyError:
      continue

    link = div.find('a')
    videoDict[showName + "/" + episodeNumber] = 'https:' + link.get('href').split('?')[0].split(':')[1]
    #print (showName + "/" + episodeNumber + "\t" + link.get('href').split('?')[0]).encode('utf8') ### debugging line


#### MAIN PROGRAM ####
def runScrape(update_sources=True):
    genreList, genreDict = loadGenres()
    #genreList = ["83", "1365", "7424", "783", "31574", "6548", "7627", "6839", "5763", "26835", "5977", "8711", "7077", "78367", "1701", "13335", "8883", "1492", "4370", "8933"]
    if update_sources:
        downloadGenres(genreList, genreDict)
        downloadSearches()
    initialDict = {}
    videoDict = {}
    scrapeGenres(genreList, initialDict)
    print("Genre Scrape Complete")
    scrapeSearches(initialDict)
    print("Search Scrape Complete")
    numLinks = len(initialDict)
    print("Total number of sites to visit is: " + str(numLinks))
    totalVisited = 0
    for key, value in initialDict.iteritems():
      checkIfShowOrMovie(value, key, videoDict)
      totalVisited += 1
      if totalVisited % 50 == 0:
        print("Visited " + str(totalVisited) + " out of " + str(numLinks))


    # final dump of all individual videos
    date = time.strftime("%m_%d")
    final_results = open("results/mainResults_" + date + ".txt", 'wt')
    for key, value in videoDict.iteritems():
      #print (key + "\t" + value).encode('utf8')
      final_results.write((key + "\t" + value + '\n').encode('utf8'))
    final_results.close()
    if __name__ != "__main__":
        return videoDict

if __name__ == "__main__":
    runScrape(update_sources=False)

