"""Script profiling sebelum/sesudah index — Unit Profiling Program.

Membuat tabel uji penggunaan_pf berisi 50.000 baris, lalu mengukur
query agregat per periode SEBELUM dan SESUDAH index dibuat.
Metode: EXPLAIN (type & rows) + rata-rata waktu 5x eksekusi.
Jalankan: python -m scripts.profiling_before_after
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db import get_connection  # noqa: E402

QUERY = ("SELECT COUNT(*), SUM(meter_ahir - meter_awal) FROM penggunaan_pf "
         "WHERE bulan = 10 AND tahun = 2026")


def ukur(cur, label):
    cur.execute("EXPLAIN " + QUERY)
    ex = cur.fetchone()
    waktu = []
    for _ in range(5):
        t0 = time.perf_counter()
        cur.execute(QUERY)
        cur.fetchone()
        waktu.append(time.perf_counter() - t0)
    rata = sum(waktu) / len(waktu)
    print(f"{label}: EXPLAIN type={ex[4]} rows={ex[9]} key={ex[6]} | "
          f"rata-rata {rata:.6f} detik")
    return rata


def main():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS penggunaan_pf")
    cur.execute(
        "CREATE TABLE penggunaan_pf ("
        "id INT UNSIGNED NOT NULL AUTO_INCREMENT, "
        "id_pelanggan INT NOT NULL, bulan TINYINT NOT NULL, tahun SMALLINT NOT NULL, "
        "meter_awal INT NOT NULL, meter_ahir INT NOT NULL, PRIMARY KEY (id)) ENGINE=InnoDB")
    print("Mengisi 50.000 baris data uji...")
    baris = [(1 + (i % 4), 1 + (i % 12), 2026, i * 10, i * 10 + (i % 300))
             for i in range(50000)]
    cur.executemany(
        "INSERT INTO penggunaan_pf (id_pelanggan, bulan, tahun, meter_awal, meter_ahir) "
        "VALUES (%s, %s, %s, %s, %s)", baris)
    conn.commit()
    sebelum = ukur(cur, "SEBELUM index")
    cur.execute("CREATE INDEX idx_pf_periode ON penggunaan_pf (bulan, tahun)")
    conn.commit()
    sesudah = ukur(cur, "SESUDAH index")
    if sesudah > 0:
        print(f"Peningkatan kecepatan: {(1 - sesudah / sebelum) * 100:.1f}%")
    cur.execute("DROP TABLE penggunaan_pf")
    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
