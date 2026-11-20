# Dokumen 04 — Profiling Program (Unit J.620100.031.01)

## Prinsip
Profiling **mengukur** performa (waktu eksekusi dan pemakaian sumber daya per bagian program); debugging **mencari kesalahan**. Keduanya berbeda. Aturan kerja: ukur dulu → temukan hotspot/bottleneck → analisis kompleksitas → optimasi → ukur ulang dan bandingkan. Tidak ada optimasi berdasarkan tebakan.

## Pengukuran pada proyek ini
Script: `scripts/profiling_before_after.py` — membuat tabel uji `penggunaan_pf` 50.000 baris dan mengukur query agregat per periode (`SELECT COUNT(*), SUM(...) WHERE bulan=10 AND tahun=2026`), rata-rata 5 kali eksekusi, sebelum dan sesudah `CREATE INDEX idx_pf_periode (bulan, tahun)`.

Hasil pengukuran di laptop ini (19 November 2026, MySQL 8.0 lokal, 50.000 baris):

| Tahap | EXPLAIN type | rows diperiksa | key | Rata-rata waktu |
|---|---|---|---|---|
| SEBELUM index | ALL (full table scan) | 50.000 | — | 0,066258 detik |
| SESUDAH index | ref | 4.166 | idx_pf_periode | 0,027760 detik |

**Peningkatan kecepatan: 58,1%.** Bottleneck-nya adalah full table scan pada query agregat per periode; satu index komposit pada kolom yang dipakai di WHERE menghilangkan bottleneck itu. Inilah pola umum bottleneck database: bukan kode aplikasinya yang lambat, melainkan cara database mencari barisnya.

## Cara membaca hasil
- EXPLAIN sebelum index: `type=ALL` (full table scan), `rows` ≈ seluruh tabel.
- EXPLAIN sesudah index: `type=ref`, `rows` jauh lebih kecil, `key=idx_pf_periode`.
- Bottleneck lain yang khas: query di dalam loop (N+1) dan algoritma O(n²) pada data besar.
- Dampak negatif bottleneck: waktu respons membengkak, throughput turun, sumber daya terkuras di satu titik, dan sistem cepat jenuh saat pengguna naik.

## Jenis profiler berdasarkan keluaran
Flat profiler (daftar fungsi menurut waktu/jumlah panggilan) dan call-graph profiler (pohon pemanggilan antar fungsi). Tipe keluaran profiler umumnya: jumlah pemanggilan (ncalls), waktu sendiri (tottime), waktu kumulatif (cumtime), waktu per panggilan, serta daftar pemanggil/yang dipanggil.
