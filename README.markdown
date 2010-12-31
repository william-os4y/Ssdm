Simple Sqlite Data Mapper (Ssdm in short)
=========================================

Why a new data mapper ?
----------------------
After having looked at the different DataMapper available for Sqlite: SQLObject, .... I've got one main difficulties coming from the fact that my DB are already existing. More over they have been improve by a DBA by adding indexes, views, ...

Because using pure sql commands is a bit annoying, I was looking for a simple data mapper. You know, the very basic one which could match most of the sql needs. Finally, I've found it in the ActiveState code repository: http://code.activestate.com/recipes/473834/. This is a simple Sqlite Data Mapper developped by Andy Chambers. 

Finally months after months this small peace of code has grow and becomes a real application I would like to share with the OpenSource community.

Philosophy:
-----------
Ssdm must remain simple and very quick. Ssdm must facilate the DB usage, but t's possible that some specific SQL commands will be required.  

samples:
--------
For 2 tables with a foreignkey like this:
CREATE TABLE artist(
  artistid    INTEGER PRIMARY KEY,
  artistname  TEXT
);
CREATE TABLE track(
  trackid     INTEGER,
  trackname   TEXT,
  trackartist INTEGER,
  FOREIGN KEY(trackartist) REFERENCES artist(artistid)
);


You can easily access the data with the following commands:
>>> t=db.track.get({'trackid':11})
>>> print t.trackid
11
>>> print t.trackartist.artistname
u'Dean Martin'
>>> a=db.artist.getall()
>>> [e.artistname for e in a]
[u'Dean Martin', u'Frank sinatra']
>>> newa=db.artist.new()
>>> newa.artistid=3
>>> newa.artistname="Beethoven"
>>> newa.save()
>>> con.commit()
>>> a=db.artist.getall()
>>> [e.artistname for e in a]
[u'Dean Martin', u'Frank sinatra', u'Beethoven']

please check the samples to better understand

Performance
-----------
Tested with a simple wiki application served by Fapws3 and Mako (for the html templates), Ssdm has showed the following performance results:

* read and write: 281 requests per seconds for Ssdm; 359 requests per second for a pure sql script. 
* read only: 1226 requests per second for Ssdm; 1643 requests per second for a pure sql script.

This small wiki is available in the samples directory of this application.

The "performance cost" of Ssdm is thus limitted and acceptable for my websites.

How to install Ssdm:
---------------------
Please read the INSTALL document provided. 

How to use Ssdm ?
----------------
under construction.
Currently you have to look at the samples.

License
-------

    Copyright (C) 2009 William.os4y@gmail.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, version 2 of the License.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.



Have fun with Ssdm. 

William
