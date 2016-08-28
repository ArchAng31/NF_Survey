

movies = {}
sites_file = open("allResults.txt", "rt")
with sites_file as f:
    lines = f.read().split('\n')
    for line in lines:
        movie_split = line.split('\t')
        if len(movie_split) > 1:
            movies[movie_split[1].strip()] = movie_split[0]

sites2_file = open("allResults2.txt", "rt")
diff_file = open("allResultsDiff.txt", "wt")
with sites2_file as f:
    lines = f.read().split('\n')
    for line in lines:
        movie_split = line.split('\t')
        if len(movie_split) > 1:
            if not movie_split[1].strip() in movies:
                print(line)
                diff_file.write(line)
                diff_file.write('\n')
diff_file.close()