# DEPLOY.md - repo GitHub dan Cloudflare Pages

> Baca saat: "deploy github dan pages.dev", "push ke github", "deploy ulang",
> atau "situsnya belum update".

Dokumen ini memuat semua yang sudah terbukti jalan untuk proyek ini. Kalau ada
yang bertentangan dengan kenyataan di mesin, yang menang adalah hasil perintah,
bukan dokumen ini. Perbarui dokumen ini setiap kali ada yang berubah.

## 1. Keadaan sekarang (23 November 2026)

| Hal | Nilai |
|---|---|
| Folder kerja | `D:\Alif\Project\UMKM\dessertbyanyha\situs` |
| Repo GitHub | https://github.com/alifvir/Dessertby-Anyha (publik, branch `main`) |
| Repo id | `1468799015` |
| Proyek Pages | `dessertby-anyha` |
| URL live | https://dessertby-anyha.pages.dev |
| Jenis proyek Pages | Connect to Git (BUKAN Direct Upload) |
| Akun Cloudflare | `alifvir78@gmail.com`, account id `6974ed1876aaf81ed6adbc30ae874fde` |
| Akun GitHub | `alifvir` |

Catatan nama: repo dan proyek Pages memakai huruf besar `Dessertby-Anyha`, tetapi
subdomain `pages.dev` selalu huruf kecil, jadi alamatnya `dessertby-anyha.pages.dev`.

Folder `../web/` adalah mockup empat arah (repo `alifvir/mockup-dessertbyanyha`,
proyek Pages `mockup-dessertbyanyha`). Itu pembanding desain, bukan situs resmi.
Jangan ikut merilis isinya ke repo ini.

Setelan build proyek Pages:

| Kolom | Isi |
|---|---|
| Framework preset | None |
| Build command | `pip install -r requirements.txt && python build.py` |
| Build output directory | `dist` |
| Root directory | kosong |
| Production branch | `main` |

## 2. Alur normal: revisi lalu deploy

Ini yang dipakai 95 persen waktu. Tidak perlu membuka dashboard Cloudflare.

```
cd D:\Alif\Project\UMKM\dessertbyanyha\situs

python build.py
python tools\audit.py          # wajib berakhir: masalah: 0

git add -A
git commit -F <berkas-pesan>
git push
```

`git push` ke `main` = rilis. Pages membangun ulang otomatis.

Jangan jalankan `python.exe` untuk server pratinjau: itu memunculkan jendela konsol.
Pakai pola di bagian 6. Untuk build dan audit sekali jalan, tool shell sudah cukup
karena stdio-nya ditangkap pipe.

Pesan commit ditulis ke berkas lalu dipakai dengan `-F`, tanpa BOM:

```powershell
$f = "C:\Users\ASUS\AppData\Local\Temp\pesan-commit.txt"
[IO.File]::WriteAllText($f, $pesan, (New-Object Text.UTF8Encoding($false)))
git commit -F $f
```

## 3. Kredensial yang tersedia (terverifikasi)

- **GitHub**: kredensial HTTPS tersimpan di Git Credential Manager, akun
  `alifvir`. Ambil token untuk `gh` tanpa menampilkannya:

  ```powershell
  $env:GCM_INTERACTIVE="never"; $env:GIT_TERMINAL_PROMPT="0"
  $cred = ("protocol=https`nhost=github.com`n`n" | git credential fill) -join "`n"
  foreach ($b in ($cred -split "`r?`n")) { if ($b -match '^password=(.+)$') { $env:GH_TOKEN = $Matches[1].Trim() } }
  ```

  Jangan menyalin token ke laporan, chat, atau berkas.

- **Cloudflare**: token OAuth wrangler di
  `%APPDATA%\xdg.config\.wrangler\config\default.toml` (kunci `oauth_token`).
  Scope sudah termasuk `pages (write)` dan `account (read)`.

## 4. Kalau harus membuat proyek dari nol

Hanya perlu kalau proyeknya dihapus. Nama proyek Pages tidak bisa di-rename.

1. Cek subdomain dulu, karena `pages.dev` unik lintas akun Cloudflare:

   ```powershell
   try { [System.Net.Dns]::GetHostAddresses("dessertby-anyha.pages.dev") | Out-Null; "TERPAKAI" } catch { "kosong" }
   ```

2. Ambil `repo_id` dari GitHub, bukan hanya nama repo:

   ```powershell
   gh api repos/alifvir/Dessertby-Anyha --jq '.id'
   ```

