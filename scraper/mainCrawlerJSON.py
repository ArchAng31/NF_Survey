import httplib
import json
import time
import os
from gzip import GzipFile
from StringIO import StringIO
from bs4 import BeautifulSoup


maxSeasons = 20
maxEpisodes = 40

headerDict = {"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
              "Accept-Encoding":"gzip, deflate, br",
              "Accept-Language":"en-US,en;q=0.5",
              "Connection":"keep-alive",
              "Cookie": "memclid=e004fc9c-f4ac-4b36-a602-831e9b0e437b; nfvdid=BQFmAAEBEC0oSZfYwyCO%2F0cSPeFowo5QBDWyGyqaowwkHqRhVF2wi4m8fmiLIHWdUgUUJ27N38UTL" \
                        "%2Fs7XbtuKZ504%2FnUScPd2dHm92SVc0CcaS%2FFOZ5QFT4sAytHO%2BWZdx3DVZtCLZE%3D; NetflixId=ct%3DBQAOAAEBEI" \
                        "tTh6JW7RPUb1VkCcCJ35OBwMFP7eeLBZAt_WUnykRwbls-KtXDH7M_movXtitHDEgFyT0OqN7pt8PNhCAkS8VDs3iHrgAyGURRh1" \
                        "pI8dLx06PCBtq8M9G1qB9izxPfQOLL4LdQd2G9usVIX85AdnlD_5vHfkUjJKse1bpbsY9KaMaPRn8abaQwz5CdOR5kMcUroqoXXn" \
                        "yyi-RQHgiP9og81wDSp57uybeUsioltV_ObyBSv_O0MWwuRsFlP-QKNXk89e-lNZSudVjoRLtOdi14BucD1orRIkZbrifk61sdxU" \
                        "i3FiwqF6peb5d0oNfPSl2MSoo6XbZjpxVTAQfCH3J6pimDz4XwkglbGcVNIhw_DV_yPbYTfNbvuiy3zzi5UufPHhlpmeUmuvXuJj" \
                        "ZEF0K_ESuIrSnaUBMj5geIXvxl8kif5eLwiWLMh2XfcB51hhEWkKgt_7UxRn1Q1R8Ap7k6_R8AsSdpIJR0vwCjzHTBRLtJARlY0_" \
                        "_2Klm1BteRK7AVkZoEkFrU3ezVgcNeSzZ6l7L6fuLIAL4P-_Osa-klit8d-IoO3s0SmOva-Jevr2Zg8jNoZkF2qd9AhvMo_vYMihcY91_T6L2nHsdKlDEOhbs" \
                        ".%26bt%3Ddbl%26ch%3DAQEAEAABABRSaIonHc56Whd4n7kloeMtc32ls9cpOeE.%26v%3D2%26mac%3DAQEAEAABABRQWaQTcY2Qrz3msw0jSCKrlyQrxlxLsQM" \
                        ".; SecureNetflixId=v%3D2%26mac%3DAQEAEQABABRn2qgSse5ame4jaexwwNNL0c5SRWoHU6A.%26dt%3D1460743143113; nmab" \
                        "=MDAxLTY1NDM6MQ%3D%3D; cL=1460743120276%7C146074311710006448%7C146074311715117126%7C%7C15%7CMO7C5FNXMZDIDPVJA4V23WSIIM" \
                        "; profilesNewSession=0; profilesNewUser=0; lhpuuidh-browse-3HAZXSFPVNBFLAOWA6FX5VACAA=US%3AEN-US%3A3" \
                        "a95dbd9-d0ab-4c6b-8214-dc83edba7dc2_ROOT",
              "Host":"www.netflix.com",
              "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0"}
		    
