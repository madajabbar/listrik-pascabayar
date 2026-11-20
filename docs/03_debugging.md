# Dokumen 03 — Catatan Debugging (Unit Melakukan Debugging)

## Metode yang dipakai
Reproduksi bug → pasang breakpoint / baca stack trace dan log → amati variabel (watch/locals) → rumuskan hipotesis → perbaiki pada sumbernya → jalankan ulang kasus yang sama untuk verifikasi.

## Lembar ringkasan kode kesalahan — contoh terisi (dari `examples/buggy_demo.py`)
| Item | Isi |
|---|---|
| Lokasi | `examples/buggy_demo.py`, fungsi `hitung_total_buggy` |
| Jenis kesalahan | Logika (program berjalan tanpa error, hasil salah) |
| Gejala / reproduksi | Pemakaian 3 kWh × Rp1.444,70 + admin Rp2.500 menghasilkan Rp6.834, padahal seharusnya Rp6.834,10 |
| Pesan error / stack trace | Tidak ada (logic error tidak memunculkan error) |
| Akar masalah | `int(...)` memangkas pecahan rupiah (truncation) alih-alih membulatkan |
| Perbaikan | Gunakan `Decimal` + `quantize(ROUND_HALF_UP)` — diterapkan di `src/service.py` fungsi `hitung_total_bayar` |
| Verifikasi | Kasus yang sama dijalankan ulang: hasil Rp6.834,10; unit test `test_hitung_total_bayar_pembulatan` lulus, termasuk kasus setengah ke atas 100,005 → 100,01 |

## Kasus division by zero (rujukan teori)
Bila muncul kesalahan "division by zero": temukan baris pembagian dari stack trace, telusuri asal nilai nol (input/data kosong), tambahkan validasi penyebut sebelum membagi dan/atau tangkap eksepsinya agar program tidak crash, lalu uji ulang dengan data pemicu yang sama.

## Jenis error (pengingat)
Compile/sintaks = kode tidak dapat berjalan; runtime = berhenti di tengah eksekusi; logika = berjalan selesai tetapi hasil salah (paling sulit ditemukan, hanya terlihat dari pemeriksaan hasil).
