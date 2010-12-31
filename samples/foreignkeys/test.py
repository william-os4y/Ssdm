# -*- coding: utf-8 -*-
 
from ssdm import ssdm
import sys
import os


dbfile="test.db"

try:
    os.stat(dbfile)
except OSError:
    print """ERROR!!!! \nSounds that you have not yet created the "test.db" file. \nPlease check the README"""
    sys.exit(1)

con=ssdm.connect(dbfile)
db=ssdm.scan_db(con)
r=db.track.get({'trackid':11})
print "trackid:",r.trackid
print "trackartist:", r.trackartist.artistname


