# -*- coding: utf-8 -*-
from mako.lookup import TemplateLookup
import fapws._evwsgi as evwsgi
from fapws import base
from ssdm import ssdm
import sys

dbpath='database.db'
ssdm.debug=False

print ssdm.debug

lookup = TemplateLookup(directories=['templates',], filesystem_checks=True, module_directory='./modules')
con=ssdm.connect(dbpath)
db=ssdm.scan_db(con)

evwsgi.start("0.0.0.0", "8080")
evwsgi.set_base_module(base)
   

def commit(param):
   con.commit()
   print "commit"
 
def disppage(environ, start_response):
    start_response('200 OK', [('Content-Type','text/html')])
    #print environ
    page=environ['PATH_INFO']
    rec=db.pages.get({'page':page})
    template=lookup.get_template('page.html')
    if rec:
        ndisp=rec.display+1
        rec.set({'display':ndisp})
        rec.save()
        #con.commit()
        evwsgi.defer(commit,None, True)
        return [template.render(**{"page":rec.page,"text":rec.text,"display":ndisp})]
    else:
        return["Page not found"]
def homepage(environ, start_response):
    count=db.pages.count()
    start_response('200 OK', [('Content-Type','text/plain')])
    return ["you should check /page/page<number> where number can be 1 to %s" % count]
 
evwsgi.wsgi_cb(("/page/", disppage))
evwsgi.wsgi_cb(("/", homepage))
evwsgi.set_debug(0)    
evwsgi.run()
  
con.close()