kidHeaderDict = {"Host": "www.netflix.com",
                 "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0",
                 "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                 "Accept-Language": "en-US,en;q=0.5",
                 "Accept-Encoding": "gzip, deflate, br",
                 "Cookie": "memclid=e004fc9c-f4ac-4b36-a602-831e9b0e437b; nfvdid=BQFmAAEBEC0oSZfYwyCO%2F0cSPeFowo5QBDWyGyqaowwkHqRhVF2wi4m8fmiLIHWdUgUUJ27N38UTL" \
                           "%2Fs7XbtuKZ504%2FnUScPd2dHm92SVc0CcaS%2FFOZ5QFT4sAytHO%2BWZdx3DVZtCLZE%3D; NetflixId=v%3D2%26ct%3DBQ" \
                           "AOAAEBEJM0WyIL3ieIuZX6IMnzXZKBwGsiiT5JE2KKN4fbjmaxw8eqS8ssGGMXdA7g7Vo3lest6qnC8GqdG8rdERO5oSAfss6mdK" \
                           "0jN3a8HGtnZOzC4YdfMQN0sWF51eKxI3RGsKPeeOKVlm0EOlFMJThgMIwUjcE1GzZe6pbGvr3AUhZ2crNSLxI1mjPel7WHsi9U7U" \
                           "N2zvrLt5WmWzEqJLWYctGN8H0iMVtvovat14uwwSW6mKNgncCvcK4OPZokmJmycC6qZv1mbeMqozDhb-1K_16tbjY68bgUcofGUt" \
                           "4QfcjGB2MOYx7tl1iSXLjQwxTKdXL8noautGH_7YOeH8jGMEC9XbUE7CP9BlRT1FFI9hR3fyOte8upGVvbXDXFW4UR_NbktKqHqj" \
                           "9u_rkfFfnwz5RknPceur1S8TMIbnufmhNZCIjkesIfq1ntPt9U1yaPIfo3fJx3zxRD0ocRTrPYaPRqspUn1HwnCrcJO_uBaA6K18" \
                           "d1ufFf40rzgij-QR4kiwjzoDIy1nDk-VZe-URXEdg9AL1tCaXBYaR3fXRcu78z7RGfqhP2udYxD4ubmrNVQmddLho_UHatDN001IiuCY4KN4zN_M_C_Qx89SJE3u3BAsw" \
                           ".%26bt%3Ddbl%26ch%3DAQEAEAABABQAV74vJcFM-86tIr-n2F9X6IHeBsscR_0.%26mac%3DAQEAEAABABTzWh8-nH06LZjBlihyCaUCuWgk1CMYnLA" \
                           ".; SecureNetflixId=v%3D2%26mac%3DAQEAEQABABQSt0MeTRBtK2ussa19WPcLWj9GSyY0KhY.%26dt%3D1460745107865; nmab" \
                           "=MDAxLTY1NDM6MQ%3D%3D; cL=1460745107881%7C14607431446731730%7C146074314447585226%7C%7C31%7C3HAZXSFPVNBFLAOWA6FX5VACAA" \
                           "; profilesNewSession=0; profilesNewUser=0; lhpuuidh-browse-3HAZXSFPVNBFLAOWA6FX5VACAA=US%3AEN-US%3A3a95dbd9-d0ab-4c6b-8214-dc83edba7dc2_ROOT" \
                           "; docBytes=219772",
                 "Connection": "keep-alive"}

