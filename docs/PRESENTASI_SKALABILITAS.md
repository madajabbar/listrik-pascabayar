# Kerangka Presentasi Skalabilitas — Aplikasi Pembayaran Listrik Pascabayar
## Bahan presentasi teknis 10 menit ke asesor (FR.IA.02 Unit J.620100.002.01)

**Slide 1 — Sistemnya.** Aplikasi pembayaran listrik pascabayar client-server (web): pelanggan cek tagihan, petugas catat meter dan terima pembayaran. Satu server aplikasi + MySQL. Platform desktop/web/mobile memberi tekanan berbeda: input massal petugas di awal bulan, lonjakan baca pelanggan saat jatuh tempo. *(±1 menit)*

**Slide 2 — Kebutuhan skalabilitas.** Tiga hal: kompleksitas operasi (catat meter → tagihan otomatis → pembayaran → laporan), jumlah data (baris penggunaan/tagihan tumbuh linier: pelanggan × bulan, tidak pernah dihapus), lingkungan operasi (jam sibuk terkonsentrasi). *(±1,5 menit)*

**Slide 3 — Di mana beratnya.** Bukan di CPU aplikasi — transaksi per pelanggan ringan. Yang berat: query agregat dan pencarian per periode di tabel yang terus membesar. Tanpa index, kompleksitasnya O(n) full scan. *(±1,5 menit)*

**Slide 4 — Bukti pengukuran.** Tunjukkan hasil Dokumen 04: EXPLAIN sebelum index type=ALL rows≈50.000 vs sesudah index rows jauh lebih kecil + persentase percepatannya. "Saya tidak menebak; saya mengukur." *(±2 menit)*

**Slide 5 — Proyeksi 10×.** Pengguna dan data naik 10×: bottleneck pertama tetap database. Kebutuhan perangkat keras dianalisis dari baseline terukur, bukan dari rasa. *(±1,5 menit)*

**Slide 6 — Strategi bertahap.** (1) Vertical + index — termurah, cukup untuk skala ini. (2) Caching agregat yang sering diminta. (3) Horizontal/read replica — hanya bila perlu; langsung horizontal di awal berarti membayar kompleksitas yang belum dibutuhkan. Bedakan dengan tegas: vertical = naikkan spek satu server; horizontal = tambah server. *(±1,5 menit)*

**Slide 7 — Penutup.** Prinsipnya satu kalimat: skalabilitas direncanakan dari pengukuran beban dan bottleneck, bukan dari menambah mesin secara reaktif. Siap menjawab pertanyaan. *(±1 menit)*
