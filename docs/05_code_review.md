# Dokumen 05 — Code Review (Unit J.620100.032.01)

## Prinsip
Code review mengevaluasi kode terhadap **spesifikasi**, lalu memperbaikinya sesuai coding guideline dan best practice **tanpa mengubah spesifikasinya**. Pengecualian terhadap guideline diperbolehkan **asal didokumentasikan alasannya**.

## Hasil review proyek ini (pemeriksaan 19 November 2026)
| # | Aspek | Yang diperiksa | Temuan | Perbaikan / Keputusan |
|---|---|---|---|---|
| 1 | Penamaan | Nama fungsi/variabel konsisten dan bermakna | Konsisten snake_case berbahasa Indonesia di semua modul (tambah_penggunaan, hitung_total_bayar) | Tidak ada perbaikan |
| 2 | Duplikasi | Tidak ada blok kode sama berulang di dua tempat | Perhitungan total terpusat di satu fungsi `hitung_total_bayar`; CLI dan web sama-sama memanggil `src/service.py` | Tidak ada perbaikan |
| 3 | Eksepsi | Error ditangani di tempat yang tepat, tidak disembunyikan | Validasi bisnis (meter, periode) melempar ValueError di service; lapisan CLI/web menangkap dan menampilkan pesan | Sesuai; lihat pengecualian beralasan di bawah |
| 4 | Keamanan | Kredensial tidak hardcode; query terparameter; hash password | Semua query memakai parameter `%s`; kredensial dari `.env`. Catatan: hash password memakai SHA-256 tanpa salt — memadai untuk aplikasi asesmen lokal; untuk produksi gunakan bcrypt/argon2 | Diterima dan dicatat sebagai keterbatasan yang disadari |
| 5 | Performa & konsistensi data | Index pada kolom periode/pelanggan; konsistensi antar tabel | **TEMUAN:** tagihan hanya lahir dari trigger INSERT — bila petugas mengoreksi meter (UPDATE penggunaan), jumlah_meter tagihan menjadi basi/tidak selaras | **DIPERBAIKI:** trigger `tr_tagihan_after_update_penggunaan` (AFTER UPDATE) ditambahkan di `sql/schema.sql`; dibuktikan oleh test `test_trigger_update_menyelaraskan_tagihan` |
| 6 | Komentar | Menjelaskan mengapa, bukan mengulang apa | Docstring modul menyatakan tujuan dan alasan desain (mis. kenapa Decimal untuk uang) | Tidak ada perbaikan |
| 7 | Kesesuaian spesifikasi | Fitur sesuai kebutuhan soal; tidak ada fitur liar | **TEMUAN:** halaman web Penggunaan baru menyediakan Tambah — ubah/hapus belum ada di UI, padahal spesifikasi meminta CRUD penggunaan (fungsi service-nya sudah ada) | **DIPERBAIKI:** route dan tombol Ubah/Hapus ditambahkan di `web/app.py` + `penggunaan.html` (khusus Administrator) |
| 8 | Pengujian | Setiap perubahan ditutup unit/integration test | Perbaikan #5 dan #7 ditutup test baru; seluruh suite dijalankan ulang | 22 test lulus (lihat Dokumen 06) |

## Temuan tambahan — peringatan dependensi
`pytest` memunculkan DeprecationWarning: pemanggilan method `cur.stored_results()` di `service.pelanggan_daya_900` dinyatakan deprecated oleh mysql-connector 26.x (akan menjadi property). Fungsi tetap berjalan benar dan hasil test lulus; bentuk property penggantinya belum tersedia pada versi connector yang terpasang, sehingga kode dipertahankan apa adanya dan temuan ini dicatat untuk ditangani saat upgrade connector berikutnya. Keputusan sadar, bukan kelalaian.

## Pengecualian beralasan (contoh nyata di kode ini)
Di `src/cli.py` fungsi `menu_admin`, penangkapan `except Exception` umum adalah **pengecualian yang disengaja dan didokumentasikan di komentar kode**: titik masuk CLI harus tetap hidup dan menampilkan pesan kesalahan kepada pengguna, bukan crash; kesalahan spesifik (validasi meter, periode, aturan bisnis) sudah ditangani lebih dulu di `src/service.py`. Kategori kode lain yang wajar dikecualikan dari guideline: kode hasil generate tools, library pihak ketiga, dan kode legacy yang dipertahankan demi kompatibilitas.

## Praktik baik yang diterapkan
- SELECT menyebutkan kolom yang dibutuhkan, bukan `SELECT *`, pada query bisnis (kecuali membaca view demo).
- Semua query memakai parameter `%s` (bukan penggabungan string) — anti SQL injection.
- Password pengguna disimpan sebagai hash SHA-256, bukan teks asli.
