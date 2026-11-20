"""Unit test algoritma sorting & searching (tanpa database).

Pola AAA: Arrange -> Act -> Assert. Data uji tiga kondisi:
normal, batas (boundary), dan tidak valid/khusus.
"""
from src.algorithms import binary_search, bubble_sort, linear_search


def test_bubble_sort_normal():
    # Arrange
    data = [70, 50, 90]
    # Act
    hasil = bubble_sort(data)
    # Assert (contoh persis tampilan soal: 70, 50, 90 -> 50, 70, 90)
    assert hasil == [50, 70, 90]


def test_bubble_sort_batas_satu_elemen_dan_kosong():
    assert bubble_sort([42]) == [42]
    assert bubble_sort([]) == []


def test_bubble_sort_sudah_terurut_dan_duplikat():
    assert bubble_sort([1, 2, 3]) == [1, 2, 3]
    assert bubble_sort([5, 5, 1]) == [1, 5, 5]


def test_binary_search_ditemukan():
    assert binary_search([50, 70, 90], 70) == 1


def test_binary_search_tidak_ditemukan():
    assert binary_search([50, 70, 90], 60) == -1


def test_linear_search():
    assert linear_search([70, 50, 90], 90) == 2
    assert linear_search([70, 50, 90], 10) == -1
