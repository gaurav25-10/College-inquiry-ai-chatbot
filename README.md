# 🎓 College Inquiry AI Chatbot
### Final Year Project — Complete Setup Guide

---

## 📁 Project Structure (What Each File Does)

```
college_chatbot/
│
├── app.py                  ← MAIN FILE: Flask server + all routes + AI logic
├── requirements.txt        ← List of Python libraries to install
├── README.md               ← This file (instructions)
│
├── database/
│   └── college.db          ← SQLite database (auto-created on first run)
│
├── templates/              ← HTML pages (Flask uses these)
│   ├── index.html          ← Main chatbot page (students see this)
│   ├── admin_login.html    ← Admin login page
│   ├── admin_dashboard.html← Admin home/stats page
│   ├── admin_courses.html  ← Manage courses
│   ├── admin_faqs.html     ← Manage FAQs
│   ├── admin_faculty.html  ← Manage faculty
│   ├── admin_table.html    ← Generic table (college info, fees)
│   └── admin_chats.html    ← View chat history
│
└── static/
    └── css/
        └── style.css       ← All styling for the chatbot page
```

---

## 🚀 How to Run — Step by Step

### Step 1: Install Python
Download Python 3.9+ from https://python.org
Make sure to check "Add Python to PATH" during installation!

### Step 2: Open Terminal/Command Prompt
- Windows: Press Win+R, type `cmd`, press Enter
- Mac: Press Cmd+Space, type `terminal`, press Enter

### Step 3: Go to project folder
```bash
cd path/to/college_chatbot
# Example: cd C:\Users\YourName\Desktop\college_chatbot
```

### Step 4: Install required libraries
```bash
pip install -r requirements.txt
```

### Step 5: Run the application
```bash
python app.py
```

You will see:
```
✅ Database tables created successfully!
✅ Sample data inserted successfully!
==================================================
🎓 COLLEGE INQUIRY CHATBOT IS RUNNING!
==================================================
📱 Chatbot:     http://localhost:5000
⚙️  Admin Panel: http://localhost:5000/admin
   Admin Login: username=admin, password=admin123
==================================================
```

### Step 6: Open in browser
- **Chatbot**: http://localhost:5000
- **Admin Panel**: http://localhost:5000/admin

---

## 🔐 Admin Panel Login
- **Username**: admin
- **Password**: admin123

⚠️ Change these in app.py before deploying!

---

## ✏️ How to Customize for YOUR College

### Option 1: Through Admin Panel (Easy — No coding!)
1. Go to http://localhost:5000/admin
2. Login with admin/admin123
3. Click any section (College Info, Courses, etc.)
4. Edit, Add, or Delete entries
5. Changes are INSTANT — chatbot uses new data immediately!

### Option 2: Edit the seed_sample_data() function in app.py
Find the function `seed_sample_data()` in app.py and:
- Change college name, location, phone, email
- Add/remove courses
- Update fee structure
- Add your own FAQs

---

## 🤖 How the AI Works (Simple Explanation)

```
Student types question
        ↓
JavaScript sends it to Flask (/chat route)
        ↓
Flask fetches ALL college data from SQLite database
        ↓
Flask sends: question + college data → Claude AI API
        ↓
Claude AI reads the data and generates a smart answer
        ↓
Flask sends answer back to JavaScript
        ↓
JavaScript displays it in the chat bubble
```

The AI (Claude) acts like a HUMAN who has read all our college documents!

---

## 📊 Database Tables Explained

| Table | What it stores |
|-------|---------------|
| college_info | Name, address, phone, email, achievements |
| courses | All courses with eligibility and descriptions |
| admissions | Process, dates, required documents |
| fees | Fee structure for each course |
| faculty | Teacher profiles and details |
| facilities | Hostel, labs, sports, etc. |
| faqs | Common Q&A for the chatbot |
| chat_history | All conversations (for analytics) |
| admin_users | Admin login accounts |

---

## 🛠️ Technologies Used

| Technology | What it does | Why we used it |
|-----------|-------------|----------------|
| Python | Main programming language | Easy to learn, powerful |
| Flask | Web framework | Simple, minimal, great for beginners |
| SQLite | Database | No setup needed, file-based |
| HTML | Page structure | Standard web language |
| CSS | Page styling | Makes it look beautiful |
| JavaScript | Page interactivity | Sends messages without refresh |
| Claude AI API | The "brain" of chatbot | Best AI available, accurate answers |

---

## ❓ Common Questions (FAQ for You!)

**Q: Why is the chatbot not responding?**
A: Make sure Python is running (`python app.py` in terminal). Check terminal for errors.

**Q: How to change the college name?**
A: Go to Admin Panel → College Info → Edit the `college_name` entry.

**Q: Can multiple students use it at once?**
A: Yes! Flask handles multiple requests. For production, use gunicorn.

**Q: How to add more admin users?**
A: Currently add them directly in the database. Future: add an admin management page.

**Q: How to deploy it online?**
A: Use platforms like Railway, Render, or PythonAnywhere. Ask me when ready!

---

## 📞 Project Info
- **Project Type**: Final Year Project
- **Technologies**: Python, Flask, SQLite, HTML, CSS, JavaScript, AI API
- **Features**: AI Chatbot, Admin Panel, Database CRUD, Chat History

---

*Built with ❤️ for Final Year Submission*
