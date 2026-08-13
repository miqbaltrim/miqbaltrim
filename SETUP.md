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

Snake dan kartu streak dijadwalkan diperbarui otomatis setiap 6 jam.

## Membaca kontribusi privat dan streak secara akurat

Tanpa konfigurasi tambahan, workflow hanya dapat membaca kontribusi publik. Agar
snake dan kartu streak mengikuti kalender kontribusi yang terlihat saat Anda
login, tambahkan token profil sebagai repository secret:

1. Pastikan **Contribution settings > Private contributions** pada profil GitHub
   sudah aktif.
2. Buat **Personal Access Token (classic)** di
   `https://github.com/settings/tokens/new?description=Profile%20Contribution%20Stats`.
3. Tidak perlu memilih scope apa pun; token hanya dipakai untuk membaca kalender
   kontribusi milik akun sendiri.
4. Buka repository **Settings > Secrets and variables > Actions**.
5. Pilih **New repository secret**, beri nama `PROFILE_TOKEN`, lalu tempel token.
6. Jalankan kembali workflow **📊 Generate Profile Contribution Assets**.

Jangan pernah menulis token langsung di `README.md`, workflow, commit, atau file
lain di repository.
