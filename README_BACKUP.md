# Sistema di Backup Incrementale in Python

Sistema di backup incrementale che copia file da una cartella origine a una destinazione, tenendo traccia dei cambiamenti tramite un file JSON.

## Caratteristiche

- **Backup completo**: Prima copia completa di tutti i file
- **Backup incrementale**: Copie successive copiano solo file nuovi o modificati
- **Tracciamento con hash MD5**: Identifica modifiche tramite hash del contenuto
- **File JSON di metadati**: Memorizza lo stato dei file per confronti futuri
- **Preserva struttura directory**: Ricrea la struttura completa di cartelle e sottocartelle
- **Preserva timestamp**: Mantiene date di modifica originali

## Come funziona

Il programma crea un file `backup_metadata.json` nella home directory che contiene:
- Hash MD5 di ogni file
- Dimensione
- Data di modifica
- Percorso relativo

Quando esegui un backup incrementale, il programma:
1. Scansiona la cartella origine
2. Confronta con i metadati dell'ultimo backup
3. Copia SOLO i file nuovi o modificati

## Uso

### Sintassi base

```bash
python incremental_backup.py <cartella_origine> <cartella_destinazione> [--full]
```

### Opzioni

- `--full`: Esegue un backup completo (sovrascrive tutto)

## Esempio dello scenario richiesto

### Scenario: Backup incrementale A → B → C

```bash
# 1. Prima copia: A → B (backup completo)
python incremental_backup.py ./cartella_A ./cartella_B

# 2. Modifica alcuni file in cartella_A
# (ad esempio, modifica file1.txt, aggiungi file4.txt, ecc.)

# 3. Seconda copia: A → C (backup incrementale - solo file modificati/nuovi)
python incremental_backup.py ./cartella_A ./cartella_C

# Risultato:
# - cartella_B contiene lo snapshot completo di A al momento della prima copia
# - cartella_C contiene SOLO i file modificati o aggiunti dopo la prima copia
# - Unendo B + C (con C che sovrascrive), si ottiene lo stato attuale di A
```

### Esempio pratico completo

```bash
# Crea cartelle di test
mkdir -p test_A test_B test_C

# Crea alcuni file in test_A
echo "Contenuto originale 1" > test_A/file1.txt
echo "Contenuto originale 2" > test_A/file2.txt
mkdir test_A/subfolder
echo "Contenuto originale 3" > test_A/subfolder/file3.txt

# PRIMA COPIA: test_A → test_B
python incremental_backup.py test_A test_B

# Modifica alcuni file in test_A
echo "Contenuto MODIFICATO 1" > test_A/file1.txt
echo "Nuovo file 4" > test_A/file4.txt

# SECONDA COPIA: test_A → test_C (incrementale)
python incremental_backup.py test_A test_C

# Verifica risultati:
# test_B contiene: file1.txt (vecchio), file2.txt, subfolder/file3.txt
# test_C contiene: file1.txt (nuovo), file4.txt
# Unendo B e C si ottiene lo stato completo di A
```

## Output del programma

Il programma mostra informazioni dettagliate:

```
======================================================================
BACKUP INCREMENTALE
======================================================================
Origine:      /path/to/source
Destinazione: /path/to/destination
Modalità:     Incrementale
======================================================================

Scansione della cartella: /path/to/source
  Scansionato: file1.txt
  Scansionato: file2.txt
  ...

======================================================================
ANALISI INCREMENTALE
======================================================================
File totali nella origine:  10
File nell'ultimo backup:    8
File nuovi:                 2
File modificati:            3
File eliminati:             0
File da copiare:            5
======================================================================

File nuovi:
  + nuovo_file.txt
  + altro_file.txt

File modificati:
  M file_modificato1.txt
  M file_modificato2.txt
  M file_modificato3.txt

======================================================================
COPIA IN CORSO
======================================================================
  Copiato: nuovo_file.txt
  Copiato: altro_file.txt
  Copiato: file_modificato1.txt
  ...

5 file copiati con successo!

Metadati salvati in: /home/user/backup_metadata.json

======================================================================
BACKUP COMPLETATO
======================================================================
```

## File dei metadati

Il file `backup_metadata.json` (salvato nella home directory) ha questa struttura:

```json
{
  "last_backup": "2025-10-23T10:30:00.123456",
  "source": "/path/to/source",
  "destination": "/path/to/destination",
  "backup_type": "incremental",
  "files": {
    "file1.txt": {
      "hash": "5d41402abc4b2a76b9719d911017c592",
      "size": 1024,
      "mtime": 1729675800.123,
      "mtime_readable": "2025-10-23T10:30:00.123456"
    },
    ...
  }
}
```

## Note importanti

1. **File eliminati**: Il programma NON elimina file dalla destinazione se sono stati rimossi dall'origine. Questo è intenzionale per il caso d'uso di backup incrementale.

2. **Metadati globali**: Il file JSON è unico e condiviso. Ogni backup aggiorna i metadati, quindi l'ultimo backup eseguito determina il confronto per il successivo.

3. **Backup completo**: Usa `--full` se vuoi resettare e fare un backup completo:
   ```bash
   python incremental_backup.py ./source ./destination --full
   ```

4. **Performance**: Per file molto grandi, il calcolo dell'hash può richiedere tempo. Il programma legge i file a blocchi di 4KB per gestire file di grandi dimensioni.

## Caso d'uso: Ricostruzione completa

Per ricostruire lo stato completo di A da backup incrementali:

```bash
# Copia B (backup completo) in una nuova cartella
cp -r cartella_B cartella_completa

# Sovrascrivi con C (backup incrementale)
cp -rf cartella_C/* cartella_completa/

# cartella_completa ora contiene lo stato completo di A
```

## Requisiti

- Python 3.6 o superiore
- Moduli standard: os, sys, json, hashlib, shutil, pathlib, datetime, typing

Nessuna dipendenza esterna richiesta!
