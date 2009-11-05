Simple Sqlite Data Mapper (Ssdm is short)
=========================================

Why a new data mapper ?
----------------------
After having looked at the different DataMapper available for Sqlite: SQLObject, .... I've got one main difficulties coming from the fact that my DB are already existing. More over they have been improve by a DBA by adding indexes, views, ...

Because using pure sql commands is a bit borring, I was looking for a simple data mapper. You know, the vey basic one who could match most of the sql needs. Finally, I've found it in the Activate code repository: http://code.activestate.com/recipes/473834/. This is a simple Sqlite Data Mapper developped by Andy Chambers. 

Finally months after months this small peace of code has grow and becomes a real application a would like to share with the OpenSource community.

Philosophy:
-----------
Ssdm must remains simple and very quick.

Performance
-----------
Tested with a simple wiki application served by Fapws3 and Mako (for the html templates), Ssdm has showed a performance of 1223 requests per seconds against 1634 requests per second for a pure sql script. 
This small wiki is available in the samples directoy of this application

The "performance cost" of Ssdm is thus very limitted and acceptable for my websites.

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
