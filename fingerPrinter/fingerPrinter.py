###   REQUIRED    ###
from math import ceil
from struct import *
#####################

### createFingerprint ###
# INPUT: an mp4 header (for a single bitrate of a video)
# RETURNS: a string that represents the fingerprint of the Netflix video
#          (again, this is a fingerprint for a single bitrate of a video)
def createFingerprint(mp4header):
  ## locate the start of the sidx box
  sidxLoc = 0
  for x in range(0, len(mp4header)-3):
    sidxFinder = unpack('4s', mp4header[x:x+4])[0]
    if (sidxFinder == "sidx"):
      sidxLoc = x
      break
  if (sidxLoc == 0):
    return "" # error... sidx wasn't found

  ## determine the number of segments
  refCountLoc = sidxLoc + 34
  refCount = unpack('>H', mp4header[refCountLoc:refCountLoc+2])[0]

  ## initialize an array full of 0's
  segmentSizes = [0] * int(ceil(refCount/2.0))
  
  ## the mp4 header lists every 2 seconds of video, but Netflix
  ##   requests are for 4-second chunks, so this loop adds the
  ##   the 2-second segments in pairs
  segmentSizeLoc = refCountLoc + 2
  for x in range(refCount):
    segmentSizes[x/2] += unpack('>I', mp4header[segmentSizeLoc:segmentSizeLoc+4])[0]
    segmentSizeLoc += 12

  ## calculate the average bitrate
  averageBitrate = (sum(segmentSizes)*8)/(refCount*2) / 1000
  if (averageBitrate < 100):
    return "" # bitrate too low... probably one of the audio tracks

  ## build the final fingerprint
  fingerprint = str(averageBitrate) + "\t"
  for x in range(len(segmentSizes)-1):
    fingerprint += str(segmentSizes[x]) + ","
  fingerprint += str(segmentSizes[-1:][0])

  return fingerprint

### DEMONSTRATION OF FUNCTION ###
for x in range(1,3):
  file = open("home/audio" + str(x) + ".mp4", 'rb')
  data = file.read()
  file.close()
  print createFingerprint(data)

for x in range(1,10):
  file = open("home/video" + str(x) + ".mp4", 'rb')
  data = file.read()
  file.close()
  print createFingerprint(data)
