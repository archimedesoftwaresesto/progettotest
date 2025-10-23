#!/usr/bin/env python3
"""
Sistema di Backup Incrementale
Copia file da una cartella origine a una destinazione, tenendo traccia
dei cambiamenti tramite un file JSON per copie incrementali successive.
"""

import os
import sys
import json
import hashlib
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Set, Tuple


class IncrementalBackup:
    """Gestisce il backup incrementale di una directory"""

    def __init__(self, metadata_file: str = "backup_metadata.json"):
        """
        Inizializza il sistema di backup

        Args:
            metadata_file: Nome del file JSON per i metadati (salvato nella home o cartella corrente)
        """
        self.metadata_file = Path.home() / metadata_file
        self.metadata = self._load_metadata()

    def _calculate_file_hash(self, filepath: Path) -> str:
        """
        Calcola l'hash MD5 di un file

        Args:
            filepath: Percorso del file

        Returns:
            Hash MD5 del file come stringa esadecimale
        """
        hash_md5 = hashlib.md5()
        try:
            with open(filepath, "rb") as f:
                # Leggi il file a blocchi per gestire file grandi
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except (IOError, OSError) as e:
            print(f"Errore durante il calcolo hash di {filepath}: {e}")
            return ""

    def _scan_directory(self, source_path: Path) -> Dict[str, dict]:
        """
        Scansiona una directory e raccoglie informazioni su tutti i file

        Args:
            source_path: Percorso della directory da scansionare

        Returns:
            Dizionario con path relativo come chiave e metadati come valore
        """
        files_info = {}

        if not source_path.exists():
            print(f"Errore: la cartella {source_path} non esiste")
            return files_info

        print(f"\nScansione della cartella: {source_path}")

        for root, dirs, files in os.walk(source_path):
            for filename in files:
                filepath = Path(root) / filename
                relative_path = filepath.relative_to(source_path)

                try:
                    stat = filepath.stat()
                    file_hash = self._calculate_file_hash(filepath)

                    files_info[str(relative_path)] = {
                        "hash": file_hash,
                        "size": stat.st_size,
                        "mtime": stat.st_mtime,
                        "mtime_readable": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    }

                    print(f"  Scansionato: {relative_path}")

                except (IOError, OSError) as e:
                    print(f"Errore durante la scansione di {filepath}: {e}")

        return files_info

    def _load_metadata(self) -> Dict:
        """
        Carica i metadati dal file JSON

        Returns:
            Dizionario con i metadati o dizionario vuoto se il file non esiste
        """
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (IOError, json.JSONDecodeError) as e:
                print(f"Errore durante il caricamento dei metadati: {e}")
                return {}
        return {}

    def _save_metadata(self):
        """Salva i metadati nel file JSON"""
        try:
            with open(self.metadata_file, "w", encoding="utf-8") as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)
            print(f"\nMetadati salvati in: {self.metadata_file}")
        except IOError as e:
            print(f"Errore durante il salvataggio dei metadati: {e}")

    def _compare_files(self, current_files: Dict[str, dict]) -> Tuple[Set[str], Set[str], Set[str]]:
        """
        Confronta i file attuali con quelli dell'ultimo backup

        Args:
            current_files: Dizionario dei file attuali

        Returns:
            Tupla di (file nuovi, file modificati, file eliminati)
        """
        previous_files = self.metadata.get("files", {})

        current_set = set(current_files.keys())
        previous_set = set(previous_files.keys())

        new_files = current_set - previous_set
        deleted_files = previous_set - current_set
        potentially_modified = current_set & previous_set

        modified_files = set()
        for filepath in potentially_modified:
            if current_files[filepath]["hash"] != previous_files[filepath]["hash"]:
                modified_files.add(filepath)

        return new_files, modified_files, deleted_files

    def backup(self, source: str, destination: str, incremental: bool = True):
        """
        Esegue il backup della cartella origine verso la destinazione

        Args:
            source: Percorso della cartella origine
            destination: Percorso della cartella destinazione
            incremental: Se True, copia solo file nuovi/modificati; se False, copia tutto
        """
        source_path = Path(source).resolve()
        dest_path = Path(destination).resolve()

        print("=" * 70)
        print("BACKUP INCREMENTALE")
        print("=" * 70)
        print(f"Origine:      {source_path}")
        print(f"Destinazione: {dest_path}")
        print(f"Modalità:     {'Incrementale' if incremental else 'Completo'}")
        print("=" * 70)

        if not source_path.exists():
            print(f"\nErrore: la cartella origine '{source_path}' non esiste!")
            return

        # Crea la cartella di destinazione se non esiste
        dest_path.mkdir(parents=True, exist_ok=True)

        # Scansiona i file nella cartella origine
        current_files = self._scan_directory(source_path)

        if not current_files:
            print("\nNessun file trovato nella cartella origine.")
            return

        # Determina quali file copiare
        if incremental and "files" in self.metadata:
            new_files, modified_files, deleted_files = self._compare_files(current_files)
            files_to_copy = new_files | modified_files

            print(f"\n{'=' * 70}")
            print("ANALISI INCREMENTALE")
            print(f"{'=' * 70}")
            print(f"File totali nella origine:  {len(current_files)}")
            print(f"File nell'ultimo backup:    {len(self.metadata.get('files', {}))}")
            print(f"File nuovi:                 {len(new_files)}")
            print(f"File modificati:            {len(modified_files)}")
            print(f"File eliminati:             {len(deleted_files)}")
            print(f"File da copiare:            {len(files_to_copy)}")
            print(f"{'=' * 70}")

            if new_files:
                print("\nFile nuovi:")
                for f in sorted(new_files):
                    print(f"  + {f}")

            if modified_files:
                print("\nFile modificati:")
                for f in sorted(modified_files):
                    print(f"  M {f}")

            if deleted_files:
                print("\nFile eliminati dall'origine (NON rimossi dalla destinazione):")
                for f in sorted(deleted_files):
                    print(f"  - {f}")
        else:
            files_to_copy = set(current_files.keys())
            print(f"\nBackup completo: {len(files_to_copy)} file da copiare")

        # Copia i file
        if files_to_copy:
            print(f"\n{'=' * 70}")
            print("COPIA IN CORSO")
            print(f"{'=' * 70}")

            copied_count = 0
            for relative_path in sorted(files_to_copy):
                src_file = source_path / relative_path
                dst_file = dest_path / relative_path

                # Crea le directory necessarie
                dst_file.parent.mkdir(parents=True, exist_ok=True)

                try:
                    shutil.copy2(src_file, dst_file)
                    print(f"  Copiato: {relative_path}")
                    copied_count += 1
                except (IOError, OSError) as e:
                    print(f"  Errore durante la copia di {relative_path}: {e}")

            print(f"\n{copied_count} file copiati con successo!")
        else:
            print("\nNessun file da copiare (nessuna modifica rilevata).")

        # Aggiorna e salva i metadati
        self.metadata = {
            "last_backup": datetime.now().isoformat(),
            "source": str(source_path),
            "destination": str(dest_path),
            "files": current_files,
            "backup_type": "incremental" if incremental else "full"
        }
        self._save_metadata()

        print(f"\n{'=' * 70}")
        print("BACKUP COMPLETATO")
        print(f"{'=' * 70}\n")


def main():
    """Funzione principale del programma"""

    if len(sys.argv) < 3:
        print("Uso: python incremental_backup.py <cartella_origine> <cartella_destinazione> [--full]")
        print("\nOpzioni:")
        print("  --full    Esegue un backup completo invece di uno incrementale")
        print("\nEsempi:")
        print("  python incremental_backup.py ./folder_A ./folder_B")
        print("  python incremental_backup.py ./folder_A ./folder_C")
        print("  python incremental_backup.py ./folder_A ./folder_D --full")
        sys.exit(1)

    source = sys.argv[1]
    destination = sys.argv[2]
    incremental = "--full" not in sys.argv

    backup = IncrementalBackup()
    backup.backup(source, destination, incremental)


if __name__ == "__main__":
    main()
