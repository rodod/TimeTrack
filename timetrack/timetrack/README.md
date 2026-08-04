# Gestione Orari Lavorativi

App web in Flask per la pianificazione e rendicontazione delle ore di lavoro,
pronta per l'export verso la busta paga.

## Funzionalità

- **Login sicuro** (password con hash, sessioni Flask-Login, protezione CSRF).
- **Due ruoli**: `admin` e `employee`, con permessi separati e verificati lato server.
- **Ogni dipendente** vede e modifica **solo le proprie** ore (isolamento dati garantito nelle query).
- **Pianificazione rolling**: il dipendente può inserire/modificare ore per una finestra di date configurabile (di default: da 7 giorni nel passato fino a 30 giorni nel futuro — vedi `config.py`).
- Ogni voce di orario è legata a **data + progetto + ore + note**.
- **Amministratore**: gestisce utenti, progetti, visualizza e filtra tutte le ore, le conferma (blocco modifiche) ed esporta in **Excel (.xlsx)** pronto per la busta paga.

## Struttura del progetto

```
timetrack/
  app.py              -> punto di ingresso, application factory, comando CLI
  config.py            -> configurazione (DB, chiave segreta, finestre di pianificazione)
  extensions.py         -> istanze condivise (db, login, csrf)
  models.py             -> modelli DB: User, Project, TimeEntry
  forms.py               -> form con validazione
  blueprints/
    auth.py              -> login/logout
    core.py               -> smistamento dashboard per ruolo
    employee.py            -> pianificazione ore del dipendente
    admin.py                -> gestione utenti/progetti/ore/export
  templates/               -> pagine HTML (Bootstrap 5)
  static/style.css
```

## Installazione locale

```bash
cd timetrack
python3 -m venv venv
source venv/bin/activate      # su Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Crea il primo amministratore:

```bash
flask --app app create-admin
```
(ti chiederà username, nome completo e password)

Avvia il server di sviluppo:

```bash
python app.py
```

Vai su `http://localhost:5000`, accedi come amministratore e crea:
1. i **progetti** (menu "Progetti")
2. gli **utenti dipendenti** (menu "Utenti")

I dipendenti potranno poi accedere autonomamente e inserire la propria pianificazione.

## Passaggio a un vero server web (produzione)

Per uso da remoto con più dipendenti, come indicato:

1. **Database**: passa da SQLite a Postgres (consigliato) impostando la variabile
   d'ambiente `DATABASE_URL`, es:
   ```
   DATABASE_URL=postgresql://utente:password@host:5432/nomedb
   ```
2. **Chiave segreta**: imposta `SECRET_KEY` con un valore lungo e casuale (non lasciare quella di default in `config.py`).
3. **HTTPS**: metti l'app dietro un reverse proxy con certificato SSL (es. Nginx + Let's Encrypt) — obbligatorio per non far viaggiare le password in chiaro.
4. **Server WSGI**: non usare `python app.py` in produzione, ma un server come Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```
5. Hosting tipici adatti: un VPS (Hetzner, DigitalOcean, Contabo...), oppure PaaS come Render/Railway/Fly.io con addon Postgres.

## Note sulla sicurezza già implementate

- Password mai salvate in chiaro (hash con `werkzeug.security`).
- Ogni dipendente può leggere/modificare solo le proprie voci (controllo `user_id` lato server, non solo lato interfaccia).
- Le pagine amministrative sono protette da un controllo esplicito del ruolo (`@admin_required`), non solo nascoste nel menu.
- Protezione CSRF su tutti i form.
- Le voci "confermate" dall'amministratore diventano bloccate: il dipendente non può più modificarle (utile una volta inviati i dati in busta paga).

## Personalizzazioni facili

- `PLANNING_HORIZON_DAYS` e `EDIT_GRACE_DAYS` in `config.py`: quanto avanti/indietro un dipendente può pianificare/modificare.
- Aggiungi campi (es. straordinari, reparto, commessa cliente) modificando `models.py` + `forms.py` + template corrispondenti.
