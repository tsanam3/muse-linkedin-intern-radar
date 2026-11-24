# LinkedIn Intern Job Radar

## When to use

- Use this skill when the user asks to check new LinkedIn internship, trainee, or apprenticeship listings, runs their daily job digest, or wants to update their internship criteria.
- Do NOT use this skill for general LinkedIn social posts or people search unless the user specifically asks for job listings.

## Safety & Read-only rules

- **Zero LinkedIn login**: Never ask for, store, or use the user's LinkedIn password, session cookies, or account credentials.
- **No direct scraping**: Never run Playwright, Selenium, curl, or automated browsers against `linkedin.com` directly.
- **Built-in web search only**: Always use Muse's built-in web search targeting publicly indexed LinkedIn job pages (`site:linkedin.com/jobs/view` and `site:id.linkedin.com/jobs/view`).
- **Read-only**: Never apply to jobs, message recruiters, or perform any write action on LinkedIn.

## Skill directory layout

All paths below are relative to this skill's folder (`~/workspace/custom-skills/linkedin_intern_radar/`):

- `profile.md` — User's target roles, fields, locations, background, and red flags.
- `scripts/job_tracker.py` — Zero-dependency Python 3 script for LinkedIn Job ID canonicalization and deduplication.
- `state/seen_jobs.json` — Automatically managed local state of previously reported jobs.
- `reports/YYYY-MM-DD.md` — Saved daily digest files.

## Step-by-step workflow

### 1. Read user preferences
- Read `profile.md` first. If the user asks to change keywords, locations, or preferences, update `profile.md` before searching.

### 2. Run focused web searches (3–5 queries max)
- Build 3 to 5 concise queries using Muse's built-in web search, combining `site:linkedin.com/jobs/view` (or `site:id.linkedin.com/jobs/view`) with the user's target roles, fields, and location from `profile.md`.
- Include the current month/year or recency cues when helpful so fresh listings surface first.
- Example query patterns:
  - `site:linkedin.com/jobs/view ("intern" OR "internship" OR "magang") ("electrical" OR "elektro" OR "instrumentation") Indonesia`
  - `site:linkedin.com/jobs/view ("intern" OR "internship" OR "magang") ("automation" OR "engineering" OR "maintenance" OR "project") ("electrical" OR "engineering") Indonesia`
  - `site:linkedin.com/jobs/view ("trainee" OR "apprenticeship" OR "intern") ("data center" OR "energy" OR "manufacturing" OR "oil") Indonesia`
  - `site:id.linkedin.com/jobs/view ("intern" OR "magang") ("electrical" OR "teknik elektro" OR "engineering" OR "instrumentation") Indonesia`
- Keep queries scoped and low-volume; avoid running dozens of repetitive searches.

### 3. Deduplicate against previously seen jobs
- Collect the candidate listings into a JSON array with fields: `title`, `company`, `location`, `url`, `snippet`, `posted_hint`.
- Pipe the JSON into the tracker script in a single shell call:
  ```bash
  python3 ~/workspace/custom-skills/linkedin_intern_radar/scripts/job_tracker.py filter --mark-seen <<'EOF'
  [
    {
      "title": "Intern - Automation Design Engineer",
      "company": "Schneider Electric",
      "location": "Cikarang Barat, West Java, Indonesia",
      "url": "https://www.linkedin.com/jobs/view/intern-automation-design-engineer-at-schneider-electric-4412345678",
      "snippet": "On-site, Temporary internship in automation design...",
      "posted_hint": "recent"
    }
  ]
  EOF
  ```
- The script normalizes URLs by extracting the canonical LinkedIn numeric Job ID (so `id.linkedin.com` and `www.linkedin.com` links to the same job are treated as duplicates) and returns **only new jobs** that have not been reported before.
- If the user explicitly asks to "re-check all" without updating state, omit `--mark-seen`.

### 4. Score job fit (LinkedIn Premium-style match check)
- Compare each **new** job against `profile.md` (especially the **Openness Rule**) and assign a match tier:
  - **High Match**: Intern/Magang/Trainee/Apprenticeship in Indonesia open to Electrical Engineering (Semester 7 / final-year) students, especially in Electrical, Instrumentation (E&I), Automation, Engineering Operations, Energy/Oil & Gas, Manufacturing, Data Center (DCEO), or Project Engineering.
  - **Medium Match**: Broad engineering, tech, data, or STEM internships in Indonesia where Electrical Engineering students are eligible or likely accepted even if outside the user's core track, or roles with minor caveats (e.g., fresh-graduate phrasing that may accept final-year students).
  - **Low Match**: Non-intern full-time roles requiring 2+ years experience, completely unrelated majors (e.g., Accounting/Law/Nursing), or clearly expired listings. Omit Low Match from the report unless zero High/Medium jobs were found.
- For every High/Medium job, write a concise 1-sentence reason explaining why it fits the user's background (e.g., relevant to Electrical Engineering / Pertamina E&I experience / open for Sem 7) and any caveats (on-site city, duration, etc.).

### 5. Save and present the daily report
- Save the digest to `reports/YYYY-MM-DD.md` (using today's local date).
- Present the report in the user's preferred language from `profile.md` (default: Bahasa Indonesia) with this clean format:
  - Header: date + count of new jobs found vs. duplicates skipped.
  - Sections: `🔥 High Match` and `👍 Medium Match`.
  - Per job: **Role — Company** (`Location`), 1-sentence fit note, and direct `https://www.linkedin.com/jobs/view/<id>/` link.
- **No hallucination**: Never invent jobs, companies, or LinkedIn URLs. If 0 new jobs remain after deduplication, reply honestly: *"Belum ada loker intern baru yang cocok sejak pengecekan terakhir."*

## Maintenance commands

- Check tracker stats:
  `python3 ~/workspace/custom-skills/linkedin_intern_radar/scripts/job_tracker.py status`
- Prune entries older than 60 days so `seen_jobs.json` stays compact:
  `python3 ~/workspace/custom-skills/linkedin_intern_radar/scripts/job_tracker.py prune --days 60`

## Daily schedule (1x sehari)

- If the user asks for automatic daily reports (default: 1x per day in the evening, e.g., 19:00 WIB), set up a recurring daily task/reminder in Muse that runs this skill once a day and sends the digest only when new matching jobs are found (or a short "tidak ada loker baru hari ini" note if the user prefers confirmation).