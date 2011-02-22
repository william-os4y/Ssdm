CREATE TABLE artist(
  artistid    text PRIMARY KEY,
  artistname  TEXT
);
INSERT INTO "artist" VALUES("dm",'Dean Martin');
INSERT INTO "artist" VALUES("fs",'Frank sinatra');
CREATE TABLE track(
  tracknum     INTEGER,
  diskid       INTEGER,
  trackname   TEXT,
  trackartist text,
  FOREIGN KEY(trackartist) REFERENCES artist(artistid),
  PRIMARY KEY (tracknum, diskid)
);
INSERT INTO "track" VALUES(1,1,'That''s Amore',"dm");
INSERT INTO "track" VALUES(1,2,'Christmas blues',"dm");
INSERT INTO "track" VALUES(1,3,'My way',"fs");

