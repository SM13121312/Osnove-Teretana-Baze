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
INSERT INTO korisnici(korisnicko_ime, lozinka, ime, prezime, uloga) VALUES('boza', 'boza1234', 'Boza', 'Paunovic', 'instruktor');
INSERT INTO korisnici(korisnicko_ime, lozinka, ime, prezime, uloga) VALUES('moma', 'moma1234', 'Moma', 'Paunovic', 'instruktor');
INSERT INTO korisnici(korisnicko_ime, lozinka, ime, prezime, uloga) VALUES('ljubomir', 'ljubomir1234', 'Ljuba', 'Misic', 'instruktor');


DROP TABLE IF EXISTS sale;
CREATE TABLE sale (
  sifra_sale int NOT NULL,
  naziv_sale varchar(10) DEFAULT NULL,
  broj_redova int DEFAULT NULL,
  oznaka_mesta varchar(10) DEFAULT NULL,
  PRIMARY KEY (sifra_sale)
);

INSERT INTO sale (sifra_sale, naziv_sale, broj_redova, oznaka_mesta)
VALUES
  (1, 'Sala 1', 5, 'ABCD'),
  (2, 'Sala 2', 3, 'ABC'),
  (3, 'Sala 3', 6, 'AB');

DROP TABLE IF EXISTS programi_treninga;
CREATE TABLE programi_treninga (
  naziv_programa varchar(30) PRIMARY KEY,
  vrsta_programa varchar(20),
  trajanje int,
  instruktor varchar(40),
  opis varchar(100),
  paket varchar(20)
);

INSERT INTO programi_treninga (naziv_programa, vrsta_programa, trajanje, instruktor, opis, paket)
VALUES
  ('Kardio', 'Hard-core', 60, 'Ljuba Misic', 'Skinite mast i loj, za sve narodne mase.', 'standard'),
  ('Push-pull', 'Medium', 60, 'Moma Paunovic', 'Vezbe na sipkama, za zene i muskarce.', 'premium'),
  ('Leg-day', 'Easy', 75, 'Boza Paunovic', 'Prenosite pakete sa lakocom.', 'standard');


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

INSERT INTO trening (sifra_treninga, sifra_sale, vreme_pocetka, vreme_kraja, dan, naziv_programa)
VALUES
  (1111, 1, '09:00:00', '10:30:00', 'ponedeljak|utorak|sreda', 'Kardio'),
  (2222, 1, '10:30:00', '11:30:00', 'utorak|sreda', 'Kardio'),
  (3333, 2, '12:30:00', '14:00:00', 'sreda', 'Leg-day'),
  (4444, 2, '14:20:00', '15:00:00', 'cetvrtak|petak', 'Leg-day'),
  (5555, 3, '15:30:00', '16:30:00', 'petak', 'Push-pull'),
  (6666, 3, '16:00:00', '17:30:00', 'subota', 'Push-pull');


DROP TABLE IF EXISTS termin;
CREATE TABLE termin (
  sifra_termina varchar(10) NOT NULL,
  datum date DEFAULT NULL,
  sifra_treninga int DEFAULT NULL,
  dan_termina VARCHAR(15),
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

