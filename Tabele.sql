PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS korisnici;
CREATE TABLE korisnici (
  korisnicko_ime varchar(30) PRIMARY KEY,
  lozinka varchar(20),
  ime varchar(20),
  prezime varchar(20),
  uloga varchar(20),
  status_korisnika varchar(20),
  paket varchar(20),
  datum date, 
  datum_aktivacije date,
  datum_isteka date
);

INSERT INTO korisnici(korisnicko_ime, lozinka, ime, prezime, uloga) VALUES ('admin', 'admin123', 'Lanmi', 'Miami', 'admin');


DROP TABLE IF EXISTS sale;
CREATE TABLE sale (
  sifra_sale int NOT NULL,
  naziv_sale varchar(10) DEFAULT NULL,
  broj_redova int DEFAULT NULL,
  oznaka_mesta varchar(10) DEFAULT NULL,
  PRIMARY KEY (sifra_sale)
);


DROP TABLE IF EXISTS programi_treninga;
CREATE TABLE programi_treninga (
  naziv_programa varchar(30) PRIMARY KEY,
  vrsta_programa varchar(20),
  trajanje int,
  instruktor varchar(40),
  opis varchar(100),
  paket varchar(20)
);


DROP TABLE IF EXISTS trening;
CREATE TABLE trening (
  sifra_treninga int PRIMARY KEY,
  sifra_sale int,
  vreme_pocetka time,
  vreme_kraja time,
  dan varchar(20),
  naziv_programa varchar(30),
  FOREIGN KEY (naziv_programa) REFERENCES programi_treninga (naziv_programa) ON DELETE SET NULL ON UPDATE CASCADE,
  FOREIGN KEY (sifra_sale) REFERENCES sale (sifra_sale) ON DELETE SET NULL
);


DROP TABLE IF EXISTS termin;
CREATE TABLE termin (
  sifra_termina varchar(10) NOT NULL,
  datum date DEFAULT NULL,
  sifra_treninga int DEFAULT NULL,
  PRIMARY KEY (sifra_termina),
  FOREIGN KEY (sifra_treninga) REFERENCES trening (sifra_treninga) ON DELETE SET NULL
);

DROP TABLE IF EXISTS rezervacije;
CREATE TABLE rezervacije (
  sifra_rezervacije int NOT NULL,
  korisnicko_ime varchar(30) DEFAULT NULL,
  sifra_termina varchar(10) DEFAULT NULL,
  oznaka_reda_i_mesta varchar(3) DEFAULT NULL,
  datum date DEFAULT NULL,
  PRIMARY KEY (sifra_rezervacije),
  FOREIGN KEY (korisnicko_ime) REFERENCES korisnici (korisnicko_ime) ON DELETE SET NULL,
  FOREIGN KEY (sifra_termina) REFERENCES termin (sifra_termina) ON DELETE SET NULL
);

