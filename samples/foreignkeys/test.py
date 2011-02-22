# -*- coding: utf-8 -*-
 
from ssdm import ssdm
import sys
import os


dbfile="test.db"

try:
    os.stat(dbfile)
except OSError:
    print """ERROR!!!! \nApparently you have not yet created the "test.db" file. \nPlease check the README"""
    sys.exit(1)

con=ssdm.connect(dbfile)
db=ssdm.scan_db(con)
r=db.track.get({'trackid':11})
print "FOREIGN KEY"
print r.items()
print "r.trackid:",r.trackid
print "r.trackartist.artistname:", r.trackartist.artistname
print "r._rowid_:", r._rowid_

print "NEW TRACK"
n = db.track.new()
n.trackartist = 1
n.trackname = "All of me"
res = n.save() 
#db.commit()
print "save result", res
print n.items()

print "UPDATE TRACK"
u = db.track.get({'trackid':12})
print "u",type(u)
u.trackname = "Where are you"
res = u.save()
#db.commit()
print "save result", res
print u.items()
