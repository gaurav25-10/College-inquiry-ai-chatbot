"""
=============================================================
  COLLEGE INQUIRY CHATBOT - Main Application (app.py)
=============================================================
  This is the HEART of our project.
  
  WHAT IS FLASK?
  Flask is a Python web framework. Think of it like this:
  - Your browser asks a question  →  Flask receives it
  - Flask processes it            →  Flask sends back an answer
  - It's like a waiter in a restaurant — takes your order,
    goes to the kitchen, brings back food!

  HOW THIS FILE WORKS:
  1. We import libraries (tools we need)
  2. We set up our database
  3. We create "routes" — URLs that do specific things
  4. We run the app

=============================================================
"""

# ── IMPORTS ──────────────────────────────────────────────
# These are like "importing tools from a toolbox"

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import sqlite3          # Built-in Python tool to work with SQLite database
import json             # For handling JSON data (how computers share info)
import os              # For file/folder operations
import hashlib         # For password hashing (security)
import requests         # For making HTTP requests to the AI API
from datetime import datetime  # For timestamps
import re              # Regular expressions (text pattern matching)

# ── CREATE THE FLASK APP ──────────────────────────────────
# This one line creates our entire web application!
app = Flask(__name__)

# Secret key for sessions (like a password to keep sessions secure)
# In production, use a long random string!
app.secret_key = "college_chatbot_secret_key_2024_change_this"

# ── DATABASE SETUP ────────────────────────────────────────
# SQLite database file path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "college.db")

# ── ANTHROPIC API SETUP ───────────────────────────────────
# This is the AI "brain" — we call Claude API to get smart answers
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "").strip()

# ══════════════════════════════════════════════════════════
#  DATABASE FUNCTIONS
#  These functions handle all database operations
# ══════════════════════════════════════════════════════════

