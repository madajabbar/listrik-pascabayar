"""Modul web — Aplikasi Pembayaran Listrik Pascabayar (Flask).

Identitas modul : web/app.py
Tujuan          : antarmuka web client-server aplikasi. Login membedakan
                  privilege Administrator dan Pelanggan: admin mengelola
                  penggunaan dan pembayaran, pelanggan hanya melihat
                  penggunaan dan tagihannya sendiri.
Cara menjalankan: python -m web.app  lalu buka http://localhost:5000
Riwayat revisi  : 2026-11-19 versi awal; 2026-11-19 tambah ubah/hapus
                  penggunaan (CRUD lengkap) hasil code review.
"""
import os
import sys
from functools import wraps

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import (Flask, flash, redirect, render_template, request,
                   session, url_for)

from src import service
from src.algorithms import binary_search, bubble_sort
from src.config import FLASK_SECRET
from src.db import get_connection, ping

app = Flask(__name__)
app.secret_key = FLASK_SECRET


def butuh_login(f):
    @wraps(f)
    def pembungkus(*a, **kw):
        if "sesi" not in session:
            return redirect(url_for("login"))
        return f(*a, **kw)
    return pembungkus


def butuh_admin(f):
    @wraps(f)
    def pembungkus(*a, **kw):
        if session.get("sesi", {}).get("peran") != "Administrator":
            flash("Halaman ini khusus Administrator.", "error")
            return redirect(url_for("dashboard"))
        return f(*a, **kw)
    return pembungkus


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        conn = get_connection()
        sesi = service.login(conn, request.form["username"], request.form["password"])
        conn.close()
        if sesi:
            session["sesi"] = sesi
            return redirect(url_for("dashboard"))
        flash("Username atau password salah.", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
@butuh_login
def dashboard():
    sesi = session["sesi"]
    conn = get_connection()
    penggunaan = service.daftar_penggunaan(conn, sesi["id_pelanggan"])
    tagihan = service.daftar_tagihan(conn, sesi["id_pelanggan"])
    conn.close()
    belum = [t for t in tagihan if t["status"] != "LUNAS"]
    return render_template("dashboard.html", sesi=sesi, db_ok=ping(),
                           jml_penggunaan=len(penggunaan),
                           jml_tagihan=len(tagihan), jml_belum=len(belum))


@app.route("/penggunaan")
@butuh_login
def penggunaan():
    sesi = session["sesi"]
    conn = get_connection()
    data = service.daftar_penggunaan(conn, sesi["id_pelanggan"])
    pelanggan = service.daftar_pelanggan(conn) if sesi["peran"] == "Administrator" else []
    conn.close()
    return render_template("penggunaan.html", sesi=sesi, data=data, pelanggan=pelanggan)


@app.route("/penggunaan/baru", methods=["POST"])
@butuh_admin
def penggunaan_baru():
    f = request.form
    conn = get_connection()
    try:
        service.tambah_penggunaan(conn, int(f["id_pelanggan"]), int(f["bulan"]),
                                  int(f["tahun"]), int(f["meter_awal"]), int(f["meter_ahir"]))
        flash("Penggunaan tersimpan; tagihan dibuat otomatis oleh trigger.", "ok")
    except Exception as e:
        flash(f"Gagal: {e}", "error")
    conn.close()
    return redirect(url_for("penggunaan"))


@app.route("/penggunaan/<int:id_penggunaan>/ubah", methods=["POST"])
@butuh_admin
def penggunaan_ubah(id_penggunaan):
    f = request.form
    conn = get_connection()
    try:
        service.ubah_penggunaan(conn, id_penggunaan, int(f["meter_awal"]), int(f["meter_ahir"]))
        flash("Penggunaan diubah; jumlah tagihan diselaraskan oleh trigger.", "ok")
    except Exception as e:
        flash(f"Gagal: {e}", "error")
    conn.close()
    return redirect(url_for("penggunaan"))


@app.route("/penggunaan/<int:id_penggunaan>/hapus", methods=["POST"])
@butuh_admin
def penggunaan_hapus(id_penggunaan):
    conn = get_connection()
    try:
        service.hapus_penggunaan(conn, id_penggunaan)
        flash("Penggunaan beserta tagihannya dihapus.", "ok")
    except Exception as e:
        flash(f"Gagal: {e}", "error")
    conn.close()
    return redirect(url_for("penggunaan"))


@app.route("/tagihan")
@butuh_login
def tagihan():
    sesi = session["sesi"]
    conn = get_connection()
    data = service.daftar_tagihan(conn, sesi["id_pelanggan"])
    conn.close()
    return render_template("tagihan.html", sesi=sesi, data=data)


@app.route("/tagihan/<int:id_tagihan>/bayar", methods=["POST"])
@butuh_admin
def tagihan_bayar(id_tagihan):
    from datetime import date
    hari_ini = date.today()
    conn = get_connection()
    try:
        total = service.bayar_tagihan(conn, id_tagihan, session["sesi"]["id_user"],
                                      hari_ini.isoformat(), hari_ini.month)
        flash(f"Tagihan {id_tagihan} LUNAS. Total dibayar Rp{total}.", "ok")
    except Exception as e:
        flash(f"Gagal: {e}", "error")
    conn.close()
    return redirect(url_for("tagihan"))


@app.route("/pelanggan")
@butuh_admin
def pelanggan():
    conn = get_connection()
    semua = service.daftar_pelanggan(conn)
    sembilan = service.pelanggan_daya_900(conn)
    conn.close()
    return render_template("pelanggan.html", sesi=session["sesi"],
                           semua=semua, sembilan=sembilan)


@app.route("/algoritma", methods=["GET", "POST"])
@butuh_login
def algoritma():
    hasil = None
    if request.method == "POST":
        angka = [int(x) for x in request.form["angka"].replace(";", ",").split(",") if x.strip()]
        terurut = bubble_sort(angka)
        dicari = request.form.get("dicari")
        temuan = None
        if dicari not in (None, ""):
            temuan = "Angka ditemukan" if binary_search(terurut, int(dicari)) >= 0 else "Angka tidak ditemukan"
        hasil = {"asal": angka, "terurut": terurut, "temuan": temuan}
    return render_template("algoritma.html", sesi=session["sesi"], hasil=hasil)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
