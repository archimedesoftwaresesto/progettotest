#!/bin/bash
# Script di test per dimostrare il backup incrementale

echo "=========================================="
echo "DEMO: Sistema di Backup Incrementale"
echo "=========================================="
echo ""

# Pulisci eventuali test precedenti
echo "1. Pulizia cartelle di test precedenti..."
rm -rf test_A test_B test_C test_D ~/backup_metadata.json
echo "   Fatto!"
echo ""

# Crea la cartella origine con alcuni file
echo "2. Creazione cartella origine (test_A) con file iniziali..."
mkdir -p test_A/subfolder1/subfolder2
echo "Contenuto del file 1" > test_A/file1.txt
echo "Contenuto del file 2" > test_A/file2.txt
echo "Contenuto del file 3" > test_A/subfolder1/file3.txt
echo "Contenuto del file 4" > test_A/subfolder1/subfolder2/file4.txt
echo "   Creati 4 file in test_A"
echo ""

# Prima copia: A → B (backup completo)
echo "3. PRIMA COPIA: test_A → test_B (backup completo)"
echo "   ------------------------------------------------"
python3 incremental_backup.py test_A test_B
echo ""

# Pausa
echo "Premi INVIO per continuare con le modifiche..."
read

# Modifica alcuni file in A
echo "4. Modifica di alcuni file in test_A..."
echo "Contenuto MODIFICATO del file 1" > test_A/file1.txt
echo "Nuovo file 5" > test_A/file5.txt
echo "Nuovo file 6" > test_A/subfolder1/file6.txt
echo "   - Modificato: file1.txt"
echo "   - Aggiunti: file5.txt, subfolder1/file6.txt"
echo ""

# Pausa
echo "Premi INVIO per eseguire il backup incrementale..."
read

# Seconda copia: A → C (backup incrementale)
echo "5. SECONDA COPIA: test_A → test_C (backup incrementale)"
echo "   ------------------------------------------------"
python3 incremental_backup.py test_A test_C
echo ""

# Mostra il contenuto delle cartelle
echo "6. CONFRONTO DEL CONTENUTO:"
echo "   ------------------------------------------------"
echo ""
echo "   Contenuto di test_B (backup completo iniziale):"
find test_B -type f | sed 's|^test_B/|      |' | sort
echo ""
echo "   Contenuto di test_C (solo file modificati/nuovi):"
find test_C -type f | sed 's|^test_C/|      |' | sort
echo ""

# Verifica unione
echo "7. VERIFICA: Unione di B + C"
echo "   ------------------------------------------------"
mkdir -p test_D
cp -r test_B/* test_D/
cp -rf test_C/* test_D/
echo "   Contenuto di test_D (B + C uniti):"
find test_D -type f | sed 's|^test_D/|      |' | sort
echo ""
echo "   Contenuto di test_A (originale):"
find test_A -type f | sed 's|^test_A/|      |' | sort
echo ""

# Verifica hash dei file
echo "8. VERIFICA HASH (test_A vs test_D):"
echo "   ------------------------------------------------"
cd test_A
find . -type f | while read f; do
    hash_a=$(md5sum "$f" | cut -d' ' -f1)
    hash_d=$(md5sum "../test_D/$f" 2>/dev/null | cut -d' ' -f1)
    if [ "$hash_a" = "$hash_d" ]; then
        echo "   ✓ $f: IDENTICO"
    else
        echo "   ✗ $f: DIFFERENTE"
    fi
done
cd ..
echo ""

echo "=========================================="
echo "DEMO COMPLETATA!"
echo "=========================================="
echo ""
echo "Riepilogo:"
echo "  - test_A: Cartella originale"
echo "  - test_B: Backup completo iniziale"
echo "  - test_C: Backup incrementale (solo modifiche)"
echo "  - test_D: Unione di B + C (ricostruzione completa)"
echo ""
echo "Il file ~/backup_metadata.json contiene i metadati dell'ultimo backup"
echo ""
