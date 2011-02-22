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
r=db.artist.get({'artistid':2})
print "AUTOINCREMENT"
print r.items()

print "NEW TRACK"
n = db.artist.new()
n.artistname = "Elvis Presley"
res = n.save() 
#db.commit()
print "save result", res
print n.items()

print "RETRIEVE IT BACK"
r=db.artist.get({'rowid':res})
print r.items()


print "UPDATE TRACK"
u = db.artist .get({'rowid':2})
u.artistname = "Jimmy Page"
res = u.save()
#db.commit()
print "save result", res
print u.items()
