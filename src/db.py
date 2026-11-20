"""Modul db — Aplikasi Pembayaran Listrik Pascabayar.

Identitas modul : src/db.py
Tujuan          : menyediakan koneksi MySQL melalui library
                  mysql-connector-python (library akses basis data).
Input           : DB_CONFIG dari src/config.py.
Output          : objek koneksi MySQL (autocommit=False agar transaksi
                  COMMIT/ROLLBACK dikendalikan eksplisit oleh service).
Eksepsi         : mysql.connector.Error bila server tidak terjangkau
                  atau hak akses ditolak.
Riwayat revisi  : 2026-11-19 versi awal.
"""
import mysql.connector

from .config import DB_CONFIG


def get_connection(database=True):
    """Membuka koneksi baru ke MySQL.

    Parameter:
        database (bool): True bila langsung memilih database aplikasi;
            False dipakai saat init-db (database mungkin belum ada).
    Return:
        MySQLConnection dengan autocommit=False.
    """
    cfg = dict(DB_CONFIG)
    if not database:
        cfg.pop("database", None)
    conn = mysql.connector.connect(**cfg)
    conn.autocommit = False
    return conn


def ping():
    """Memeriksa kesehatan koneksi (dipakai indikator status di web).

    Return: True bila SELECT 1 berhasil, False bila gagal.
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.fetchone()
        cur.close()
        conn.close()
        return True
    except Exception:
        return False