def get_db_connection():
    """
    WHAT THIS DOES: Opens a connection to our SQLite database.
    Think of it like "opening a filing cabinet" to read/write files.
    
    'Row' makes results behave like dictionaries:
    Instead of result[0], you can write result['name'] — much easier!
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn


def init_database():
    """
    WHAT THIS DOES: Creates all our database tables if they don't exist yet.
    It's like setting up empty filing folders before you start filing papers.
    
    DATABASE TABLES WE CREATE:
    1. college_info     — General college information
    2. courses          — All courses offered
    3. admissions       — Admission process details
    4. fees             — Fee structure
    5. faculty          — Faculty information
    6. facilities       — Campus facilities
    7. faqs             — Frequently asked questions
    8. chat_history     — Stores all conversations
    9. admin_users      — Admin login accounts
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # ── TABLE 1: College General Info ─────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS college_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT NOT NULL,
            category TEXT DEFAULT 'general',
            last_updated TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── TABLE 2: Courses ──────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT UNIQUE,
            duration TEXT,
            degree_type TEXT,
            department TEXT,
            description TEXT,
            eligibility TEXT,
            seats INTEGER,
            is_active INTEGER DEFAULT 1,
            last_updated TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── TABLE 3: Admissions ───────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT NOT NULL,
            category TEXT DEFAULT 'general',
            last_updated TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── TABLE 4: Fees ─────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_name TEXT NOT NULL,
            annual_fee REAL,
            semester_fee REAL,
            admission_fee REAL,
            other_charges TEXT,
            scholarship_available INTEGER DEFAULT 0,
            last_updated TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── TABLE 5: Faculty ──────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS faculty (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            designation TEXT,
            department TEXT,
            qualification TEXT,
            experience_years INTEGER,
            email TEXT,
            specialization TEXT,
            is_active INTEGER DEFAULT 1,
            last_updated TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── TABLE 6: Facilities ───────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS facilities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            category TEXT,
            is_available INTEGER DEFAULT 1,
            last_updated TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── TABLE 7: FAQs ─────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS faqs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            category TEXT DEFAULT 'general',
            is_active INTEGER DEFAULT 1,
            last_updated TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── TABLE 8: Chat History ─────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            user_message TEXT NOT NULL,
            bot_response TEXT NOT NULL,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            user_ip TEXT
        )
    """)

    # ── TABLE 9: Admin Users ──────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            email TEXT,
            last_login TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Database tables created successfully!")


def seed_sample_data():
    """
    WHAT THIS DOES: Fills the database with sample data so the chatbot
    has information to work with from day one.
    
    Think of it like filling a new filing cabinet with starter documents.
    The admin can edit/add more data later through the admin panel.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # ── College Info ──────────────────────────────────────
    college_data = [
        ("college_name", "Uttarakhand Institute of Technology & Management", "general"),
        ("established", "1995", "general"),
        ("location", "Rishikesh, Uttarakhand", "general"),
        ("phone", "+91-120-4567890, +91-9876543210", "contact"),
        ("email", "info@utk.edu.in", "contact"),
        ("website", "www.utk.edu.in", "contact"),
        ("principal", "Dr. Rajesh Kumar Sharma", "administration"),
        ("affiliation", "Dr. A.P.J. Abdul Kalam Technical University (AKTU), Lucknow", "academic"),
        ("accreditation", "NAAC 'A' Grade, NBA Accredited", "academic"),
        ("campus_area", "25 acres", "infrastructure"),
        ("total_students", "5000+", "general"),
        ("total_faculty", "200+", "general"),
        ("hostel", "Available for both boys and girls with 24/7 security", "facilities"),
        ("library_books", "50,000+ books and 100+ journals", "facilities"),
        ("placement_rate", "92% placement rate (2023 batch)", "placement"),
        ("top_recruiters", "TCS, Infosys, Wipro, HCL, Accenture, Cognizant, IBM, Amazon", "placement"),
        ("address", "Uttarakhand Institute of Technology & Management, Rishikesh, Uttarakhand", "contact"),
        ("timing", "Monday to Saturday: 8:00 AM to 5:00 PM", "general"),
        ("vision", "To be a world-class institution imparting quality technical education", "general"),
        ("mission", "To produce competent engineers and managers who contribute to society", "general"),
    ]

    for key, value, category in college_data:
        cursor.execute("""
            INSERT OR IGNORE INTO college_info (key, value, category)
            VALUES (?, ?, ?)
        """, (key, value, category))

    # ── Courses ───────────────────────────────────────────
    courses_data = [
        ("B.Tech Computer Science Engineering", "CSE", "4 Years", "B.Tech", "Engineering", 
         "Covers programming, algorithms, AI, web development, databases, and software engineering.",
         "10+2 with Physics, Chemistry, Math (PCM) with min 45% marks. JEE Mains score required.", 120),
        
        ("B.Tech Electronics & Communication", "ECE", "4 Years", "B.Tech", "Engineering",
         "Covers electronics, communication systems, VLSI, embedded systems, and signal processing.",
         "10+2 with PCM, min 45% marks. JEE Mains score required.", 60),
        
        ("B.Tech Mechanical Engineering", "ME", "4 Years", "B.Tech", "Engineering",
         "Covers thermodynamics, fluid mechanics, manufacturing, CAD/CAM, and machine design.",
         "10+2 with PCM, min 45% marks. JEE Mains score required.", 60),
        
        ("B.Tech Civil Engineering", "CE", "4 Years", "B.Tech", "Engineering",
         "Covers structural engineering, construction management, environmental engineering, and surveying.",
         "10+2 with PCM, min 45% marks. JEE Mains score required.", 60),
        
        ("B.Tech Artificial Intelligence & ML", "AIML", "4 Years", "B.Tech", "Engineering",
         "Covers machine learning, deep learning, NLP, computer vision, data science, and AI ethics.",
         "10+2 with PCM, min 50% marks. JEE Mains score required.", 60),
        
        ("MBA (Master of Business Administration)", "MBA", "2 Years", "Post Graduate", "Management",
         "Covers marketing, finance, HR, operations, entrepreneurship, and business strategy.",
         "Graduation in any stream with min 50% marks. CAT/MAT/CMAT score required.", 120),
        
        ("MCA (Master of Computer Applications)", "MCA", "3 Years", "Post Graduate", "Computer Science",
         "Advanced programming, software engineering, database management, and project management.",
         "BCA or B.Sc (CS/IT) with Mathematics with min 50% marks.", 60),
        
        ("B.Sc Computer Science", "BSC-CS", "3 Years", "B.Sc", "Science",
         "Covers programming languages, data structures, operating systems, networking, and databases.",
         "10+2 with Mathematics/Computer Science, min 45% marks.", 60),
        
        ("BCA (Bachelor of Computer Applications)", "BCA", "3 Years", "BCA", "Computer Science",
         "Application development, web technologies, database, software development methodologies.",
         "10+2 in any stream with Mathematics, min 45% marks.", 60),
        
        ("Diploma in Computer Science", "DIP-CS", "3 Years", "Diploma", "Engineering",
         "Practical-oriented diploma covering programming, hardware, networking basics.",
         "10th pass with min 35% marks.", 60),
    ]

    for course in courses_data:
        cursor.execute("""
            INSERT OR IGNORE INTO courses 
            (name, code, duration, degree_type, department, description, eligibility, seats)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, course)

    # ── Admissions ────────────────────────────────────────
    admission_data = [
        ("admission_process", "1. Fill online application form at website\n2. Upload required documents\n3. Pay application fee ₹500\n4. Appear for counseling/interview\n5. Receive admission letter\n6. Pay fees and confirm seat", "process"),
        ("documents_required", "1. 10th Marksheet & Certificate\n2. 12th Marksheet & Certificate\n3. Transfer Certificate (TC)\n4. Character Certificate\n5. Migration Certificate\n6. Aadhar Card\n7. 4 Passport Size Photos\n8. Category Certificate (if applicable)\n9. JEE/CAT Score Card", "documents"),
        ("admission_last_date_btech", "July 31, 2024 (B.Tech Programs)", "dates"),
        ("admission_last_date_mba", "August 15, 2024 (MBA Program)", "dates"),
        ("counseling_date", "First week of August 2024", "dates"),
        ("classes_start", "August 1, 2024", "dates"),
        ("application_fee", "₹500 (Non-refundable)", "fees"),
        ("helpline", "+91-120-4567890 (9 AM to 5 PM, Mon-Sat)", "contact"),
        ("reservation_policy", "SC: 15%, ST: 7.5%, OBC: 27%, EWS: 10%, General: 40.5% as per UP Government norms", "policy"),
        ("lateral_entry", "Available for Diploma holders in B.Tech 2nd year (Direct 2nd Year admission)", "policy"),
    ]

    for key, value, category in admission_data:
        cursor.execute("""
            INSERT OR IGNORE INTO admissions (key, value, category)
            VALUES (?, ?, ?)
        """, (key, value, category))

    # ── Fees ──────────────────────────────────────────────
    fees_data = [
        ("B.Tech (All Branches)", 125000, 62500, 15000, "Exam Fee: ₹2000/semester, Library: ₹1000/year", 1),
        ("B.Tech AIML", 140000, 70000, 15000, "Lab Fee: ₹3000/semester, Software: ₹2000/year", 1),
        ("MBA", 95000, 47500, 10000, "Study Material: ₹5000/semester", 1),
        ("MCA", 85000, 42500, 10000, "Software Lab: ₹2000/semester", 1),
        ("BCA", 55000, 27500, 8000, "Lab Fee: ₹1500/semester", 1),
        ("B.Sc CS", 45000, 22500, 7000, "Lab Fee: ₹1000/semester", 1),
        ("Diploma (Engineering)", 65000, 32500, 8000, "Workshop Fee: ₹2000/semester", 0),
    ]

    for fee in fees_data:
        cursor.execute("""
            INSERT OR IGNORE INTO fees 
            (course_name, annual_fee, semester_fee, admission_fee, other_charges, scholarship_available)
            VALUES (?, ?, ?, ?, ?, ?)
        """, fee)

    # ── Faculty ───────────────────────────────────────────
    faculty_data = [
        ("Dr. Priya Sharma", "Professor & HOD", "Computer Science", "Ph.D (IIT Delhi)", 18, "priya.sharma@sunrisetech.edu.in", "Machine Learning, AI"),
        ("Dr. Amit Verma", "Associate Professor", "Computer Science", "Ph.D (NIT Allahabad)", 12, "amit.verma@sunrisetech.edu.in", "Databases, Cloud Computing"),
        ("Prof. Sunita Gupta", "Assistant Professor", "Computer Science", "M.Tech (BITS Pilani)", 8, "sunita.gupta@sunrisetech.edu.in", "Web Development, Python"),
        ("Dr. Rakesh Singh", "Professor & HOD", "Electronics", "Ph.D (IIT Kanpur)", 20, "rakesh.singh@sunrisetech.edu.in", "VLSI, Embedded Systems"),
        ("Dr. Meena Patel", "Professor", "Management", "Ph.D (IIM Lucknow)", 15, "meena.patel@sunrisetech.edu.in", "Marketing, Strategy"),
        ("Prof. Vivek Kumar", "Assistant Professor", "Mechanical", "M.Tech (IIT BHU)", 6, "vivek.kumar@sunrisetech.edu.in", "CAD/CAM, Robotics"),
    ]

    for faculty in faculty_data:
        cursor.execute("""
            INSERT OR IGNORE INTO faculty
            (name, designation, department, qualification, experience_years, email, specialization)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, faculty)

    # ── Facilities ────────────────────────────────────────
    facilities_data = [
        ("Computer Labs", "10 modern computer labs with 500+ computers, high-speed internet, latest software", "academic", 1),
        ("Central Library", "50,000+ books, e-library access, NPTEL, Coursera subscriptions, reading hall for 300 students", "academic", 1),
        ("Boys Hostel", "3 hostels with 1000 capacity, Wi-Fi, TV room, gym, mess with hygienic food", "accommodation", 1),
        ("Girls Hostel", "2 hostels with 600 capacity, 24/7 security, CCTV, Wi-Fi, mess facility", "accommodation", 1),
        ("Sports Complex", "Cricket ground, football field, basketball court, indoor badminton, table tennis, gym", "sports", 1),
        ("Canteen", "Multiple canteens with hygienic food, vegetarian & non-vegetarian options, 24/7 availability", "food", 1),
        ("Medical Center", "Full-time doctor, nurse, ambulance facility, first aid, tie-up with nearby hospitals", "health", 1),
        ("Auditorium", "1200 capacity AC auditorium for events, seminars, cultural programs", "events", 1),
        ("Transport", "College buses covering 30+ routes across city, GPS tracked, safe and reliable", "transport", 1),
        ("Wi-Fi Campus", "Entire campus covered with high-speed Wi-Fi (100 Mbps), student access with ID", "tech", 1),
        ("ATM", "SBI and PNB ATM on campus, 24/7 access", "finance", 1),
        ("Placement Cell", "Dedicated placement office, interview rooms, video conferencing for online interviews", "placement", 1),
    ]

    for facility in facilities_data:
        cursor.execute("""
            INSERT OR IGNORE INTO facilities (name, description, category, is_available)
            VALUES (?, ?, ?, ?)
        """, facility)

    # ── FAQs ──────────────────────────────────────────────
    faq_data = [
        ("What is the last date to apply?", "For B.Tech: July 31, 2024. For MBA/MCA: August 15, 2024. Apply early to avoid last-minute rush!", "admission"),
        ("Is hostel facility available?", "Yes! We have separate hostels for boys (1000 capacity) and girls (600 capacity) with all modern amenities.", "facilities"),
        ("What is the fee structure?", "B.Tech fees are ₹1.25 lakh/year. MBA is ₹95,000/year. Scholarships available based on merit and category.", "fees"),
        ("Is there a scholarship?", "Yes! Merit scholarships for top rankers. Government scholarships for SC/ST/OBC students. Sports quota available.", "fees"),
        ("What is the placement record?", "92% placement in 2023 batch. Average package: ₹4.5 LPA. Highest: ₹18 LPA. Top companies: TCS, Infosys, Wipro.", "placement"),
        ("How to reach the college?", "Located in Knowledge Park-II, Greater Noida. Nearest metro: Pari Chowk (2 km). College buses from 30+ locations.", "general"),
        ("Is the college AICTE approved?", "Yes, fully AICTE approved and affiliated to AKTU. NAAC 'A' grade accredited.", "general"),
        ("Can I apply without JEE score?", "JEE is preferred but not mandatory for some programs. Management quota seats available. Contact admissions office.", "admission"),
        ("What documents are needed for admission?", "10th & 12th marksheets, TC, CC, Migration Certificate, Aadhar Card, 4 photos, Category certificate if applicable.", "admission"),
        ("Are there any entrance exams?", "B.Tech: JEE Mains. MBA: CAT/MAT/CMAT. MCA: NIMCET or equivalent. B.Sc/BCA: Direct admission on merit.", "admission"),
    ]

    for faq in faq_data:
        cursor.execute("""
            INSERT OR IGNORE INTO faqs (question, answer, category)
            VALUES (?, ?, ?)
        """, faq)

    # ── Default Admin User ─────────────────────────────────
    # Password: admin123 (hashed for security)
    admin_password = hashlib.sha256("admin123".encode()).hexdigest()
    cursor.execute("""
        INSERT OR IGNORE INTO admin_users (username, password_hash, full_name, email)
        VALUES (?, ?, ?, ?)
    """, ("admin", admin_password, "System Administrator", "admin@uttarakhandtech.edu.in"))

    conn.commit()
    conn.close()
    print("✅ Sample data inserted successfully!")