3. POST ke Pages API dengan `source.type = "github"`. **Jangan** pakai
   `wrangler pages deploy` atau dashboard "Upload assets": keduanya mengunci proyek
   sebagai Direct Upload yang tidak bisa dihubungkan ke Git selamanya.

   Body yang terbukti jalan:

   ```powershell
   $c   = Get-Content "$env:APPDATA\xdg.config\.wrangler\config\default.toml" -Raw
   $tok = ([regex]::Match($c,'oauth_token\s*=\s*"([^"]+)"')).Groups[1].Value
   $acc = "6974ed1876aaf81ed6adbc30ae874fde"
   $h   = @{ Authorization = "Bearer $tok"; "Content-Type" = "application/json" }

   $body = @{
     name = "dessertby-anyha"
     production_branch = "main"
     source = @{ type = "github"; config = @{
       owner = "alifvir"; repo_name = "Dessertby-Anyha"; repo_id = "1468799015"
       production_branch = "main"; pr_comments_enabled = $false
       deployments_enabled = $true; production_deployments_enabled = $true
       preview_deployment_setting = "all"
       preview_branch_includes = @("*"); preview_branch_excludes = @()
       path_includes = @("*"); path_excludes = @()
     } }
     build_config = @{
       build_command = "pip install -r requirements.txt && python build.py"
       destination_dir = "dist"; root_dir = ""
     }
     deployment_configs = @{
       production = @{ compatibility_date = "2026-11-23"; build_image_major_version = 3; usage_model = "standard"; fail_open = $true; always_use_latest_compatibility_date = $false; compatibility_flags = @(); env_vars = $null }
       preview    = @{ compatibility_date = "2026-11-23"; build_image_major_version = 3; usage_model = "standard"; fail_open = $true; always_use_latest_compatibility_date = $false; compatibility_flags = @(); env_vars = $null }
     }
   } | ConvertTo-Json -Depth 8

   Invoke-RestMethod -Method Post -Uri "https://api.cloudflare.com/client/v4/accounts/$acc/pages/projects" -Headers $h -Body $body -ContentType "application/json"
   ```

4. Proyek baru belum punya deployment. Picu satu:

   ```powershell
   Invoke-RestMethod -Method Post -Uri "https://api.cloudflare.com/client/v4/accounts/$acc/pages/projects/dessertby-anyha/deployments" -Headers $h -Body "{}"
   ```

   Ini juga yang dipakai kalau push sudah masuk tapi belum ada build sama sekali.
   Jangan tunggu lebih dari 10 menit tanpa memicu: deployment tidak muncul sendiri.

## 5. Memantau dan membuktikan deploy

Jangan berhenti di "push sukses". Buktikan Pages membangun commit yang benar,
lalu buktikan isinya naik.

### 5a. Status build

```powershell
$d = Invoke-RestMethod -Uri "https://api.cloudflare.com/client/v4/accounts/$acc/pages/projects/dessertby-anyha/deployments" -Headers $h
$d.result[0] | Select-Object `
  @{n="commit";e={$_.deployment_trigger.metadata.commit_hash.Substring(0,7)}},
  @{n="stage"; e={$_.latest_stage.name}},
  @{n="status";e={$_.latest_stage.status}}
```

Yang ditunggu: `stage=deploy`, `status=success`, dan hash commit sama dengan
`git rev-parse --short=7 HEAD`.

### 5b. Isi live

Status 200 tidak membuktikan apa pun. Uji frasa yang hanya ada di revisi baru,
dan uji frasa yang harus HILANG.

```powershell
$u = "https://dessertby-anyha.pages.dev"
$ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
$html = (& curl.exe -s --max-time 30 -A $ua "$u/") -join "`n"

$html.Contains("Segarnya buah")                                   # True
-not $html.Contains("Mockup")                                     # True
-not $html.Contains("pita-mockup")                                # True
-not $html.Contains("/arah-4/")                                   # True
$html.Contains('rel="canonical" href="https://dessertby-anyha.pages.dev/"')  # True
```

Untuk status rute:

```powershell
foreach ($p in @('/','/menu/','/tentang/','/kontak/','/sitemap.xml','/robots.txt','/404','/path-ngawur-xyz')) {
  "$(curl.exe -s -o NUL -w '%{http_code}' --max-time 25 "$u$p") $p"
}
```

Harapan: semua 200 kecuali `/path-ngawur-xyz` yang 404. `/404` membalas 200 karena
Cloudflare menyajikan `404.html` di path itu, dan itu normal. Path ngawur memakai
halaman 404 milik situs.

### 5c. Jebakan verifikasi

- `curl.exe` mengembalikan array baris. Gabungkan dengan `-join "`n"` sebelum
  `-match` atau `.Contains`, kalau tidak hasilnya `System.Object[]`.
- Default User-Agent `urllib` diblokir Cloudflare dengan 403 yang terlihat seperti
  situs mati. Itu bot protection, bukan deploy gagal. Kirim UA browser.
- `Invoke-WebRequest` bawaan PowerShell bisa menggantung pada halaman besar.

## 6. Pratinjau lokal tanpa jendela

`python.exe` membuat jendela konsol baru. Untuk server, pakai `pythonw.exe` dan
sembunyikan jendelanya:

```powershell
$dir = "D:\Alif\Project\UMKM\dessertbyanyha\situs"
$p = Start-Process pythonw.exe -ArgumentList "tools\serve.py 8127" `
  -WorkingDirectory $dir -WindowStyle Hidden `
  -RedirectStandardOutput "$dir\pratinjau.log" -RedirectStandardError "$dir\pratinjau.err.log" -PassThru
