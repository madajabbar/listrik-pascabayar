"""Contoh SENGAJA berisi bug logika — bahan latihan Unit Debugging.

Bug: total tagihan dihitung dengan int(...) sehingga pecahan rupiah
DIPANGKAS (truncation), bukan DIBULATKAN. Program berjalan tanpa
error, tetapi hasilnya salah beberapa rupiah — ciri khas logic error.
Perbaikan resminya ada di src/service.py fungsi hitung_total_bayar
yang memakai Decimal + ROUND_HALF_UP.
Jalankan: python -m examples.buggy_demo
"""
from decimal import Decimal

from src.service import hitung_total_bayar


def hitung_total_buggy(jumlah_kwh, tarifperkwh, biaya_admin=2500):
    """Versi SALAH: memangkas desimal dengan int()."""
    return int(jumlah_kwh * tarifperkwh) + biaya_admin


if __name__ == "__main__":
    kwh, tarif = 3, 1444.70
    salah = hitung_total_buggy(kwh, tarif)
    benar = hitung_total_bayar(kwh, Decimal("1444.70"))
    print(f"Pemakaian {kwh} kWh x Rp{tarif} + admin Rp2.500")
    print(f"Hasil buggy (dipangkas) : Rp{salah}")
    print(f"Hasil benar (dibulatkan): Rp{benar}")
    print(f"Selisih                 : Rp{benar - salah}")
