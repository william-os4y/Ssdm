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
r=db.track.get({'rowid':1})
print "MULTI PRIMARY KEYs"
print r.items()
print "r.tracknum:",r.tracknum
print "r.trackartist.artistname:", r.trackartist.artistname
print "r.rowid:", r.rowid

print "NEW TRACK"
n = db.track.new()
n.trackartist = "fs"
n.trackname = "All of me"
n.tracknum = 4
n.diskid = 33
res = n.save() 
#db.commit()
print "save result", res
print n.items()

print "UPDATE TRACK"
u = db.track.get({'rowid':2})
u.trackname = "Where are you"
res = u.save()
#db.commit()
print "save result", res
print u.items()
