# Intern & Project Job Radar (Multi-Source)

## When to use

- Use this skill when the user asks to check new internship, trainee, apprenticeship, daily worker, or open project opportunities, runs their daily job digest, or wants to update their criteria.
- Do NOT use this skill for general social posts or people search unless the user specifically asks for job/project listings.

## Safety & Read-only rules

- **Zero account login**: Never ask for, store, or use the user's LinkedIn, JobStreet, Glints, or other job-board passwords, session cookies, or credentials.
- **No direct scraping**: Never run Playwright, Selenium, curl, or automated browsers against login-walled job sites.
- **Built-in web search only**: Always use Muse's built-in web search targeting publicly accessible job listings across LinkedIn, company career portals, Indonesian job boards, and legitimate project/daily-worker platforms.
- **Read-only**: Never apply to jobs, submit forms, message recruiters, or perform any write action on external platforms.

## Skill directory layout

All paths below are relative to this skill's folder (`~/workspace/custom-skills/linkedin_intern_radar/`):

- `profile.md` — User's target opportunity types, fields, locations, background, and red flags.
- `scripts/job_tracker.py` — Zero-dependency Python 3 script for URL/Job ID canonicalization and deduplication across LinkedIn and non-LinkedIn sources.
- `state/seen_jobs.json` — Automatically managed local state of previously reported listings.
- `reports/YYYY-MM-DD.md` — Saved daily digest files.

## Step-by-step workflow

### 1. Read user preferences
- Read `profile.md` first. If the user asks to change keywords, locations, opportunity types, or preferences, update `profile.md` before searching.

### 2. Run focused multi-source web searches (5–6 natural queries)
- **IMPORTANT — Keep queries simple and natural!** Do NOT combine deep path operators like `site:linkedin.com/jobs/view` with nested `OR` parentheses (many search engines return 0 results for complex boolean strings).
- Run 5 to 6 concise, natural-language queries covering multiple sources and opportunity types from `profile.md`, including the current year/month when helpful for freshness:
  1. **LinkedIn public jobs (simple query)**:
     `linkedin jobs intern electrical engineering automation Indonesia 2026`
  2. **Company career portals & ATS (E&I / Automation / Energy / Manufacturing)**:
     `internship electrical instrumentation automation engineering Indonesia careers 2026`
  3. **Trainee / DCEO / Energy / Utilities**:
     `engineering trainee DCEO apprenticeship Indonesia Siemens Schneider Pertamina AWS 2026`
  4. **Indonesian job boards & campus career centers**:
     `magang teknik elektro engineering Indonesia jobstreet glints kalibrr dealls 2026`
  5. **Broad Tech / Data / IoT intern open to Engineering**:
     `internship data engineering IoT embedded cybersecurity Indonesia 2026`
  6. **Daily worker / Open project / Part-time / Freelance**:
     `daily worker part time open project electrical engineering technician data Indonesia 2026`
