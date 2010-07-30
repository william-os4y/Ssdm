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
import os.path

import sys

#check the python version
if sys.version_info[0:2]<(2,6):
    print "SSDM requires python 2.6"
    sys.exit(1)


debug=False

def sqldata(value):
    if not value:
        return 'NULL'
    return '"%s"' % value

def db_exist(path):
    return os.path.isfile(path)
 
def connect(*args, **kw):
    if args:
        conn=sqlite3.connect(*args)
    else:
        conn=sqlite3.connect(**kw)
    conn.row_factory=Record
    return conn

class Model:
    "A class providing limited introspective access to sqlite"
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
    """
    This class is required because we add features to Cursor. 
    This is the only way I've found to pass info to the Record object
    """
    pass

        
class Record(object):
    """
    This is the representation of ONE record. It contains all fields of the record
    """

    def __init__(self, curobj, data, new=False):
        if new==False:
            self.__dict__["_row"]=sqlite3.Row(curobj,data)
            self.__dict__["_newdata"]={}
        else:
            rec={}
            for key,val,dummy in curobj.table_defaults:
                rec[key]=val
            self.__dict__["_newdata"]=rec
            self.__dict__["_row"]={}
        self.__dict__["_new"]=new
        self.__dict__["_curobj"]=curobj
        self.__dict__["_fields"]=[]
        self.__dict__["_pk"]=[]
        self.__dict__["_dflt"]={}
        self.__dict__["_modified"]=False
        if hasattr(curobj,'table_name'):
            self.__dict__["_tablename"]=curobj.table_name
        if hasattr(curobj,'table_defaults'):
            for key,dfltval,pk in curobj.table_defaults:
                self.__dict__["_fields"].append(key)
                self.__dict__["_dflt"][key]=dfltval
                if pk:
                    self.__dict__["_pk"].append(key)
        else:
            self.__dict__["_fields"]=self.__dict__["_row"].keys()

    def __getitem__(self, key):
        res=None
        if key in self._newdata.keys():
            res=self._newdata[key] 
        elif key in self._row.keys(): 
            res=self._row[key]
        if (hasattr(self._curobj, 'table_foreignkeys')) and (key in self._curobj.table_foreignkeys.keys()):
            table,fkey=self._curobj.table_foreignkeys[key]
            val=res
            res=table.get(**dict([(str(fkey),val)]))
        return res

    def __setitem__(self, key, val):
        if key not in self._fields: 
            raise ValueError, "Not a valid field"
        self.__dict__["_newdata"][key]=val
        self.__dict__["_modified"]=True

    def __getattr__(self, key):
        return self.__getitem__(key)

    def set(self, data):
        "change values of the current record"
        self.__dict__["_newdata"]=data
        self.__dict__["_modified"]=True

    def __setattr__(self, key, val):
        if debug: print "SET", key, val 
        if key[0]!="_":  #fields CANNOT start with the character "_"
            self.__setitem__(key,val)
    
    def __str__(self):
        res={}
        for key in self._fields:
            if key in self._newdata:
                res[key]=self._newdata[key]
            else:
                res[key]=self._row[key]
        return str(res)

    def __repr__(self):
        return "<%s at %s>" % (self.__class__.__name__, hex(id(self)))

    def save(self):
        "insert or update the current record. But does not commit it"
        if self._modified==False:
            print "nothing new"
            return
        if self._new:
            #INSERT INTO table_name VALUES (value1, value2, value3,...)
            vals=[]
            for key in self._fields:   #we must keep the right sequence
                if self._newdata.get(key, None):
                    vals.append(sqldata(self._newdata[key]))
                else:
                    vals.append(sqldata(self._dflt[key]))  
            sql="INSERT INTO %s VALUES (" % self._tablename
            sql+=",".join(vals)+")"
        else:
            #UPDATE table_name SET column1=value, column2=value2,... WHERE some_column=some_value
            set_clause=", ".join(['%s=%s' % (e[0],sqldata(e[1])) for e in self._newdata.items()])
            where_clause=" and ".join(['%s=%s' % (e,sqldata(self._row[str(e)])) for e in self._pk])
            sql="update %s set %s where %s" % (self._tablename, set_clause, where_clause)
        if debug: print "Insert/Update SQL", sql
        self._curobj.execute(sql)
        self.__dict__["_modified"]=False

    def delete(self):
        "delete the record, but does not commit this operation"
        #DELETE FROM table_name WHERE some_column=some_value
        where_clause=" and ".join(['%s="%s"' % (e,self._row[str(e)]) for e in self._pk])
        sql="delete from %s where %s" % (self._tablename, where_clause)
        if debug: print "Delete SQL", sql
        self._curobj.execute(sql)

    def keys(self):
        "return fields of the record"
        return self._fields

    def values(self):
        "Return the values of the current record object"
        res=[]
        if not self._newdata:
            return self._row
        for key in self._fields:
            if key in self._newdata:
                res.append(self._newdata[key])
            else:
                res.append(self._row[key])
        return res

    def rowdata(self):
        "Return the raw data of the record like present in the DB"
        return self._row
        
    
