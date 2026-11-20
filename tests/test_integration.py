"""Pengujian integrasi aplikasi <-> MySQL asli (bukan mock).

Skenario menutup langkah soal FR.IA.02: trigger membuat tagihan,
trigger update menyelaraskan tagihan, function total per bulan,
stored procedure daya 900, dan ROLLBACK membatalkan penghapusan
pelanggan. Test dilewati (skip) bila database belum disiapkan.
"""
import pytest

from src import service
from src.db import get_connection, ping

pytestmark = pytest.mark.skipif(not ping(), reason="MySQL aplikasi belum siap")


@pytest.fixture()
def conn():
    c = get_connection()
    yield c
    c.close()


def test_trigger_membuat_tagihan(conn):
    # Arrange + Act: tambah penggunaan untuk Sari (id 2), Desember 2026
    id_baru = service.tambah_penggunaan(conn, 2, 12, 2026, 590, 640)
    # Assert: tagihan lahir otomatis dengan jumlah_meter 50
    tagihan = [t for t in service.daftar_tagihan(conn, 2)
               if t["bulan"] == 12 and t["tahun"] == 2026]
    assert len(tagihan) == 1
    assert tagihan[0]["jumlah_meter"] == 50
    assert tagihan[0]["status"] == "BELUM BAYAR"
    service.hapus_penggunaan(conn, id_baru)  # bersihkan


def test_trigger_update_menyelaraskan_tagihan(conn):
    # Koreksi meter pada penggunaan yang sudah ada harus mengubah
    # jumlah_meter tagihannya (trigger AFTER UPDATE).
    id_baru = service.tambah_penggunaan(conn, 3, 12, 2026, 2320, 2400)  # Agus, 80 kWh
    service.ubah_penggunaan(conn, id_baru, 2320, 2450)  # dikoreksi menjadi 130 kWh
    tagihan = [t for t in service.daftar_tagihan(conn, 3)
               if t["bulan"] == 12 and t["tahun"] == 2026]
    assert len(tagihan) == 1
    assert tagihan[0]["jumlah_meter"] == 130
    service.hapus_penggunaan(conn, id_baru)  # bersihkan


def test_function_total_per_bulan(conn):
    # Data seed Oktober 2026: 150 + 90 + 320 = 560 kWh
    assert service.total_penggunaan_per_bulan(conn, 10, 2026) == 560


def test_procedure_daya_900(conn):
    nama = {b["nama_pelanggan"] for b in service.pelanggan_daya_900(conn)}
    assert nama == {"Budi Santoso", "Sari Wulandari"}


def test_rollback_membatalkan_hapus_pelanggan(conn):
    # Skenario soal: hapus 1 data pelanggan lalu ROLLBACK.
    cur = conn.cursor()
    cur.execute("DELETE FROM pelanggan WHERE id_pelanggan = 4")  # Rina
    conn.rollback()  # batalkan - data harus kembali
    cur.execute("SELECT COUNT(*) FROM pelanggan WHERE id_pelanggan = 4")
    assert cur.fetchone()[0] == 1
    cur.close()


def test_pembayaran_satu_transaksi(conn):
    # Bayar tagihan pertama Budi (Oktober) sebagai admin (id_user 1)
    tagihan = [t for t in service.daftar_tagihan(conn, 1)
               if t["status"] == "BELUM BAYAR"]
    assert tagihan, "perlu tagihan belum lunas dari seed"
    target = tagihan[0]
    total = service.bayar_tagihan(conn, target["id_tagihan"], 1, "2026-11-19", 11)
    assert total == target["total_bayar"]
    sesudah = [t for t in service.daftar_tagihan(conn, 1)
               if t["id_tagihan"] == target["id_tagihan"]]
    assert sesudah[0]["status"] == "LUNAS"