- Rotate or vary 1–2 keywords across runs (e.g., Cikarang, Semarang, Jakarta, Batam, EPC, PLC, SCADA, research assistant, CAD) so fresh listings surface without hammering search.
- Only include actual job/project/career listing URLs (skip generic news articles, random LinkedIn feed posts without an actual vacancy link, or homepage-only URLs unless it's a direct active listing).

### 3. Deduplicate against previously seen listings
- Collect candidate listings into a JSON array with fields: `title`, `company`, `location`, `type` (`Intern`, `Trainee`, `Daily Worker`, or `Open Project`), `source` (e.g., `LinkedIn`, `Siemens Careers`, `Glints`, `JobStreet`, `ITB Career Center`), `url`, `snippet`, `deadline` (if stated, else `null`), `posted_at` (upload/posting date if stated, else `null`), `last_updated` (last update date if stated, else `null`).
- Pipe the JSON into the tracker script in a single shell call:
  ```bash
  python3 ~/workspace/custom-skills/linkedin_intern_radar/scripts/job_tracker.py filter --mark-seen <<'EOF'
  [
    {
      "title": "Production Technician Intern",
      "company": "Siemens",
      "location": "Jakarta, Indonesia",
      "type": "Intern",
      "source": "Siemens Careers",
      "url": "https://jobs.siemens.com/careers/job/563156123456",
      "snippet": "Internship opportunity for Electrical/Engineering students in Jakarta...",
      "deadline": null,
      "posted_at": "2026-11-20",
      "last_updated": "2026-11-20"
    }
  ]
  EOF
  ```
- The script canonicalizes both LinkedIn Job IDs (`li:<id>`) and non-LinkedIn URLs (`url:<normalized>` with tracking parameters stripped while preserving meaningful job ID query params) and returns **only new listings** that have not been reported before.
- If the user explicitly asks to "re-check all" without updating state, omit `--mark-seen`.

### 4. Deadline filter & opportunity fit scoring
- **Strict Deadline & Freshness Check (WAJIB sebelum masuk laporan):**
  - Cek tanggal hari ini (WIB) dan bandingkan dengan deadline setiap lowongan.
  - **Buang otomatis** lowongan yang deadline-nya sudah lewat (`deadline < hari ini`) atau tertulis *closed / expired / no longer accepting applications*.
  - Jika **tidak ada tulisan deadline**: tetap boleh dimasukkan ke laporan selama tidak berstatus tutup/kedaluwarsa, **dengan syarat wajib mencantumkan tanggal upload (`Posted`) dan/atau `Last update`** yang tertera di halaman/snippet sumber (jangan mengarang tanggal; kalau memang tidak tertera, tulis jujur `tidak tercantum`).
- Compare each valid **new** listing against `profile.md` (especially the **Openness Rule**) and assign a match tier:
  - **High Match**:
    - Intern / Magang / Trainee / Apprenticeship in Indonesia open to Electrical Engineering (Semester 7 / final-year), especially in Electrical, Instrumentation (E&I), Automation, Engineering Operations, Energy/Oil & Gas, Manufacturing, Data Center (DCEO), or Project Engineering.
    - Daily Worker / Open Project / Part-time that is directly linear (electrical, instrumentation, automation, engineering support, technical documentation, data/IoT) and clearly legitimate + worth applying to.
  - **Medium Match**:
    - Broad engineering, tech, data, or STEM internships in Indonesia where Electrical Engineering students are eligible or likely accepted, or roles with minor caveats (e.g., fresh-graduate phrasing that may accept final-year students).
    - Cross-discipline Daily Worker / Part-time / Open Project that a Semester 7 student can realistically apply to and looks worth it (good pay, reputable company/organization, or valuable experience/network).
  - **Low Match**:
    - Non-intern full-time roles requiring 2+ years experience, completely unrelated majors (e.g., Accounting/Law/Nursing), suspicious/scam listings, or expired/closed vacancies. Omit Low Match from the report unless zero High/Medium listings were found.
- For every High/Medium listing, write a concise 1-sentence reason explaining why it fits the user's background or why it's worth applying to, plus any caveats (on-site city, duration, unpaid note).

### 5. Save and present the daily report
- Save the digest to `reports/YYYY-MM-DD.md` (using today's local date).
- Present the report in the user's preferred language from `profile.md` (default: Bahasa Indonesia) with this clean format:
  - Header: date + count of new listings found vs. duplicates/expired skipped.
  - Sections: `🔥 High Match` and `👍 Medium Match`.
  - Per listing:
    - **`[Type]` Role — Company** (`Location` · *Source*)
    - **Info tanggal (wajib)**: `DL: <tanggal atau tidak tercantum> | Upload: <tanggal atau tidak tercantum> | Last update: <tanggal atau tidak tercantum>`
    - 1-sentence fit note + direct clickable URL.
- **No hallucination**: Never invent jobs, companies, deadlines, posting dates, or URLs. Every URL and date must come directly from the search results/listing page. If 0 new matching listings remain after deduplication & deadline filtering, reply honestly: *"Belum ada loker intern / daily worker / open project baru yang masih buka & cocok sejak pengecekan terakhir."*

## Maintenance commands

- Check tracker stats:
  `python3 ~/workspace/custom-skills/linkedin_intern_radar/scripts/job_tracker.py status`
- Prune entries older than 60 days so `seen_jobs.json` stays compact:
  `python3 ~/workspace/custom-skills/linkedin_intern_radar/scripts/job_tracker.py prune --days 60`

## Daily schedule (1x sehari)

- If the user asks for automatic daily reports (default: 1x per day at 19:00 WIB), run this skill once a day and send the digest (or a short note if no new listings were found).