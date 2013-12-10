import scipy
import ast
import csv
import sys
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

if len(sys.argv) <= 2:
    print "You need to specify an input file and a hashtag to map."
    sys.exit(1)
    
infile = sys.argv[1]
hashTagSearch  = sys.argv[2]
hashTagCol = int(sys.argv[3]) if len(sys.argv) > 3 else 2
timeCol = int(sys.argv[4]) if len(sys.argv) > 4 else 1
outfile = sys.argv[5] if len(sys.argv) > 5 else hashTagSearch + "_times.csv"

inf = open(infile, "rb")
reader = csv.reader(inf, dialect='excel')

times = {}
rowcount = 0

for row in reader:
    rowcount += 1
    if rowcount == 1:
        continue

    actualTime = datetime.strptime(row[timeCol], "%a %b %d %H:%M:%S +0000 %Y")
    roundedTime = actualTime - timedelta(hours=actualTime.hour % 6, minutes=actualTime.minute, seconds=actualTime.second)

    if roundedTime not in times:
        times[roundedTime] = 0

    hashstring = row[hashTagCol]
    listblah = hashstring.split(' ')
    for bla in listblah:
        hashtag =  bla.replace("u'", '').replace('u"', '').replace('u[', '').translate(None, ' .,\'\"`[]').lower()
        if hashtag == hashTagSearch:
            times[roundedTime] += 1

inf.close()

fig, ax = plt.subplots(1)
ax.plot(sorted(times.keys()), [times[x] for x in sorted(times.keys())])
fig.autofmt_xdate()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b %H:%M'))
d = scipy.zeros(len(times))
ax.grid(True)
plt.xlabel('Time')
plt.ylabel('Number of Occurrences')
plt.title('#' + hashTagSearch)
plt.show()

#outf = open(outfile, "w")

#for time in times:
    #outf.write('{0}\t{1}\n'.format(time, times[time]))
    #print '{0}\t{1}\n'.format(time, times[time])

#outf.flush()
#outf.close()