def get_all_college_data():
    """
    WHAT THIS DOES: Fetches ALL data from ALL tables and organizes it
    into a single dictionary. This data is then sent to the AI
    so it can answer questions intelligently.
    
    Think of it as: "Giving the AI a complete fact sheet about the college"
    """
    conn = get_db_connection()

    # Fetch all data from each table
    college_info = conn.execute("SELECT key, value, category FROM college_info").fetchall()
    courses = conn.execute("SELECT * FROM courses WHERE is_active=1").fetchall()
    admissions = conn.execute("SELECT key, value, category FROM admissions").fetchall()
    fees = conn.execute("SELECT * FROM fees").fetchall()
    faculty = conn.execute("SELECT * FROM faculty WHERE is_active=1").fetchall()
    facilities = conn.execute("SELECT * FROM facilities WHERE is_available=1").fetchall()
    faqs = conn.execute("SELECT question, answer, category FROM faqs WHERE is_active=1").fetchall()

    conn.close()

    # Convert to dictionaries for easy use
    data = {
        "college_info": {row['key']: row['value'] for row in college_info},
        "courses": [dict(row) for row in courses],
        "admissions": {row['key']: row['value'] for row in admissions},
        "fees": [dict(row) for row in fees],
        "faculty": [dict(row) for row in faculty],
        "facilities": [dict(row) for row in facilities],
        "faqs": [{"q": row['question'], "a": row['answer']} for row in faqs],
    }
    return data


