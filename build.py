"""Build situs Dessert by Anyha, satu arah (Kebun Buah).

Sumber:
  data/site.json    identitas, tautan WhatsApp dan Instagram, alamat, jam buka
  data/menu.json    tiga produk, harga, dan rincian isian dari pemilik
  assets-src/*.jpeg foto dari pemilik akun
  assets/css/situs.css
  assets/js/site.js menu mobile dan lightbox foto

Halaman: beranda, menu, tentang, cara pesan, plus 404.
Hasil: dist/ siap dipasang di Cloudflare Pages.

Jalankan: python build.py
"""

import json
import os
import shutil
from html import escape
from urllib.parse import quote

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "assets-src")
DIST = os.path.join(ROOT, "dist")
IMG = os.path.join(DIST, "assets", "img")

SITE = json.load(open(os.path.join(ROOT, "data", "site.json"), encoding="utf-8-sig"))
MENU = json.load(open(os.path.join(ROOT, "data", "menu.json"), encoding="utf-8-sig"))

NAMA = SITE["nama"]
USAHA = SITE.get("nama_usaha") or SITE["nama"]

FONTS = "family=Plus+Jakarta+Sans:wght@400;500;700;800"

DESKRIPSI = {
    "beranda": "Mango Sago, Fruit Punch, dan Asinan Kiamboy buatan rumahan dari Dessert by Anyha di Simpang IV Sipin, Jambi. Lihat harga dan isiannya, lalu pesan lewat WhatsApp +62 852-1084-1113. Buka 09.00 sampai 17.00.",
    "menu": "Menu Dessert by Anyha: Mango Sago Rp12.000, Fruit Punch Rp12.000, Asinan Kiamboy Rp15.000, lengkap dengan isiannya. Pesan lewat WhatsApp +62 852-1084-1113.",
    "tentang": "Cerita Dessert by Anyha, dessert dan minuman rumahan di Simpang IV Sipin, Jambi, yang diracik per pesanan. Buka 09.00 sampai 17.00.",
    "kontak": "Cara pesan Dessert by Anyha lewat WhatsApp +62 852-1084-1113, jam buka 09.00 sampai 17.00, plus peta lokasi di Simpang IV Sipin, Jambi City.",
}

IKON_IG = (
    '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true" focusable="false">'
    '<rect x="2.5" y="2.5" width="19" height="19" rx="5.5" fill="none" stroke="currentColor" stroke-width="1.7"/>'
    '<circle cx="12" cy="12" r="4.4" fill="none" stroke="currentColor" stroke-width="1.7"/>'
    '<circle cx="17.6" cy="6.6" r="1.2" fill="currentColor"/></svg>'
)

IKON_WA = (
    '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true" focusable="false">'
    '<path fill="currentColor" d="M12.04 2A9.9 9.9 0 0 0 2.1 11.9c0 1.75.46 3.45 1.32 4.95L2 22l5.3-1.38a9.9 9.9 0 0 0 4.74 1.2h.01A9.9 9.9 0 0 0 22 11.9 9.9 9.9 0 0 0 12.04 2Zm0 18.15h-.01a8.2 8.2 0 0 1-4.18-1.14l-.3-.18-3.11.81.83-3.03-.19-.31a8.2 8.2 0 0 1-1.26-4.4 8.23 8.23 0 0 1 8.23-8.21 8.2 8.2 0 0 1 5.82 2.41 8.18 8.18 0 0 1 2.4 5.82 8.23 8.23 0 0 1-8.23 8.23Zm4.52-6.16c-.25-.12-1.47-.72-1.7-.81-.23-.08-.39-.12-.56.13-.16.24-.64.8-.78.97-.15.16-.29.18-.54.06-.25-.12-1.05-.39-2-1.23-.74-.66-1.24-1.47-1.38-1.72-.15-.25-.02-.38.11-.5.11-.11.25-.29.37-.43.12-.15.16-.25.25-.41.08-.17.04-.31-.02-.43-.06-.12-.56-1.34-.76-1.84-.2-.48-.4-.42-.56-.43h-.48c-.16 0-.43.06-.65.31-.23.25-.86.84-.86 2.05s.88 2.38 1 2.54c.12.17 1.73 2.64 4.19 3.7.59.25 1.04.4 1.4.51.59.19 1.12.16 1.55.1.47-.07 1.47-.6 1.67-1.18.21-.58.21-1.08.15-1.18-.06-.11-.23-.17-.48-.29Z"/>'
    '</svg>'
)

IKON_ZOOM = (
    '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" focusable="false">'
    '<circle cx="10.5" cy="10.5" r="6.5" fill="none" stroke="currentColor" stroke-width="1.8"/>'
    '<path d="M15.4 15.4l4.1 4.1M10.5 8v5M8 10.5h5" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>'
)


