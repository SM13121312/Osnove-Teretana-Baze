PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS korisnici;
CREATE TABLE korisnici (
  korisnicko_ime varchar(30) PRIMARY KEY,
  lozinka varchar(20),
  ime varchar(20),
  prezime varchar(20),
  uloga varchar(20),
  status varchar(20),
  paket varchar(20),
  datum date, 
  datum_aktivacije date,
  datum_isteka date
);
