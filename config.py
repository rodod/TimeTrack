import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Chiave segreta per sessioni/CSRF: in produzione impostala come variabile
    # d'ambiente SECRET_KEY, non lasciare quella di default.
    SECRET_KEY = os.environ.get("SECRET_KEY", "cambia-questa-chiave-in-produzione")

    # Database: PostgreSQL. Configura la connessione tramite variabili
    # d'ambiente (consigliato, specie in produzione) oppure lascia i valori
    # di default pensati per lo sviluppo locale.
    #
    # Puoi impostare direttamente l'URL completo con DATABASE_URL, es:
    #   postgresql://utente:password@host:5432/nomedb
    # oppure impostare i singoli pezzi (PGUSER, PGPASSWORD, PGHOST, PGPORT, PGDATABASE)
    # e verrà composto automaticamente qui sotto.
    _pg_user = os.environ.get("PGUSER", "timetrack")
    _pg_password = os.environ.get("PGPASSWORD", "timetrack")
    _pg_host = os.environ.get("PGHOST", "localhost")
    _pg_port = os.environ.get("PGPORT", "5432")
    _pg_database = os.environ.get("PGDATABASE", "timetrack")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"postgresql+psycopg2://{_pg_user}:{_pg_password}@{_pg_host}:{_pg_port}/{_pg_database}",
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