jsonHeaderDict = {"Host": "www.netflix.com",
                 "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0",
                 "Accept": "application/json, text/javascript, */*",
                 "Accept-Language": "en-US,en;q=0.5",
                 "Accept-Encoding": "gzip, deflate, br",
                 "Content-Type": "application/json",
                 "Cookie": "memclid=e004fc9c-f4ac-4b36-a602-831e9b0e437b; nfvdid=BQFmAAEBEPTrH8mjyfF1dPoFV1cDKx4wGx36enRIMLeCMpery6" \
                           "/vqODqjJJwxtc97Q03YkhGi9JDFWOkH9je21PUdigAOmhR; NetflixId=v%3D2%26ct%3DBQAOAAEBEJM0WyIL3ieIuZX6IMnzX" \
                           "ZKBwGsiiT5JE2KKN4fbjmaxw8eqS8ssGGMXdA7g7Vo3lest6qnC8GqdG8rdERO5oSAfss6mdK0jN3a8HGtnZOzC4YdfMQN0sWF51" \
                           "eKxI3RGsKPeeOKVlm0EOlFMJThgMIwUjcE1GzZe6pbGvr3AUhZ2crNSLxI1mjPel7WHsi9U7UN2zvrLt5WmWzEqJLWYctGN8H0iM" \
                           "Vtvovat14uwwSW6mKNgncCvcK4OPZokmJmycC6qZv1mbeMqozDhb-1K_16tbjY68bgUcofGUt4QfcjGB2MOYx7tl1iSXLjQwxTKd" \
                           "XL8noautGH_7YOeH8jGMEC9XbUE7CP9BlRT1FFI9hR3fyOte8upGVvbXDXFW4UR_NbktKqHqj9u_rkfFfnwz5RknPceur1S8TMIb" \
                           "nufmhNZCIjkesIfq1ntPt9U1yaPIfo3fJx3zxRD0ocRTrPYaPRqspUn1HwnCrcJO_uBaA6K18d1ufFf40rzgij-QR4kiwjzoDIy1" \
                           "nDk-VZe-URXEdg9AL1tCaXBYaR3fXRcu78z7RGfqhP2udYxD4ubmrNVQmddLho_UHatDN001IiuCY4KN4zN_M_C_Qx89SJE3u3BAsw" \
                           ".%26bt%3Ddbl%26ch%3DAQEAEAABABQAV74vJcFM-86tIr-n2F9X6IHeBsscR_0.%26mac%3DAQEAEAABABTzWh8-nH06LZjBlihyCaUCuWgk1CMYnLA" \
                           ".; SecureNetflixId=v%3D2%26mac%3DAQEAEQABABQSt0MeTRBtK2ussa19WPcLWj9GSyY0KhY.%26dt%3D1460745107865; nmab" \
                           "=MDAxLTY1NDM6MQ%3D%3D; cL=1460745118455%7C14607431446731730%7C146074314447585226%7C%7C40%7C3HAZXSFPVNBFLAOWA6FX5VACAA" \
                           "; profilesNewSession=0; profilesNewUser=0; lhpuuidh-browse-3HAZXSFPVNBFLAOWA6FX5VACAA=US%3AEN-US%3A3a95dbd9-d0ab-4c6b-8214-dc83edba7dc2_ROOT" \
                           "; docBytes=163485",
                 "Connection": "keep-alive"}

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
        if response.status == 200:
            genreHTM = GzipFile(fileobj=StringIO(data)).read()
            file = open("htm_sources/" + genre, 'wt')
            file.write(genreHTM)
            file.close()
        else:
            print response

#### Crawl Genres
def crawlGenres(genreList, initialDict):
    for genre in genreList:
        file = open("htm_sources/" + genre, 'rb')
        data = file.read()
        file.close()
        page = BeautifulSoup(data, 'lxml')

        for div in page.find_all('div', 'smallTitleCard lockup title_card sliderRefocus '):
            title = div.get('aria-label')
            
            videoID = div.get('data-reactid').split('_')[1]

            #initialDict[title] = videoID
            initialDict[videoID] = title


# Download Searches
def downloadSearches():
    for x in range(97,123):
        conn = httplib.HTTPSConnection("www.netflix.com")
        conn.request(method="GET", url="/search/" + chr(x), headers=headerDict)
        response = conn.getresponse()
        data = response.read()
        searchHTM = GzipFile(fileobj=StringIO(data)).read()

        file = open("htm_sources/" + chr(x), 'wt')
        file.write(searchHTM)
        file.close()


# Crawl Searches
def crawlSearches():
  initialDict = {}
  for x in range(97,123):
    file = open("htm_sources/" + chr(x), 'rb')
    data = file.read()
    file.close()

    page = BeautifulSoup(data)

    for div in page.find_all('div', 'smallTitleCard lockup title_card sliderRefocus '):
      title = div.get('aria-label')

      videoID = div.get('data-reactid').split('_')[1]
      initialDict[videoID] = title
  return initialDict

