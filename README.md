# 📌 PostList

Assistant for tracking artworks, commissions, and where they were posted.  
Designed for anyone involved in posting: posters, artists, and managers.

> **Status:** Work in progress 🧪

---

## ✨ Features

- 🖼️ Track which artworks were posted and where (X/Twitter, Bluesky, FA, etc.)
- 🧾 Link artworks to commissions (who, what, when)
- 📅 See planned vs actual posting (queue, dates, targets)
- 👥 Roles:
  - **Poster** — sees what to post today and where
  - **Artist** — quickly checks that all their pieces were posted and to which platforms
  - **Manager** — monitors both flows, status, and coverage
- 🔎 Search / filter by character, tag, platform, status (planned / posted / skipped)
- ✅ Lightweight, minimal UI focused on clarity

---

## 🧱 Tech Stack

- **Frontend:** Vue 3 + Vite
- **Backend:** Python + Django
- **Database:** SQLite (db.sqlite3) 
- **Docker:** Not used yet (may be added later)


---

## 🚀 Getting Started (local)

The frontend lives inside the `posthub-ui` directory.

```bash
cd frontend/posthub-ui     # or cd "PostList Front/posthub-ui"
npm install                # install dependencies
npm run dev                # start Vite dev server
