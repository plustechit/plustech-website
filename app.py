from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import hashlib
import hmac
import json
import time
import base64

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)

DB_PATH = "plustech.db"
JWT_SECRET = "plustech_secret_key_2025"

# ─────────────────────────────────────────
# DATABASE
# ─────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            phone TEXT,
            role TEXT DEFAULT 'student',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            duration TEXT,
            level TEXT DEFAULT 'Beginner',
            price TEXT,
            icon TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS contact_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            subject TEXT,
            message TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS blogs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            excerpt TEXT,
            content TEXT,
            category TEXT,
            author TEXT DEFAULT 'Plustech Team',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            course_id INTEGER,
            status TEXT DEFAULT 'pending',
            enrolled_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(course_id) REFERENCES courses(id)
        );
    """)
    conn.commit()

    # Seed admin account
    admin = c.execute("SELECT id FROM users WHERE email=?", ("admin@plustech.in",)).fetchone()
    if not admin:
        c.execute(
            "INSERT INTO users (name,email,password,phone,role) VALUES (?,?,?,?,?)",
            ("Admin", "admin@plustech.in", hash_password("Admin@123"), "9999999999", "admin")
        )
        print("Admin account created!")
        print("  Email   : admin@plustech.in")
        print("  Password: Admin@123")

    # Seed courses
    count = c.execute("SELECT COUNT(*) FROM courses").fetchone()[0]
    if count == 0:
        courses = [
            ("Python Programming","Technology","Master Python from basics to advanced.","3 Months","Beginner to Advanced","Rs.8,000","[PY]"),
            ("Web Development (HTML/CSS/JS)","Technology","Build responsive websites from scratch.","3 Months","Beginner","Rs.9,000","[WEB]"),
            ("Java Programming","Technology","Learn Java OOP and enterprise development.","4 Months","Intermediate","Rs.9,500","[JAVA]"),
            ("C / C++ Programming","Technology","Fundamentals of programming with C and C++.","3 Months","Beginner","Rs.7,500","[C++]"),
            ("React / Node.js","Technology","Full-stack JavaScript development.","5 Months","Intermediate","Rs.14,000","[JS]"),
            ("Diploma in Fullstack Developer","Technology","End-to-end web development diploma.","6 Months","Intermediate","Rs.18,000","[FS]"),
            ("Diploma in Web Designing","Technology","Creative web design with UI/UX.","3 Months","Beginner","Rs.8,500","[UI]"),
            ("Diploma in Digital & Software Technology","Technology","Comprehensive software and digital skills.","6 Months","Beginner","Rs.16,000","[DST]"),
            ("Diploma in Programming (C,C++,SQL,HTML,CSS,JS)","Technology","Complete multi-language programming diploma.","6 Months","Beginner","Rs.15,000","[PRG]"),
            ("SAP FICO (Financial & Costing)","Accounting & Finance","SAP Finance and Controlling module.","4 Months","Intermediate","Rs.20,000","[SAP]"),
            ("SAP-MM (Material Management)","Accounting & Finance","SAP Material Management module.","4 Months","Intermediate","Rs.20,000","[MM]"),
            ("Diploma in Accounting","Accounting & Finance","Fundamental accounting principles.","3 Months","Beginner","Rs.7,000","[ACC]"),
            ("Diploma in Professional Accounting & MIS","Accounting & Finance","Advanced accounting and MIS reporting.","5 Months","Intermediate","Rs.12,000","[MIS]"),
            ("Diploma in Professional Industrial Accounting","Accounting & Finance","Industry-focused accounting course.","5 Months","Intermediate","Rs.13,000","[IND]"),
            ("Diploma in Tally Prime / Tally ERP","Accounting & Finance","Complete Tally software training.","2 Months","Beginner","Rs.6,000","[TAL]"),
            ("Diploma in Advance Tally","Accounting & Finance","Advanced Tally with payroll and TDS.","2 Months","Intermediate","Rs.7,000","[ADT]"),
            ("Diploma in Data Analyst","Data & Analytics","Data analysis using Python, SQL, Excel.","5 Months","Intermediate","Rs.16,000","[DA]"),
            ("Diploma in Power BI","Data & Analytics","Business intelligence with Power BI.","2 Months","Beginner","Rs.8,000","[BI]"),
            ("Diploma in Advance Excel","Data & Analytics","Pivot tables, VLOOKUP, macros, VBA.","2 Months","Beginner","Rs.6,000","[XL]"),
            ("Diploma in Dashboard","Data & Analytics","Design professional data dashboards.","2 Months","Intermediate","Rs.7,000","[DSH]"),
            ("Diploma in MIS","Data & Analytics","Management Information Systems.","3 Months","Intermediate","Rs.9,000","[MISD]"),
            ("Diploma in Graphical Designing","Design & Marketing","Photoshop, Illustrator, CorelDRAW.","3 Months","Beginner","Rs.9,000","[GFX]"),
            ("Diploma in Digital Marketing","Design & Marketing","SEO, SEM, social media, Google Ads.","3 Months","Beginner","Rs.10,000","[DM]"),
            ("Diploma in MS-Office","Office Productivity","Word, PowerPoint, Excel mastery.","2 Months","Beginner","Rs.5,000","[MS]"),
            ("Fluent English Speaking","Office Productivity","Spoken English and communication skills.","3 Months","Beginner","Rs.6,000","[ENG]"),
            ("Personality Development","Office Productivity","Confidence, body language, public speaking.","2 Months","Beginner","Rs.5,000","[PD]"),
            ("Interview Preparation","Office Productivity","Resume, mock interviews, aptitude prep.","1 Month","Beginner","Rs.4,000","[INT]"),
        ]
        c.executemany(
            "INSERT INTO courses (title,category,description,duration,level,price,icon) VALUES (?,?,?,?,?,?,?)",
            courses
        )
        print("Courses seeded!")

    # Seed blogs
    blog_count = c.execute("SELECT COUNT(*) FROM blogs").fetchone()[0]
    if blog_count == 0:
        blogs = [
            ("Why Learn Python in 2026?",
             "Python dominates the programming world. Here is why every student should learn it in 2026.",
             "Python is versatile, readable, and in high demand across AI, web development, and data science. Starting with Python gives you a strong foundation for any tech career.",
             "Technology"),
            ("Top 5 Careers After Tally",
             "Tally certification opens many doors in finance. Let us explore the top roles you can land.",
             "After Tally Prime training, you can work as an accountant, GST consultant, billing executive, inventory manager, or financial analyst in hundreds of companies.",
             "Finance"),
            ("The Future of Web Development",
             "React, Node.js, and the MERN stack are shaping the future of web. Are you ready?",
             "Modern web development revolves around component-based architecture. Fullstack developers are among the highest-paid tech professionals in India today.",
             "Technology"),
            ("How Digital Marketing Can Launch Your Career",
             "Digital marketing is one of the fastest growing fields in India. Here is how to get started.",
             "With businesses moving online, demand for digital marketers has skyrocketed. Skills in SEO, social media, and Google Ads can lead to great career opportunities.",
             "Marketing"),
        ]
        c.executemany(
            "INSERT INTO blogs (title,excerpt,content,category) VALUES (?,?,?,?)",
            blogs
        )
        print("Blogs seeded!")

    conn.commit()
    conn.close()

# ─────────────────────────────────────────
# AUTH HELPERS
# ─────────────────────────────────────────

def hash_password(password):
    return hashlib.sha256((password + JWT_SECRET).encode()).hexdigest()

def make_token(user_id, role):
    payload = {"id": user_id, "role": role, "exp": int(time.time()) + 7 * 24 * 3600}
    data = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()
    sig = hmac.new(JWT_SECRET.encode(), data.encode(), hashlib.sha256).hexdigest()
    return data + "." + sig

def verify_token(token):
    try:
        data, sig = token.rsplit(".", 1)
        expected = hmac.new(JWT_SECRET.encode(), data.encode(), hashlib.sha256).hexdigest()
        if sig != expected:
            return None
        payload = json.loads(base64.urlsafe_b64decode(data + "=="))
        if payload["exp"] < time.time():
            return None
        return payload
    except Exception:
        return None

def get_current_user():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    return verify_token(auth[7:])

def require_admin():
    payload = get_current_user()
    if not payload or payload.get("role") != "admin":
        return None
    return payload

# ─────────────────────────────────────────
# FRONTEND PAGES
# ─────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/courses")
def courses_page():
    return send_from_directory("static/pages", "courses.html")

@app.route("/about")
def about_page():
    return send_from_directory("static/pages", "about.html")

@app.route("/contact")
def contact_page():
    return send_from_directory("static/pages", "contact.html")

@app.route("/blog")
def blog_page():
    return send_from_directory("static/pages", "blog.html")

@app.route("/login")
def login_page():
    return send_from_directory("static/pages", "login.html")

@app.route("/register")
def register_page():
    return send_from_directory("static/pages", "register.html")

@app.route("/dashboard")
def dashboard_page():
    return send_from_directory("static/pages", "dashboard.html")

@app.route("/admin")
def admin_page():
    return send_from_directory("static/pages", "admin.html")

# ─────────────────────────────────────────
# API — AUTH
# ─────────────────────────────────────────

@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json()
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")
    phone = data.get("phone", "")
    if not name or not email or not password:
        return jsonify({"error": "Name, email and password are required."}), 400
    conn = get_db()
    existing = conn.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()
    if existing:
        conn.close()
        return jsonify({"error": "Email already registered."}), 409
    hashed = hash_password(password)
    cur = conn.execute(
        "INSERT INTO users (name,email,password,phone) VALUES (?,?,?,?)",
        (name, email, hashed, phone)
    )
    conn.commit()
    user_id = cur.lastrowid
    conn.close()
    token = make_token(user_id, "student")
    return jsonify({"success": True, "token": token, "user": {"id": user_id, "name": name, "email": email, "role": "student"}})

@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email", "").strip()
    password = data.get("password", "")
    if not email or not password:
        return jsonify({"error": "Email and password required."}), 400
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    conn.close()
    if not user or user["password"] != hash_password(password):
        return jsonify({"error": "Invalid email or password."}), 401
    token = make_token(user["id"], user["role"])
    return jsonify({"success": True, "token": token, "user": {"id": user["id"], "name": user["name"], "email": user["email"], "role": user["role"]}})

@app.route("/api/auth/me", methods=["GET"])
def me():
    payload = get_current_user()
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401
    conn = get_db()
    user = conn.execute(
        "SELECT id,name,email,phone,role,created_at FROM users WHERE id=?",
        (payload["id"],)
    ).fetchone()
    conn.close()
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(dict(user))

# ─────────────────────────────────────────
# API — COURSES
# ─────────────────────────────────────────

@app.route("/api/courses", methods=["GET"])
def get_courses():
    category = request.args.get("category")
    conn = get_db()
    if category and category != "All":
        rows = conn.execute(
            "SELECT * FROM courses WHERE category=? ORDER BY id", (category,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM courses ORDER BY category, id").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/courses/<int:course_id>", methods=["GET"])
def get_course(course_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM courses WHERE id=?", (course_id,)).fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "Course not found"}), 404
    return jsonify(dict(row))

# ─────────────────────────────────────────
# API — BLOGS
# ─────────────────────────────────────────

@app.route("/api/blogs", methods=["GET"])
def get_blogs():
    conn = get_db()
    rows = conn.execute("SELECT * FROM blogs ORDER BY created_at DESC").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/blogs/<int:blog_id>", methods=["GET"])
def get_blog(blog_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM blogs WHERE id=?", (blog_id,)).fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "Blog not found"}), 404
    return jsonify(dict(row))

# ─────────────────────────────────────────
# API — CONTACT
# ─────────────────────────────────────────

@app.route("/api/contact", methods=["POST"])
def contact():
    data = request.get_json()
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    phone = data.get("phone", "")
    subject = data.get("subject", "")
    message = data.get("message", "").strip()
    if not name or not email or not message:
        return jsonify({"error": "Name, email and message are required."}), 400
    conn = get_db()
    conn.execute(
        "INSERT INTO contact_messages (name,email,phone,subject,message) VALUES (?,?,?,?,?)",
        (name, email, phone, subject, message)
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Message sent! We will get back to you within 24 hours."})

# ─────────────────────────────────────────
# API — ENROLLMENTS
# ─────────────────────────────────────────

@app.route("/api/enrollments", methods=["POST"])
def enroll():
    payload = get_current_user()
    if not payload:
        return jsonify({"error": "Please login to enroll."}), 401
    data = request.get_json()
    course_id = data.get("course_id")
    if not course_id:
        return jsonify({"error": "Course ID required."}), 400
    conn = get_db()
    existing = conn.execute(
        "SELECT id FROM enrollments WHERE user_id=? AND course_id=?",
        (payload["id"], course_id)
    ).fetchone()
    if existing:
        conn.close()
        return jsonify({"error": "Already enrolled in this course."}), 409
    conn.execute(
        "INSERT INTO enrollments (user_id,course_id) VALUES (?,?)",
        (payload["id"], course_id)
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Successfully enrolled! Our team will contact you shortly."})

@app.route("/api/enrollments/my", methods=["GET"])
def my_enrollments():
    payload = get_current_user()
    if not payload:
        return jsonify({"error": "Unauthorized"}), 401
    conn = get_db()
    rows = conn.execute("""
        SELECT e.id, e.status, e.enrolled_at, c.title, c.category, c.duration, c.icon
        FROM enrollments e JOIN courses c ON e.course_id = c.id
        WHERE e.user_id=? ORDER BY e.enrolled_at DESC
    """, (payload["id"],)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

# ─────────────────────────────────────────
# API — ADMIN (Protected)
# ─────────────────────────────────────────

@app.route("/api/admin/students", methods=["GET"])
def admin_students():
    if not require_admin():
        return jsonify({"error": "Admins only."}), 403
    conn = get_db()
    rows = conn.execute(
        "SELECT id,name,email,phone,role,created_at FROM users ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/admin/enrollments", methods=["GET"])
def admin_enrollments():
    if not require_admin():
        return jsonify({"error": "Admins only."}), 403
    conn = get_db()
    rows = conn.execute("""
        SELECT e.id, e.status, e.enrolled_at,
               u.name as student_name, u.email,
               c.title, c.category, c.duration
        FROM enrollments e
        JOIN users u ON e.user_id = u.id
        JOIN courses c ON e.course_id = c.id
        ORDER BY e.enrolled_at DESC
    """).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/admin/messages", methods=["GET"])
def admin_messages():
    if not require_admin():
        return jsonify({"error": "Admins only."}), 403
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM contact_messages ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

# ─────────────────────────────────────────
# START
# ─────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    print("")
    print("=========================================")
    print("  Plustech server -> http://localhost:3000")
    print("  Admin panel   -> http://localhost:3000/admin")
    print("  Admin email   -> admin@plustech.in")
    print("  Admin pass    -> Admin@123")
    print("=========================================")
    print("")
    import os
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port, debug=False)