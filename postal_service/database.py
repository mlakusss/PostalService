"""Сохранение истории расчётов в SQLite."""
import sqlite3
from pathlib import Path


class PostalRepository:
    def __init__(self, db_path="data/postal_history.db"):
        self.db_path = str(db_path)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _initialize(self):
        with self._connect() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS calculations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    category TEXT NOT NULL,
                    sender TEXT NOT NULL,
                    recipient TEXT NOT NULL,
                    distance_km REAL NOT NULL,
                    weight_kg REAL NOT NULL,
                    volume_cm3 REAL NOT NULL,
                    delivery_type TEXT NOT NULL,
                    delivery_days INTEGER NOT NULL,
                    total REAL NOT NULL
                )
            """)

    def save(self, result):
        with self._connect() as connection:
            cursor = connection.execute("""
                INSERT INTO calculations
                (category, sender, recipient, distance_km, weight_kg,
                 volume_cm3, delivery_type, delivery_days, total)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                result["category"], result["sender"], result["recipient"],
                result["distance_km"], result["weight_kg"],
                result["volume_cm3"], result["delivery_type"],
                result["delivery_days"], result["total"]
            ))
            return cursor.lastrowid

    def get_all(self):
        with self._connect() as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                "SELECT * FROM calculations ORDER BY id DESC"
            ).fetchall()
            return [dict(row) for row in rows]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def __repr__(self):
        return f"PostalRepository(db_path={self.db_path!r})"

    def __str__(self):
        return f"Хранилище истории: {self.db_path}"
