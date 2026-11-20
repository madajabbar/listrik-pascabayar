# Dokumen 01 — Analisis Skalabilitas Perangkat Lunak
## Aplikasi Pembayaran Listrik Pascabayar (Unit J.620100.002.01)

### 1. Lingkup (scope) dan lingkungan operasi
Aplikasi pembayaran listrik pascabayar berbasis client-server (web): pelanggan melihat tagihan dan riwayat pemakaian; petugas/administrator mencatat penggunaan (meter awal–ahir), mengelola pelanggan dan tarif, serta menerima pembayaran. Sistem berjalan desktop/web/mobile melalui browser, dengan satu server aplikasi dan satu server basis data MySQL. Tekanan berbeda per platform: desktop petugas = input massal di awal bulan; web/mobile pelanggan = lonjakan baca tagihan pada tanggal jatuh tempo.

### 2. Kebutuhan skalabilitas
- **Kompleksitas operasi:** pencatatan meter bulanan, perhitungan tagihan otomatis (trigger), pembayaran, dan laporan agregat per periode.
- **Jumlah data:** pertumbuhan baris `penggunaan` dan `tagihan` bersifat linier terhadap jumlah pelanggan × bulan; arsip tidak pernah dihapus.
- **Lingkungan operasi:** satu wilayah layanan, jam sibuk terkonsentrasi (awal bulan dan tanggal jatuh tempo), pengguna bersamaan naik seiring jumlah pelanggan.

### 3. Analisis masalah dan kompleksitas
Komponen paling berat adalah basis data, khususnya query agregat dan pencarian per periode pada tabel `penggunaan`/`tagihan` yang terus membesar. Kompleksitas aplikasi: pemrosesan per transaksi ringan (O(1)–O(log n) dengan index), tetapi agregat tanpa index menjadi O(n) full scan. Faktor skalabilitas yang menentukan: jumlah pengguna bersamaan, volume data historis, dan kompleksitas laporan.

### 4. Kebutuhan perangkat keras (analisis)
- **Beban saat ini (baseline):** 1 server aplikasi + MySQL satu mesin, ±4 vCPU, 8 GB RAM; data uji 50.000 baris terbukti terlayani (lihat Dokumen 04 — Profiling).
- **Proyeksi 10×:** pengguna dan data naik 10× → bottleneck pertama adalah query database (dibuktikan dengan EXPLAIN pada Dokumen 04), bukan CPU aplikasi.
- **Strategi bertahap:** (1) *vertical scaling* + index pada kolom periode/pelanggan — cukup dan paling murah pada skala ini; (2) caching hasil agregat yang sering diminta (total per bulan); (3) *horizontal scaling* — pisahkan server aplikasi dan database, tambah read replica untuk laporan — hanya bila tahap 1–2 tidak lagi mencukupi, karena biaya dan kompleksitasnya tidak sebanding untuk skala awal.

### 5. Kesimpulan
Urutan keputusan: ukur → temukan bottleneck → perbaiki yang paling berat dulu (index) → naikkan spek (vertical) → terakhir tambah mesin (horizontal). Dokumentasi ini menjadi bahan presentasi teknis 10 menit kepada asesor.
