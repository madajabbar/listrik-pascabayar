# Dokumen 02 — Dokumentasi Kode Program (Unit J.620100.023.02)

## Standar yang dipakai proyek ini
1. Setiap modul diawali docstring berisi: identitas modul, tujuan, input, output, eksepsi yang mungkin terjadi, dan riwayat revisi.
2. Setiap fungsi publik memiliki docstring: tujuan, parameter, nilai kembali, eksepsi.
3. Komentar di dalam kode menjelaskan **mengapa** keputusan diambil, bukan mengulang **apa** yang dilakukan baris tersebut.
4. Dokumentasi direvisi pada perubahan yang sama dengan perubahan kode — bukan belakangan.

## Peta modul
| Modul | Tanggung jawab |
|---|---|
| `src/config.py` | Membaca konfigurasi dari `.env` (tanpa hardcode kredensial) |
| `src/db.py` | Koneksi MySQL via mysql-connector (library akses basis data), `ping()` untuk indikator status |
| `src/service.py` | Logika bisnis: login per level, CRUD penggunaan, tagihan, pembayaran (transaksi COMMIT/ROLLBACK) |
| `src/algorithms.py` | Bubble sort O(n²), linear search O(n), binary search O(log n) |
| `src/cli.py` | Antarmuka CLI: init-db, seed, menu Administrator/Pelanggan, demo algoritma |
| `web/app.py` | Antarmuka web Flask dengan sesi login dan pembatasan peran |
| `sql/schema.sql` | PDM: 7 tabel, view, stored procedure, function, trigger |

## Generate dokumentasi
Docstring pada proyek ini mengikuti format yang dapat di-generate menjadi halaman dokumentasi dengan **pdoc** (Python): `pdoc src/service.py` menghasilkan HTML dari docstring. Alternatif per bahasa: Sphinx (Python, proyek besar), Javadoc (Java), DocFX/XML comments (.NET). Bila generate gagal, penyebab tersering adalah docstring tidak terstruktur atau modul gagal diimpor (dependensi belum terpasang) — perbaiki sumbernya lalu generate ulang.

## Pseudocode vs flowchart (rujukan Unit Algoritma)
Pseudocode = uraian langkah dalam teks mirip kode; flowchart = diagram grafis bersimbol standar. Keduanya mendokumentasikan algoritma yang sama; proyek ini menuliskan pseudocode pada docstring dan flowchart digambar saat presentasi/praktik.
