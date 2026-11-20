"""Modul config — Aplikasi Pembayaran Listrik Pascabayar.

Identitas modul : src/config.py
Tujuan          : membaca konfigurasi koneksi database dari file .env
                  (environment), BUKAN hardcode di dalam kode, agar
                  kredensial mudah diganti dan tidak tersebar di kode.
Input           : file .env di folder proyek (DB_HOST, DB_PORT,
                  DB_USER, DB_PASSWORD, DB_NAME).
Output          : dictionary konfigurasi untuk mysql-connector.
Riwayat revisi  : 2026-11-19 versi awal untuk asesmen Analis Program.
"""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _muat_env():
    """Membaca file .env sederhana (format KUNCI=NILAI per baris)."""
    path = os.path.join(BASE_DIR, ".env")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for baris in f:
                baris = baris.strip()
                if not baris or baris.startswith("#") or "=" not in baris:
                    continue
                kunci, nilai = baris.split("=", 1)
                os.environ.setdefault(kunci.strip(), nilai.strip())


_muat_env()

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "127.0.0.1"),
    "port": int(os.environ.get("DB_PORT", "3306")),
    "user": os.environ.get("DB_USER", "app_listrik"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": os.environ.get("DB_NAME", "listrik_pascabayar"),
}

FLASK_SECRET = os.environ.get("FLASK_SECRET", "listrik-dev-secret")
BIAYA_ADMIN = 2500  # rupiah, biaya admin tetap per pembayaran
