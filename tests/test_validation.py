"""Unit test fungsi perhitungan & validasi service (tanpa database)."""
from decimal import Decimal

import pytest

from src.service import (hitung_pemakaian, hitung_total_bayar,
                         validasi_periode)


def test_hitung_pemakaian_normal():
    assert hitung_pemakaian(1000, 1150) == 150


def test_hitung_pemakaian_batas_nol():
    # Batas: meter tidak bergerak -> pemakaian 0, bukan error
    assert hitung_pemakaian(500, 500) == 0


def test_hitung_pemakaian_tidak_valid():
    # Meter ahir lebih kecil dari meter awal harus ditolak
    with pytest.raises(ValueError):
        hitung_pemakaian(1150, 1000)


def test_hitung_total_bayar_normal():
    # 150 kWh x Rp1.352 + admin Rp2.500 = Rp205.300
    assert hitung_total_bayar(150, Decimal("1352.00")) == Decimal("205300.00")


def test_hitung_total_bayar_pembulatan():
    # 3 kWh x Rp1.444,70 = Rp4.334,10 + 2.500 = Rp6.834,10 (dua desimal)
    assert hitung_total_bayar(3, Decimal("1444.70")) == Decimal("6834.10")
    # Kasus pembulatan setengah ke atas: 1 x 100,005 -> 100,01 bukan 100,00
    assert hitung_total_bayar(1, Decimal("100.005"), 0) == Decimal("100.01")


def test_validasi_periode():
    validasi_periode(1, 2026)   # batas bawah sah
    validasi_periode(12, 2026)  # batas atas sah
    with pytest.raises(ValueError):
        validasi_periode(13, 2026)
    with pytest.raises(ValueError):
        validasi_periode(0, 2026)
