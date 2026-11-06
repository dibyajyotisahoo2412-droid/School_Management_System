import json
from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd
import streamlit as st

# ----------------------------------------------------------------------------
# Data layer (same JSON file as your original script)
# ----------------------------------------------------------------------------
DATABASE = Path("school_data.json")


def load_data():
    data = {"students": [], "teachers": []}
    if DATABASE.exists():
        try:
            content = DATABASE.read_text().strip()
            if content:
                data.update(json.loads(content))
        except json.JSONDecodeError:
            st.error("school_data.json is damaged. Starting with empty records.")

    # Older or hand-edited records may be missing fields; fill in safe defaults.
    data.setdefault("students", [])
    data.setdefault("teachers", [])
    for s in data["students"]:
        s.setdefault("name", "Unknown")
        s.setdefault("age", "–")
        s.setdefault("email", "–")
        s.setdefault("roll_no", "")
        if not isinstance(s.get("grades"), dict):
            s["grades"] = {}
    for t in data["teachers"]:
        t.setdefault("name", "Unknown")
        t.setdefault("age", "–")
        t.setdefault("email", "–")
        t.setdefault("subject", "")
        t.setdefault("emp_id", "")
    return data


def save_data(data):
    DATABASE.write_text(json.dumps(data, indent=4))


# ----------------------------------------------------------------------------
# Domain classes (your OOP structure, now returning (ok, message) for the UI)
# ----------------------------------------------------------------------------
class Persons(ABC):
    @abstractmethod
    def get_roles(self):
        pass

    @abstractmethod
    def register(self, data, **fields):
        pass

    @staticmethod
    def validate_email(email):
        return "@" in email and "." in email


class Student(Persons):
    def get_roles(self):
        return "student"

    def register(self, data, name, age, email, roll_no):
        if not name.strip() or not roll_no.strip():
            return False, "Name and roll number are required."
        if not Persons.validate_email(email):
            return False, "That email address doesn't look valid."
        if any(s["roll_no"] == roll_no for s in data["students"]):
            return False, f"Roll number {roll_no} is already registered."

        data["students"].append(
            {"name": name.strip(), "age": age, "email": email.strip(),
             "roll_no": roll_no.strip(), "grades": {}}
        )
        save_data(data)
        return True, f"{name} is registered as a student."

    def add_grade(self, data, roll_no, subject, marks):
        if not subject.strip():
            return False, "Enter a subject name."
        for s in data["students"]:
            if s["roll_no"] == roll_no:
                s["grades"][subject.strip()] = marks
                save_data(data)
                return True, f"Saved {subject}: {marks:g} marks."
        return False, "Student not found."


class Teacher(Persons):
    def get_roles(self):
        return "teacher"

    def register(self, data, name, age, email, subject, emp_id):
        if not name.strip() or not emp_id.strip():
            return False, "Name and employee ID are required."
        if not Persons.validate_email(email):
            return False, "That email address doesn't look valid."
        if any(t["emp_id"] == emp_id for t in data["teachers"]):
            return False, f"Employee ID {emp_id} is already registered."

        data["teachers"].append(
            {"name": name.strip(), "age": age, "email": email.strip(),
             "subject": subject.strip(), "emp_id": emp_id.strip()}
        )
        save_data(data)
        return True, f"{name} is registered as a teacher."


student_service = Student()
teacher_service = Teacher()


