from flask import Flask, render_template, request, redirect, session, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import mysql.connector
from mysql.connector import pooling
import os
from dotenv import load_dotenv
import logging

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "change-this-in-production")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── DB Connection Pool ────────────────────────────────────────────────────────
db_pool = pooling.MySQLConnectionPool(
    pool_name="sqms_pool",
    pool_size=5,
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", ""),
    database=os.getenv("DB_NAME", "sqms")
)

def get_db():
    return db_pool.get_connection()

# ── Auth Decorators ───────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("is_admin"):
            flash("Admin access required.", "danger")
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return decorated

# ── User Routes ───────────────────────────────────────────────────────────────
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name     = request.form["name"].strip()
        email    = request.form["email"].strip().lower()
        phone    = request.form["phone"].strip()
        password = request.form["password"]
        hashed   = generate_password_hash(password)
        try:
            conn   = get_db()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (name, email, phone, password) VALUES (%s, %s, %s, %s)",
                (name, email, phone, hashed)
            )
            conn.commit()
            flash("Account created! Please log in.", "success")
            return redirect(url_for("login"))
        except mysql.connector.IntegrityError:
            flash("Email already registered.", "danger")
        except mysql.connector.Error as e:
            logger.error("Register DB error: %s", e)
            flash("Something went wrong. Try again.", "danger")
        finally:
            cursor.close()
            conn.close()
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email    = request.form["email"].strip().lower()
        password = request.form["password"]
        try:
            conn   = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, name, password FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
        finally:
            cursor.close()
            conn.close()
        if user and check_password_hash(user[2], password):
            session["user_id"]   = user[0]
            session["user_name"] = user[1]
            flash(f"Welcome back, {user[1]}!", "success")
            return redirect(url_for("appointment"))
        flash("Invalid email or password.", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("home"))


@app.route("/appointment", methods=["GET", "POST"])
@login_required
def appointment():
    if request.method == "POST":
        hospital   = request.form["hospital"].strip()
        department = request.form["department"].strip()
        doctor     = request.form["doctor"].strip()
        date       = request.form["date"]
        slot       = request.form["slot"].strip()
        user_id    = session["user_id"]
        try:
            conn   = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM appointments")
            count = cursor.fetchone()[0]
            token = f"CAR{count + 1:03d}"
            cursor.execute(
                """INSERT INTO appointments
                   (hospital, department, doctor, appointment_date, time_slot, token_number, user_id, status)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, 'Pending')""",
                (hospital, department, doctor, date, slot, token, user_id)
            )
            conn.commit()
            return render_template("success.html", token=token)
        except mysql.connector.Error as e:
            logger.error("Appointment DB error: %s", e)
            flash("Could not book appointment. Try again.", "danger")
        finally:
            cursor.close()
            conn.close()
    return render_template("appointment.html")


@app.route("/track")
@login_required
def track():
    user_id = session["user_id"]
    result  = None
    position = None
    try:
        conn   = get_db()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT token_number, status FROM appointments
               WHERE user_id = %s ORDER BY appointment_id DESC LIMIT 1""",
            (user_id,)
        )
        result = cursor.fetchone()
        if result:
            cursor.execute(
                """SELECT COUNT(*) FROM appointments
                   WHERE status = 'Pending'
                   AND appointment_id < (
                       SELECT appointment_id FROM appointments
                       WHERE user_id = %s ORDER BY appointment_id DESC LIMIT 1
                   )""",
                (user_id,)
            )
            position = cursor.fetchone()[0] + 1
    finally:
        cursor.close()
        conn.close()
    token  = result[0] if result else None
    status = result[1] if result else None
    return render_template("track.html", token=token, status=status, position=position)


# ── Admin Routes ──────────────────────────────────────────────────────────────
@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == os.getenv("ADMIN_USER", "admin") and \
           password == os.getenv("ADMIN_PASS", "admin123"):
            session["is_admin"] = True
            return redirect(url_for("admin"))
        flash("Invalid admin credentials.", "danger")
    return render_template("adminlogin.html")


@app.route("/admin-logout")
def admin_logout():
    session.pop("is_admin", None)
    return redirect(url_for("home"))


@app.route("/admin")
@admin_required
def admin():
    try:
        conn   = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM appointments ORDER BY appointment_id DESC")
        appointments = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
    return render_template("admin.html", appointments=appointments)


@app.route("/search", methods=["POST"])
@admin_required
def search():
    token = request.form["token"].strip()
    try:
        conn   = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM appointments WHERE token_number = %s", (token,))
        appointments = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
    return render_template("admin.html", appointments=appointments)


@app.route("/delete/<int:appt_id>")
@admin_required
def delete_appointment(appt_id):
    try:
        conn   = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM appointments WHERE appointment_id = %s", (appt_id,))
        conn.commit()
        flash("Appointment deleted.", "success")
    except mysql.connector.Error as e:
        logger.error("Delete error: %s", e)
        flash("Could not delete appointment.", "danger")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for("admin"))


@app.route("/complete/<int:appt_id>")
@admin_required
def complete_appointment(appt_id):
    _update_status(appt_id, "Completed")
    return redirect(url_for("admin"))


@app.route("/pending/<int:appt_id>")
@admin_required
def pending_appointment(appt_id):
    _update_status(appt_id, "Pending")
    return redirect(url_for("admin"))


def _update_status(appt_id, status):
    try:
        conn   = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE appointments SET status = %s WHERE appointment_id = %s",
            (status, appt_id)
        )
        conn.commit()
    except mysql.connector.Error as e:
        logger.error("Status update error: %s", e)
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug_mode)