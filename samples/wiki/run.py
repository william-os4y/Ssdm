# -*- coding: utf-8 -*-
from mako.lookup import TemplateLookup
import fapws._evwsgi as evwsgi
from fapws import base
import ssdm
import sys

dbpath='database.db'
ssdm.debug=False

if not ssdm.db_exist(dbpath):
    print "Please first create the DB!!!!"
    print "We don't find the db called:%s" % dbpath
    sys.exit(1)
lookup = TemplateLookup(directories=['templates',], filesystem_checks=True, module_directory='./modules')
con=ssdm.connect(dbpath)
db=ssdm.scan_db(con)

evwsgi.start("0.0.0.0", 8080)
evwsgi.set_base_module(base)
    
def disppage(environ, start_response):
    start_response('200 OK', [('Content-Type','text/html')])
    #print environ
    page=environ['PATH_INFO']
    rec=db.pages.get(page=page)
    template=lookup.get_template('page.html')
    if rec:
        ndisp=rec.display+1
        rec.set({'display':ndisp})
        rec.save()
        #db.pages.commit()
        return [template.render(**{"page":rec.page,"text":rec.text,"display":ndisp})]
    else:
        return["Page not found"]

evwsgi.wsgi_cb(("/page/", disppage))
evwsgi.set_debug(0)    
evwsgi.run()
  
con.close()
