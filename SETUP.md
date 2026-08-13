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
3. Pilih **🐍 Generate Contribution Snake**.
4. Klik **Run workflow**.
5. Setelah workflow berhasil, branch `output` akan dibuat otomatis.
6. Refresh halaman profil GitHub.

Snake juga dijadwalkan berjalan otomatis setiap hari.