$p.Id | Set-Content "$dir\.pid-pratinjau" -NoNewline
```

Matikan dengan `Stop-Process -Id <isi .pid-pratinjau>`, lalu pastikan port bebas:
`Get-NetTCPConnection -LocalPort 8127` harus kosong. Jangan biarkan port terpakai.

Untuk pratinjau di HP dalam WiFi yang sama: `tools\serve.py 8127 0.0.0.0`.

## 7. Berkas yang dipakai build di host

Semua ini wajib ter-commit:

```
build.py
requirements.txt
data/site.json
data/menu.json
assets/css/situs.css
assets/js/site.js
assets-src/*.jpeg
tools/audit.py         (tidak dipakai host, tapi ikut untuk pemeriksaan lokal)
```

Diabaikan `.gitignore`: `dist/`, `pratinjau/`, `pratinjau.log`, `.pid-pratinjau`,
`.wrangler/`, `__pycache__/`.

`assets-src/` wajib ter-commit. Tanpa foto sumber, `build.py` gagal di host pada
langkah Pillow.

### Uji build dari clone bersih

Lakukan sebelum push kalau ada berkas baru:

```powershell
$tmp = Join-Path $env:TEMP "uji-dessertby-anyha"
if (Test-Path $tmp) { Remove-Item -Recurse -Force $tmp }
git clone -q "D:\Alif\Project\UMKM\dessertbyanyha\situs" $tmp
Set-Location $tmp
python build.py
python tools\audit.py        # harus masalah: 0
Set-Location "D:\Alif\Project"; Remove-Item -Recurse -Force $tmp
```

## 8. Domain sendiri (kalau nanti diminta)

1. Dashboard Cloudflare: Workers & Pages > `dessertby-anyha` > Custom domains.
2. Isi `url` di `data/site.json` dengan domain baru, lalu `python build.py`.
3. Push. Canonical, `og:url`, dan `sitemap.xml` ikut berubah otomatis.
4. Tunggu sertifikat aktif, lalu ulangi pemeriksaan bagian 5b dengan domain baru.

## 9. Riwayat deploy

| Commit | Isi | Status |
|---|---|---|
| `f0afe4d` | Situs resmi satu arah (Kebun Buah), 5 halaman | success |

## 10. Jebakan yang sudah kena

1. **`wrangler pages deploy` mengunci proyek sebagai Direct Upload.** Tidak bisa
   dihubungkan ke Git selamanya. Selalu Connect to Git atau POST Pages API dengan
   `source.type = github`.
2. **Nama proyek Pages tidak bisa di-rename.** Huruf besar di nama repo tidak
   menjadi huruf besar di subdomain: hasilnya tetap huruf kecil.
3. **Token OAuth wrangler kedaluwarsa tiap jam.** Ciri: Pages API membalas 401
   `Unauthorized` padahal `wrangler whoami` masih bilang login. Obatnya jalankan
   `npx --yes wrangler@latest whoami` (dia refresh sendiri), lalu baca ulang
   `oauth_token`.
4. **Proyek baru tidak otomatis punya deployment.** Push saja tidak cukup; picu
   lewat `POST .../deployments` dengan body `{}`.
5. **BOM di pesan commit.** PowerShell 5.1 `Set-Content -Encoding UTF8` menambah
   BOM dan judul commit tampil aneh. Pakai `UTF8Encoding($false)`.
6. **`curl` di PowerShell mengembalikan array.** Wajib `-join "`n"`. Tanpa itu,
   `-match` mengembalikan `System.Object[]` dan pemeriksaan isi terlihat gagal
   padahal halamannya benar.
7. **Foto lama tetap tampil di HP pengunjung walau deploy sukses.** Dulu gambar
   memakai nama tetap dengan `max-age=604800`, jadi browser memegang salinan lama
   sampai 7 hari. Sekarang `build.py` menyisipkan hash isi ke nama berkas
   (`fruit-punch-6f54eddb.webp`) dan `_headers` memakai `max-age=31536000,
   immutable`. Kalau suatu saat nama gambar dikembalikan ke bentuk tetap, cache
   gambar WAJIB diturunkan lagi. Ciri masalah ini: HTML live sudah versi baru,
   tetapi foto di HP masih lama.
