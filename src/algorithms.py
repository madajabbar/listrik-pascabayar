"""Modul algorithms — Aplikasi Pembayaran Listrik Pascabayar.

Identitas modul : src/algorithms.py
Tujuan          : implementasi algoritma pengurutan dan pencarian untuk
                  Unit Mengimplementasikan Algoritma Pemrograman
                  (J.620100.022.02), dipakai demo CLI "Input angka /
                  Sorting / Searching" sesuai tampilan pada soal.
Riwayat revisi  : 2026-11-19 versi awal.
"""


def bubble_sort(data):
    """Mengurutkan list angka menaik dengan bubble sort.

    Cara kerja: bandingkan pasangan bersebelahan berulang-ulang dan
    tukar bila urutannya salah, sampai tidak ada pertukaran.
    Kompleksitas waktu : O(n^2) — dua loop bersarang.
    Kompleksitas memori: O(1) — in-place, hanya variabel penukar.

    Parameter: data (list[int/float]) angka yang akan diurutkan.
    Return   : list baru yang sudah terurut menaik.
    """
    hasil = list(data)
    n = len(hasil)
    for i in range(n - 1):
        for j in range(n - 1 - i):
            if hasil[j] > hasil[j + 1]:
                hasil[j], hasil[j + 1] = hasil[j + 1], hasil[j]
    return hasil


def linear_search(data, dicari):
    """Mencari angka dengan linear search (satu per satu dari awal).

    Kompleksitas waktu : O(n). Tidak menuntut data terurut.
    Parameter: data (list), dicari (angka yang dicari).
    Return   : indeks pertama bila ditemukan, -1 bila tidak ditemukan.
    """
    for i, nilai in enumerate(data):
        if nilai == dicari:
            return i
    return -1


def binary_search(data_terurut, dicari):
    """Mencari angka dengan binary search pada data yang SUDAH terurut.

    Cara kerja: periksa elemen tengah; bila lebih kecil, buang separuh
    kiri; bila lebih besar, buang separuh kanan; ulangi.
    Kompleksitas waktu : O(log n) — ruang pencarian menyusut separuh
                         setiap langkah. Syarat: data harus terurut.
    Kompleksitas memori: O(1) — iteratif, tanpa rekursi/stack tambahan.
    Parameter: data_terurut (list terurut menaik), dicari (angka).
    Return   : indeks bila ditemukan, -1 bila tidak ditemukan.
    """
    lo, hi = 0, len(data_terurut) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if data_terurut[mid] == dicari:
            return mid
        if data_terurut[mid] < dicari:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
