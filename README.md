# muse-linkedin-intern-radar

Custom skill untuk **Meta Muse** guna memantau loker **Intern / Trainee / Apprenticeship / Daily Worker / Open Project** secara **Multi-Source** (LinkedIn publik, career portal perusahaan, job board Indonesia, dan platform project)—**tanpa login akun, tanpa cookie, dan tanpa API key**.

Terinspirasi dari struktur skill [`kgmkm/muse-grok-x-search`](https://github.com/kgmkm/muse-grok-x-search).

## Fitur

- **100% Aman & Read-Only** — Tidak perlu login LinkedIn atau job board mana pun, tidak pakai cookie/scraping browser, dan tidak melakukan aksi tulis (nol risiko ban akun).
- **Multi-Source & Tanpa API Key** — Menggunakan built-in web search bawaan Muse ke LinkedIn publik, career portal perusahaan (Siemens, Schneider, KUKA, Pertamina, Workday, Greenhouse, Lever, dll.), job board Indonesia (JobStreet, Kalibrr, Glints, Dealls, Career Center kampus), serta peluang *daily worker* & *open project*.
- **Anti Duplikat Multi-Source** — Script Python ringan (`scripts/job_tracker.py`, zero dependency) mengekstrak LinkedIn Job ID kanonis sekaligus menormalisasi URL non-LinkedIn (membuang parameter tracking `utm_*` sambil mempertahankan parameter ID lowongan) dan menyimpannya di `state/seen_jobs.json`.
- **Opportunity Fit Scoring** — Muse membandingkan setiap peluang baru terhadap `profile.md` milikmu dan mengelompokkannya ke `High Match` dan `Medium Match` dengan label tipe (`[Intern]`, `[Trainee]`, `[Daily Worker]`, `[Open Project]`) beserta alasan singkat.
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