def _money(value):
    """Formats rupee amounts from the database in a student-friendly way."""
    if value in (None, ""):
        return "N/A"
    try:
        amount = float(value)
        return f"Rs. {amount:,.0f}"
    except (TypeError, ValueError):
        return str(value)


def _find_course(college_data, message):
    """Returns the best matching course row for a user message, if any."""
    text = message.lower()
    for course in college_data["courses"]:
        haystack = " ".join([
            str(course.get("name", "")),
            str(course.get("code", "")),
            str(course.get("department", "")),
            str(course.get("degree_type", "")),
        ]).lower()
        tokens = [
            str(course.get("name", "")).lower(),
            str(course.get("code", "")).lower(),
            str(course.get("department", "")).lower(),
        ]
        if any(token and token in text for token in tokens) or any(word in haystack for word in text.split()):
            return course
    return None


def answer_from_database(user_message, college_data):
    """
    Creates a useful answer directly from SQLite when the AI API is unavailable.
    This keeps the chatbot working for demos and local development.
    """
    text = user_message.lower()
    college_info = college_data["college_info"]
    contact = college_info.get("phone") or college_info.get("contact") or "the admissions office"
    email = college_info.get("email", "")
    contact_line = f"For more help, contact {contact}" + (f" or email {email}." if email else ".")

    faq_matches = []
    for faq in college_data["faqs"]:
        question = faq["q"].lower()
        overlap = set(re.findall(r"[a-zA-Z0-9]+", text)) & set(re.findall(r"[a-zA-Z0-9]+", question))
        if len(overlap) >= 2 or question in text or text in question:
            faq_matches.append((len(overlap), faq))
    if faq_matches:
        faq_matches.sort(key=lambda item: item[0], reverse=True)
        return faq_matches[0][1]["a"]

    if any(word in text for word in ["course", "courses", "b.tech", "btech", "program", "programs", "branch", "branches"]):
        course = _find_course(college_data, user_message)
        if course:
            parts = [
                f"{course.get('name')} ({course.get('code', 'N/A')})",
                f"Duration: {course.get('duration', 'N/A')}",
                f"Department: {course.get('department', 'N/A')}",
                f"Eligibility: {course.get('eligibility', 'N/A')}",
                f"Seats: {course.get('seats', 'N/A')}",
            ]
            if course.get("description"):
                parts.append(course["description"])
            return "\n".join(parts)

        if college_data["courses"]:
            lines = ["Courses available:"]
            for course in college_data["courses"]:
                detail = f"- {course.get('name')}"
                if course.get("degree_type"):
                    detail += f" ({course.get('degree_type')})"
                if course.get("duration"):
                    detail += f" - {course.get('duration')}"
                lines.append(detail)
            return "\n".join(lines)

    if any(word in text for word in ["fee", "fees", "cost", "tuition", "charges"]):
        course = _find_course(college_data, user_message)
        rows = college_data["fees"]
        if course:
            rows = [row for row in rows if course.get("name", "").lower() in str(row.get("course_name", "")).lower()]
        if rows:
            lines = ["Fee structure:"]
            for fee in rows:
                lines.append(
                    f"- {fee.get('course_name')}: annual {_money(fee.get('annual_fee'))}, "
                    f"semester {_money(fee.get('semester_fee'))}, admission {_money(fee.get('admission_fee'))}"
                )
                if fee.get("scholarship_available"):
                    lines.append("  Scholarship options are available.")
            return "\n".join(lines)

    if any(word in text for word in ["admission", "apply", "eligibility", "process", "document", "documents"]):
        if college_data["admissions"]:
            lines = ["Admission information:"]
            for key, value in college_data["admissions"].items():
                lines.append(f"- {key.replace('_', ' ').title()}: {value}")
            return "\n".join(lines)

    if any(word in text for word in ["facility", "facilities", "hostel", "library", "lab", "campus"]):
        if college_data["facilities"]:
            lines = ["Campus facilities:"]
            for facility in college_data["facilities"]:
                detail = f"- {facility.get('name')}"
                if facility.get("description"):
                    detail += f": {facility.get('description')}"
                lines.append(detail)
            return "\n".join(lines)

    if any(word in text for word in ["faculty", "teacher", "professor", "staff"]):
        if college_data["faculty"]:
            lines = ["Faculty members:"]
            for member in college_data["faculty"]:
                detail = f"- {member.get('name')}"
                if member.get("designation"):
                    detail += f", {member.get('designation')}"
                if member.get("department"):
                    detail += f" ({member.get('department')})"
                lines.append(detail)
            return "\n".join(lines)

    if any(word in text for word in ["contact", "phone", "email", "address", "location"]):
        lines = [college_info.get("college_name", "College contact details")]
        for key in ["phone", "email", "address", "website"]:
            if college_info.get(key):
                lines.append(f"{key.title()}: {college_info[key]}")
        return "\n".join(lines)

    return f"I found the college database, but I do not have that specific information yet. {contact_line}"


