#!./bin/daemonpy

import sys, subprocess
import feedparser

if len(sys.argv) == 3:
    input_rss = sys.argv[1]
    output_iso = sys.argv[2]
else:
    print 'too many or too few arguments in makeDvdIso command'
    sys.exit(1)

try:
    rss = feedparser.parse(input_rss)
except:
    print 'cannot open rss feed url'

cmd = [u'./bin/todisc', u'-menu-fontsize', u'36', u'-title-color', u'\'#ff7700\'', u'-stroke-color', u'black']

dvd_title = unicode(rss.feed.title)
cmd += [u'-menu-title'] 
cmd += dvd_title

files = []
titles = []
for entry in rss.entries:
    files.append(entry.link)
    titles.append(entry.title)

cmd += [u'-files'] + files
cmd += [u'-titles'] + titles
cmd += [u'-out']
cmd += unicode(output_iso)

try:
    subprocess.call(cmd)
except:
    print 'problem when calling tovid command'

    




