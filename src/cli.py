"""Modul cli — Aplikasi Pembayaran Listrik Pascabayar.

Identitas modul : src/cli.py
Tujuan          : antarmuka baris perintah (client) aplikasi:
                  inisialisasi database (init-db), isi data awal (seed),
                  login berdasarkan level, menu Administrator dan menu
                  Pelanggan, serta submenu demo algoritma persis
                  tampilan soal (Input angka / Sorting / Searching).
Cara menjalankan:
    python -m src.cli init-db     (membuat tabel, view, SP, function, trigger)
    python -m src.cli seed        (mengisi data awal)
    python -m src.cli             (menjalankan aplikasi)
Riwayat revisi  : 2026-11-19 versi awal.
"""
import argparse
import getpass
import os
import sys

from . import service
from .algorithms import binary_search, bubble_sort, linear_search
from .config import BASE_DIR
from .db import get_connection


def _jalankan_file_sql(conn, nama_file):
    """Menjalankan seluruh isi file .sql (mendukung DELIMITER)."""
    path = os.path.join(BASE_DIR, "sql", nama_file)
    with open(path, encoding="utf-8") as f:
        isi = f.read()
    cur = conn.cursor()
    # mysql-connector tidak memahami DELIMITER; blok routine dipisah manual.
    pernyataan = []
    penampung = ""
    delimiter = ";"
    for baris in isi.splitlines():
        if baris.strip().upper().startswith("DELIMITER"):
            delimiter = baris.strip().split()[1]
            continue
        penampung += baris + "\n"
        if baris.strip().endswith(delimiter):
            pernyataan.append(penampung.strip()[: -len(delimiter)].strip())
            penampung = ""
    if penampung.strip():
        pernyataan.append(penampung.strip())
    for sql in pernyataan:
        if sql:
            cur.execute(sql)
    conn.commit()
    cur.close()


def init_db():
    conn = get_connection()
    _jalankan_file_sql(conn, "schema.sql")
    conn.close()
    print("Skema database berhasil dibuat (tabel, view, SP, function, trigger).")


def seed():
    conn = get_connection()
    _jalankan_file_sql(conn, "seed.sql")
    conn.close()
    print("Data awal berhasil diisi.")


# ---------------- submenu demo algoritma (sesuai tampilan soal) --------

def menu_algoritma():
    angka = []
    while True:
        print("\n        MENU PILIHAN")
        print("1. Input angka")
        print("2. Sorting")
        print("3. Searching")
        print("4. Selesai")
        pilihan = input("Masukkan pilihan [1/2/3/4] : ").strip()
        if pilihan == "1":
            print("\n        INPUT ANGKA")
            n = int(input("Masukkan jumlah nilai tugas : "))
            print("\nInput Angka Secara Acak")
            print("----------------------------------------")
            angka = []
            for i in range(n):
                angka.append(int(input(f"Angka {i + 1} : ")))
        elif pilihan == "2":
            print("\n        TAMPIL HASIL SORTING")
            terurut = bubble_sort(angka)
            print("Hasil sorting : " + ", ".join(str(a) for a in terurut))
            print("(Bubble sort - kompleksitas waktu O(n^2), memori O(1))")
        elif pilihan == "3":
            print("\n        TAMPIL HASIL SEARCHING")
            dicari = int(input("Masukkan angka yang dicari : "))
            terurut = bubble_sort(angka)
            idx = binary_search(terurut, dicari)
            if idx >= 0:
                print("Angka ditemukan")
            else:
                print("Angka tidak ditemukan")
            print("(Binary search pada data terurut - kompleksitas O(log n); "
                  f"linear search O(n) menemukan di indeks {linear_search(angka, dicari)})")
        elif pilihan == "4":
            break
        else:
            print("Pilihan tidak dikenal.")


# ---------------- menu utama per peran --------------------------------

def _cetak_penggunaan(conn, id_pelanggan=None):
    for b in service.daftar_penggunaan(conn, id_pelanggan):
        print(f"- {b['nama_pelanggan']} | {b['bulan']}/{b['tahun']} | "
              f"meter {b['meter_awal']}->{b['meter_ahir']} | "
              f"{b['jumlah_pemakaian_kwh']} kWh | perkiraan Rp{b['perkiraan_tagihan']}")


def _cetak_tagihan(conn, id_pelanggan=None):
    for b in service.daftar_tagihan(conn, id_pelanggan):
        print(f"- [{b['id_tagihan']}] {b['nama_pelanggan']} | {b['bulan']}/{b['tahun']} | "
              f"{b['jumlah_meter']} kWh | total Rp{b['total_bayar']} | {b['status']}")