# ══════════════════════════════════════════════════════════
#  MAIN ROUTES (Pages of our website)
# ══════════════════════════════════════════════════════════

@app.route("/")
def home():
    """
    ROUTE: / (homepage)
    WHAT: Shows the main chatbot interface to users.
    
    In Flask, @app.route("/") means:
    "When someone visits our website's main page, run this function"
    """
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    """
    ROUTE: /chat (POST only — receives data, doesn't show a page)
    WHAT: This is where the magic happens!
    
    1. Receives user's message from the browser
    2. Gets all college data from database
    3. Sends message + college data to Claude AI
    4. Returns AI's response back to browser
    5. Saves conversation to database
    
    POST method means: this route only accepts form submissions/data,
    not regular page visits.
    """
    data = request.get_json()  # Get data sent from JavaScript
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    # Get conversation history from session (for context)
    # 'session' is like a temporary memory for each user
    conversation_history = session.get("chat_history", [])

    # Get all college data from database
    college_data = get_all_college_data()

    # Build the system prompt (instructions for the AI)
    # This tells Claude HOW to behave and WHAT data it has
    system_prompt = f"""You are an intelligent and friendly AI admission counselor and inquiry assistant for {college_data['college_info'].get('college_name', 'our college')}.

Your role is to help prospective students, parents, and visitors with accurate information about the college.

## COLLEGE DATABASE (Use this to answer questions accurately):

### COLLEGE INFORMATION:
{json.dumps(college_data['college_info'], indent=2)}

### COURSES OFFERED:
{json.dumps(college_data['courses'], indent=2)}

### ADMISSION DETAILS:
{json.dumps(college_data['admissions'], indent=2)}

### FEE STRUCTURE:
{json.dumps(college_data['fees'], indent=2)}

### FACULTY:
{json.dumps(college_data['faculty'], indent=2)}

### FACILITIES:
{json.dumps(college_data['facilities'], indent=2)}

### FREQUENTLY ASKED QUESTIONS:
{json.dumps(college_data['faqs'], indent=2)}

## INSTRUCTIONS:
1. ALWAYS use the database information above to answer questions accurately
2. Be warm, helpful, and encouraging — students are often nervous about admissions
3. If asked about something not in the database, say "I don't have that specific information right now. Please contact our admissions office at {college_data['college_info'].get('phone', 'our helpline')} or email {college_data['college_info'].get('email', 'our email')}"
4. Format responses clearly with bullet points or numbered lists when listing multiple items
5. Keep responses concise but complete (not too short, not too long)
6. Always offer to help with more questions
7. For fees, always mention scholarship possibilities
8. Be proactive — if someone asks about a course, also mention related admission info
9. Respond in the same language the user writes in (Hindi or English)
10. Never make up information not in the database
11. Use emojis occasionally to make responses friendly (📚 🎓 ✅ 💡)

## PERSONALITY:
- Warm, professional, encouraging
- Patient with repeated questions
- Always positive about the college
- Honest about limitations
"""

    # Prepare the messages for Claude API
    # We include conversation history for context
    messages = conversation_history[-10:]  # Last 10 messages for context
    messages.append({"role": "user", "content": user_message})

    # Call Claude AI API only when a key is configured.
    if not ANTHROPIC_API_KEY:
        bot_reply = answer_from_database(user_message, college_data)
    else:
        try:
            response = requests.post(
                ANTHROPIC_API_URL,
                headers={
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01",
                    "x-api-key": ANTHROPIC_API_KEY
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 1024,
                    "system": system_prompt,
                    "messages": messages
                },
                timeout=30
            )

            if response.status_code == 200:
                response_data = response.json()
                bot_reply = response_data["content"][0]["text"]
            else:
                print(f"Anthropic API error {response.status_code}: {response.text[:300]}")
                bot_reply = answer_from_database(user_message, college_data)

        except Exception as e:
            print(f"Anthropic API request failed: {e}")
            bot_reply = answer_from_database(user_message, college_data)

    # Update conversation history in session
    conversation_history.append({"role": "user", "content": user_message})
    conversation_history.append({"role": "assistant", "content": bot_reply})
    session["chat_history"] = conversation_history[-20:]  # Keep last 20 messages

    # Save to database for analytics
    try:
        conn = get_db_connection()
        conn.execute("""
            INSERT INTO chat_history (session_id, user_message, bot_response, user_ip)
            VALUES (?, ?, ?, ?)
        """, (
            session.get("session_id", "anonymous"),
            user_message,
            bot_reply,
            request.remote_addr
        ))
        conn.commit()
        conn.close()
    except:
        pass  # Don't fail the response if logging fails

    return jsonify({"reply": bot_reply})


