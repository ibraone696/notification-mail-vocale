"""Historique des mails déjà annoncés (SQLite) pour éviter les doublons,
y compris après un redémarrage du script."""
from __future__ import annotations

import sqlite3
import threading
from pathlib import Path


class HistoriqueMails:
    def __init__(self, chemin_db: str | Path):
        self.chemin_db = str(chemin_db)
        self._verrou = threading.Lock()
        self._init_db()

    def _connexion(self):
        return sqlite3.connect(self.chemin_db, check_same_thread=False)

    def _init_db(self):
        with self._verrou, self._connexion() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS historique (
                    message_id TEXT PRIMARY KEY,
                    compte TEXT,
                    expediteur TEXT,
                    sujet TEXT,
                    date_traitement TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def deja_traite(self, message_id: str) -> bool:
        if not message_id:
            return False
        with self._verrou, self._connexion() as conn:
            cur = conn.execute(
                "SELECT 1 FROM historique WHERE message_id = ?", (message_id,)
            )
            return cur.fetchone() is not None

    def enregistrer(self, message_id: str, compte: str, expediteur: str, sujet: str):
        if not message_id:
            return
        with self._verrou, self._connexion() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO historique (message_id, compte, expediteur, sujet) "
                "VALUES (?, ?, ?, ?)",
                (message_id, compte, expediteur, sujet),
            )
