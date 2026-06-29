# 🏥 SQMS – Smart Queue Management System

> A full-stack web application to manage and reduce patient waiting time in healthcare facilities

[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat&logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0-black?style=flat&logo=flask)](https://flask.palletsprojects.com)
[![MySQL](https://img.shields.io/badge/MySQL-Database-orange?style=flat&logo=mysql)](https://mysql.com)

---

## 📌 About

SQMS is a healthcare queue management system that helps clinics and hospitals manage patient flow efficiently. Patients can register, get a token number, and track their position in real time — reducing crowding and waiting time.

---

## ✨ Features

- 🎫 **Token-based queue system** — auto-assign queue numbers to patients
- 📊 **Real-time queue tracking** — live position updates
- 🏥 **Department-wise queues** — separate queues per department
- ✅ **Patient registration** — name, age, department selection
- 🎨 **Modern UI** — glassmorphism design with animations
- 🔔 **Toast notifications** — real-time status alerts
- 📱 **Responsive design** — works on mobile and desktop

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, Flask |
| Database | MySQL |
| UI Design | Glassmorphism, CSS Animations |

---

## 🚀 Setup & Run

```bash
# 1. Clone the repo
git clone https://github.com/lavanya-2212-s/sqms-queue-management.git
cd sqms-queue-management

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup MySQL database
# Create a database and run the SQL file in /database folder

# 4. Create .env file with your DB credentials
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=yourpassword
DB_NAME=sqms

# 5. Run the app
python app.py
```

Open **http://localhost:5000**

---

## 📁 Project Structure

```
SmartQ/
├── app.py              ← Flask routes + logic
├── requirements.txt
├── .env                ← DB credentials (not in repo)
├── database/           ← SQL schema files
├── templates/          ← HTML pages
└── static/             ← CSS, JS, images
```

---

## 👩‍💻 Developer

**Lavanya S** — CSE Graduate, Vels University  
[GitHub](https://github.com/lavanya-2212-s)
