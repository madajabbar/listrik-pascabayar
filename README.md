# Aplikasi Pembayaran Listrik Pascabayar

Aplikasi client-server (Python + MySQL 8) untuk asesmen kompetensi **Analis Program** (LSP Nusa Mandiri, TUK Jatiwaringin) — dibangun mengikuti skenario resmi FR.IA.02: pencatatan penggunaan listrik per bulan, tagihan otomatis, dan pembayaran, dengan login berjenjang Administrator dan Pelanggan.

## Cakupan per unit kompetensi
| Unit | Bukti di proyek ini |
|---|---|
| Skalabilitas | `docs/01_analisis_skalabilitas.md` + `docs/PRESENTASI_SKALABILITAS.md` |
| Menggunakan SQL | `sql/schema.sql` — 7 tabel (PDM dari CDM), view, stored procedure pelanggan daya 900, function total penggunaan per bulan, trigger tagihan, COMMIT/ROLLBACK di `sql/seed.sql` dan service |
| Akses Basis Data | `src/db.py` (mysql-connector), hak akses per pengguna (`sql/setup_database.sql`, `sql/grants.sql`), index untuk mempercepat akses |
| Algoritma | `src/algorithms.py` — bubble sort O(n²), linear search O(n), binary search O(log n); demo CLI persis tampilan soal |
| Dokumen Kode | Docstring identitas/tujuan/input/output di semua modul + `docs/02_dokumentasi_kode.md` |
| Debugging | `examples/buggy_demo.py` + `docs/03_debugging.md` (lembar ringkasan kesalahan terisi) |
| Profiling | `scripts/profiling_before_after.py` + `docs/04_profiling.md` |
| Code Review | `docs/05_code_review.md` (checklist + pengecualian beralasan di `src/cli.py`) |
| Pengujian Unit | `tests/test_algorithms.py`, `tests/test_validation.py` (pola AAA, normal/batas/tidak valid) |
| Pengujian Integrasi | `tests/test_integration.py`, `tests/test_web.py` + lembar pengujian di `docs/06_pengujian.md` |

## Persiapan database (satu kali, oleh root)
Di PowerShell, dari folder proyek:
```powershell
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -uroot -p < sql\setup_database.sql
```
Perintah ini membuat database `listrik_pascabayar` dan user aplikasi `app_listrik`. Aplikasi tidak pernah memakai root.

## Menjalankan
```powershell
pip install -r requirements.txt
python -m src.cli init-db
python -m src.cli seed
python -m src.cli            # aplikasi CLI (login: admin/admin123 atau budi/budi123)
python -m web.app            # aplikasi web di http://localhost:5000
python -m pytest -v          # seluruh pengujian
python -m scripts.profiling_before_after
python -m examples.buggy_demo
```

## Akun demo
Administrator: `admin` / `admin123` · Pelanggan: `budi` / `budi123`, `sari` / `sari123`, `agus` / `agus123`, `rina` / `rina123` (password tersimpan sebagai hash SHA-256).

## Alur data utama
Petugas memasukkan penggunaan (meter awal–ahir) → **trigger** membuat tagihan otomatis (jumlah_meter = meter_ahir − meter_awal, status BELUM BAYAR) → pelanggan melihat tagihannya → petugas menerima pembayaran dalam satu transaksi (INSERT pembayaran + UPDATE status LUNAS + COMMIT; gagal di tengah = ROLLBACK).
