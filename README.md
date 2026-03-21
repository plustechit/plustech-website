# 🚀 Plustech Institute Website (Flask / Python)

A full-stack web application for **Plustech Institute** built with Python + Flask.

---

## 📁 Project Structure

```
plustech-flask/
├── app.py               ← Main Flask app (all routes + database)
├── requirements.txt     ← pip packages (only 3!)
├── plustech.db          ← SQLite database (auto-created on first run)
└── static/
    ├── index.html       ← Homepage
    ├── css/
    │   └── style.css
    ├── js/
    │   ├── layout.js    ← Navbar + Footer
    │   └── app.js       ← Auth helpers, API calls
    └── pages/
        ├── courses.html
        ├── about.html
        ├── contact.html
        ├── blog.html
        ├── login.html
        ├── register.html
        └── dashboard.html
```

---

## ⚙️ Tech Stack

| Layer    | Technology                        |
|----------|-----------------------------------|
| Frontend | HTML5, CSS3, Vanilla JavaScript   |
| Backend  | Python + Flask                    |
| Database | SQLite (Python built-in!)         |
| Auth     | Custom JWT (no extra library!)    |

---

## 🛠️ Setup (3 Simple Steps!)

### Step 1 — Check Python is installed
```
python --version
```
Should show Python 3.x. If not, download from https://python.org

### Step 2 — Install packages
```
pip install flask flask-cors pyjwt
```

### Step 3 — Run the website!
```
python app.py
```

Open browser → http://localhost:3000 🎉

---

## 🌐 Pages

| Page      | URL          |
|-----------|--------------|
| Home      | /            |
| Courses   | /courses     |
| About Us  | /about       |
| Contact   | /contact     |
| Blog      | /blog        |
| Login     | /login       |
| Register  | /register    |
| Dashboard | /dashboard   |

---

## 🔌 API Endpoints

```
POST /api/auth/register     → Create account
POST /api/auth/login        → Login
GET  /api/auth/me           → Get current user
GET  /api/courses           → All courses
GET  /api/blogs             → All blogs
POST /api/contact           → Submit contact form
POST /api/enrollments       → Enroll in course
GET  /api/enrollments/my    → My enrollments
```

---

## ☁️ Free Hosting on Render.com

1. Push project to GitHub
2. Go to https://render.com → New Web Service
3. Connect your GitHub repo
4. Set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python app.py`
5. Click Deploy → get free `.onrender.com` URL ✅

---

*Built with ❤️ for Plustech Institute, Dombivli East — TYBScIT Project*