@app.route("/clear_chat", methods=["POST"])
def clear_chat():
    """Clears the conversation history for a fresh start"""
    session.pop("chat_history", None)
    return jsonify({"status": "cleared"})


# ══════════════════════════════════════════════════════════
#  ADMIN PANEL ROUTES
# ══════════════════════════════════════════════════════════

@app.route("/admin")
def admin_login():
    """Shows the admin login page"""
    if session.get("admin_logged_in"):
        return redirect(url_for("admin_dashboard"))
    return render_template("admin_login.html")


@app.route("/admin/login", methods=["POST"])
def admin_authenticate():
    """
    WHAT THIS DOES: Checks if username and password are correct.
    We hash the password (convert to a secret code) and compare.
    Never store plain passwords in database — always hash them!
    """
    username = request.form.get("username")
    password = request.form.get("password")

    # Hash the entered password to compare with stored hash
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    conn = get_db_connection()
    admin = conn.execute("""
        SELECT * FROM admin_users WHERE username=? AND password_hash=?
    """, (username, password_hash)).fetchone()

    if admin:
        session["admin_logged_in"] = True
        session["admin_username"] = username
        # Update last login time
        conn.execute("UPDATE admin_users SET last_login=? WHERE username=?",
                    (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), username))
        conn.commit()
        conn.close()
        return redirect(url_for("admin_dashboard"))
    else:
        conn.close()
        flash("❌ Invalid username or password!", "error")
        return redirect(url_for("admin_login"))


