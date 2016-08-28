import os
import time

import scraper.Old_Python_Files.kidsScraper.py as kids

from scraper.Old_Python_Files import mainScraper as main

kidsDict = kids.runScrape(update_sources=False)
mainDict = main.runScrape(update_sources=False)

totalDict = {}
for key, value in kidsDict.iteritems():
    totalDict[key] = value
for key, value in mainDict.iteritems():
    totalDict[key] = value

date = time.strftime("%m_%d")
final_results = open("results/totalResults_" + date + ".txt", 'wt')
for key, value in kids.iteritems():
    final_results.write((key + "\t" + value + '\n').encode('utf8'))
final_results.close()


cur_directory = os.path.dirname(os.path.realpath(__file__))
results_dir = cur_directory + '/results/'
for filename in os.listdir(results_dir):
    print("Matching crawled URLs with movie names")