def menu_admin(conn, sesi):
    while True:
        print(f"\n=== MENU ADMINISTRATOR ({sesi['nama']}) ===")
        print("1. Daftar pelanggan")
        print("2. Pelanggan daya 900 watt (stored procedure)")
        print("3. Tambah data penggunaan")
        print("4. Lihat penggunaan (view)")
        print("5. Lihat tagihan")
        print("6. Bayar tagihan")
        print("7. Total penggunaan per bulan (function)")
        print("8. Demo algoritma (sorting & searching)")
        print("0. Logout")
        p = input("Pilihan: ").strip()
        try:
            if p == "1":
                for b in service.daftar_pelanggan(conn):
                    print(f"- {b['nomor_kwh']} | {b['nama_pelanggan']} | daya {b['daya']} | Rp{b['tarifperkwh']}/kWh")
            elif p == "2":
                for b in service.pelanggan_daya_900(conn):
                    print(f"- {b['nomor_kwh']} | {b['nama_pelanggan']} | {b['alamat']} | daya {b['daya']}")
            elif p == "3":
                idp = int(input("ID pelanggan        : "))
                bln = int(input("Bulan (1-12)        : "))
                thn = int(input("Tahun               : "))
                awal = int(input("Meter awal          : "))
                ahir = int(input("Meter ahir          : "))
                id_baru = service.tambah_penggunaan(conn, idp, bln, thn, awal, ahir)
                print(f"Penggunaan tersimpan (id {id_baru}); tagihan dibuat otomatis oleh trigger.")
            elif p == "4":
                _cetak_penggunaan(conn)
            elif p == "5":
                _cetak_tagihan(conn)
            elif p == "6":
                idt = int(input("ID tagihan          : "))
                tgl = input("Tanggal bayar (YYYY-MM-DD): ").strip()
                bln = int(input("Bulan bayar (1-12)  : "))
                total = service.bayar_tagihan(conn, idt, sesi["id_user"], tgl, bln)
                print(f"Pembayaran berhasil. Total dibayar Rp{total}; status tagihan LUNAS.")
            elif p == "7":
                bln = int(input("Bulan (1-12): "))
                thn = int(input("Tahun       : "))
                print(f"Total penggunaan {bln}/{thn} = {service.total_penggunaan_per_bulan(conn, bln, thn)} kWh")
            elif p == "8":
                menu_algoritma()
            elif p == "0":
                break
            else:
                print("Pilihan tidak dikenal.")
        except Exception as e:
            # Pengecualian: except Exception di titik masuk CLI disengaja -
            # program harus tetap hidup dan menampilkan pesan, bukan crash;
            # kesalahan spesifik sudah divalidasi di src/service.py.
            print(f"Terjadi kesalahan: {e}")


def menu_pelanggan(conn, sesi):
    while True:
        print(f"\n=== MENU PELANGGAN ({sesi['nama']}) ===")
        print("1. Penggunaan listrik saya")
        print("2. Tagihan saya")
        print("3. Demo algoritma (sorting & searching)")
        print("0. Logout")
        p = input("Pilihan: ").strip()
        try:
            if p == "1":
                _cetak_penggunaan(conn, sesi["id_pelanggan"])
            elif p == "2":
                _cetak_tagihan(conn, sesi["id_pelanggan"])
            elif p == "3":
                menu_algoritma()
            elif p == "0":
                break
            else:
                print("Pilihan tidak dikenal.")
        except Exception as e:
            print(f"Terjadi kesalahan: {e}")


def aplikasi():
    conn = get_connection()
    print("=== APLIKASI PEMBAYARAN LISTRIK PASCABAYAR ===")
    username = input("Username: ").strip()
    password = getpass.getpass("Password: ")
    sesi = service.login(conn, username, password)
    if sesi is None:
        print("Login gagal: username atau password salah.")
        conn.close()
        return
    print(f"Selamat datang, {sesi['nama']} ({sesi['peran']})")
    if sesi["peran"] == "Pelanggan":
        menu_pelanggan(conn, sesi)
    else:
        menu_admin(conn, sesi)
    conn.close()
    print("Logout. Sampai jumpa.")


def main():
    parser = argparse.ArgumentParser(description="Aplikasi Pembayaran Listrik Pascabayar")
    parser.add_argument("perintah", nargs="?", choices=["init-db", "seed"],
                        help="init-db = buat skema; seed = isi data awal; kosong = jalankan aplikasi")
    args = parser.parse_args()
    if args.perintah == "init-db":
        init_db()
    elif args.perintah == "seed":
        seed()
    else:
        aplikasi()


if __name__ == "__main__":
    sys.exit(main())
