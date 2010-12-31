# -*- coding: utf-8 -*-


#    Copyright (C) 2009 William.os4y@gmail.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 2 of the License.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""
Inspired by Simple Object Relational Mapper proposed by Andy on http://code.activestate.com/recipes/473834/
"""


import sqlite3
debug=True

#Tanks to adapt this list if you have more sqlite functions in your default values.
sqlite3functions=['datetime','date','time', 'julianday', 'strftime']


#
# Sqlite converters methods
#
def convert_integer(val):
    try:
        return int(val)
    except:
        return 0
sqlite3.register_converter("integer", convert_integer)
#as reported in the issue 7921 of Django, the sqlite3 module is no more converting str itself. 
if sqlite3.version_info >= (2,4,1):
    sqlite3.register_adapter(str, lambda s:s.decode('utf-8'))


def sqldata(value):
    if not value:
        return 'NULL'
    return "'%s'" % value
 
def sqlite3row_to_dict(row):
    res={}
    for k in row.keys():
       res[k]=row[k]
    return res
 
def is_sqlite_function(data):
    #Sqlite function must be escaped from the default values. 
    #You can find them on sqlite website:http://www.sqlite.org/lang_datefunc.html
    if not data:
        return False
    for fct in sqlite3functions:
        if data[:len(fct)]==fct:
            return True
    return False
 
def connect(*args, **kw):
    if args:
        kwargs={'detect_types': sqlite3.PARSE_DECLTYPES}
        conn=sqlite3.connect(*args, **kwargs)
    else:
        kw.update({'detect_types': sqlite3.PARSE_DECLTYPES})
        conn=sqlite3.connect(**kw)
    conn.row_factory=Record
    return conn

class Model(object):
    '''A class providing limited introspective access to sqlite'''
    def __init__(self, connection):
        self.conn = connection

    def __getattr__(self, name):
        if unicode(name) in self.tables_and_views():
            DataSource = type(name, (Table,object), {'conn': self.conn})
            return DataSource
        else:
            raise AttributeError, 'Attribute %s not found' % name

    def tables_and_views(self):
        sql = """select name from main.sqlite_master where type="table" or type="view"  """
        cursor = self.conn.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        return [i["name"] for i in result]

class MyCursor(sqlite3.Cursor):
    #This class is required because we add features to Cursor. 
    #This is the only way I've found to pass info to the Record object
    pass



        
class Record(object):
    """
    This is the representation of ONE record. It contains all fields of the record
    _row contains the data coming from the DB, either default values, either record already existing
    _newdata contains the new data we will insert/update in the DB
    """
    def __init__(self, curobj, data, new=False):
        if new==False:
            self.__dict__["_row"]=sqlite3row_to_dict(sqlite3.Row(curobj,data))
            self.__dict__["_newdata"]={}
        else:
            rec={}
            for key,val,dummy in curobj.table_defaults:
                rec[key]=val
            self.__dict__["_newdata"]={}
            self.__dict__["_row"]=rec
        self.__dict__["_new"]=new
        self.__dict__["_curobj"]=curobj
        self.__dict__["_pk"]=[]
        self.__dict__["_dflt"]={}
        self.__dict__["_modified"]=False
        if hasattr(curobj,'table_name'):
            self.__dict__["_tablename"]=curobj.table_name
        if hasattr(curobj,'table_defaults'):
            for key,dfltval,pk in curobj.table_defaults:
                self.__dict__["_dflt"][key]=dfltval
                if pk:
                    self.__dict__["_pk"].append(key)
    def __getitem__(self, key):
        return self.get(key)
    def __setitem__(self, key, val):
        if key[0]=="_":  
            raise ValueError, "fields CANNOT start with the character _"
        if key not in self._row.keys(): 
            raise ValueError, "Not a valid field:%s" % key
        self.__dict__["_newdata"][key]=val
        self.__dict__["_modified"]=True
    def __getattr__(self, key):
        return self.get(key)
    def __setattr__(self, key, val):
            self.__setitem__(key,val)
    def __str__(self):
        res=[]
        for key in self._pk:
            if key in self._newdata:
                #res[key]=self._newdata[key]
                res.append(str(self._newdata[key]))
            else:
                #res[key]=self._row[key]
                res.append(str(self._row[key]))
        if res:
            return "-".join(res)
        else:
            return ""
    def __repr__(self):
        return "<%s of %s at %s>" % (self.__class__.__name__, self.__dict__["_tablename"], hex(id(self)))
    def __nonzero__(self):
        #nonzero means we have data, either from _newdata, either from the db
        if self._new and not self._newdata:
            return False
        return True

    def delete(self):
        #delete but not commit
        #DELETE FROM table_name WHERE some_column=some_value
        where_clause=" and ".join(['%s="%s"' % (e,self._row[str(e)]) for e in self._pk])
        sql="delete from %s where %s" % (self._tablename, where_clause)
        if debug: print "Delete SQL", sql
        self._curobj.execute(sql)
    def dictvalues(self):
        res={}
        for key in self.keys():
            res[key]=self.get(key)
        return res
    def get(self, key, default=None):  #default is present just to be complient with the dictionry.get method. 
        res=None
        if key in self._newdata.keys():
            res=self._newdata[key] 
        elif key in self._row.keys(): 
            res=self._row[key]
        else:
            raise ValueError, "Not a valid field:%s" % key   #we prefer to generate an error than to return a default value
        if (hasattr(self._curobj, 'table_foreignkeys')) and (key in self._curobj.table_foreignkeys.keys()):
            table,fkey=self._curobj.table_foreignkeys[key]
            val=res
            res=table.get({str(fkey):val})
        return res
    def has_key(self, key):
        return key in self.keys()
    def items(self):
        res=[]
        for key in self.keys():
            res.append((key,self.get(key)))
        return res
    def keys(self):
        return self._row.keys()
    def rowdata(self):
        return self._row
    def save(self):
        if self._modified==False:
            if debug: print "nothing new"
            return
        if self._new:
            #INSERT INTO table_name (field1, field2, ...) VALUES (value1, value2, value3,...)
            #the following construciton is to assure a perfect sequence between the key list and the value list.
            #does _newdata.keys() always match _newdata.values() ?
            vals=[]
            keys=[]
            for key,val in self._newdata.items():  
                keys.append(key)
                vals.append(val)
            sql="INSERT INTO %s (%s) VALUES (" % (self._tablename, ",".join(keys))
            #sql+=",".join(vals)+")"
            vals_elems="?,"*len(vals)
            sql+=vals_elems[:-1] #remove the last comma
            sql+=")"
            params_list=vals 
        else:
            #UPDATE table_name SET column1=value, column2=value2,... WHERE some_column=some_value
            #set_clause=", ".join(["%s=%s" % (e[0],sqldata(e[1])) for e in self._newdata.items()])
            set_clause_list=[]
            params_list=[]
            for  e in self._newdata.items():
                set_clause_list.append("%s=?" % e[0])
                params_list.append(e[1])
            set_clause=", ".join(set_clause_list)
            where_clause=" and ".join(["%s=%s" % (e,sqldata(self._row[str(e)])) for e in self._pk])
            sql=u"update %s set %s where %s" % (self._tablename, set_clause, where_clause)
        if debug: print "Insert/Update SQL:", sql, params_list
        self._curobj.execute(sql, params_list)
        #we cleanup the records
        self.__dict__["_modified"]=False
        self.__dict__["_new"]=False
        #TODO: we update _row with what we know. But what about default values ???? and autoincrement value ????
        
        for key, val in self._newdata.items():
            self.__dict__["_row"][key]=val
        self.__dict__["_newdata"]={}
    def set(self, data):
        self.__dict__["_newdata"]=data
        self.__dict__["_modified"]=True
    def values(self):
        res=[]
        for key,val in self.items():
            res.append(val)
        return res
        
    
class RecordSet(object):
    """This is a list of Record"""
    def __init__(self):
        self.data=[]
    def __len__(self):
        return len(self.data)
    def __str__(self):
        return "<%s: %s Rec at %s>" % (self.__class__.__name__, len(self.data), hex(id(self)))
    def __getitem__(self, item):
        return self.data[item]

    def append(self, record):
        self.data.append(record)
    def filter(self, where=None, limit_offset=None): 
        res=RecordSet()
        limit=None
        offset=0
        if limit_offset:
            limit, offset=limit_offset
        for rec in self.data:
            if limit!=None and limit<=0:
                break
            if eval(where,dict(rec.rowdata())):
                if offset>0:
                    offset-=1
                else:
                    res.append(rec)
                    if limit:
                        limit-=1               
        return res
    def order_by(self, name, ascendant=True):
        def mysort(a,b):
            if ascendant:
               return cmp(a[name], b[name])
            else:
               return -cmp(a[name],b[name])
        self.data.sort(mysort)

class Table(object):
    """
    cursor is open and closed except for the get (because of potential update). 
    TODO: ??? why not opening the cursor at the object creation and close it at the object deletion ????
    """
    def __init__(self):
        self.defaults=self._get_defaults() # TODO: change to a property
        self.foreignkeys={}  
        self.maxrecords=100

    def get(self, criteria, quiet=False, only_first_record=True):
        "select records based on their primary keys (as dict) and return a recordset"
        #TODO: get is always against pk. Thus return only one record. In all other case, use select instead
        sql = self._select_query(table=self.__class__.__name__, pkey=criteria)
        res = RecordSet()
        cursor = self._execute(sql, criteria)
        res.data = cursor.fetchmany(self.maxrecords)             
        cursor.close()
        if not quiet and len(res)>1:
            print "You request a record from %s, but you got %s!!. Better to use select instead" % (self.__class__.__name__, len(res))
        if only_first_record and len(res)>0:
            res=res[0]
        return res
    
    def count(self, where = None):
        sql = "select count(*) as count from %s " % self.__class__.__name__
        if where:
            sql +=" where %s " % where
        if debug: print "SQL", sql
        res = RecordSet()
        cursor = self._execute(sql)
        res.data = cursor.fetchall()
        cursor.close()
        return res[0]['count']
    
    def getall(self):
        "return all records in a record set"
        #TODO: to rename into all()
        cursor = self._execute("select * from %s" % self.__class__.__name__)
        res=RecordSet()
        res.data=cursor.fetchall()
        cursor.close()
        return res

    def select(self, where=None, order=None, limit_offset=None, clause=None):
        "select some records and return them in a record set"
        if clause:
            sql = "select %s from %s " % (clause, self.__class__.__name__)
        else:
            sql = "select * from %s " % self.__class__.__name__
        if where:
            sql +=" where %s " % where
        if order:
            sql+=" order by %s " % order
        if limit_offset:
            sql+=" limit %s offset %s " % limit_offset
        if debug: print "SQL", sql
        res = RecordSet()
        cursor = self._execute(sql)
        res.data = cursor.fetchmany(self.maxrecords) #TODO implement next in RecordSet
        cursor.close()
        return res
            

    def _execute(self, template, data=None, commit=False):
        cursor = self.conn.cursor(MyCursor)
        cursor.table_defaults=self.defaults
        cursor.table_foreignkeys=self.foreignkeys
        cursor.table_name=self.__class__.__name__
        if data:
            cursor.execute(template, data) #execute stmt returns None
        else:
            cursor.execute(template) #execute stmt returns None
        if commit:
            self.commit()
        return cursor

    def _select_query(self, table=None, pkey=None):
        template = ''' select * from %s ''' % table
        values=[]
        if pkey:
            template += ''' where''' 
            crit=[]
            for key, val in pkey.iteritems():
                crit.append(''' %s=:%s ''' % (key, key))
            template += " and ".join(crit)
        return template

    def _get_defaults(self):
        tablename=self.__class__.__name__
        cursor=self.conn.cursor() # we use the generic cursor
        cursor.execute("""pragma table_info("%s") """  % tablename) #field name: 'cid', 'name', 'type', 'notnull', 'dflt_value', 'pk'
        data=cursor.fetchall()
        #res = [(str(e['name']),e['dflt_value'],e['pk']) for e in data]
        res=[]
        for rec in data:
            if not is_sqlite_function(rec['dflt_value']):
                res.append((rec['name'], rec['dflt_value'], rec['pk']))
            else:
                res.append((rec['name'], None, rec['pk']))
        cursor.close()
        return res

    def new(self, data={}):
        cursor = self.conn.cursor(MyCursor)
        cursor.table_defaults=self.defaults
        cursor.table_foreignkeys=self.foreignkeys
        cursor.table_name=self.__class__.__name__
        r=Record(cursor, [], new=True)
        if data:
            r.set(data)
        cursor.close()
        return r

    def commit(self):
        self.conn.commit()
    # TODO: add rollback

    def __str__(self):
        return "<%s object at %s>" % (self.__class__.__name__,hex(id(self)))
    def __repr__(self):
        return "<%s object at %s>" % (self.__class__.__name__,hex(id(self)))
    def __len__(self):
        cursor=self.conn.cursor() # we use the generic cursor
        cursor.execute("""select count(*) from "%s" """  % self.__class__.__name__)
        data=cursor.fetchone()
        cursor.close()
        return data.items()[0]
    def len(self):
        return self.__len__()
    
        
#
#pragma foreign_key_list(<tablename>)
#id|seq|table|from|to|on_update|on_delete|match 
def scan_db(conn):
    """transform the DB into corresponding objects"""
    db=type('DB',(object,),{})()
    setattr(db,'commit',conn.commit)
    model=Model(conn)
    tables=model.tables_and_views()
    for table in tables:
         tableclass=type(str(table), (Table,object), {'conn': conn})
         setattr(db,table,tableclass())
    for table in tables:
         tableobj=getattr(db, str(table))
         cur=conn.execute("pragma foreign_key_list(%s)" % table)
         #['id', 'seq', 'table', 'from', 'to', 'on_update', 'on_delete', 'match']
         res=cur.fetchall()
         tableobj.foreignkeys={}
         for elem in res:
             data=elem.rowdata()
             field=str(data['table'])
             if field[0]=='"':
                 field=field[1:]
             if field[-1]=='"':
                 field=field[:-1]
             remoteobj=getattr(db, field)
             tableobj.foreignkeys[data['from']]=(remoteobj,data['to'])
    return db

