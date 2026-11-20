-- =====================================================================
-- setup_database.sql - dijalankan SEKALI oleh DBA (root) di laptop.
-- Membuat database aplikasi dan user aplikasi khusus (least privilege:
-- user ini HANYA berhak atas database listrik_pascabayar, bukan server).
--
-- Cara menjalankan (PowerShell):
--   cmd /c '"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -uroot -p < D:\Code\Python\listrik-pascabayar\sql\setup_database.sql'
-- (mysql akan meminta password root secara interaktif)
-- =====================================================================
CREATE DATABASE IF NOT EXISTS listrik_pascabayar
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'app_listrik'@'localhost'
  IDENTIFIED BY 'listrik_app_2026';
CREATE USER IF NOT EXISTS 'app_listrik'@'127.0.0.1'
  IDENTIFIED BY 'listrik_app_2026';

-- Hak penuh HANYA di database aplikasi (perlu untuk membuat tabel,
-- view, stored procedure, function, dan trigger saat init-db).
GRANT ALL PRIVILEGES ON listrik_pascabayar.* TO 'app_listrik'@'localhost';
GRANT ALL PRIVILEGES ON listrik_pascabayar.* TO 'app_listrik'@'127.0.0.1';
FLUSH PRIVILEGES;

-- Binary logging aktif di server ini: tanpa baris berikut, user
-- non-SUPER dilarang membuat TRIGGER (error 1419). Saklar resmi MySQL
-- agar user tepercaya boleh membuat function/trigger; SET PERSIST
-- membuatnya tetap berlaku setelah MySQL restart.
SET PERSIST log_bin_trust_function_creators = 1;
