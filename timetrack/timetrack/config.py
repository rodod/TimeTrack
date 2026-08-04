import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Chiave segreta per sessioni/CSRF: in produzione impostala come variabile
    # d'ambiente SECRET_KEY, non lasciare quella di default.
    SECRET_KEY = os.environ.get("SECRET_KEY", "cambia-questa-chiave-in-produzione")

    # Di default usa SQLite (un file locale). Per un vero sito multi-utente
    # in produzione ti consiglio Postgres o MySQL: basta impostare la
    # variabile d'ambiente DATABASE_URL, es:
    # postgresql://utente:password@host:5432/nomedb
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(basedir, 'timetrack.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Sessione utente valida per 8 ore di inattività
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)

    # Quanti giorni in avanti un dipendente può pianificare (rolling window)
    PLANNING_HORIZON_DAYS = int(os.environ.get("PLANNING_HORIZON_DAYS", 30))

    # Quanti giorni indietro un dipendente può ancora modificare/inserire
    # ore (dopo di che solo l'admin può correggere, utile prima dell'invio
    # in busta paga)
    EDIT_GRACE_DAYS = int(os.environ.get("EDIT_GRACE_DAYS", 7))
