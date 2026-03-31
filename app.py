from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3, hashlib, hmac, json, time, base64, os

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)

DB_PATH = "plustech.db"
JWT_SECRET = "plustech_secret_key_2025"

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
            name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, password TEXT NOT NULL,
            phone TEXT, role TEXT DEFAULT 'student',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL, category TEXT NOT NULL, description TEXT,
            duration TEXT, level TEXT DEFAULT 'Beginner', price TEXT, icon TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER, course_id INTEGER, status TEXT DEFAULT 'pending',
            enrolled_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(course_id) REFERENCES courses(id)
        );
        CREATE TABLE IF NOT EXISTS course_materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL, type TEXT NOT NULL,
            title TEXT NOT NULL, content TEXT, url TEXT, order_num INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(course_id) REFERENCES courses(id)
        );
        CREATE TABLE IF NOT EXISTS contact_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, email TEXT NOT NULL, phone TEXT,
            subject TEXT, message TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS blogs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL, excerpt TEXT, content TEXT,
            category TEXT, author TEXT DEFAULT 'Plustech Team',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()

    if not c.execute("SELECT id FROM users WHERE email=?", ("admin@plustech.in",)).fetchone():
        c.execute("INSERT INTO users (name,email,password,phone,role) VALUES (?,?,?,?,?)",
                  ("Admin","admin@plustech.in",hash_password("Admin@123"),"9136819666","admin"))

    if c.execute("SELECT COUNT(*) FROM courses").fetchone()[0] == 0:
        courses = [
            ("Python Programming","Technology","Master Python from basics to advanced with real projects.","3 Months","Beginner to Advanced","Rs.8,000","PY"),
            ("Web Development (HTML/CSS/JS)","Technology","Build responsive websites from scratch using modern tools.","3 Months","Beginner","Rs.9,000","WEB"),
            ("Java Programming","Technology","Learn Java OOP, collections and enterprise development.","4 Months","Intermediate","Rs.9,500","JAVA"),
            ("C / C++ Programming","Technology","Fundamentals of programming using C and C++.","3 Months","Beginner","Rs.7,500","CPP"),
            ("React / Node.js","Technology","Full-stack JavaScript development with MERN stack.","5 Months","Intermediate","Rs.14,000","JS"),
            ("Diploma in Fullstack Developer","Technology","End-to-end web development diploma program.","6 Months","Intermediate","Rs.18,000","FS"),
            ("Diploma in Web Designing","Technology","Creative web design with UI/UX principles.","3 Months","Beginner","Rs.8,500","UI"),
            ("Diploma in Digital & Software Technology","Technology","Comprehensive software and digital skills course.","6 Months","Beginner","Rs.16,000","DST"),
            ("Diploma in Programming","Technology","Complete multi-language programming diploma.","6 Months","Beginner","Rs.15,000","PRG"),
            ("SAP FICO","Accounting & Finance","SAP Finance and Controlling module with live practice.","4 Months","Intermediate","Rs.20,000","SAP"),
            ("SAP-MM (Material Management)","Accounting & Finance","SAP Material Management with hands-on training.","4 Months","Intermediate","Rs.20,000","MM"),
            ("Diploma in Accounting","Accounting & Finance","Fundamental accounting principles and practices.","3 Months","Beginner","Rs.7,000","ACC"),
            ("Diploma in Professional Accounting & MIS","Accounting & Finance","Advanced accounting and MIS reporting skills.","5 Months","Intermediate","Rs.12,000","MIS"),
            ("Diploma in Professional Industrial Accounting","Accounting & Finance","Industry-focused accounting with real case studies.","5 Months","Intermediate","Rs.13,000","IND"),
            ("Tally Prime / Tally ERP","Accounting & Finance","Complete Tally software training from basics to GST.","2 Months","Beginner","Rs.6,000","TAL"),
            ("Diploma in Advance Tally","Accounting & Finance","Advanced Tally with payroll, TDS and audit reports.","2 Months","Intermediate","Rs.7,000","ADT"),
            ("Diploma in Data Analyst","Data & Analytics","Data analysis using Python, SQL and Excel.","5 Months","Intermediate","Rs.16,000","DA"),
            ("Diploma in Power BI","Data & Analytics","Business intelligence dashboards with Power BI.","2 Months","Beginner","Rs.8,000","BI"),
            ("Diploma in Advance Excel","Data & Analytics","Pivot tables, VLOOKUP, macros and VBA automation.","2 Months","Beginner","Rs.6,000","XL"),
            ("Diploma in Dashboard Design","Data & Analytics","Design professional data dashboards for business.","2 Months","Intermediate","Rs.7,000","DSH"),
            ("Diploma in MIS","Data & Analytics","Management Information Systems and reporting.","3 Months","Intermediate","Rs.9,000","MISD"),
            ("Diploma in Graphical Designing","Design & Marketing","Photoshop, Illustrator and CorelDRAW mastery.","3 Months","Beginner","Rs.9,000","GFX"),
            ("Diploma in Digital Marketing","Design & Marketing","SEO, SEM, social media marketing and Google Ads.","3 Months","Beginner","Rs.10,000","DM"),
            ("Diploma in MS-Office","Office Productivity","Word, PowerPoint and Excel for office professionals.","2 Months","Beginner","Rs.5,000","MS"),
            ("Fluent English Speaking","Office Productivity","Spoken English and professional communication skills.","3 Months","Beginner","Rs.6,000","ENG"),
            ("Personality Development","Office Productivity","Confidence, body language and public speaking skills.","2 Months","Beginner","Rs.5,000","PD"),
            ("Interview Preparation","Office Productivity","Resume building, mock interviews and aptitude prep.","1 Month","Beginner","Rs.4,000","INT"),
        ]
        c.executemany("INSERT INTO courses (title,category,description,duration,level,price,icon) VALUES (?,?,?,?,?,?,?)", courses)

    if c.execute("SELECT COUNT(*) FROM course_materials").fetchone()[0] == 0:
        all_courses = c.execute("SELECT id, title, icon FROM courses").fetchall()
        materials = []
        for course in all_courses:
            cid = course["id"]
            icon = course["icon"]
            title = course["title"]
            if icon == "PY":
                materials += [
                    (cid,"note","Introduction to Python","Python is a high-level, interpreted, general-purpose programming language created by Guido van Rossum in 1991.\n\nKey Features:\n- Easy to read and write\n- Interpreted language (no compilation needed)\n- Dynamically typed\n- Large standard library\n- Supports OOP, functional and procedural programming\n\nPython is used in: Web Development, Data Science, AI/ML, Automation, Game Development.\n\nFirst Python Program:\nprint(\'Hello, World!\')",None,1),
                    (cid,"note","Variables and Data Types","Variable Types:\n- int   : whole numbers  (x = 10)\n- float : decimals       (y = 3.14)\n- str   : text           (name = \'Aditya\')\n- bool  : True/False     (flag = True)\n- list  : ordered, mutable   ([1, 2, 3])\n- tuple : ordered, immutable ((1, 2, 3))\n- dict  : key-value pairs    ({\'name\': \'Aditya\'})\n- set   : unique unordered   ({1, 2, 3})\n\nType Conversion:\nint(\'10\')  -> 10\nstr(100)   -> \'100\'\nfloat(\'3.14\') -> 3.14\n\nInput from user:\nname = input(\'Enter your name: \')",None,2),
                    (cid,"note","Control Flow - If/Else & Loops","If-Elif-Else:\nif marks >= 70:\n    print(\'Distinction\')\nelif marks >= 60:\n    print(\'First Class\')\nelse:\n    print(\'Pass\')\n\nFor Loop:\nfor i in range(5):\n    print(i)  # prints 0 to 4\n\nFor loop with list:\nfruits = [\'apple\', \'mango\', \'banana\']\nfor fruit in fruits:\n    print(fruit)\n\nWhile Loop:\ncount = 0\nwhile count < 5:\n    print(count)\n    count += 1\n\nbreak  - exits loop\ncontinue - skips current iteration",None,3),
                    (cid,"note","Functions and Modules","Function Definition:\ndef function_name(parameters):\n    # code block\n    return result\n\nExample:\ndef add(a, b):\n    return a + b\n\nresult = add(10, 20)  # 30\n\nDefault Parameters:\ndef greet(name, msg=\'Hello\'):\n    return f\'{msg}, {name}!\'\n\nLambda Functions:\nsquare = lambda x: x ** 2\nprint(square(5))  # 25\n\nImporting Modules:\nimport math\nprint(math.sqrt(16))  # 4.0\n\nfrom datetime import date\ntoday = date.today()",None,4),
                    (cid,"code","Variables and Basic Programs","# Variable declarations\nname = \'Aditya Parab\'\nage = 20\nmarks = 95.5\nis_student = True\n\n# String formatting\nprint(f\'Name: {name}\')\nprint(f\'Age: {age}, Marks: {marks}\')\n\n# Arithmetic operations\na = 15\nb = 4\nprint(a + b)   # 19\nprint(a - b)   # 11\nprint(a * b)   # 60\nprint(a / b)   # 3.75\nprint(a // b)  # 3  (floor division)\nprint(a % b)   # 3  (remainder)\nprint(a ** b)  # 50625 (power)\n\n# String methods\ntext = \'hello world\'\nprint(text.upper())        # HELLO WORLD\nprint(text.title())        # Hello World\nprint(text.replace(\'l\',\'L\'))  # heLLo worLd\nprint(len(text))           # 11\nprint(text.split())        # [\'hello\', \'world\']",None,5),
                    (cid,"code","Lists, Dictionaries and Functions","# Lists\nstudents = [\'Aditya\', \'Rahul\', \'Priya\', \'Anjali\']\nstudents.append(\'Sita\')    # add at end\nstudents.insert(1, \'Raj\')  # add at position 1\nstudents.remove(\'Rahul\')   # remove by value\nprint(students[0])          # first item\nprint(students[-1])         # last item\nprint(students[1:3])        # slice\n\n# Dictionary\nstudent = {\n    \'name\': \'Aditya\',\n    \'roll\': \'TY001\',\n    \'marks\': 88.5\n}\nprint(student[\'name\'])     # Aditya\nstudent[\'grade\'] = \'A\'   # add new key\n\n# List comprehension\nnumbers = [1, 2, 3, 4, 5]\nsquares = [n**2 for n in numbers]\nprint(squares)  # [1, 4, 9, 16, 25]\n\n# Function with dictionary\ndef get_grade(marks):\n    if marks >= 70: return \'Distinction\'\n    elif marks >= 60: return \'First Class\'\n    elif marks >= 40: return \'Pass\'\n    else: return \'Fail\'\n\nprint(get_grade(88))  # Distinction",None,6),
                    (cid,"code","Classes and OOP","class Student:\n    # Class variable\n    school = \'Plustech Institute\'\n    \n    def __init__(self, name, roll_no, marks):\n        # Instance variables\n        self.name = name\n        self.roll_no = roll_no\n        self.marks = marks\n    \n    def get_grade(self):\n        if self.marks >= 70: return \'Distinction\'\n        elif self.marks >= 60: return \'First Class\'\n        elif self.marks >= 40: return \'Pass\'\n        return \'Fail\'\n    \n    def introduce(self):\n        return f\'I am {self.name}, Roll: {self.roll_no}, Grade: {self.get_grade()}\'\n    \n    def __str__(self):\n        return f\'Student({self.name}, {self.marks})\'\n\n# Inheritance\nclass TYStudent(Student):\n    def __init__(self, name, roll_no, marks, project):\n        super().__init__(name, roll_no, marks)\n        self.project = project\n    \n    def introduce(self):\n        base = super().introduce()\n        return f\'{base}, Project: {self.project}\'\n\n# Usage\ns1 = Student(\'Aditya\', \'TY001\', 88)\nprint(s1)\nprint(s1.introduce())\n\ns2 = TYStudent(\'Rahul\', \'TY002\', 75, \'Plustech Website\')\nprint(s2.introduce())",None,7),
                    (cid,"video","Python Full Course for Beginners (Programming with Mosh)",None,"https://www.youtube.com/watch?v=_uQrJ0TkZlc",8),
                    (cid,"video","Python OOP Tutorial (Corey Schafer)",None,"https://www.youtube.com/watch?v=ZDa-Z5JzLYM",9),
                    (cid,"video","Python Projects for Beginners",None,"https://www.youtube.com/watch?v=8ext9G7xspg",10),
                ]
            elif icon == "WEB":
                materials += [
                    (cid,"note","HTML Fundamentals","HTML (HyperText Markup Language) gives structure to web content.\n\nBasic Structure:\n<!DOCTYPE html>\n<html>\n  <head>\n    <title>Page Title</title>\n  </head>\n  <body>\n    content here\n  </body>\n</html>\n\nCommon Tags:\n- <h1> to <h6> : Headings\n- <p>          : Paragraph\n- <a href=\'url\'>  : Link\n- <img src=\'file.jpg\'>  : Image\n- <div>        : Container\n- <ul>/<li>    : Unordered list\n- <ol>/<li>    : Ordered list\n- <table>/<tr>/<td> : Tables\n- <form>/<input>/<button> : Forms\n- <header>/<main>/<footer> : Semantic HTML",None,1),
                    (cid,"note","CSS Styling Guide","CSS (Cascading Style Sheets) controls visual appearance.\n\nAdding CSS:\n1. Inline: <p style=\'color:red;\'>\n2. Internal: <style> tag in <head>\n3. External: <link rel=\'stylesheet\' href=\'style.css\'>\n\nSelectors:\n- Tag:   p { color: blue; }\n- Class: .box { padding: 10px; }\n- ID:    #header { background: navy; }\n\nKey Properties:\n- color, background-color\n- font-size, font-weight, font-family\n- margin, padding, border, border-radius\n- width, height, display\n- position: relative/absolute/fixed\n\nFlexbox:\n.container { display: flex; justify-content: center; align-items: center; }\n\nCSS Grid:\n.grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }",None,2),
                    (cid,"note","JavaScript Basics","JS makes pages interactive.\n\nVariables:\nlet name = \'Aditya\';  // can change\nconst PI = 3.14;       // cannot change\n\nFunctions:\nfunction greet(name) {\n    return \'Hello, \' + name;\n}\n\nDOM Manipulation:\n// Select elements\ndocument.getElementById(\'myId\')\ndocument.querySelector(\'.myClass\')\n\n// Change content\nelement.textContent = \'New Text\';\nelement.style.color = \'red\';\n\n// Events\nbutton.addEventListener(\'click\', function() {\n    alert(\'Clicked!\');\n});\n\nFetch API (call backend):\nasync function getData() {\n    const res = await fetch(\'/api/data\');\n    const data = await res.json();\n    console.log(data);\n}",None,3),
                    (cid,"code","Complete HTML Webpage","<!DOCTYPE html>\n<html lang=\'en\'>\n<head>\n  <meta charset=\'UTF-8\'>\n  <meta name=\'viewport\' content=\'width=device-width, initial-scale=1.0\'>\n  <title>Plustech - My First Page</title>\n  <style>\n    * { margin: 0; padding: 0; box-sizing: border-box; }\n    body { font-family: Arial, sans-serif; }\n    header {\n      background: #1e5aa8; color: white;\n      padding: 15px 30px;\n      display: flex; justify-content: space-between; align-items: center;\n    }\n    nav a { color: white; margin-left: 20px; text-decoration: none; }\n    .hero {\n      background: linear-gradient(135deg, #0a1628, #1e5aa8);\n      color: white; text-align: center; padding: 80px 20px;\n    }\n    .hero h1 { font-size: 48px; margin-bottom: 15px; }\n    .btn {\n      background: #f59e0b; color: #0a1628;\n      padding: 12px 30px; border: none;\n      border-radius: 6px; font-size: 16px;\n      cursor: pointer; margin-top: 20px;\n    }\n    .grid {\n      display: grid; grid-template-columns: repeat(3, 1fr);\n      gap: 20px; padding: 40px;\n    }\n    .card {\n      background: white; border-radius: 10px;\n      padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);\n    }\n    footer { background: #333; color: white; text-align: center; padding: 20px; }\n  </style>\n</head>\n<body>\n  <header>\n    <h2>Plustech Institute</h2>\n    <nav>\n      <a href=\'#\'>Home</a>\n      <a href=\'#courses\'>Courses</a>\n      <a href=\'#contact\'>Contact</a>\n    </nav>\n  </header>\n  <div class=\'hero\'>\n    <h1>Learn to Code</h1>\n    <p>Build your future with Plustech Institute, Dombivli</p>\n    <button class=\'btn\' onclick=\'alert(\"Welcome!\")\'> Explore Courses</button>\n  </div>\n  <div class=\'grid\' id=\'courses\'>\n    <div class=\'card\'><h3>Python</h3><p>Rs.8,000 | 3 Months</p></div>\n    <div class=\'card\'><h3>Web Dev</h3><p>Rs.9,000 | 3 Months</p></div>\n    <div class=\'card\'><h3>React</h3><p>Rs.14,000 | 5 Months</p></div>\n  </div>\n  <footer>© 2026 Plustech Institute, Dombivli East</footer>\n</body>\n</html>",None,4),
                    (cid,"video","HTML Full Course - Build a Website Tutorial",None,"https://www.youtube.com/watch?v=pQN-pnXPaVg",5),
                    (cid,"video","CSS Tutorial - Zero to Hero (FreeCodeCamp)",None,"https://www.youtube.com/watch?v=1Rs2ND1ryYc",6),
                    (cid,"video","JavaScript Crash Course for Beginners",None,"https://www.youtube.com/watch?v=hdI2bqOjy3c",7),
                ]
            elif icon == "TAL":
                materials += [
                    (cid,"note","Tally Prime Introduction","Tally Prime is India most popular accounting software.\n\nKey Areas:\n- Gateway of Tally (Main Menu)\n- Company Creation and Setup\n- Ledger Creation (assets, liabilities, income, expenses)\n- Groups in Tally\n- Voucher Entry: Sales, Purchase, Payment, Receipt, Journal\n- Inventory Management\n- Reports: Balance Sheet, P&L, Trial Balance, Day Book\n\nImportant Shortcut Keys:\nF1 - Help            F2 - Change Date\nF3 - Select Company  F4 - Contra Voucher\nF5 - Payment         F6 - Receipt\nF7 - Journal         F8 - Sales Voucher\nF9 - Purchase        F10 - View Reports\nAlt+F4 - Close       Ctrl+A - Accept/Save",None,1),
                    (cid,"note","GST Configuration in Tally Prime","Steps to Configure GST in Tally Prime:\n\n1. Enable GST:\n   F11 > Statutory & Taxation\n   Enable Goods and Services Tax (GST) = Yes\n   Set GSTIN, State, Registration Type\n\n2. Create Tax Ledgers:\n   - CGST @ 9% under Duties & Taxes\n   - SGST @ 9% under Duties & Taxes\n   - IGST @ 18% under Duties & Taxes\n\n3. Create Stock Item:\n   - Set GST rate on stock items\n   - Set HSN/SAC code\n\n4. Record GST Invoice:\n   - Create Sales Voucher (F8)\n   - Tax auto-calculates\n\n5. GST Reports:\n   - GSTR-1 (Sales Return)\n   - GSTR-3B (Monthly Summary)\n   - GSTR-2A (Purchase)\n\nGST Rates: 0%, 5%, 12%, 18%, 28%",None,2),
                    (cid,"note","Journal Entries in Tally","Basic Accounting Entries:\n\nCapital Introduced:\n  Cash A/c Dr.\n    To Capital A/c\n\nPurchase of Goods:\n  Purchase A/c Dr.\n    To Cash/Creditor A/c\n\nSales of Goods:\n  Cash/Debtor A/c Dr.\n    To Sales A/c\n\nPayment of Expenses:\n  Expense A/c Dr.\n    To Cash A/c\n\nDepreciation:\n  Depreciation A/c Dr.\n    To Asset A/c\n\nIn Tally:\n- F7 for Journal entry\n- Debit entry first, then credit\n- Golden Rules:\n  * Real A/c: Debit what comes in\n  * Personal A/c: Debit the receiver\n  * Nominal A/c: Debit all expenses",None,3),
                    (cid,"video","Tally Prime Complete Course for Beginners",None,"https://www.youtube.com/watch?v=3TDHzBnDHc0",4),
                    (cid,"video","GST in Tally Prime Full Tutorial",None,"https://www.youtube.com/watch?v=nkuCKaWJhIs",5),
                    (cid,"video","Tally Prime Payroll and TDS Tutorial",None,"https://www.youtube.com/watch?v=yqO3xh2D3RU",6),
                ]
            elif icon == "DA":
                materials += [
                    (cid,"note","Data Analysis Introduction","Data Analysis = Inspect + Clean + Model + Interpret data to find insights.\n\nData Analysis Process:\n1. Data Collection (CSV, Excel, Database, API)\n2. Data Cleaning (missing values, duplicates, format)\n3. Exploratory Data Analysis (EDA)\n4. Data Visualization (charts, graphs)\n5. Statistical Analysis\n6. Insights and Conclusions\n\nKey Python Libraries:\n- NumPy    : Numerical computing, arrays\n- Pandas   : Data manipulation and analysis\n- Matplotlib : Basic charts\n- Seaborn  : Statistical visualization\n- Plotly   : Interactive charts\n\nCommon Data Formats:\n- CSV  : Comma Separated Values\n- Excel (.xlsx) : Spreadsheets\n- JSON : JavaScript Object Notation\n- SQL  : Relational Databases",None,1),
                    (cid,"code","Pandas Data Analysis Example","import pandas as pd\nimport matplotlib.pyplot as plt\n\n# Load data from CSV\ndf = pd.read_csv(\'students.csv\')\n\n# Basic exploration\nprint(df.head())          # first 5 rows\nprint(df.shape)           # (rows, columns)\nprint(df.dtypes)          # data types\nprint(df.describe())      # statistics\nprint(df.isnull().sum())  # missing values\n\n# Clean data\ndf = df.dropna()                     # remove rows with NaN\ndf[\'marks\'] = pd.to_numeric(df[\'marks\'])  # fix data type\n\n# Filter\npassed = df[df[\'marks\'] >= 40]\nprint(f\'Passed: {len(passed)} students\')\n\n# Group and aggregate\navg = df.groupby(\'subject\')[\'marks\'].mean()\nprint(avg)\n\n# Visualization\nplt.figure(figsize=(10, 5))\n\nplt.subplot(1, 2, 1)\ndf[\'marks\'].hist(bins=10, color=\'steelblue\')\nplt.title(\'Marks Distribution\')\n\nplt.subplot(1, 2, 2)\navg.plot(kind=\'bar\', color=\'orange\')\nplt.title(\'Average by Subject\')\n\nplt.tight_layout()\nplt.savefig(\'analysis.png\')\nplt.show()",None,2),
                    (cid,"video","Data Analysis with Python Full Course",None,"https://www.youtube.com/watch?v=r-uOLxNrNk8",3),
                    (cid,"video","Pandas Tutorial for Beginners (Corey Schafer)",None,"https://www.youtube.com/watch?v=vmEHCJofslg",4),
                    (cid,"video","Power BI Full Tutorial for Beginners",None,"https://www.youtube.com/watch?v=3u7MQz1EyPY",5),
                ]
            else:
                materials += [
                    (cid,"note",f"Course Notes - {title}",f"Welcome to {title}!\n\nThis course is taught at Plustech Institute, Dombivli East.\n\nYour faculty has prepared detailed notes and practice materials for this course. Please check with your faculty for the latest notes.\n\nStudy Tips:\n- Attend all sessions regularly\n- Practice every day for at least 1-2 hours\n- Complete all assignments on time\n- Ask doubts immediately - never stay confused\n- Make short notes in your own words\n\nFor any queries:\nPhone: +91 91368 19666\nLocation: Dombivli East, Maharashtra\nWebsite: plustech-website.onrender.com",None,1),
                    (cid,"note","How to Use These Study Materials","How to Get the Best Out of This Course:\n\n1. NOTES SECTION\n   - Read notes carefully before each class\n   - These are concept summaries to help you understand\n   - Cross reference with your classroom notes\n\n2. CODE EXAMPLES\n   - Type the code yourself - do not just read it\n   - Run the code and see the output\n   - Modify the code and experiment\n   - This is how you truly learn programming\n\n3. VIDEO SECTION\n   - Watch the recommended videos\n   - Pause and practice along with the video\n   - Rewatch difficult concepts multiple times\n\n4. ASSIGNMENTS\n   - Complete all assignments given by faculty\n   - Submit on time\n\n5. DOUBT RESOLUTION\n   - Ask doubts in class or WhatsApp group\n   - Search on Google or Stack Overflow\n   - Practice makes you perfect!",None,2),
                    (cid,"video",f"Search: {title} Full Course Tutorial",None,f"https://www.youtube.com/results?search_query={title.replace(' ', '+')}+tutorial+beginners",3),
                ]
        if materials:
            c.executemany("INSERT INTO course_materials (course_id,type,title,content,url,order_num) VALUES (?,?,?,?,?,?)", materials)
            print(f"Seeded materials for all courses!")

    if c.execute("SELECT COUNT(*) FROM blogs").fetchone()[0] == 0:
        blogs = [
            ("Why Learn Python in 2026?","Python dominates the programming world. Here is why every student should learn it.","Python is versatile, readable, and in high demand across AI, web development, and data science.","Technology"),
            ("Top 5 Careers After Tally","Tally certification opens many doors in finance. Explore the top roles you can land.","After Tally Prime, you can work as accountant, GST consultant, billing executive and more.","Finance"),
            ("The Future of Web Development","React, Node.js and MERN stack are shaping the future. Are you ready?","Modern web development uses component-based architecture. Fullstack developers are highest paid.","Technology"),
            ("How Digital Marketing Launches Careers","Digital marketing is one of the fastest growing fields in India.","SEO, SEM, social media and Google Ads skills lead to great career opportunities.","Marketing"),
        ]
        c.executemany("INSERT INTO blogs (title,excerpt,content,category) VALUES (?,?,?,?)", blogs)

    conn.commit()
    conn.close()

