# Dokumen 06 — Pengujian Unit & Integrasi (Unit J.620100.033.02 dan J.620100.034.02)

## A. Pengujian unit — `python -m pytest tests/test_algorithms.py tests/test_validation.py`
Unit yang diuji adalah fungsi terkecil secara terisolasi (tanpa database), pola **AAA** (Arrange–Act–Assert), data uji tiga kondisi: normal, batas, tidak valid.

| Fungsi | Normal | Batas | Tidak valid |
|---|---|---|---|
| `bubble_sort` | [70,50,90] → [50,70,90] | 1 elemen; list kosong; sudah terurut; duplikat | — |
| `binary_search` | 70 ditemukan di indeks 1 | — | 60 → -1 (tidak ditemukan) |
| `hitung_pemakaian` | 1000→1150 = 150 | meter diam = 0 | meter ahir < awal → ValueError |
| `hitung_total_bayar` | 150 kWh = Rp205.300 | pembulatan 100,005 → 100,01 | — |
| `validasi_periode` | bulan 1 dan 12 sah | — | bulan 0 dan 13 → ValueError |

## B. Pengujian integrasi — `python -m pytest tests/test_integration.py tests/test_web.py`
Menguji interaksi antar modul dan aplikasi ↔ database/API web. Hasil dicatat dengan membandingkan aktual vs diharapkan; ketidaksesuaian dicatat beserta perkiraan penyebabnya, dilaporkan, dan diarsipkan di dokumen ini.

**Hasil eksekusi terakhir: `python -m pytest -v` → 21 passed, 0 failed** (19 November 2026, di laptop ini, terhadap MySQL asli — bukan mock). Uji web tambahan terhadap server yang sedang berjalan: login admin 200, dashboard menampilkan status "MySQL Terkoneksi", halaman pelanggan 200 untuk admin; login pelanggan budi berhasil dan aksesnya ke halaman admin dialihkan ke dashboard.

| # | Skenario | Diharapkan | Aktual | Status |
|---|---|---|---|---|
| 1 | Insert penggunaan (CLI/service → DB) | Baris penggunaan tersimpan; trigger membuat tagihan jumlah_meter yang benar, status BELUM BAYAR | Tagihan lahir otomatis; uji tambah Sari Des 2026 (590→640) menghasilkan tagihan jumlah_meter 50, status BELUM BAYAR | LULUS |
| 2 | Function total per bulan | Oktober 2026 = 560 kWh (150+90+320) | 560 kWh | LULUS |
| 3 | Stored procedure daya 900 | Mengembalikan Budi Santoso dan Sari Wulandari | Budi Santoso, Sari Wulandari | LULUS |
| 4 | DELETE pelanggan lalu ROLLBACK | Data pelanggan kembali ada (transaksi batal bersih) | Pelanggan Rina (id 4) tetap ada setelah ROLLBACK | LULUS |
| 5 | Pembayaran tagihan (service → pembayaran + tagihan) | Baris pembayaran tercatat; status tagihan menjadi LUNAS; total sesuai hitungan | Pembayaran tercatat dalam satu transaksi; status menjadi LUNAS; total sama dengan hitungan view | LULUS |
| 6 | Web: login admin → dashboard & pelanggan 200; login pelanggan → halaman admin dialihkan | Privilege per level bekerja | Admin: semua halaman 200. Pelanggan: dashboard 200, halaman admin dialihkan ke dashboard | LULUS |

Pendekatan integrasi yang dipakai: **bottom-up** — modul data (db/service) diuji terhadap database lebih dulu, lalu modul antarmuka (CLI/web) di atasnya; stub tidak diperlukan karena database lokal tersedia. (Pendekatan lain yang dikenal: top-down memakai stub untuk modul bawahan, dan sandwich gabungan keduanya.)

## C. Cara melaporkan & mengarsipkan
Jalankan `python -m pytest -v`, salin ringkasan hasilnya ke tabel di atas, lalu simpan dokumen ini bersama keluaran pytest sebagai arsip pengujian. Kegagalan tidak disembunyikan: catat, analisis penyebabnya, perbaiki, dan jalankan ulang skenario yang sama.
