# 1. Usa un'immagine ufficiale di Python
FROM python:3.10-slim

# 2. Crea e imposta la cartella di lavoro dentro il container
WORKDIR /app

# 3. Copia il file delle dipendenze e installa i pacchetti
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copia tutto il resto del codice sorgente della tua app nel container
COPY . .

# 5. Espone la porta su cui lavora Flask
EXPOSE 5000

# 6. Comando per avviare il server Flask dentro il container
CMD ["flask", "run", "--host=0.0.0.0"]