def hash_password(pw):
    return hashlib.sha256((pw + JWT_SECRET).encode()).hexdigest()

def make_token(user_id, role):
    payload = {"id": user_id, "role": role, "exp": int(time.time()) + 7 * 24 * 3600}
    data = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()
    sig = hmac.new(JWT_SECRET.encode(), data.encode(), hashlib.sha256).hexdigest()
    return data + "." + sig

def verify_token(token):
    try:
        data, sig = token.rsplit(".", 1)
        expected = hmac.new(JWT_SECRET.encode(), data.encode(), hashlib.sha256).hexdigest()
        if sig != expected: return None
        payload = json.loads(base64.urlsafe_b64decode(data + "=="))
        if payload["exp"] < time.time(): return None
        return payload
    except: return None

def get_current_user():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "): return None
    return verify_token(auth[7:])

def require_admin():
    payload = get_current_user()
    if not payload or payload.get("role") != "admin": return None
    return payload

@app.route("/")
def index(): return send_from_directory("static", "index.html")
@app.route("/courses")
def courses_page(): return send_from_directory("static/pages", "courses.html")
@app.route("/about")
def about_page(): return send_from_directory("static/pages", "about.html")
@app.route("/contact")
def contact_page(): return send_from_directory("static/pages", "contact.html")
@app.route("/blog")
def blog_page(): return send_from_directory("static/pages", "blog.html")
@app.route("/login")
def login_page(): return send_from_directory("static/pages", "login.html")
@app.route("/register")
def register_page(): return send_from_directory("static/pages", "register.html")
@app.route("/dashboard")
def dashboard_page(): return send_from_directory("static/pages", "dashboard.html")
@app.route("/admin")
def admin_page(): return send_from_directory("static/pages", "admin.html")
@app.route("/learn")
def learn_page(): return send_from_directory("static/pages", "learn.html")