def tautan_pesan(produk=None):
    dasar = SITE.get("wa") or SITE["wa_cadangan"]
    pesan = SITE["wa_pesan"] if not produk else "Halo Dessert by Anyha, saya mau pesan %s." % produk
    if dasar.startswith("https://wa.me/"):
        return dasar + "?text=" + quote(pesan)
    return dasar


def nomor_wa():
    return SITE.get("wa_tampil", "")


def jam_buka():
    return SITE.get("jam_buka_hari") or SITE.get("jam_buka", "")


def peta_semat():
    """Peta Google yang bisa digeser tanpa membuka tab baru."""
    src = SITE.get("peta_semat")
    if not src:
        return ""
    return (
        '<div class="peta">'
        '<iframe src="%s" title="Peta lokasi %s" loading="lazy" '
        'referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe>'
        '</div>' % (escape(src), escape(SITE.get("alamat", "")))
    )


def tombol_maps(kelas="tombol tombol--garis"):
    maps = SITE.get("maps")
    if not maps:
        return ""
    return ('<a class="%s" href="%s" target="_blank" rel="noopener">Buka di Google Maps</a>'
            % (kelas, escape(maps)))


def pesan(kelas, teks, produk=None, ikon=False):
    isi = ("%s " % (IKON_WA if SITE.get("wa") else IKON_IG)) if ikon else ""
    return '<a class="%s" href="%s" target="_blank" rel="noopener">%s%s</a>' % (
        kelas, escape(tautan_pesan(produk)), isi, teks)


# ------------------------------------------------------------------ produk
_PETA_FOTO = {"mango-sago": "cup", "fruit-punch": "punch", "asinan-kiamboy": "asinan"}


def kunci_foto(p):
    return "foto_%s" % _PETA_FOTO[p["slug"]]


def rincian(p, kelas="rincian"):
    """Blok rincian isian. Tiap kelompok jadi satu kolom berjudul."""
    kolom = []
    for k in p.get("kelompok", []):
        butir = "".join("<li>%s</li>" % escape(t) for t in k["isi"])
        kolom.append(f'<div class="{kelas}__kolom"><p class="{kelas}__judul">{escape(k["judul"])}</p>'
                     f'<ul class="{kelas}__daftar">{butir}</ul></div>')
    if not kolom:
        return ""
    catatan = ""
    if p.get("catatan"):
        catatan = '<p class="%s__catatan">%s</p>' % (kelas, escape(p["catatan"]))
    return '<div class="%s">%s</div>%s' % (kelas, "".join(kolom), catatan)


# ------------------------------------------------------------------ gambar
def webp(im, nama, mutu=84):
    im.save(os.path.join(IMG, nama), "WEBP", quality=mutu, method=6)
    return {"berkas": "assets/img/" + nama, "w": im.width, "h": im.height}


def sumber(nama):
    return Image.open(os.path.join(SRC, nama)).convert("RGB")


_WATERMARK = (0.795, 0.912, 0.947, 0.982)
_WATERMARK_GESER = 0.074


