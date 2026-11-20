"""Modul service — Aplikasi Pembayaran Listrik Pascabayar.

Identitas modul : src/service.py
Tujuan          : logika bisnis aplikasi — login berdasarkan level
                  (Administrator/Pelanggan), CRUD data penggunaan,
                  melihat tagihan, dan pembayaran. Semua akses data
                  memakai parameterized query (aman dari SQL injection)
                  dan transaksi eksplisit COMMIT/ROLLBACK.
Input           : objek koneksi dari src/db.py.
Output          : dictionary/list hasil query dan nilai perhitungan.
Eksepsi         : ValueError untuk input tidak valid (periode, meter).
Riwayat revisi  : 2026-11-19 versi awal.
"""
import hashlib
from decimal import Decimal, ROUND_HALF_UP

from .config import BIAYA_ADMIN


# ---------- fungsi murni (diuji unit test tanpa database) ----------

def hash_password(teks):
    """Mengembalikan hash SHA-256 dari password teks asli."""
    return hashlib.sha256(teks.encode("utf-8")).hexdigest()


def validasi_periode(bulan, tahun):
    """Memvalidasi periode pemakaian.

    Parameter: bulan (int 1..12), tahun (int 2000..2100).
    Eksepsi  : ValueError bila di luar rentang.
    """
    if not (1 <= int(bulan) <= 12):
        raise ValueError("Bulan harus 1..12")
    if not (2000 <= int(tahun) <= 2100):
        raise ValueError("Tahun harus 2000..2100")


def hitung_pemakaian(meter_awal, meter_ahir):
    """Menghitung pemakaian kWh = meter_ahir - meter_awal.

    Parameter: meter_awal (int), meter_ahir (int) posisi meter.
    Return   : int pemakaian kWh (>= 0).
    Eksepsi  : ValueError bila meter_ahir < meter_awal (data tidak
               masuk akal; kemungkinan salah catat meter).
    """
    if int(meter_ahir) < int(meter_awal):
        raise ValueError("Meter ahir tidak boleh lebih kecil dari meter awal")
    return int(meter_ahir) - int(meter_awal)


def hitung_total_bayar(jumlah_kwh, tarifperkwh, biaya_admin=BIAYA_ADMIN):
    """Menghitung total bayar tagihan dengan PEMBULATAN yang benar.

    Total = jumlah_kwh x tarifperkwh + biaya_admin, dibulatkan ke dua
    desimal dengan ROUND_HALF_UP (bukan dipangkas — lihat contoh bug
    di examples/buggy_demo.py).
    Return: Decimal total bayar.
    """
    total = (Decimal(str(jumlah_kwh)) * Decimal(str(tarifperkwh))
             + Decimal(str(biaya_admin)))
    return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# ---------- autentikasi ----------

def login(conn, username, password):
    """Memeriksa login pada tabel user (petugas) lalu pelanggan.

    Return: dict {nama, peran, id_user, id_pelanggan} bila cocok,
            None bila username/password salah.
    """
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT u.id_user, u.nama_admin, l.nama_level FROM user u "
        "JOIN level l ON l.id_level = u.id_level "
        "WHERE u.username = %s AND u.password = %s",
        (username, hash_password(password)),
    )
    baris = cur.fetchone()
    if baris:
        cur.close()
        return {"nama": baris["nama_admin"], "peran": baris["nama_level"],
                "id_user": baris["id_user"], "id_pelanggan": None}
    cur.execute(
        "SELECT id_pelanggan, nama_pelanggan FROM pelanggan "
        "WHERE username = %s AND password = %s",
        (username, hash_password(password)),
    )
    baris = cur.fetchone()
    cur.close()
    if baris:
        return {"nama": baris["nama_pelanggan"], "peran": "Pelanggan",
                "id_user": None, "id_pelanggan": baris["id_pelanggan"]}
    return None


# ---------- data pelanggan & tarif ----------

def daftar_pelanggan(conn):
    """Menampilkan semua pelanggan beserta daya dan tarifnya."""
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT p.id_pelanggan, p.nomor_kwh, p.nama_pelanggan, p.alamat, "
        "t.daya, t.tarifperkwh FROM pelanggan p "
        "JOIN tarif t ON t.id_tarif = p.id_tarif ORDER BY p.id_pelanggan")
    hasil = cur.fetchall()
    cur.close()
    return hasil


def pelanggan_daya_900(conn):
    """Memanggil stored procedure sp_pelanggan_daya_900."""
    cur = conn.cursor(dictionary=True)
    cur.callproc("sp_pelanggan_daya_900")
    hasil = []
    for kumpulan in cur.stored_results():
        hasil = kumpulan.fetchall()
    cur.close()
    return hasil


def total_penggunaan_per_bulan(conn, bulan, tahun):
    """Memanggil function fn_total_penggunaan_per_bulan."""
    validasi_periode(bulan, tahun)
    cur = conn.cursor()
    cur.execute("SELECT fn_total_penggunaan_per_bulan(%s, %s)", (bulan, tahun))
    total = cur.fetchone()[0]
    cur.close()
    return total


# ---------- penggunaan (CRUD) ----------