@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json()
    name = data.get("name","").strip()
    email = data.get("email","").strip()
    password = data.get("password","")
    phone = data.get("phone","")
    if not name or not email or not password:
        return jsonify({"error": "Name, email and password are required."}), 400
    conn = get_db()
    if conn.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone():
        conn.close()
        return jsonify({"error": "Email already registered."}), 409
    cur = conn.execute("INSERT INTO users (name,email,password,phone) VALUES (?,?,?,?)",
                       (name, email, hash_password(password), phone))
    conn.commit(); uid = cur.lastrowid; conn.close()
    return jsonify({"success": True, "token": make_token(uid, "student"), "user": {"id": uid, "name": name, "email": email, "role": "student"}})

@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email","").strip()
    password = data.get("password","")
    if not email or not password:
        return jsonify({"error": "Email and password required."}), 400
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    conn.close()
    if not user or user["password"] != hash_password(password):
        return jsonify({"error": "Invalid email or password."}), 401
    return jsonify({"success": True, "token": make_token(user["id"], user["role"]), "user": {"id": user["id"], "name": user["name"], "email": user["email"], "role": user["role"]}})

@app.route("/api/auth/me", methods=["GET"])
def me():
    payload = get_current_user()
    if not payload: return jsonify({"error": "Unauthorized"}), 401
    conn = get_db()
    user = conn.execute("SELECT id,name,email,phone,role,created_at FROM users WHERE id=?", (payload["id"],)).fetchone()
    conn.close()
    if not user: return jsonify({"error": "User not found"}), 404
    return jsonify(dict(user))