def sumber_bersih(nama):
    """Foto kiriman pemilik: dua foto botol membawa tulisan "Dola AI" di sudut
    kanan bawah. Tulisan ditutup tambalan dari area bersih di atasnya, tepinya
    dilembutkan supaya batas tambalan tidak terlihat."""
    im = sumber(nama)
    w, h = im.size
    kiri, atas, kanan, bawah = (
        int(round(_WATERMARK[0] * w)), int(round(_WATERMARK[1] * h)),
        int(round(_WATERMARK[2] * w)), int(round(_WATERMARK[3] * h)),
    )
    geser = int(round(_WATERMARK_GESER * h))
    lebar, tinggi = kanan - kiri, bawah - atas
    bulu = max(6, tinggi // 10)

    tambalan = im.crop((kiri, atas + geser, kanan, bawah + geser))
    mask = Image.new("L", (lebar, tinggi), 0)
    ImageDraw.Draw(mask).rectangle(
        (bulu, bulu, lebar - bulu, tinggi - bulu), fill=255)
    im.paste(tambalan, (kiri, atas), mask.filter(ImageFilter.GaussianBlur(bulu)))
    return im


def logo_transparan(nama, sisi, tinta, mutu=92, margin=0.08):
    """Logo kiriman pemilik: JPEG bergaris hitam di atas kertas putih, tersimpan
    miring 90 derajat. Kertasnya dibuang jadi transparan dan tinta diwarnai
    ulang sesuai latar, jadi logo menyatu dengan halaman."""
    im = sumber(nama).convert("L").rotate(-90, expand=True)

    kotak = im.point(lambda v: 255 if v < 245 else 0).getbbox()
    if kotak:
        tepi = 8
        im = im.crop((
            max(0, kotak[0] - tepi), max(0, kotak[1] - tepi),
            min(im.width, kotak[2] + tepi), min(im.height, kotak[3] + tepi),
        ))

    alfa = im.point(lambda v: 0 if v >= 246 else min(255, (246 - v) * 255 // 210))
    tinta_im = Image.new("RGBA", im.size, tuple(tinta) + (255,))
    tinta_im.putalpha(alfa)

    kanvas_sisi = int(round(max(im.width, im.height) * (1 + 2 * margin)))
    kanvas = Image.new("RGBA", (kanvas_sisi, kanvas_sisi), (0, 0, 0, 0))
    kanvas.paste(tinta_im, ((kanvas_sisi - im.width) // 2, (kanvas_sisi - im.height) // 2))
    return kanvas.resize((sisi, sisi), Image.LANCZOS)


def bidik(im, kotak, ukuran):
    """Potong ke kotak pilihan, lalu kecilkan ke ukuran akhir. Angka kotaknya
    dipilih supaya judul poster dan doodle pinggir tidak ikut masuk."""
    return im.crop(kotak).resize(ukuran, Image.LANCZOS)


def siapkan_gambar():
    if os.path.isdir(IMG):
        shutil.rmtree(IMG)
    os.makedirs(IMG, exist_ok=True)
    hasil = {}

    sago_jars = sumber("mango-sago-jars.jpeg")
    asinan_cups = sumber("asinan-cups.jpeg")
    asinan_bowl = sumber("asinan-bowl.jpeg")
    punch_bottle = sumber_bersih("fruit-punch-bottle.jpeg")
    punch_bottles = sumber_bersih("fruit-punch-bottles.jpeg")

    hasil["logo"] = webp(logo_transparan("logo-anyha.jpeg", 560, (18, 63, 42)), "logo.webp")
    hasil["hero"] = webp(bidik(sago_jars, (151, 120, 1484, 1120), (1100, 825)), "hero.webp")
    hasil["foto_cup"] = webp(bidik(sago_jars, (300, 380, 1100, 980), (720, 540)), "mango-sago.webp")
    hasil["foto_punch"] = webp(bidik(punch_bottles, (0, 340, 1200, 1240), (720, 540)), "fruit-punch.webp")
    hasil["foto_asinan"] = webp(bidik(asinan_cups, (300, 440, 1020, 980), (720, 540)), "asinan-kiamboy.webp")
    hasil["cerita"] = webp(bidik(asinan_bowl, (100, 400, 1100, 1400), (820, 820)), "cerita.webp")
    hasil["proses"] = webp(bidik(punch_bottle, (100, 230, 1100, 1230), (820, 820)), "proses.webp")

    og = bidik(sago_jars, (200, 150, 1400, 780), (1200, 630))
    og.save(os.path.join(IMG, "og.jpg"), "JPEG", quality=84, optimize=True, progressive=True)
    hasil["og"] = {"berkas": "assets/img/og.jpg", "w": 1200, "h": 630}

    ikon = Image.new("RGB", (128, 128), (251, 247, 238))
    g = ImageDraw.Draw(ikon)
    try:
        font = ImageFont.truetype("georgiab.ttf", 86)
    except OSError:
        try:
            font = ImageFont.truetype("arialbd.ttf", 84)
        except OSError:
            font = ImageFont.load_default()
    kotak = g.textbbox((0, 0), "A", font=font)
    g.text(((128 - (kotak[2] - kotak[0])) / 2 - kotak[0],
            (128 - (kotak[3] - kotak[1])) / 2 - kotak[1]),
           "A", font=font, fill=(18, 63, 42))
    ikon.save(os.path.join(DIST, "assets", "favicon.png"), "PNG")

    return hasil


def gambar(d, alt, prioritas=False):
    muat = 'fetchpriority="high" decoding="async" ' if prioritas else 'loading="lazy" decoding="async" '
    return '<img src="/%s" alt="%s" width="%d" height="%d" %s>' % (
        d["berkas"], escape(alt), d["w"], d["h"], muat)


# ------------------------------------------------------------------ kepala dan kaki
def kepala(judul, deskripsi, kanonikal, prioritas=None):
    kanon = og_url = ""
    if SITE.get("url"):
        kanon = '<link rel="canonical" href="%s%s">' % (SITE["url"], kanonikal)
        og_url = '<meta property="og:url" content="%s%s">' % (SITE["url"], kanonikal)
    pra = ('<link rel="preload" as="image" href="/%s" fetchpriority="high">\n' % prioritas) if prioritas else ""
    return f"""<!doctype html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#FBF7EE">
<title>{escape(judul)}</title>
<meta name="description" content="{escape(deskripsi)}">
{kanon}
<meta property="og:type" content="website">
<meta property="og:locale" content="id_ID">
<meta property="og:site_name" content="{escape(NAMA)}">
<meta property="og:title" content="{escape(judul)}">
<meta property="og:description" content="{escape(deskripsi)}">
<meta property="og:image" content="/assets/img/og.jpg">
<meta property="og:image:type" content="image/jpeg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
{og_url}
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" href="/assets/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{FONTS}&display=swap">
<link rel="stylesheet" href="/assets/css/situs.css">
{pra}</head>
<body>
<a class="lewati" href="#utama">Lewati ke isi utama</a>
"""


def tutup(melayang=True):
    tombol = ""
    if melayang:
        tombol = ('<a class="wa-melayang" href="%s" target="_blank" rel="noopener" '
                  'aria-label="Pesan lewat WhatsApp %s">%s</a>\n'
                  % (escape(tautan_pesan()), escape(USAHA), IKON_WA if SITE.get("wa") else IKON_IG))
    return f"""
{tombol}<script src="/assets/js/site.js" defer></script>
</body>
</html>
"""


_CACHE_LOGO_KAKI = {}


def kaki():
    if "logo" not in _CACHE_LOGO_KAKI:
        _CACHE_LOGO_KAKI["logo"] = webp(logo_transparan("logo-anyha.jpeg", 420, (203, 218, 208)), "kaki-logo.webp")
    logo = _CACHE_LOGO_KAKI["logo"]
    return f"""
<footer class="kaki">
  <div class="wrap kaki__grid">
    <div>
      <a class="kaki__merek" href="/">
        <img src="/{logo['berkas']}" alt="Logo Fruit Punch by Anyha" width="{logo['w']}" height="{logo['h']}" loading="lazy" decoding="async">
      </a>
      <strong>{escape(NAMA)}</strong>
      <p>Dessert dan minuman buah rumahan di {escape(SITE.get('alamat', 'Jambi'))}. Buka {escape(jam_buka())}.</p>
    </div>
    <div>
      <ul>
        <li><a href="/menu/">Menu</a></li>
        <li><a href="/tentang/">Tentang</a></li>
        <li><a href="/kontak/">Cara pesan</a></li>
        <li><a href="{escape(tautan_pesan())}" target="_blank" rel="noopener">WhatsApp {escape(nomor_wa())}</a></li>
        <li><a href="{escape(SITE['instagram'])}" target="_blank" rel="noopener">Instagram {escape(SITE['handle'])}</a></li>
        <li><a href="{escape(SITE.get('maps', SITE['instagram']))}" target="_blank" rel="noopener">{escape(SITE.get('alamat', 'Lokasi'))}</a></li>
        <li>Buka {escape(jam_buka())}</li>
      </ul>
    </div>
  </div>
  <div class="wrap kaki__bawah">
    <span>&copy; 2026 {escape(USAHA)}.</span>
    <span>Dessert dan minuman buah rumahan, Jambi.</span>
  </div>
</footer>"""


def nav(aktif):
    def item(kunci, href, teks):
        tanda = ' aria-current="page"' if aktif == kunci else ""
        return '<li><a href="%s"%s>%s</a></li>' % (href, tanda, teks)
    return f"""
<header class="kepala">
  <div class="wrap kepala__bar">
    <a class="merek" href="/"><strong>{escape(NAMA)}</strong><span>Dessert &amp; minuman buah</span></a>
    <button class="menu-tombol" type="button" data-nav-tombol aria-expanded="false" aria-controls="nav-utama">
      <span class="menu-tombol__garis" aria-hidden="true"></span>Menu
    </button>
    <nav class="nav" id="nav-utama" data-nav data-terbuka="false" aria-label="Navigasi utama">
      <ul>
        {item("menu", "/menu/", "Menu")}
        {item("tentang", "/tentang/", "Tentang")}
        {item("kontak", "/kontak/", "Pesan")}
        <li>{pesan("nav__cta", "Pesan Sekarang")}</li>
      </ul>
    </nav>
  </div>
</header>"""


def kepala_dalam(label, h1, intro):
    return f"""
<section class="d-kepala">
  <div class="wrap">
    <p class="eyebrow">{escape(label)}</p>
    <h1>{escape(h1)}</h1>
    <p class="d-intro">{escape(intro)}</p>
  </div>
</section>"""


# ------------------------------------------------------------------ isi halaman
def kartu(p, g):
    kunci = kunci_foto(p)
    unggulan = ' produk--favorit' if p["slug"] == "mango-sago" else ""
    label = '<span class="produk__label">Favorit</span>' if unggulan else ""
    return f"""
      <article class="produk{unggulan}">
        <div class="produk__foto">
          {label}
          {gambar(g[kunci], p['foto_alt'])}
          <button class="tombol-zoom" type="button" data-zoom="/{g[kunci]['berkas']}" data-zoom-alt="{escape(p['foto_alt'])}" aria-label="Perbesar foto {escape(p['nama'])}">{IKON_ZOOM}</button>
        </div>
        <div class="produk__isi">
          <p class="produk__kategori">{escape(p['label'])}</p>
          <h3>{escape(p['nama'])}</h3>
          <p class="produk__harga">{escape(p['harga'])}</p>
          <p class="produk__ket">{escape(p['deskripsi'])}</p>
          {rincian(p, "rincian-4")}
          <div class="produk__kaki">
            {pesan("tombol", "Pesan " + p['nama'], p["nama"] + " seharga " + p["harga"])}
          </div>
        </div>
      </article>"""


def semua_kartu(g):
    return "".join(kartu(p, g) for p in MENU)


def langkah():
    daftar = [
        ("Pilih menunya", "Lihat tiga menu beserta harga dan isiannya, lalu tentukan jumlah."),
        ("Chat WhatsApp", "Sebut menu, jumlah, dan kapan mau diambil atau dikirim."),
        ("Konfirmasi", "Pemilik membalas total dan jadwal siap. Pesanan dirakit setelah itu."),
    ]
    return "".join(f"""
        <li>
          <span class="langkah__no">{i:02d}</span>
          <div>
            <h3>{escape(j)}</h3>
            <p>{escape(t)}</p>
          </div>
        </li>""" for i, (j, t) in enumerate(daftar, 1))


def blok_lokasi():
    alamat = SITE.get("alamat", "")
    return f"""
<section class="bagian bagian--krim2" id="lokasi">
  <div class="wrap">
    <div class="bagian__kepala bagian__kepala--kiri">
      <p class="eyebrow">Lokasi &amp; jam buka</p>
      <h2>Ambil di {escape(alamat)}.</h2>
      <p>Buka setiap hari, {escape(SITE.get('jam_buka', ''))}. Sebelum berangkat, chat dulu lewat WhatsApp {escape(nomor_wa())} supaya pesanan sudah siap.</p>
    </div>
    <div class="lokasi">
      <div class="lokasi__info">
        <ul class="d-fakta">
          <li><strong>Alamat</strong><span>{escape(alamat)}</span></li>
          <li><strong>Jam buka</strong><span>Setiap hari, {escape(SITE.get('jam_buka', ''))}</span></li>
          <li><strong>WhatsApp</strong><span>{escape(nomor_wa())}</span></li>
          <li><strong>Ambil atau kirim</strong><span>Bisa diambil langsung, atau dikirim dengan ongkir dari pemilik.</span></li>
        </ul>
        <div class="aksi">{tombol_maps()}{pesan("tombol", "Chat WhatsApp", ikon=True)}</div>
      </div>
      {peta_semat()}
    </div>
  </div>
</section>"""


def halaman_beranda(g):
    return kepala(
        "Dessert by Anyha, Mango Sago, Fruit Punch, dan Asinan Kiamboy",
        DESKRIPSI["beranda"], "/", g["hero"]["berkas"],
    ) + nav("beranda") + f"""
<main id="utama">
<section class="hero">
  <div class="wrap hero__grid">
    <div>
      <p class="eyebrow">Dessert rumahan, Jambi</p>
      <h1>Segarnya buah,<em>dirakit saat dipesan.</em></h1>
      <p class="hero__p">Mango Sago, Fruit Punch, dan Asinan Kiamboy. Semua diracik setelah pesanan masuk, jadi tidak ada yang menginap di kulkas. Pesan lewat WhatsApp, ambil di Simpang IV Sipin.</p>
      <div class="aksi">
        {pesan("tombol", "Pesan lewat WhatsApp", ikon=True)}
        <a class="tombol tombol--garis" href="#menu">Lihat menu</a>
      </div>
    </div>
    <figure class="hero__foto">
      {gambar(g["hero"], "Deretan cup Mango Sago berisi potongan mangga dengan sagu mutiara, di atas meja krem", prioritas=True)}
      <button class="tombol-zoom" type="button" data-zoom="/{g['hero']['berkas']}" data-zoom-alt="Deretan cup Mango Sago berisi potongan mangga" aria-label="Perbesar foto Mango Sago">{IKON_ZOOM}</button>
      <div class="stiker-grup">
        <figcaption class="stiker">
          <span class="stiker__ikon" aria-hidden="true">A</span>
          <span class="stiker__teks"><strong>Segar, asli, nikmat</strong><span>Bahan dipilih</span></span>
        </figcaption>
        <figcaption class="stiker stiker--kanan"><span class="stiker__teks"><strong>Dibuat saat dipesan</strong><span>Bukan stok kulkas</span></span></figcaption>
      </div>
    </figure>
  </div>
</section>

<div class="strip">
  <div class="wrap">
    <ul>
      <li>Mangga potong asli</li>
      <li>Sagu mutiara</li>
      <li>Buah segar</li>
      <li>Dirakit per pesanan</li>
    </ul>
  </div>
</div>

<section class="bagian" id="menu">
  <div class="wrap">
    <div class="bagian__kepala">
      <p class="eyebrow">Menu &amp; harga</p>
      <h2>Pilih yang paling kamu suka.</h2>
      <p>Harga per cup atau botol. Isian lengkap tiap menu ada di kartunya, supaya tidak perlu tanya dulu.</p>
    </div>
    <div class="produk-grid">{semua_kartu(g)}</div>
  </div>
</section>

<section class="bagian bagian--putih">
  <div class="wrap dua">
    <div>
      <p class="eyebrow">Tentang</p>
      <h2>Ketika buah segar bertemu kuah yang pas.</h2>
      <p>Dessert by Anyha mulai dari satu dessert cup mangga yang sering diminta ulang. Sekarang menunya bertambah fruit punch dan asinan kiamboy, dengan cara kerja yang sama: dirakit setelah pesanan masuk.</p>
      <p>Mangga dipotong hari itu, sagu dimasak sampai kenyal, dan kuah susu diracik dengan gula yang lebih ringan supaya rasa buahnya tetap terasa.</p>
      <div class="aksi">{pesan("tombol", "Chat WhatsApp", ikon=True)}</div>
    </div>
    <figure>
      {gambar(g["cerita"], "Empat cup Asinan Kiamboy berisi potongan buah, jeruk limau, dan kismis di atas kertas kraft")}
      <figcaption class="stiker stiker--kanan"><span class="stiker__teks"><strong>Asinan Kiamboy</strong><span>Segar, manis, pedas, asin, gurih</span></span></figcaption>
    </figure>
  </div>
</section>

<section class="bagian bagian--krim2">
  <div class="wrap">
    <div class="bagian__kepala">
      <p class="eyebrow">Kenapa Anyha</p>
      <h2>Bukan sekadar minuman buah.</h2>
    </div>
    <div class="unggul-grid">
      <div class="unggul">
        <span class="unggul__no" aria-hidden="true">01</span>
        <h3>Buah dipotong hari itu</h3>
        <p>Tidak ada buah yang disiapkan berhari-hari sebelumnya, karena itu rasanya masih segar saat sampai.</p>
      </div>
      <div class="unggul">
        <span class="unggul__no" aria-hidden="true">02</span>
        <h3>Gula lebih ringan</h3>
        <p>Kuah susu dan jus diracik dengan takaran gula yang tidak menutupi rasa buahnya.</p>
      </div>
      <div class="unggul">
        <span class="unggul__no" aria-hidden="true">03</span>
        <h3>Dirakit per pesanan</h3>
        <p>Pesanan disiapkan setelah chat masuk, jadi tidak ada stok menganggur di kulkas.</p>
      </div>
    </div>
  </div>
</section>

<section class="bagian bagian--putih">
  <div class="wrap dua--proses">
    <div>
      <p class="eyebrow">Cara pesan</p>
      <h2>Tiga langkah, lewat WhatsApp.</h2>
      <ol class="langkah" style="margin-top:1.75rem">{langkah()}</ol>
    </div>
    <figure>
      {gambar(g["proses"], "Botol Fruit Punch dengan irisan jeruk dan nanas di dalamnya, diapit es batu")}
    </figure>
  </div>
</section>
{blok_lokasi()}

<section class="cta">
  <div class="wrap cta__isi">
    <p class="eyebrow">Saatnya pesan</p>
    <h2>Segarnya bikin pesan lagi.</h2>
    <p>Sebut menu, jumlah, dan tanggal. Balasan berisi total dan jadwal siap.</p>
    <div class="aksi">{pesan("tombol tombol--putih", "Pesan lewat WhatsApp", ikon=True)}</div>
  </div>
</section>
</main>
""" + kaki() + tutup()


def halaman(aktif, judul, deskripsi, path, isi):
    return kepala(judul, deskripsi, path) + nav(aktif) + '<main id="utama">' + isi + "</main>" + kaki() + tutup()


def isi_menu(g):
    return kepala_dalam("Menu", "Tiga menu, harga jelas.", "Harga per cup atau botol. Isian lengkap di tiap kartu.") + f"""
<section class="bagian">
  <div class="wrap">
    <div class="produk-grid">{semua_kartu(g)}</div>
    <div class="d-catatan">
      <p><strong>Pesan lewat WhatsApp.</strong> Sebutkan menu, jumlah, dan tanggal ambil atau kirim.</p>
      {pesan("tombol", "Chat WhatsApp", ikon=True)}
    </div>
  </div>
</section>
<section class="bagian bagian--putih">
  <div class="wrap">
    <div class="bagian__kepala">
      <p class="eyebrow">Cara pesan</p>
      <h2>Tiga langkah.</h2>
    </div>
    <ol class="langkah">{langkah()}</ol>
  </div>
</section>"""


def isi_tentang(g):
    return kepala_dalam("Tentang", "Dibuat di rumah, dirakit saat dipesan.", "Dessert by Anyha mulai dari satu dessert cup mangga yang sering diminta ulang. Cara kerjanya tetap sama: dirakit setelah pesanan masuk.") + f"""
<section class="bagian">
  <div class="wrap dua">
    <div>
      <p class="eyebrow">Cara kerja</p>
      <h2>Tidak ada stok menganggur.</h2>
      <p>Mangga dipotong setelah pesanan masuk, lalu cup dirakit dan langsung disimpan dingin. Fruit punch diracik dari jus dan irisan buah, dan asinan kiamboy memakai kuah segar berasa manis, pedas, asin, dan gurih.</p>
      <p>Pesanan jumlah banyak sebaiknya masuk sehari sebelumnya, supaya semua bisa disiapkan tepat waktu.</p>
      <ul class="d-fakta">
        <li><strong>Bahan</strong><span>Mangga, sagu mutiara, nata de coco, jus jeruk, nanas, lemon, dan buah segar.</span></li>
        <li><strong>Kemasan</strong><span>Cup plastik bening dan botol, siap disantap langsung.</span></li>
        <li><strong>Lokasi</strong><span>{escape(SITE.get('alamat', ''))}</span></li>
      </ul>
      <div class="aksi">{pesan("tombol", "Chat WhatsApp", ikon=True)}</div>
    </div>
    <figure>
      {gambar(g["logo"], "Label Fruit Punch by Anyha bertuliskan mix fruit, fresh, less sugar")}
    </figure>
  </div>
</section>
<section class="bagian bagian--krim2">
  <div class="wrap">
    <div class="bagian__kepala">
      <p class="eyebrow">Foto produk</p>
      <h2>Seperti ini bentuknya.</h2>
      <p>Foto dari pemilik akun, tanpa penyuntingan warna.</p>
    </div>
    <div class="unggul-grid">
      <figure style="margin:0">
        {gambar(g["foto_cup"], "Deretan cup Mango Sago berisi potongan mangga dan sagu mutiara")}
      </figure>
      <figure style="margin:0">
        {gambar(g["foto_punch"], "Tiga botol Fruit Punch oranye berlabel Fruit Punch by Anyha di atas podium krem")}
      </figure>
      <figure style="margin:0">
        {gambar(g["foto_asinan"], "Cup Asinan Kiamboy berisi potongan buah dengan jeruk limau dan kismis")}
      </figure>
    </div>
  </div>
</section>"""


def isi_kontak():
    alamat = SITE.get("alamat", "")
    return kepala_dalam("Pesan", "Chat, konfirmasi, ambil di Sipin.", "Pesanan lewat WhatsApp atau DM Instagram. Lokasi pengambilan di " + alamat + ".") + f"""
<section class="bagian">
  <div class="wrap">
    <div class="grid3">
      <div class="kartu-info">
        <h2>Instagram</h2>
        <p>Cara utama memesan. Kirim menu, jumlah, dan tanggal.</p>
        <p class="kecil">{escape(SITE['handle'])}</p>
        {pesan("tombol tombol--garis", "Buka Instagram", ikon=True)}
      </div>
      <div class="kartu-info">
        <h2>Lokasi</h2>
        <p>{escape(alamat)}</p>
        <p class="kecil">Buka setiap hari, {escape(SITE.get('jam_buka', ''))}</p>
        {tombol_maps("tombol tombol--garis")}
      </div>
      <div class="kartu-info">
        <h2>Ambil atau kirim</h2>
        <p>Bisa diambil langsung di lokasi, atau dikirim.</p>
        <p class="kecil">Sebutkan alamat saat chat, ongkir dibalas pemilik.</p>
      </div>
    </div>
    <div class="d-catatan">
      <p><strong>Jumlah banyak</strong> sebaiknya dipesan sehari sebelumnya.</p>
      {pesan("tombol", "Tanya jadwal")}
    </div>
    <div class="peta-blok">{peta_semat()}</div>
    <div class="dua" style="margin-top:2.75rem">
      <div>
        <p class="eyebrow">Isi chat</p>
        <h2>Supaya balasan langsung berisi total.</h2>
        <ul class="d-fakta">
          <li><strong>Menu</strong><span>Mango Sago, Fruit Punch, atau Asinan Kiamboy</span></li>
          <li><strong>Jumlah</strong><span>Berapa cup atau botol</span></li>
          <li><strong>Tanggal</strong><span>Kapan mau diambil atau dikirim</span></li>
          <li><strong>Alamat</strong><span>Kalau minta dikirim</span></li>
        </ul>
      </div>
      <div>
        <p class="eyebrow">Pembayaran</p>
        <h2>Menyusul.</h2>
        <p>Metode pembayaran belum dikirim pemilik. Halaman ini diperbarui begitu informasinya ada, supaya tidak ada janji yang tidak benar.</p>
      </div>
    </div>
  </div>
</section>"""


def halaman_404():
    return kepala(
        "Halaman tidak ditemukan, " + USAHA,
        "Halaman yang dicari tidak ada. Kembali ke beranda Dessert by Anyha.",
        "/404.html",
    ) + """
<main id="utama">
<section class="d-kepala">
  <div class="wrap">
    <p class="eyebrow">404</p>
    <h1>Halaman ini tidak ada.</h1>
    <p class="d-intro">Mungkin tautannya salah ketik. Menu dan cara pesan ada di halaman depan.</p>
    <div class="aksi"><a class="tombol" href="/">Kembali ke beranda</a></div>
  </div>
</section>
</main>
""" + tutup(False)


# ------------------------------------------------------------------ tulis
def tulis(path, isi):
    tujuan = os.path.join(DIST, path)
    os.makedirs(os.path.dirname(tujuan) or DIST, exist_ok=True)
    with open(tujuan, "w", encoding="utf-8", newline="\n") as f:
        f.write(isi)


def salin_aset():
    shutil.copy(os.path.join(ROOT, "assets", "css", "situs.css"), os.path.join(DIST, "assets", "css", "situs.css"))
    shutil.copy(os.path.join(ROOT, "assets", "js", "site.js"), os.path.join(DIST, "assets", "js", "site.js"))


def main():
    if os.path.isdir(DIST):
        shutil.rmtree(DIST)
    os.makedirs(IMG, exist_ok=True)
    os.makedirs(os.path.join(DIST, "assets", "css"), exist_ok=True)
    os.makedirs(os.path.join(DIST, "assets", "js"), exist_ok=True)

    g = siapkan_gambar()

    tulis("index.html", halaman_beranda(g))
    tulis("menu/index.html", halaman("menu", "Menu " + USAHA, DESKRIPSI["menu"], "/menu/", isi_menu(g)))
    tulis("tentang/index.html", halaman("tentang", "Tentang " + USAHA, DESKRIPSI["tentang"], "/tentang/", isi_tentang(g)))
    tulis("kontak/index.html", halaman("kontak", "Cara pesan " + USAHA, DESKRIPSI["kontak"], "/kontak/", isi_kontak()))
    tulis("404.html", halaman_404())

    salin_aset()

    rute = ["/", "/menu/", "/tentang/", "/kontak/"]

    if SITE.get("url"):
        dasar = SITE["url"].rstrip("/")
        halaman_sitemap = "".join(
            "  <url><loc>%s%s</loc><changefreq>monthly</changefreq><priority>%s</priority></url>\n"
            % (dasar, r, "1.0" if r == "/" else "0.8") for r in rute)
        tulis("sitemap.xml",
              '<?xml version="1.0" encoding="UTF-8"?>\n'
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
              + halaman_sitemap + "</urlset>\n")
        tulis("robots.txt", "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % dasar)
    else:
        tulis("robots.txt", "User-agent: *\nAllow: /\n")

    tulis("_headers", "/assets/img/*\n  Cache-Control: public, max-age=604800\n/assets/css/*\n  Cache-Control: public, max-age=0, must-revalidate\n/assets/js/*\n  Cache-Control: public, max-age=0, must-revalidate\n")

    ukuran = jumlah = halaman_total = 0
    for akar, _d, berkas in os.walk(DIST):
        for b in berkas:
            jumlah += 1
            ukuran += os.path.getsize(os.path.join(akar, b))
            if b.endswith(".html"):
                halaman_total += 1
    print("halaman: %d" % halaman_total)
    print("berkas: %d, total %.1f KB" % (jumlah, ukuran / 1024))


if __name__ == "__main__":
    main()