class RecordSet:
    """This is a list of Record"""

    def __init__(self):
        self.data=[]

    def order_by(self, name, ascendant=True):
        "Order the RecordSet"
        def mysort(a,b):
            if ascendant:
               return cmp(a[name], b[name])
            else:
               return -cmp(a[name],b[name])
        self.data.sort(mysort)

    def filter(self, where=None, limit_offset=None): 
        "Return a new RecordSet which is a subset of the current one"
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

    def append(self, record):
        self.data.append(record)

    def __len__(self):
        return len(self.data)

    def __str__(self):
        return "<%s: %s Rec at %s>" % (self.__class__.__name__, len(self.data), hex(id(self)))

    def __getitem__(self, item):
        return self.data[item]

class Table:
    """
    cursor is open and closed except for the get (because of potential update). 
    TODO: ??? why not opening the cursor at the object creation and close it at the object deletion ????
    """
    def __init__(self):
        self.defaults=self._get_defaults() # TODO: change to a property
        self.foreignkeys={}  
        self.maxrecords=10

    def get(self, **kw):
        "Return a unique record, None or raise an error in case of miltiple results"
        sql = self._select_query(table=self.__class__.__name__, pkey=kw)
        #res = RecordSet()
        cursor = self.execute(sql, kw)
        res = cursor.fetchmany(self.maxrecords) 
        if len(res)==1:
            cursor.close()
            return res[0]
        elif len(res)>1:
            raise ValueError, "Your query does not return only one record. We have %s records" % len(res)
        else:
            return None
    

    def getall(self):
        "Return all possible records of the current table"
        cursor = self.execute("select * from %s" % self.__class__.__name__)
        res=RecordSet()
        res.data=cursor.fetchall()
        cursor.close()
        return res

    def select(self, where=None, limit_offset=None):
        "Common select accepting a where clause (string) and a limit_offset clause (tuple)"
        sql = "select * from %s " % self.__class__.__name__
        if where:
            sql +=" where %s " % where
        if limit_offset:
            sql+=" limit %s offset %s " % limit_offset
        if debug: print "SQL", sql
        res = RecordSet()
        cursor = self.execute(sql)
        res.data = cursor.fetchmany(self.maxrecords) #TODO implement next in RecordSet
        cursor.close()
        return res
            

    def execute(self, template, data=None, commit=False):
        "Common execute width optional data (dict) and commit (boolean)"
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
        res = [(str(e['name']),e['dflt_value'],e['pk']) for e in data]
        cursor.close()
        return res

    def new(self):
        "Return an empty new Record. Do not forget to save it and commit it"
        cursor = self.conn.cursor(MyCursor)
        cursor.table_defaults=self.defaults
        cursor.table_foreignkeys=self.foreignkeys
        cursor.table_name=self.__class__.__name__
        r=Record(cursor, [], new=True)
        cursor.close()
        return r

    def commit(self):
        "Common commit"
        self.conn.commit()
    
    def rollback(self):
        "Common rollback"
        self.conn.rollback()

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
    model=Model(conn)
    tables=model.tables_and_views()
    for table in tables:
         tableclass=type(str(table), (Table,object), {'conn': conn})
         setattr(db,table,tableclass())
    for table in tables:
         tableobj=getattr(db, str(table))
         cur=conn.execute("pragma foreign_key_list(%s)" % table)
         res=cur.fetchall()
         tableobj.foreignkeys={}
         for elem in res:
             data=elem.rowdata()
             field=str(data[2])
             if field[0]=='"':
                 field=field[1:]
             if field[-1]=='"':
                 field=field[:-1]
             remoteobj=getattr(db, field)
             tableobj.foreignkeys[data[3]]=(remoteobj,data[4])
    return db