def tambah_penggunaan(conn, id_pelanggan, bulan, tahun, meter_awal, meter_ahir):
    """Menambah data penggunaan; trigger database membuat tagihannya.

    Transaksi: COMMIT bila insert berhasil; ROLLBACK + ValueError bila
    data tidak valid. Return: id_penggunaan baru.
    """
    try:
        validasi_periode(bulan, tahun)
        hitung_pemakaian(meter_awal, meter_ahir)  # validasi meter
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO penggunaan (id_pelanggan, bulan, tahun, meter_awal, meter_ahir) "
            "VALUES (%s, %s, %s, %s, %s)",
            (id_pelanggan, bulan, tahun, meter_awal, meter_ahir))
        id_baru = cur.lastrowid
        conn.commit()
        cur.close()
        return id_baru
    except Exception:
        conn.rollback()
        raise


def ubah_penggunaan(conn, id_penggunaan, meter_awal, meter_ahir):
    """Mengubah meter awal/ahir sebuah data penggunaan."""
    hitung_pemakaian(meter_awal, meter_ahir)
    cur = conn.cursor()
    cur.execute(
        "UPDATE penggunaan SET meter_awal = %s, meter_ahir = %s WHERE id_penggunaan = %s",
        (meter_awal, meter_ahir, id_penggunaan))
    conn.commit()
    terpengaruh = cur.rowcount
    cur.close()
    return terpengaruh


def hapus_penggunaan(conn, id_penggunaan):
    """Menghapus penggunaan beserta tagihannya dalam satu transaksi.

    Tagihan harus dihapus lebih dulu karena foreign key tagihan
    menunjuk penggunaan dengan ON DELETE RESTRICT.
    """
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM tagihan WHERE id_penggunaan = %s", (id_penggunaan,))
        cur.execute("DELETE FROM penggunaan WHERE id_penggunaan = %s", (id_penggunaan,))
        conn.commit()
        cur.close()
    except Exception:
        conn.rollback()
        raise


def daftar_penggunaan(conn, id_pelanggan=None):
    """Daftar penggunaan dari view v_info_penggunaan.

    Parameter: id_pelanggan None = semua (admin); terisi = milik satu
    pelanggan (dipakai menu pelanggan agar hanya melihat datanya).
    """
    cur = conn.cursor(dictionary=True)
    if id_pelanggan is None:
        cur.execute("SELECT * FROM v_info_penggunaan ORDER BY tahun, bulan, nama_pelanggan")
    else:
        cur.execute(
            "SELECT v.* FROM v_info_penggunaan v "
            "JOIN pelanggan p ON p.nomor_kwh = v.nomor_kwh "
            "WHERE p.id_pelanggan = %s ORDER BY v.tahun, v.bulan", (id_pelanggan,))
    hasil = cur.fetchall()
    cur.close()
    return hasil


# ---------- tagihan & pembayaran ----------

def daftar_tagihan(conn, id_pelanggan=None):
    """Daftar tagihan beserta perkiraan total bayarnya."""
    cur = conn.cursor(dictionary=True)
    sql = (
        "SELECT tg.id_tagihan, p.nama_pelanggan, tg.bulan, tg.tahun, "
        "tg.jumlah_meter, t.tarifperkwh, tg.status FROM tagihan tg "
        "JOIN pelanggan p ON p.id_pelanggan = tg.id_pelanggan "
        "JOIN tarif t ON t.id_tarif = p.id_tarif ")
    if id_pelanggan is None:
        cur.execute(sql + "ORDER BY tg.tahun, tg.bulan, p.nama_pelanggan")
    else:
        cur.execute(sql + "WHERE tg.id_pelanggan = %s ORDER BY tg.tahun, tg.bulan",
                    (id_pelanggan,))
    hasil = cur.fetchall()
    cur.close()
    for b in hasil:
        b["total_bayar"] = hitung_total_bayar(b["jumlah_meter"], b["tarifperkwh"])
    return hasil


def bayar_tagihan(conn, id_tagihan, id_user, tanggal, bulan_bayar):
    """Membayar satu tagihan dalam satu transaksi.

    Langkah: kunci baris tagihan (SELECT ... FOR UPDATE) -> hitung
    total -> INSERT pembayaran -> UPDATE status tagihan menjadi
    'LUNAS' -> COMMIT. Kegagalan di tengah jalan memicu ROLLBACK
    sehingga tidak ada data setengah jadi.
    Return: Decimal total yang dibayar.
    """
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT tg.id_pelanggan, tg.jumlah_meter, tg.status, t.tarifperkwh "
            "FROM tagihan tg JOIN pelanggan p ON p.id_pelanggan = tg.id_pelanggan "
            "JOIN tarif t ON t.id_tarif = p.id_tarif WHERE tg.id_tagihan = %s FOR UPDATE",
            (id_tagihan,))
        tg = cur.fetchone()
        if tg is None:
            raise ValueError("Tagihan tidak ditemukan")
        if tg["status"] == "LUNAS":
            raise ValueError("Tagihan sudah LUNAS")
        total = hitung_total_bayar(tg["jumlah_meter"], tg["tarifperkwh"])
        cur.execute(
            "INSERT INTO pembayaran (id_tagihan, id_pelanggan, tanggal_pembayaran, "
            "bulan_bayar, biaya_admin, total_bayar, id_user) VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (id_tagihan, tg["id_pelanggan"], tanggal, bulan_bayar, BIAYA_ADMIN, total, id_user))
        cur.execute("UPDATE tagihan SET status = 'LUNAS' WHERE id_tagihan = %s", (id_tagihan,))
        conn.commit()
        cur.close()
        return total
    except Exception:
        conn.rollback()
        raise
