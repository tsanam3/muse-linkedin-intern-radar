# muse-linkedin-intern-radar

Custom skill untuk **Meta Muse** guna memantau **loker Intern / Trainee / Apprenticeship di LinkedIn** yang sesuai dengan profilmu—**tanpa LinkedIn Premium, tanpa API key, dan tanpa login akun LinkedIn**.

Terinspirasi dari struktur skill [`kgmkm/muse-grok-x-search`](https://github.com/kgmkm/muse-grok-x-search).

## Fitur

- **100% Aman & Read-Only** — Tidak perlu login LinkedIn, tidak pakai cookie/scraping browser, dan tidak melakukan aksi tulis (nol risiko ban akun).
- **Tanpa API Key** — Menggunakan built-in web search bawaan Muse ke halaman publik `linkedin.com/jobs/view`.
- **Anti Duplikat (Job ID Deduplication)** — Script Python ringan (`scripts/job_tracker.py`, zero dependency) mengekstrak LinkedIn Job ID kanonis dan menyimpannya di `state/seen_jobs.json` supaya loker yang sama tidak dilaporkan dua kali.
- **Job Fit Scoring ala LinkedIn Premium** — Muse membandingkan setiap loker baru terhadap `profile.md` milikmu dan mengelompokkannya ke `High Match` dan `Medium Match` beserta alasan singkat.
- **Siap untuk Report 1x Sehari** — Hemat, tidak berisik, dan tersimpan otomatis di `reports/YYYY-MM-DD.md`.

## Instalasi di Meta Muse

### Cara 1: Via GitHub (Paling Mudah)
Push folder ini ke repository GitHub kamu, lalu kirim URL repo-nya ke Muse dan bilang:
> *"Install custom skill ini dari `<URL repo kamu>` ke folder custom-skills."*

### Cara 2: Manual
Salin seluruh isi folder ini ke:
```text
~/workspace/custom-skills/linkedin_intern_radar/
```

## Cara Pakai

1. **Sesuaikan profilmu** di `profile.md` (role target, bidang, lokasi, red flags). Kamu juga bisa langsung bilang ke Muse, misalnya: *"Update profile intern radar: tambahin keyword Robotics dan prioritaskan lokasi Jakarta/Cikarang."*
2. **Cek on-demand**:
   - *"Cek loker intern LinkedIn baru yang cocok buat gw hari ini"*
3. **Setel jadwal rutin 1x sehari**:
   - Minta Muse membuat rutinitas/jadwal harian, misal: *"Setiap hari jam 19:00 WIB, jalankan skill `linkedin_intern_radar` dan kirim ringkasan loker intern baru buat gw."*

## Struktur File

```text
muse-linkedin-intern-radar/
├── skill.yaml              # Metadata skill untuk Meta Muse
├── SKILL.md                # SOP & guardrails untuk Muse
├── profile.md              # Profil & kriteria intern kamu
├── scripts/
│   └── job_tracker.py      # Deduplikasi LinkedIn Job ID (Python stdlib)
├── state/                  # Otomatis dibuat saat pertama kali jalan
│   └── seen_jobs.json
└── reports/                # Arsip laporan harian
    └── YYYY-MM-DD.md
```