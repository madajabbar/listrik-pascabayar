-- =====================================================================
-- seed.sql - data awal. Password disimpan sebagai hash SHA-256:
--   admin -> admin123, budi -> budi123, sari -> sari123,
--   agus -> agus123, rina -> rina123  (contoh untuk keperluan demo)
-- Insert data tarif dibungkus transaksi dan diakhiri COMMIT, sesuai
-- langkah soal: "gunakan perintah commit setelah insert data tarif".
-- =====================================================================
USE listrik_pascabayar;

INSERT INTO level (id_level, nama_level) VALUES
(1, 'Administrator'), (2, 'Pelanggan')
ON DUPLICATE KEY UPDATE nama_level = VALUES(nama_level);

INSERT INTO user (id_user, username, password, nama_admin, id_level) VALUES
(1, 'admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'Admin PLN Lokal', 1)
ON DUPLICATE KEY UPDATE nama_admin = VALUES(nama_admin);

START TRANSACTION;
INSERT INTO tarif (id_tarif, daya, tarifperkwh) VALUES
(1, 450, 415.00), (2, 900, 1352.00), (3, 1300, 1444.70), (4, 2200, 1444.70)
ON DUPLICATE KEY UPDATE tarifperkwh = VALUES(tarifperkwh);
COMMIT;

INSERT INTO pelanggan (id_pelanggan, username, password, nomor_kwh, nama_pelanggan, alamat, id_tarif) VALUES
(1, 'budi', 'e8979d2eb704c94fa2fa5044edba1c29232526eec3965ffc64308b6783f2de12', 'KWH-001', 'Budi Santoso',   'Jl. Merdeka 1',  2),
(2, 'sari', 'ec0dbbe4afd86f8e1c3e9810f5ebd7a1c23c3a286dc9b3ca4d9e0389a244b290', 'KWH-002', 'Sari Wulandari', 'Jl. Merdeka 2',  2),
(3, 'agus', '1baedd25059490937a8f7a52dbaf5a7c168bc49f5bac0d7bc48bd6b58a84a421', 'KWH-003', 'Agus Pratama',   'Jl. Sudirman 5', 3),
(4, 'rina', '041e4e852c36528e050e1d979f30b59870a2353ae6a06a9606f7b353d8a0e8d5', 'KWH-004', 'Rina Marlina',   'Jl. Sudirman 9', 4)
ON DUPLICATE KEY UPDATE nama_pelanggan = VALUES(nama_pelanggan);

-- Data penggunaan: setiap INSERT memicu trigger yang membuat tagihan.
INSERT INTO penggunaan (id_pelanggan, bulan, tahun, meter_awal, meter_ahir) VALUES
(1, 10, 2026, 1000, 1150),
(2, 10, 2026,  500,  590),
(3, 10, 2026, 2000, 2320),
(1, 11, 2026, 1150, 1310)
ON DUPLICATE KEY UPDATE meter_ahir = VALUES(meter_ahir);
