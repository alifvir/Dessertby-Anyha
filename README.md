# Dessert by Anyha - situs resmi

Situs produksi satu arah (Kebun Buah) untuk `@dessertbyanyha`: dessert cup mangga,
fruit punch botolan, dan asinan kiamboy, Simpang IV Sipin, Jambi.

Arah 04 dipilih pemilik dari empat mockup yang ditawarkan. Mockup empat arah tetap
tersimpan di folder `../web/` sebagai pembanding, dan tidak ikut dirilis ke sini.

Empat halaman: beranda, menu, tentang, cara pesan. Plus `404.html`.

## Perintah

```
pip install -r requirements.txt
python build.py
python tools/audit.py          # harus berakhir: masalah: 0
python tools/serve.py 8125     # pratinjau http://127.0.0.1:8125
```

Pratinjau wajib lewat server, bukan `file://`, karena semua path aset absolut.
Hentikan server sebelum `python build.py`: Windows tidak mengizinkan `dist/`
dihapus saat sedang dipakai.

### Aturan jendela (Windows)

`python.exe` membuat jendela konsol baru. Untuk proses lama, pakai:

```powershell
Start-Process pythonw.exe -ArgumentList "tools\serve.py 8125" `
  -WorkingDirectory "D:\Alif\Project\UMKM\dessertbyanyha\situs" -WindowStyle Hidden `
  -RedirectStandardOutput "pratinjau.log" -RedirectStandardError "pratinjau.err.log"
```

Matikan lewat PID, jangan biarkan port terpakai.

## Struktur

```
build.py              generator 5 halaman + potong gambar + favicon + OG
data/site.json        identitas, WhatsApp, Instagram, alamat, jam buka, url
data/menu.json        tiga produk, isi, dan alt foto
assets/css/situs.css  seluruh gaya situs
assets/js/site.js     menu mobile dan lightbox foto
assets-src/           foto asli kiriman pemilik
tools/audit.py        pemeriksaan hasil build
tools/serve.py        pratinjau lokal dengan 404 kustom
dist/                 hasil build, diabaikan git
```

## Cara mengubah isi

- Produk, isi, dan alt foto: `data/menu.json`, lalu build.
- Nomor WhatsApp, jam buka, alamat, peta: `data/site.json`. Semua tombol pesan
  ikut pindah tanpa menyentuh `build.py`.
- Teks halaman: `build.py`, fungsi `halaman_beranda`, `isi_menu`, `isi_tentang`,
  `isi_kontak`.
- Foto: ganti berkas di `assets-src/` dengan nama yang sama, lalu build.
  `build.py` menyisipkan hash isi ke nama berkas hasil (mis.
  `fruit-punch-6f54eddb.webp`), jadi URL gambar berubah tiap foto diganti dan
  pengunjung tidak perlu membersihkan cache. `_headers` memberi gambar cache
  satu tahun `immutable` — jangan kembalikan ke nama tetap tanpa mengubah itu.
  `mango-sago-sunlit.jpeg` membawa watermark generator AI di sudut bawah, dan
  `build.py` memotong 9 persen bagian bawah sebelum dipotong ke rasio.

## Hasil uji

- Build bersih: 5 halaman, 20 berkas, sekitar 326 KB.
- `tools/audit.py`: 0 masalah.
- 15 kombinasi halaman dan lebar layar: nol overflow horizontal, satu `h1` per
  halaman, semua gambar termuat setelah scroll.
- Rute: `/`, `/menu/`, `/tentang/`, `/kontak/`, `/sitemap.xml`, `/robots.txt`
  semua 200. `/404` dan path ngawur memakai halaman 404 sendiri.

## Deploy

Live: https://dessertby-anyha.pages.dev

Repo: `alifvir/Dessertby-Anyha`, proyek Pages `Dessertby-Anyha`, terhubung lewat
Connect to Git. `git push` ke `main` = rilis otomatis.

Build command: `pip install -r requirements.txt && python build.py`
Build output directory: `dist`

Langkah lengkap, kredensial, dan jebakan yang sudah kena ada di `DEPLOY.md`.

## Yang masih menunggu pemilik

1. Metode pembayaran dan ketentuan DP.
2. Foto tanpa watermark untuk hero.