#### Crawl Show
def crawlShow(showName, showLink, authURL, videoDict, final_results):
  if authURL == "":
    conn = httplib.HTTPSConnection("www.netflix.com")
    conn.request(method="GET", url="/Kids/title/" + showLink,headers=kidHeaderDict)
    response = conn.getresponse()
    data = response.read()
    showHTM = GzipFile(fileobj=StringIO(data)).read()
    authURL = showHTM[(showHTM.find('"authURL":"')+11):].split('"')[0]

  jsonPut = '{"paths":[["videos",'+showLink+',"seasonList",{"from":0,"to":'+str(maxSeasons)+'},"summary"],["videos",'+showLink+',"seasonList","summary"],["videos",'+showLink+',"seasonList","current","episodes",{"from":-1,"to":'+str(maxEpisodes)+'},["summary","synopsis","title","runtime","bookmarkPosition"]],["videos",'+showLink+',"seasonList","current","episodes",{"from":-1,"to":'+str(maxEpisodes)+'},"interestingMoment","_342x192","jpg"],["videos",'+showLink+',"seasonList","current","episodes","summary"],["videos",'+showLink+',"seasonList","current","episodes","current","summary"]],"authURL":"'+authURL+'"}'

  count = 0
  found = False
  while count < 5:
    count += 1
    conn = httplib.HTTPSConnection("www.netflix.com")
    conn.request(method="POST", url="/api/shakti/e6f64e0c/pathEvaluator?withSize=true&materialize=true&model=harris", body=jsonPut, headers=jsonHeaderDict)
    response = conn.getresponse()
    data = response.read()
    jsonString = GzipFile(fileobj=StringIO(data)).read()

    try:
      jsonData = json.loads(jsonString)
      found = True
      break
    except:
      continue

  if not found:
      return

  seasonList = []
  for x in range(0, maxSeasons+1):
    if len(jsonData['value']['videos'][showLink]["seasonList"][str(x)]) == 2:
      seasonList.append(jsonData['value']['videos'][showLink]["seasonList"][str(x)][1])

  if len(seasonList) == 0:
    final_results.write((showName + "\thttp://www.netflix.com/watch/" + showLink + '\n').encode('utf8'))
    videoDict[showName] = ("http://www.netflix.com/watch/" + showLink).encode('utf8')
    return

  for seasonLink in seasonList:
    jsonPut = '{"paths":[["seasons",'+seasonLink+',"episodes",{"from":-1,"to":'+str(maxEpisodes)+'},["summary","synopsis","title","runtime","bookmarkPosition"]],["seasons",'+seasonLink+',"episodes",{"from":-1,"to":'+str(maxEpisodes)+'},"interestingMoment","_342x192","jpg"],["seasons",'+seasonLink+',"episodes","summary"],["seasons",'+seasonLink+',"episodes","current","summary"]],"authURL":"'+authURL+'"}'

    while True:
      conn = httplib.HTTPSConnection("www.netflix.com")
      conn.request(method="POST", url="/api/shakti/e6f64e0c/pathEvaluator?withSize=true&materialize=true&model=harris", body=jsonPut, headers=jsonHeaderDict)
      response = conn.getresponse()
      data = response.read()
      jsonString = GzipFile(fileobj=StringIO(data)).read()

      try:
        jsonData = json.loads(jsonString)
        break
      except:
        continue

    episodeList = []
    for x in range(-1, maxEpisodes+1):
      if len(jsonData['value']['seasons'][seasonLink]["episodes"][str(x)]) == 2:
        episodeList.append(jsonData['value']['seasons'][seasonLink]["episodes"][str(x)][1])

    for episodeLink in episodeList:
      seasonNum  = str(jsonData['value']['videos'][episodeLink]["summary"]["season"])
      episodeNum = str(jsonData['value']['videos'][episodeLink]["summary"]["episode"])
      final_results.write((showName + "/Season " + seasonNum + " : Episode " + episodeNum + "\thttp://www.netflix.com/watch/" + episodeLink + '\n').encode('utf8'))
      videoDict[showName + "/Season " + seasonNum + " : Episode " + episodeNum] = ("http://www.netflix.com/watch/" + episodeLink).encode('utf8')


### Generate Kid Sources
def downloadKidSources(authURL):
    kidCategories = []
    if authURL == "":
        conn = httplib.HTTPSConnection("www.netflix.com")
        conn.request(method="GET", url="/Kids", headers=kidHeaderDict)
        response = conn.getresponse()
        data = response.read()
        showHTM = GzipFile(fileobj=StringIO(data)).read()
        authURL = showHTM[(showHTM.find('"authURL":"')+11):].split('"')[0]

    jsonPut = '{"paths":[["genreList",{"from":0,"to":40},["id","menuName"]],["genreList","summary"]],"authURL":"'+authURL+'"}'

    while True:
        conn = httplib.HTTPSConnection("www.netflix.com")
        conn.request(method="POST", url="/api/shakti/e6f64e0c/pathEvaluator?withSize=true&materialize=true&model=harris", body=jsonPut, headers=jsonHeaderDict)
        response = conn.getresponse()
        data = response.read()
        jsonString = GzipFile(fileobj=StringIO(data)).read()

        try:
            jsonData = json.loads(jsonString)
            break
        except:
            continue

    for x in range(0, 41):
        if len(jsonData['value']['genreList'][str(x)]) == 2:
            kidCategories.append(jsonData['value']['genreList'][str(x)][1])

    for kidCategory in kidCategories:
        conn = httplib.HTTPSConnection("www.netflix.com")
        conn.request(method="GET", url="/Kids/category/"+kidCategory, headers=kidHeaderDict)
        response = conn.getresponse()
        data = response.read()
        categoryHTM = GzipFile(fileobj=StringIO(data)).read()
        print("Getting Kids Category " + kidCategories),
        print(response.status, response.reason)

        file = open("htm_sources/kid_" + kidCategory, 'wt')
        file.write(categoryHTM)
        file.close()
    return kidCategories

