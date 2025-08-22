# 🖥️ Ad Server – FastAPI-Based Lightweight Ad Delivery System

A minimal, embeddable ad server built with **FastAPI**, **SQLModel**, and **Jinja2**.
Ideal for use in personal blogs, micro-publisher sites, or experimental monetization projects.

---

## ✨ Features

✅ Embeddable ad zones (via `<script src="/embed.js?zone=...">`)
✅ Weighted ad rotation with click-through logging
✅ Impressions and click tracking per ad
✅ Admin panel with zone/ad management
✅ Analytics dashboard with CTR
✅ JSON stats endpoint
✅ SQLite-based (but pluggable with other DBs)
✅ Dockerized for easy deployment

---

## 🚀 Quickstart

### 1. Clone and Install

```bash
git clone https://github.com/npneykov/ad-server
cd ad-server
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 2. Create .env

```dotenv
ADMIN_KEY=supersecretkey
DATABASE_URL=sqlite:///./adserver.db
```

### 3. Run it

```bash
uvicorn main:app --reload
```

### 4. Access

| URL                | Description                      |
| ------------------ | -------------------------------- |
| `/admin`           | Admin panel (requires header)    |
| `/render?zone=1`   | Render ads for iframe delivery   |
| `/embed.js?zone=1` | Embeddable JS script tag         |
| `/api/stats.json`  | Raw stats JSON (CTR, imps, etc.) |

### 🧪 Testing

```bash
pytest -q -v
```

### 🐳 Docker

```bash
docker build -t ad-server .
docker run --env-file=.env -p 8000:8000 ad-server
```

To persist the database:

```bash
docker run --env-file=.env -p 8000:8000 -v $(pwd)/adserver.db:/app/adserver.db ad-server
```

## 💡 Example Embed Snippet

Paste this on a partner/publisher site:

```html
<script src="http://yourdomain.com/embed.js?zone=1"></script>
```

## 📜 License

This project is **proprietary software** owned by Nikola Neykov.

You may not use, copy, distribute, or modify any part of this software without explicit written permission.

For commercial inquiries or licensing, please contact: **<nikola.neykov@gmail.com>**

## 🙋‍♂️ Author

Nikola Neykov
github.com/npneykov
