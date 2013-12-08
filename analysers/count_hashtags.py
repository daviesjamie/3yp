import ast
import csv
import sys

if len(sys.argv) <= 1:
    print "You need to specify an input file."
    sys.exit(1)
    
infile = sys.argv[1]
hashTagCol = int(sys.argv[2]) if len(sys.argv) > 2 else 2
outfile = sys.argv[3] if len(sys.argv) > 3 else 'hashtag_counts'

inf = open(infile, "rb")
reader = csv.reader(inf, dialect='excel')

hashtags = {}

for row in reader:
    hashstring = row[hashTagCol]
    listblah = hashstring.split(' ')
    for bla in listblah:
        hashtag =  bla.replace("u'", '').replace('u"', '').replace('u[', '').translate(None, ' .,\'\"`[]').lower()
        if hashtag in hashtags:
            hashtags[hashtag] += 1
        else:
            hashtags[hashtag] = 1

inf.close()

outf = open(outfile, "w")

for hashtag in hashtags:
    outf.write('{0}\t{1}\n'.format(hashtags[hashtag], hashtag))

outf.flush()
outf.close()
