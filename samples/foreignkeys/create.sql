-- taken from the sqlite website http://www.sqlite.org/foreignkeys.html
CREATE TABLE artist(
  artistid    INTEGER PRIMARY KEY,
  artistname  TEXT
);
INSERT INTO "artist" VALUES(1,'Dean Martin');
INSERT INTO "artist" VALUES(2,'Frank sinatra');
CREATE TABLE track(
  trackid     INTEGER,
  trackname   TEXT,
  trackartist INTEGER,
  FOREIGN KEY(trackartist) REFERENCES artist(artistid)
);
INSERT INTO "track" VALUES(11,'That''s Amore',1);
INSERT INTO "track" VALUES(12,'Christmas blues',1);
INSERT INTO "track" VALUES(13,'My way',2);