@app.route("/admin/logout")
def admin_logout():
    """Logs out the admin"""
    session.pop("admin_logged_in", None)
    session.pop("admin_username", None)
    return redirect(url_for("admin_login"))


def admin_required(f):
    """
    DECORATOR: This is a security wrapper.
    Any route with @admin_required will check if admin is logged in first.
    If not, redirect to login page.
    
    Think of it as a security guard at every door!
    """
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin_logged_in"):
            flash("Please login first!", "warning")
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    """Admin dashboard showing statistics"""
    conn = get_db_connection()
    
    stats = {
        "total_chats": conn.execute("SELECT COUNT(*) FROM chat_history").fetchone()[0],
        "today_chats": conn.execute(
            "SELECT COUNT(*) FROM chat_history WHERE DATE(timestamp)=DATE('now')"
        ).fetchone()[0],
        "total_courses": conn.execute("SELECT COUNT(*) FROM courses WHERE is_active=1").fetchone()[0],
        "total_faculty": conn.execute("SELECT COUNT(*) FROM faculty WHERE is_active=1").fetchone()[0],
        "total_faqs": conn.execute("SELECT COUNT(*) FROM faqs WHERE is_active=1").fetchone()[0],
    }
    
    recent_chats = conn.execute("""
        SELECT user_message, bot_response, timestamp 
        FROM chat_history 
        ORDER BY timestamp DESC 
        LIMIT 10
    """).fetchall()
    
    conn.close()
    return render_template("admin_dashboard.html", stats=stats, recent_chats=recent_chats)


# ── CRUD for College Info ─────────────────────────────────

@app.route("/admin/college-info")
@admin_required
def admin_college_info():
    conn = get_db_connection()
    data = conn.execute("SELECT * FROM college_info ORDER BY category, key").fetchall()
    conn.close()
    return render_template("admin_table.html", 
                          title="College Information",
                          table="college_info",
                          data=data,
                          columns=["id", "key", "value", "category", "last_updated"])


@app.route("/admin/courses")
@admin_required
def admin_courses():
    conn = get_db_connection()
    data = conn.execute("SELECT * FROM courses ORDER BY degree_type, name").fetchall()
    conn.close()
    return render_template("admin_courses.html", data=data)


@app.route("/admin/fees")
@admin_required
def admin_fees():
    conn = get_db_connection()
    data = conn.execute("SELECT * FROM fees ORDER BY course_name").fetchall()
    conn.close()
    return render_template("admin_table.html",
                          title="Fee Structure",
                          table="fees",
                          data=data,
                          columns=["id", "course_name", "annual_fee", "semester_fee", "admission_fee", "scholarship_available"])