# ----------------------------------------------------------------------------
# Page setup and styling
# ----------------------------------------------------------------------------
st.set_page_config(page_title="School Manager", page_icon="🎓", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@500;700&family=Inter:wght@400;500&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    h1, h2, h3 { font-family: 'Bricolage Grotesque', sans-serif !important; letter-spacing: -0.01em; }

    .block-container { padding-top: 2rem; max-width: 1100px; }

    .page-head { padding: 1.4rem 1.6rem; border-radius: 14px; margin-bottom: 1.4rem;
                 background: linear-gradient(120deg, #134e4a 0%, #0f766e 100%); color: #fff; }
    .page-head h1 { color: #fff; margin: 0; font-size: 1.9rem; }
    .page-head p  { margin: .25rem 0 0; opacity: .85; }

    div[data-testid="stMetric"] { background: rgba(15,118,110,.08);
        border: 1px solid rgba(15,118,110,.25); padding: 1rem 1.2rem; border-radius: 12px; }

    .profile { display: flex; gap: 1rem; align-items: center; padding: 1.1rem 1.3rem;
               border: 1px solid rgba(128,128,128,.3); border-radius: 14px; margin-bottom: 1rem; }
    .avatar { width: 56px; height: 56px; border-radius: 50%; background: #0f766e; color: #fff;
              display: flex; align-items: center; justify-content: center;
              font: 700 1.3rem 'Bricolage Grotesque', sans-serif; flex-shrink: 0; }
    .profile .name { font: 700 1.2rem 'Bricolage Grotesque', sans-serif; }
    .profile .meta { opacity: .7; font-size: .9rem; }

    .stButton > button, div[data-testid="stFormSubmitButton"] > button {
        background: #0f766e; color: #fff; border: 0; border-radius: 10px; padding: .55rem 1.4rem; }
    .stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover {
        background: #115e59; color: #fff; }
    </style>
    """,
    unsafe_allow_html=True,
)


def header(title, subtitle):
    st.markdown(
        f'<div class="page-head"><h1>{title}</h1><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )


def profile_card(name, meta):
    initials = "".join(w[0] for w in name.split()[:2]).upper() or "?"
    st.markdown(
        f'<div class="profile"><div class="avatar">{initials}</div>'
        f'<div><div class="name">{name}</div><div class="meta">{meta}</div></div></div>',
        unsafe_allow_html=True,
    )


def flash(result):
    ok, message = result
    (st.success if ok else st.error)(message)


# ----------------------------------------------------------------------------
# Pages
# ----------------------------------------------------------------------------
def page_dashboard(data):
    header("School Manager", "Students, teachers and grades in one place.")
    students, teachers = data["students"], data["teachers"]

    all_marks = [m for s in students for m in s["grades"].values()]
    c1, c2, c3 = st.columns(3)
    c1.metric("Students", len(students))
    c2.metric("Teachers", len(teachers))
    c3.metric("School average", f"{sum(all_marks) / len(all_marks):.1f}" if all_marks else "–")

    left, right = st.columns(2)
    with left:
        st.subheader("Student averages")
        rows = [{"Student": s["name"], "Average": sum(s["grades"].values()) / len(s["grades"])}
                for s in students if s["grades"]]
        if rows:
            st.bar_chart(pd.DataFrame(rows).set_index("Student"), color="#0f766e")
        else:
            st.info("No grades yet. Add grades to see averages here.")
    with right:
        st.subheader("Teachers by subject")
        if teachers:
            counts = pd.Series([t["subject"] or "Unassigned" for t in teachers]).value_counts()
            st.bar_chart(counts, color="#0f766e")
        else:
            st.info("No teachers yet. Register one to get started.")


def page_register_student(data):
    header("Register a student", "Roll numbers must be unique.")
    with st.form("student_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("Full name")
        roll_no = c2.text_input("Roll number")
        email = c1.text_input("Email")
        age = c2.number_input("Age", min_value=3, max_value=100, value=15, step=1)
        if st.form_submit_button("Register student"):
            flash(student_service.register(data, name, int(age), email, roll_no))


def page_register_teacher(data):
    header("Register a teacher", "Employee IDs must be unique.")
    with st.form("teacher_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("Full name")
        emp_id = c2.text_input("Employee ID")
        email = c1.text_input("Email")
        age = c2.number_input("Age", min_value=18, max_value=100, value=30, step=1)
        subject = st.text_input("Subject taught")
        if st.form_submit_button("Register teacher"):
            flash(teacher_service.register(data, name, int(age), email, subject, emp_id))


def student_label(s):
    return f"{s['roll_no']} · {s['name']}"


def page_add_grades(data):
    header("Add grades", "Saving a subject that already exists updates its marks.")
    if not data["students"]:
        st.info("Register a student first, then come back to add grades.")
        return

    with st.form("grade_form", clear_on_submit=True):
        student = st.selectbox("Student", data["students"], format_func=student_label)
        c1, c2 = st.columns([2, 1])
        subject = c1.text_input("Subject")
        marks = c2.number_input("Marks", min_value=0.0, max_value=100.0, value=0.0, step=0.5)
        if st.form_submit_button("Save grade"):
            flash(student_service.add_grade(data, student["roll_no"], subject, marks))


def page_student_details(data):
    header("Student details", "Profile, grades and average.")
    if not data["students"]:
        st.info("No students registered yet.")
        return

    s = st.selectbox("Choose a student", data["students"], format_func=student_label)
    profile_card(s["name"], f"Roll {s['roll_no']} · Age {s['age']} · {s['email']}")

    grades = s["grades"]
    if not grades:
        st.info("This student has no grades yet.")
        return

    avg = sum(grades.values()) / len(grades)
    best = max(grades, key=grades.get)
    c1, c2, c3 = st.columns(3)
    c1.metric("Average", f"{avg:.1f}")
    c2.metric("Subjects", len(grades))
    c3.metric("Best subject", f"{best} ({grades[best]:g})")

    df = pd.DataFrame({"Subject": list(grades), "Marks": list(grades.values())})
    left, right = st.columns([1, 2])
    left.dataframe(df, hide_index=True, use_container_width=True)
    right.bar_chart(df.set_index("Subject"), color="#0f766e")


def page_teacher_details(data):
    header("Teacher details", "Profile and subject.")
    if not data["teachers"]:
        st.info("No teachers registered yet.")
        return

    t = st.selectbox("Choose a teacher", data["teachers"],
                     format_func=lambda t: f"{t['emp_id']} · {t['name']}")
    profile_card(t["name"], f"ID {t['emp_id']} · Age {t['age']} · {t['email']}")
    st.metric("Subject", t["subject"] or "Unassigned")


def page_directory(data):
    header("Directory", "Everyone on record. Search by name or ID.")
    query = st.text_input("Search", placeholder="Type a name, roll number or employee ID").lower()
    tab_s, tab_t = st.tabs(["Students", "Teachers"])

    with tab_s:
        rows = [{"Roll no": s["roll_no"], "Name": s["name"], "Age": s["age"], "Email": s["email"],
                 "Average": round(sum(s["grades"].values()) / len(s["grades"]), 1) if s["grades"] else None}
                for s in data["students"]]
        df = pd.DataFrame(rows)
        if not df.empty and query:
            df = df[df["Name"].str.lower().str.contains(query) | df["Roll no"].str.lower().str.contains(query)]
        st.dataframe(df, hide_index=True, use_container_width=True) if not df.empty else st.info("No students found.")

    with tab_t:
        df = pd.DataFrame(data["teachers"])
        if not df.empty:
            df = df.rename(columns={"emp_id": "Emp ID", "name": "Name", "age": "Age",
                                    "email": "Email", "subject": "Subject"})
            df = df[["Emp ID", "Name", "Subject", "Age", "Email"]]
            if query:
                df = df[df["Name"].str.lower().str.contains(query) | df["Emp ID"].str.lower().str.contains(query)]
        st.dataframe(df, hide_index=True, use_container_width=True) if not df.empty else st.info("No teachers found.")


# ----------------------------------------------------------------------------
# Navigation
# ----------------------------------------------------------------------------
PAGES = {
    "🏠 Dashboard": page_dashboard,
    "🎓 Register student": page_register_student,
    "👩‍🏫 Register teacher": page_register_teacher,
    "📝 Add grades": page_add_grades,
    "📄 Student details": page_student_details,
    "🧾 Teacher details": page_teacher_details,
    "📚 Directory": page_directory,
}

with st.sidebar:
    st.markdown("## 🎓 School Manager")
    choice = st.radio("Go to", list(PAGES), label_visibility="collapsed")

PAGES[choice](load_data())