@app.route("/api/courses", methods=["GET"])
def get_courses():
    category = request.args.get("category")
    conn = get_db()
    if category and category != "All":
        rows = conn.execute("SELECT * FROM courses WHERE category=? ORDER BY id", (category,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM courses ORDER BY category, id").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/courses/<int:course_id>", methods=["GET"])
def get_course(course_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM courses WHERE id=?", (course_id,)).fetchone()
    conn.close()
    if not row: return jsonify({"error": "Not found"}), 404
    return jsonify(dict(row))

@app.route("/api/enrollments/my", methods=["GET"])
def my_enrollments():
    payload = get_current_user()
    if not payload: return jsonify({"error": "Unauthorized"}), 401
    conn = get_db()
    rows = conn.execute("""
        SELECT e.id, e.status, e.enrolled_at,
               c.id as course_id, c.title, c.category, c.duration, c.icon, c.description
        FROM enrollments e JOIN courses c ON e.course_id = c.id
        WHERE e.user_id=? ORDER BY e.enrolled_at DESC
    """, (payload["id"],)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/enrollments", methods=["POST"])
def enroll():
    payload = get_current_user()
    if not payload: return jsonify({"error": "Please login to enroll."}), 401
    data = request.get_json()
    course_id = data.get("course_id")
    if not course_id: return jsonify({"error": "Course ID required."}), 400
    conn = get_db()
    if conn.execute("SELECT id FROM enrollments WHERE user_id=? AND course_id=?", (payload["id"], course_id)).fetchone():
        conn.close()
        return jsonify({"error": "Already enrolled in this course."}), 409
    conn.execute("INSERT INTO enrollments (user_id,course_id) VALUES (?,?)", (payload["id"], course_id))
    conn.commit(); conn.close()
    return jsonify({"success": True, "message": "Enrolled! Our team will contact you shortly."})

@app.route("/api/enrollments/<int:enrollment_id>/materials", methods=["GET"])
def get_enrollment_materials(enrollment_id):
    payload = get_current_user()
    if not payload: return jsonify({"error": "Unauthorized"}), 401
    conn = get_db()
    enrollment = conn.execute("""
        SELECT e.id, e.status, e.course_id, c.title as course_title, c.category
        FROM enrollments e JOIN courses c ON e.course_id = c.id
        WHERE e.id=? AND e.user_id=?
    """, (enrollment_id, payload["id"])).fetchone()
    if not enrollment:
        conn.close()
        return jsonify({"error": "Enrollment not found."}), 404
    if enrollment["status"] != "active":
        conn.close()
        return jsonify({"error": "Access not granted yet. Please wait for admin approval.", "status": enrollment["status"]}), 403
    materials = conn.execute("""
        SELECT id, type, title, content, url, order_num
        FROM course_materials WHERE course_id=? ORDER BY order_num, id
    """, (enrollment["course_id"],)).fetchall()
    conn.close()
    return jsonify({"enrollment_id": enrollment_id, "course_title": enrollment["course_title"],
                    "category": enrollment["category"], "materials": [dict(m) for m in materials]})

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
    if not row: return jsonify({"error": "Not found"}), 404
    return jsonify(dict(row))

@app.route("/api/contact", methods=["POST"])
def contact():
    data = request.get_json()
    name = data.get("name","").strip()
    email = data.get("email","").strip()
    message = data.get("message","").strip()
    if not name or not email or not message:
        return jsonify({"error": "Name, email and message are required."}), 400
    conn = get_db()
    conn.execute("INSERT INTO contact_messages (name,email,phone,subject,message) VALUES (?,?,?,?,?)",
                 (name, email, data.get("phone",""), data.get("subject",""), message))
    conn.commit(); conn.close()
    return jsonify({"success": True, "message": "Message sent! We will contact you within 24 hours."})

@app.route("/api/admin/students", methods=["GET"])
def admin_students():
    if not require_admin(): return jsonify({"error": "Admins only."}), 403
    conn = get_db()
    rows = conn.execute("SELECT id,name,email,phone,role,created_at FROM users ORDER BY created_at DESC").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/admin/enrollments", methods=["GET"])
def admin_enrollments():
    if not require_admin(): return jsonify({"error": "Admins only."}), 403
    conn = get_db()
    rows = conn.execute("""
        SELECT e.id, e.status, e.enrolled_at,
               u.name as student_name, u.email, u.phone,
               c.title, c.category, c.duration, c.id as course_id
        FROM enrollments e
        JOIN users u ON e.user_id = u.id
        JOIN courses c ON e.course_id = c.id
        ORDER BY e.enrolled_at DESC
    """).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/admin/enrollments/<int:enrollment_id>/approve", methods=["PUT"])
def approve_enrollment(enrollment_id):
    if not require_admin(): return jsonify({"error": "Admins only."}), 403
    conn = get_db()
    if not conn.execute("SELECT id FROM enrollments WHERE id=?", (enrollment_id,)).fetchone():
        conn.close()
        return jsonify({"error": "Enrollment not found."}), 404
    conn.execute("UPDATE enrollments SET status=\'active\' WHERE id=?", (enrollment_id,))
    conn.commit(); conn.close()
    return jsonify({"success": True, "message": "Access granted! Student can now view course materials."})

@app.route("/api/admin/enrollments/<int:enrollment_id>/revoke", methods=["PUT"])
def revoke_enrollment(enrollment_id):
    if not require_admin(): return jsonify({"error": "Admins only."}), 403
    conn = get_db()
    conn.execute("UPDATE enrollments SET status=\'pending\' WHERE id=?", (enrollment_id,))
    conn.commit(); conn.close()
    return jsonify({"success": True, "message": "Access revoked."})

@app.route("/api/admin/enrollments/<int:enrollment_id>/complete", methods=["PUT"])
def complete_enrollment(enrollment_id):
    if not require_admin(): return jsonify({"error": "Admins only."}), 403
    conn = get_db()
    conn.execute("UPDATE enrollments SET status=\'completed\' WHERE id=?", (enrollment_id,))
    conn.commit(); conn.close()
    return jsonify({"success": True, "message": "Marked as completed."})

@app.route("/api/admin/messages", methods=["GET"])
def admin_messages():
    if not require_admin(): return jsonify({"error": "Admins only."}), 403
    conn = get_db()
    rows = conn.execute("SELECT * FROM contact_messages ORDER BY created_at DESC").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/admin/stats", methods=["GET"])
def admin_stats():
    if not require_admin(): return jsonify({"error": "Admins only."}), 403
    conn = get_db()
    stats = {
        "total_students": conn.execute("SELECT COUNT(*) FROM users WHERE role=\'student\'").fetchone()[0],
        "total_enrollments": conn.execute("SELECT COUNT(*) FROM enrollments").fetchone()[0],
        "pending_enrollments": conn.execute("SELECT COUNT(*) FROM enrollments WHERE status=\'pending\'").fetchone()[0],
        "active_enrollments": conn.execute("SELECT COUNT(*) FROM enrollments WHERE status=\'active\'").fetchone()[0],
        "total_messages": conn.execute("SELECT COUNT(*) FROM contact_messages").fetchone()[0],
        "total_courses": conn.execute("SELECT COUNT(*) FROM courses").fetchone()[0],
    }
    conn.close()
    return jsonify(stats)

if __name__ == "__main__":
    init_db()
    print("")
    print("=========================================")
    print("  Plustech -> http://localhost:3000")
    print("  Admin    -> admin@plustech.in / Admin@123")
    print("=========================================")
    print("")
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port, debug=False)
