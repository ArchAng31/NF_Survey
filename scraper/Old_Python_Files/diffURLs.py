import sys

oldList = {}
with open(sys.argv[1]) as f:
  for line in f:
    (title, url) = line.rsplit('\n')[0].split("\t")
    oldList[title] = url

with open(sys.argv[2]) as f:
  for line in f:
    result = line.rsplit('\n')[0].split("\t")
    if len(result) > 1:
      (title, newURL) = result
      if title in oldList:
        oldURL = oldList[title]
        if (oldURL != newURL):
          print(title + "\t" + oldURL + "\t" + newURL)