@app.route("/admin/faqs")
@admin_required
def admin_faqs():
    conn = get_db_connection()
    data = conn.execute("SELECT * FROM faqs ORDER BY category").fetchall()
    conn.close()
    return render_template("admin_faqs.html", data=data)


@app.route("/admin/faculty")
@admin_required
def admin_faculty():
    conn = get_db_connection()
    data = conn.execute("SELECT * FROM faculty ORDER BY department, name").fetchall()
    conn.close()
    return render_template("admin_faculty.html", data=data)


# ── Generic API endpoints for CRUD operations ─────────────

@app.route("/admin/api/update", methods=["POST"])
@admin_required
def admin_update():
    """
    WHAT THIS DOES: Updates any record in any table.
    The admin panel calls this when saving changes.
    
    It receives: table name, record ID, and new values
    """
    data = request.get_json()
    table = data.get("table")
    record_id = data.get("id")
    fields = data.get("fields", {})

    # Security: Only allow these tables to be updated
    allowed_tables = ["college_info", "courses", "admissions", "fees", "faculty", "facilities", "faqs"]
    if table not in allowed_tables:
        return jsonify({"error": "Table not allowed"}), 403

    # Build the UPDATE SQL dynamically
    # For example: UPDATE courses SET name=?, duration=? WHERE id=?
    set_clause = ", ".join([f"{k}=?" for k in fields.keys()])
    values = list(fields.values()) + [record_id]
    
    # Add last_updated timestamp
    if "last_updated" not in fields:
        set_clause += ", last_updated=?"
        values = list(fields.values()) + [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), record_id]

    try:
        conn = get_db_connection()
        conn.execute(f"UPDATE {table} SET {set_clause} WHERE id=?", values)
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Updated successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/admin/api/add", methods=["POST"])
@admin_required
def admin_add():
    """Adds a new record to a table"""
    data = request.get_json()
    table = data.get("table")
    fields = data.get("fields", {})

    allowed_tables = ["college_info", "courses", "admissions", "fees", "faculty", "facilities", "faqs"]
    if table not in allowed_tables:
        return jsonify({"error": "Table not allowed"}), 403

    columns = ", ".join(fields.keys())
    placeholders = ", ".join(["?" for _ in fields])
    values = list(fields.values())

    try:
        conn = get_db_connection()
        conn.execute(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", values)
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Added successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/admin/api/delete", methods=["POST"])
@admin_required
def admin_delete():
    """Deletes a record from a table"""
    data = request.get_json()
    table = data.get("table")
    record_id = data.get("id")

    allowed_tables = ["college_info", "courses", "admissions", "fees", "faculty", "facilities", "faqs"]
    if table not in allowed_tables:
        return jsonify({"error": "Table not allowed"}), 403

    try:
        conn = get_db_connection()
        conn.execute(f"DELETE FROM {table} WHERE id=?", [record_id])
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Deleted successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/admin/api/get-record")
@admin_required
def get_record():
    """Gets a single record for editing"""
    table = request.args.get("table")
    record_id = request.args.get("id")

    allowed_tables = ["college_info", "courses", "admissions", "fees", "faculty", "facilities", "faqs"]
    if table not in allowed_tables:
        return jsonify({"error": "Not allowed"}), 403

    conn = get_db_connection()
    record = conn.execute(f"SELECT * FROM {table} WHERE id=?", [record_id]).fetchone()
    conn.close()

    if record:
        return jsonify(dict(record))
    return jsonify({"error": "Not found"}), 404


@app.route("/admin/chat-history")
@admin_required
def admin_chat_history():
    """View all chat history"""
    conn = get_db_connection()
    chats = conn.execute("""
        SELECT * FROM chat_history ORDER BY timestamp DESC LIMIT 100
    """).fetchall()
    conn.close()
    return render_template("admin_chats.html", chats=chats)


# ══════════════════════════════════════════════════════════
#  MAIN ENTRY POINT
# ══════════════════════════════════════════════════════════

if __name__ == "__main__":
    """
    WHAT THIS DOES: This runs when you execute 'python app.py'
    
    1. Creates database folder if it doesn't exist
    2. Initializes all tables
    3. Fills with sample data
    4. Starts the web server on port 5000
    
    debug=True means:
    - Shows errors in browser (helpful during development)
    - Auto-restarts when you change code
    - Never use debug=True in production (real website)!
    """
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)  # Create database folder
    init_database()    # Create tables
    seed_sample_data() # Add sample data
    
    print("\n" + "="*60)
    print("🎓 COLLEGE INQUIRY CHATBOT IS RUNNING!")
    print("="*60)
    print("📱 Chatbot:     http://localhost:5002")
    print("⚙️  Admin Panel: http://localhost:5002/admin")
    print("   Admin Login: username=admin, password=admin123")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5002)
