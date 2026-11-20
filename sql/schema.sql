-- =====================================================================
-- schema.sql - Physical Data Model (PDM) Aplikasi Pembayaran Listrik
-- Pascabayar, diturunkan dari CDM pada soal FR.IA.02 Unit J.620100.020.02.
-- Dijalankan oleh user aplikasi (lihat src/cli.py perintah init-db).
-- Urutan pembuatan mengikuti arah foreign key.
-- =====================================================================
USE listrik_pascabayar;

CREATE TABLE IF NOT EXISTS level (
    id_level   INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nama_level VARCHAR(50) NOT NULL,
    PRIMARY KEY (id_level)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS user (
    id_user    INT UNSIGNED NOT NULL AUTO_INCREMENT,
    username   VARCHAR(50) NOT NULL,
    password   VARCHAR(255) NOT NULL,  -- hash SHA-256, bukan teks asli
    nama_admin VARCHAR(100) NOT NULL,
    id_level   INT UNSIGNED NOT NULL,
    PRIMARY KEY (id_user),
    UNIQUE KEY uq_user_username (username),
    CONSTRAINT fk_user_level FOREIGN KEY (id_level)
        REFERENCES level (id_level) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS tarif (
    id_tarif    INT UNSIGNED NOT NULL AUTO_INCREMENT,
    daya        INT NOT NULL,  -- VA: 450, 900, 1300, 2200
    tarifperkwh DECIMAL(12,2) NOT NULL,
    PRIMARY KEY (id_tarif),
    UNIQUE KEY uq_tarif_daya (daya)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS pelanggan (
    id_pelanggan   INT UNSIGNED NOT NULL AUTO_INCREMENT,
    username       VARCHAR(50) NOT NULL,
    password       VARCHAR(255) NOT NULL,  -- hash SHA-256
    nomor_kwh      VARCHAR(30) NOT NULL,
    nama_pelanggan VARCHAR(100) NOT NULL,
    alamat         VARCHAR(255) NULL,
    id_tarif       INT UNSIGNED NOT NULL,
    PRIMARY KEY (id_pelanggan),
    UNIQUE KEY uq_pelanggan_username (username),
    UNIQUE KEY uq_pelanggan_kwh (nomor_kwh),
    INDEX idx_pelanggan_tarif (id_tarif),
    CONSTRAINT fk_pelanggan_tarif FOREIGN KEY (id_tarif)
        REFERENCES tarif (id_tarif) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS penggunaan (
    id_penggunaan INT UNSIGNED NOT NULL AUTO_INCREMENT,
    id_pelanggan  INT UNSIGNED NOT NULL,
    bulan         TINYINT NOT NULL,   -- 1..12
    tahun         SMALLINT NOT NULL,
    meter_awal    INT NOT NULL,
    meter_ahir    INT NOT NULL,       -- nama kolom persis dari CDM soal
    PRIMARY KEY (id_penggunaan),
    INDEX idx_penggunaan_pelanggan (id_pelanggan),
    INDEX idx_penggunaan_periode (bulan, tahun),
    CONSTRAINT fk_penggunaan_pelanggan FOREIGN KEY (id_pelanggan)
        REFERENCES pelanggan (id_pelanggan) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS tagihan (
    id_tagihan    INT UNSIGNED NOT NULL AUTO_INCREMENT,
    id_penggunaan INT UNSIGNED NOT NULL,
    id_pelanggan  INT UNSIGNED NOT NULL,
    bulan         TINYINT NOT NULL,
    tahun         SMALLINT NOT NULL,
    jumlah_meter  INT NOT NULL,  -- meter_ahir - meter_awal (diisi trigger)
    status        VARCHAR(20) NOT NULL DEFAULT 'BELUM BAYAR',
    PRIMARY KEY (id_tagihan),
    CONSTRAINT fk_tagihan_penggunaan FOREIGN KEY (id_penggunaan)
        REFERENCES penggunaan (id_penggunaan) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_tagihan_pelanggan FOREIGN KEY (id_pelanggan)
        REFERENCES pelanggan (id_pelanggan) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS pembayaran (
    id_pembayaran      INT UNSIGNED NOT NULL AUTO_INCREMENT,
    id_tagihan         INT UNSIGNED NOT NULL,
    id_pelanggan       INT UNSIGNED NOT NULL,
    tanggal_pembayaran DATE NOT NULL,
    bulan_bayar        TINYINT NOT NULL,
    biaya_admin        DECIMAL(12,2) NOT NULL DEFAULT 2500.00,
    total_bayar        DECIMAL(12,2) NOT NULL,
    id_user            INT UNSIGNED NOT NULL,  -- petugas/admin yang melayani
    PRIMARY KEY (id_pembayaran),
    CONSTRAINT fk_bayar_tagihan FOREIGN KEY (id_tagihan)
        REFERENCES tagihan (id_tagihan) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_bayar_pelanggan FOREIGN KEY (id_pelanggan)
        REFERENCES pelanggan (id_pelanggan) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_bayar_user FOREIGN KEY (id_user)
        REFERENCES user (id_user) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

-- VIEW: informasi penggunaan listrik (join penggunaan+pelanggan+tarif) --
CREATE OR REPLACE VIEW v_info_penggunaan AS
SELECT pg.id_penggunaan,
       p.nomor_kwh,
       p.nama_pelanggan,
       t.daya,
       t.tarifperkwh,
       pg.bulan,
       pg.tahun,
       pg.meter_awal,
       pg.meter_ahir,
       (pg.meter_ahir - pg.meter_awal) AS jumlah_pemakaian_kwh,
       (pg.meter_ahir - pg.meter_awal) * t.tarifperkwh AS perkiraan_tagihan
FROM penggunaan pg
JOIN pelanggan p ON p.id_pelanggan = pg.id_pelanggan
JOIN tarif t     ON t.id_tarif = p.id_tarif;

-- STORED PROCEDURE: menampilkan pelanggan yang menggunakan daya 900 --
DROP PROCEDURE IF EXISTS sp_pelanggan_daya_900;
DELIMITER $$
CREATE PROCEDURE sp_pelanggan_daya_900()
BEGIN
    SELECT p.id_pelanggan, p.nomor_kwh, p.nama_pelanggan, p.alamat, t.daya
    FROM pelanggan p
    JOIN tarif t ON t.id_tarif = p.id_tarif
    WHERE t.daya = 900;
END$$
DELIMITER ;

-- FUNCTION: menghitung total penggunaan listrik (kWh) per bulan --
DROP FUNCTION IF EXISTS fn_total_penggunaan_per_bulan;
DELIMITER $$
CREATE FUNCTION fn_total_penggunaan_per_bulan(p_bulan TINYINT, p_tahun SMALLINT)
RETURNS INT
READS SQL DATA
BEGIN
    DECLARE total INT;
    SELECT COALESCE(SUM(meter_ahir - meter_awal), 0) INTO total
    FROM penggunaan
    WHERE bulan = p_bulan AND tahun = p_tahun;
    RETURN total;
END$$
DELIMITER ;

-- TRIGGER: setelah insert data penggunaan, simpan data tagihan --
DROP TRIGGER IF EXISTS tr_tagihan_after_insert_penggunaan;
DELIMITER $$
CREATE TRIGGER tr_tagihan_after_insert_penggunaan
AFTER INSERT ON penggunaan
FOR EACH ROW
BEGIN
    INSERT INTO tagihan (id_penggunaan, id_pelanggan, bulan, tahun, jumlah_meter, status)
    VALUES (NEW.id_penggunaan, NEW.id_pelanggan, NEW.bulan, NEW.tahun,
            NEW.meter_ahir - NEW.meter_awal, 'BELUM BAYAR');
END$$
DELIMITER ;

-- TRIGGER: setelah update data penggunaan, selaraskan jumlah_meter tagihan
-- (menjaga konsistensi bila petugas mengoreksi angka meter) --
DROP TRIGGER IF EXISTS tr_tagihan_after_update_penggunaan;
DELIMITER $$
CREATE TRIGGER tr_tagihan_after_update_penggunaan
AFTER UPDATE ON penggunaan
FOR EACH ROW
BEGIN
    UPDATE tagihan
    SET jumlah_meter = NEW.meter_ahir - NEW.meter_awal
    WHERE id_penggunaan = NEW.id_penggunaan;
END$$
DELIMITER ;
