# models.py
# Modello dati (Flask-SQLAlchemy + SQLite) secondo il diagramma UML:
#
#   Studente 1 --- * Esito * --- 1 Appello * --- 1 CorsoDiStudio * --- 1 CorsoDiLaurea
#                                                     * --- * Docente
#
# Il database è il file esami.db nella cartella del progetto:
# si può aprire direttamente con DBeaver (connessione SQLite).
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# tabella di associazione molti-a-molti CorsoDiStudio <-> Docente
corso_docente = db.Table(
    "corso_docente",
    db.Column("id_corso", db.Integer, db.ForeignKey("corso_di_studio.id"), primary_key=True),
    db.Column("id_docente", db.Integer, db.ForeignKey("docente.id"), primary_key=True),
)


class CorsoDiLaurea(db.Model):
    __tablename__ = "corso_di_laurea"

    id = db.Column(db.Integer, primary_key=True)  # codice CDS di Esse3 (es. 819)
    nome = db.Column(db.String, nullable=False)
    is_magistrale = db.Column(db.Boolean, default=False, nullable=False)

    corsi = db.relationship("CorsoDiStudio", back_populates="corso_di_laurea")


class Docente(db.Model):
    __tablename__ = "docente"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, default="")
    cognome = db.Column(db.String, nullable=False)

    corsi = db.relationship("CorsoDiStudio", secondary=corso_docente, back_populates="docenti")


class CorsoDiStudio(db.Model):
    __tablename__ = "corso_di_studio"

    id = db.Column(db.Integer, primary_key=True)
    id_corso_di_laurea = db.Column(db.Integer, db.ForeignKey("corso_di_laurea.id"))
    codice = db.Column(db.String, unique=True, nullable=False)  # codice attività Esse3 (es. MA0682)
    nome = db.Column(db.String, nullable=False)
    anno = db.Column(db.Integer)  # anno accademico di inizio (2024 = A.A. 2024/2025)

    corso_di_laurea = db.relationship("CorsoDiLaurea", back_populates="corsi")
    docenti = db.relationship("Docente", secondary=corso_docente, back_populates="corsi")
    appelli = db.relationship("Appello", back_populates="corso", order_by="Appello.data")

    def get_appelli(self, anno=None):
        if anno is None:
            return list(self.appelli)
        return [a for a in self.appelli if a.data.year == anno]


class Appello(db.Model):
    __tablename__ = "appello"

    id = db.Column(db.Integer, primary_key=True)
    id_corso = db.Column(db.Integer, db.ForeignKey("corso_di_studio.id"), nullable=False)
    data = db.Column(db.Date, nullable=False)
    aula = db.Column(db.String)
    # campi in più rispetto al diagramma, mostrati nella dashboard
    tipo_prova = db.Column(db.String)
    totale_iscritti = db.Column(db.Integer)

    corso = db.relationship("CorsoDiStudio", back_populates="appelli")
    esiti = db.relationship("Esito", back_populates="appello", cascade="all, delete-orphan")

    __table_args__ = (db.UniqueConstraint("id_corso", "data"),)

    def get_iscritti(self):
        return [e.studente for e in self.esiti]

    @property
    def etichetta(self):
        # etichetta leggibile usata nei grafici, es. "MA0682_23092025"
        return f"{self.corso.codice}_{self.data:%d%m%Y}"


class Studente(db.Model):
    __tablename__ = "studente"

    matricola = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String)
    cognome = db.Column(db.String)

    # nel diagramma la relazione è 1-1, ma uno studente può ripresentarsi
    # a più appelli: serve 1-a-molti (usata anche dal grafico delle ripetizioni)
    esiti = db.relationship("Esito", back_populates="studente")


class Esito(db.Model):
    __tablename__ = "esito"

    id = db.Column(db.Integer, primary_key=True)
    id_studente = db.Column(db.Integer, db.ForeignKey("studente.matricola"), nullable=False)
    id_appello = db.Column(db.Integer, db.ForeignKey("appello.id"), nullable=False)
    voto = db.Column(db.Integer)  # 18-30, 31 = 30L, 0 = insufficiente, NULL se assente/ritirato
    stato = db.Column(db.String, nullable=False)  # promosso, bocciato, assente, ritirato
    # campi in più rispetto al diagramma, usati da alcuni grafici
    anno_freq = db.Column(db.String)
    cfu = db.Column(db.Integer)
    svolgimento = db.Column(db.String)  # P = presenza, D = distanza

    studente = db.relationship("Studente", back_populates="esiti")
    appello = db.relationship("Appello", back_populates="esiti")
