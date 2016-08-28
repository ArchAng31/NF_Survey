# -*- coding: utf-8 -*-

import os
import sqlite3
from operator import itemgetter
import time

date = time.strftime("%m_%d")
cur_directory = os.path.dirname(os.path.realpath(__file__))
results_dir = cur_directory + '/scraper/results/'
movies = {}
for filename in sorted(os.listdir(results_dir)): ###sort so newest comes last
    if filename[0:4] == 'main' or filename[0:3] == 'all': ###just sites starting with main
        print("Matching crawled URLs with movie names from " + filename)
        sites_file = open(results_dir + filename, "rt")
        with sites_file as f:
            lines = f.read().split('\n')
            for line in lines:
                if line != '':
                    movie_split = line.split('\t')
                    movies[movie_split[1]] = movie_split[0]

fingerprints = []
crawled_movies = {}
fingerPrintsTest = {}


###Handle the multiple databases
database_dir = cur_directory + '/databases/'
duplicate_file = open("duplicateFingerprints_" + date + ".txt", 'wt')
for filename in os.listdir(database_dir):
    print("Handling DB " + database_dir + filename)
    db = sqlite3.connect(database_dir + filename)
    curr = db.cursor()
    var = curr.execute('SELECT * FROM netflix_fingerprints;')
    for item in var:
        crawled_movies[item[1]] = True
        sizeStrings = item[2].split('\t')[1].split(',')
        sizeInts = map(int, sizeStrings)
        #Do not count if very small (i.e. an audio track)
        if max(sizeInts) > 51000:
            #Now check to see if you have duplicate fingerprints
            if item[2] not in fingerPrintsTest:
                fingerPrintsTest[item[2]] = item[1]
                fingerprints.append((movies[item[1]], item[2]))
            elif fingerPrintsTest[item[2]] != item[1]:
                duplicate_file.write('{:>5}'.format(item[2].split('\t', 1)[0]) + "\t" + item[1] + " " + movies[item[1]] + '\n')
                duplicate_file.write('{:>5}'.format(item[2].split('\t', 1)[0]) + "\t" + fingerPrintsTest[item[2]] + " " + movies[item[1]] + '\n')
                print("Found duplicate " + '{:>5}'.format(item[2].split('\t', 1)[0]) + "  from " + item[1] + " " + movies[item[1]])
                print("Duplicate is    " + '{:>5}'.format(item[2].split('\t', 1)[0]) + "  from " + fingerPrintsTest[item[2]] + " " + movies[item[1]])
    db.close()
duplicate_file.close()

###Checking for missed movies
missed_movies = []
for filename in os.listdir(results_dir):
    if filename[0:4] == 'main' or filename[0:3] == 'all': ###just sites starting with main
        sites_file = open(results_dir + filename, "rt")
        with sites_file as f:
            lines = f.read().split('\n')
            for line in lines:
                if line != '':
                    movie_split = line.split('\t')
                    if movie_split[1] not in crawled_movies:
                        missed_movies.append(line)
missed_movies = set(missed_movies)
missed_file = open("missedMovies_" + date + ".txt", 'wt')
for movie in sorted(missed_movies):
    missed_file.write(movie + '\n')
missed_file.close()

#Count windows in fingerprints
output_file = open("fingerprintOutput_" + date + ".txt", "wt")
totalWindows = 0
for item in sorted(fingerprints, key=itemgetter(0)):
    output_file.write(item[0])
    output_file.write('\t' + item[1] + '\n')
    totalWindows += item[1].count(',')+1
output_file.close()

print("Total missed movies from all crawls is " + str(len(missed_movies)))
print("Total Fingerprints is " + str(len(fingerprints)))
print("Total Number of segments is " + str(totalWindows))
print("Average segments per movie is " + str(totalWindows/float(len(fingerprints))))

