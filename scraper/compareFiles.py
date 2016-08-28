old_movies = {}
with open("results/mainResults_03_21.txt", 'rt') as f:
    lines = f.read().split('\n')
    for line in lines:
        movie_split = line.split('\t')
        if len(movie_split) > 1:
            old_movies[movie_split[1].strip()] = movie_split[0]
            #print(movie_split[1].strip(), movie_split[0])


movies = {}
with open("results/mainResults_04_19_backup.txt", 'rt') as f:
    lines = f.read().split('\n')
    for line in lines:
        movie_split = line.split('\t')
        if len(movie_split) > 1:
            movies[movie_split[1].strip()] = movie_split[0]
            #print(movie_split[1].strip(), movie_split[0])
#print(movies)

count = 0
for serialNumber, title in old_movies.iteritems():
    #print(movie, serialNumber)

    if serialNumber in movies:
        if title.strip() != movies[serialNumber].strip():
            if 'last man standing' in title.strip().lower():
              print(title, movies[serialNumber])
            count += 1
print(count)
print(len(old_movies))