def loadKidCategories():
    kidsCategories = []
    curDir = os.path.dirname(os.path.realpath(__file__))
    for file in os.listdir(curDir + "htm_sources/"):
        if file[0:4] == "kid_":
            print(file)
            kidsCategories.append(file)
    return kidsCategories

#### Crawl Kid Sources
def crawlKidSources(kidCategories, initialDict):
    for category in kidCategories:
        #file = open("kids_htm_sources/" + category, 'rb')
        file = open("htm_sources/kid_" + category, 'rb')
        data = file.read()
        file.close()
        page = BeautifulSoup(data)

        for div in page.find_all('div', 'smallTitleCard lockup title_card sliderRefocus '):
            title = div.get('aria-label')

            videoID = div.get('data-reactid').split('_')[1]
            initialDict[videoID] = title

#### Crawl Sources
def crawlKidSource_old(kidCategories, initialDict):
    for category in kidCategories:
        file = open("kids_htm_sources/" + category, 'rb')
        data = file.read()
        file.close()
        sourceParsed = BeautifulSoup(data, 'lxml')
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
                initialDict[title] = 'https:' + link.get('href').split('?')[0].split(':')[1]
                #print (title + "\t" + link.get('href').split('?')[0]).encode('utf8') ### debugging line

            else:
                link = div.find('a', 'episodeBadge')
                initialDict[link.get('href').split('?')[0]] = title


#### MAIN PROGRAM ####
def runScrape(update_sources=True):
    genreList, genreDict = loadGenres()
    authURL = ""
    if update_sources:
        downloadGenres(genreList, genreDict)
        downloadSearches()
        kidCategories = downloadKidSources(authURL)
    else:
        kidCategories = loadKidCategories()
    initialDict = crawlSearches()
    print("Search Crawl Complete, Total after searches is: " + str(len(initialDict)))
    crawlGenres(genreList, initialDict)
    print("Genre Crawl Complete, Total after genres is: " + str(len(initialDict)))
    crawlKidSources(kidCategories, initialDict)
    print("Kids Crawl Complete, Total after kids is: " + str(len(initialDict)))
    numLinks = len(initialDict)
    print("Total number of sites to visit is: " + str(numLinks))
    totalVisited = 0
    videoDict = {}
    date = time.strftime("%m_%d")
    final_results = open("results/allResults_" + date + ".txt", 'wt')###used to be a+
    sitesFile = open("results/sitesVisited_" + date + ".txt", 'wt')###used to be a+ instead of wt
    sitesFile.seek(0)
    sitesVisited = {}
    lines = sitesFile.read().decode('utf8').split('\n')
    for line in lines:
        if '\t' in line:
            line = line.split('\t')
            sitesVisited[line[0]] = line[1]
    print("Sites Visited Previous: " + str(len(sitesVisited)))
    for key, value in initialDict.iteritems():
        if key in sitesVisited:
            if sitesVisited[key] == value:
                totalVisited += 1
                continue
        while True:
            try:
                crawlShow(value, key, authURL, videoDict, final_results)
                break
            except:
                print("************************* FAILED ON THIS ONE --> " + key + " " + value)
                pass

        totalVisited += 1
        sitesFile.write((key + '\t' + value + '\n').encode('utf8'))
        if totalVisited % 25 == 0:
            print("Visited " + str(totalVisited) + " out of " + str(numLinks))
    # final dump of all individual videos
    #for key, value in videoDict.iteritems():
      #print (key + "\t" + value).encode('utf8')
      #final_results.write((key + "\t" + value + '\n').encode('utf8'))
    final_results.close()
    if __name__ != "__main__":
        return videoDict

if __name__ == "__main__":
    runScrape(update_sources=True)




