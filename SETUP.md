# Setup Profile GitHub miqbaltrim

Folder ini siap dijadikan isi repository profile GitHub:

`https://github.com/miqbaltrim/miqbaltrim`

## Struktur

```text
miqbaltrim-profile/
├── README.md
├── SETUP.md
└── .github/
    └── workflows/
        └── snake.yml
```

## Cara pasang dari lokal

1. Buat repository **Public** bernama `miqbaltrim` di akun `miqbaltrim`.
2. Ekstrak ZIP ini.
3. Buka terminal di folder hasil ekstrak.
4. Jalankan:

```bash
git init
git add .
git commit -m "Create futuristic GitHub profile"
git branch -M main
git remote add origin https://github.com/miqbaltrim/miqbaltrim.git
git push -u origin main
```

Jika repository sudah pernah di-clone, cukup salin `README.md` dan folder `.github` ke root repository lalu:

```bash
git add .
git commit -m "Update GitHub profile and contribution snake"
git push
```

## Menjalankan snake pertama kali

1. Buka repository `miqbaltrim/miqbaltrim`.
2. Masuk ke tab **Actions**.
3. Pilih **📊 Generate Profile Contribution Assets**.
4. Klik **Run workflow**.
5. Setelah workflow berhasil, branch `output` akan dibuat otomatis.
6. Refresh halaman profil GitHub.

Kalender, grafik aktivitas, kartu streak, dan snake diperbarui otomatis setiap 6 jam.
Semua aset terbaru disimpan di folder `assets` pada branch `main`, sehingga README
tidak bergantung pada branch deployment terpisah.

## Membaca kontribusi privat secara akurat

Kartu kalender dan streak membaca grafik kontribusi publik yang sama dengan
halaman profil GitHub. Agar jumlah kontribusi privat ikut masuk tanpa membocorkan
nama repository atau detail commit:

1. Buka grafik kontribusi pada profil GitHub.
2. Pilih **Contribution settings > Private contributions**.
3. Jalankan kembali workflow **📊 Generate Profile Contribution Assets**.

Personal Access Token tidak diperlukan. Jika sebelumnya sudah membuat repository
secret `PROFILE_TOKEN`, secret tersebut boleh dihapus dan tokennya dapat dicabut
dari **Settings > Developer settings > Personal access tokens**.
