import json
from abc import ABC, abstractmethod
from datetime import datetime
from html import escape as esc
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
        s.setdefault("age", "-")
        s.setdefault("email", "-")
        s.setdefault("roll_no", "")
        if not isinstance(s.get("grades"), dict):
            s["grades"] = {}
    for t in data["teachers"]:
        t.setdefault("name", "Unknown")
        t.setdefault("age", "-")
        t.setdefault("email", "-")
        t.setdefault("subject", "")
        t.setdefault("emp_id", "")
    return data


def save_data(data):
    DATABASE.write_text(json.dumps(data, indent=4))


# ----------------------------------------------------------------------------
# Domain classes (your OOP structure, returning (ok, message) for the UI)
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
        if any(s["roll_no"] == roll_no.strip() for s in data["students"]):
            return False, f"Roll number {roll_no} is already registered."

        data["students"].append(
            {"name": name.strip(), "age": age, "email": email.strip(),
             "roll_no": roll_no.strip(), "grades": {}}
        )
        save_data(data)
        return True, f"{name.strip()} is registered as a student."

    def add_grade(self, data, roll_no, subject, marks):
        if not subject.strip():
            return False, "Enter a subject name."
        for s in data["students"]:
            if s["roll_no"] == roll_no:
                s["grades"][subject.strip()] = marks
                save_data(data)
                return True, f"Saved {subject.strip()}: {marks:g} marks."
        return False, "Student not found."


class Teacher(Persons):
    def get_roles(self):
        return "teacher"

    def register(self, data, name, age, email, subject, emp_id):
        if not name.strip() or not emp_id.strip():
            return False, "Name and employee ID are required."
        if not Persons.validate_email(email):
            return False, "That email address doesn't look valid."
        if any(t["emp_id"] == emp_id.strip() for t in data["teachers"]):
            return False, f"Employee ID {emp_id} is already registered."

        data["teachers"].append(
            {"name": name.strip(), "age": age, "email": email.strip(),
             "subject": subject.strip(), "emp_id": emp_id.strip()}
        )
        save_data(data)
        return True, f"{name.strip()} is registered as a teacher."


student_service = Student()
teacher_service = Teacher()


# ----------------------------------------------------------------------------
# Styling
# ----------------------------------------------------------------------------
st.set_page_config(page_title="School Manager", page_icon="🎓", layout="wide")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root {
    --ink: #1E1B4B; --muted: #6B7280; --line: #E7E8F3; --mist: #F5F6FB;
    --indigo: #4F46E5; --violet: #7C3AED;
}

html, body, .stApp, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
.stApp { background: var(--mist); color: var(--ink); }
header[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 2rem; padding-bottom: 4rem; max-width: 1120px; }

.stApp label, .stApp label p { color: var(--ink) !important; font-weight: 600; }

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] { background: linear-gradient(180deg, #1E1B4B 0%, #312E81 100%); }
section[data-testid="stSidebar"] > div { padding-top: 1rem; }
.brand { display: flex; align-items: center; gap: .75rem; padding: .3rem .4rem 1.5rem; }
.brand-logo { width: 44px; height: 44px; border-radius: 13px; display: flex; align-items: center;
              justify-content: center; font-size: 1.4rem;
              background: linear-gradient(135deg, #818CF8, #C084FC); }
.brand-name { font-weight: 800; font-size: 1.15rem; color: #fff; line-height: 1.1; }
.brand-sub { font-size: .75rem; color: #A5B4FC; }

section[data-testid="stSidebar"] div[role="radiogroup"] { gap: .25rem; }
section[data-testid="stSidebar"] div[role="radiogroup"] label {
    width: 100%; padding: .7rem .95rem; border-radius: 12px; cursor: pointer; transition: background .15s; }
section[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child { display: none; }
section[data-testid="stSidebar"] div[role="radiogroup"] label:hover { background: rgba(255,255,255,.08); }
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
    background: rgba(255,255,255,.16); box-shadow: inset 3px 0 0 #A5B4FC; }
section[data-testid="stSidebar"] label p { color: #C7D2FE !important; font-weight: 600; font-size: .95rem; }
section[data-testid="stSidebar"] label:has(input:checked) p { color: #fff !important; }

.side-foot { margin-top: 2rem; padding: 1rem 1.1rem; border-radius: 14px;
             background: rgba(255,255,255,.08); color: #C7D2FE; font-size: .85rem; }
.side-foot b { color: #fff; font-size: 1.1rem; }
.side-foot div + div { margin-top: .35rem; }

/* ---------- Headings ---------- */
.page-title { font-size: 1.9rem; font-weight: 800; letter-spacing: -.02em; color: var(--ink); margin: 0 0 .2rem; }
.page-sub { color: var(--muted); margin-bottom: 1.5rem; }
.section-title { font-weight: 800; font-size: 1.05rem; margin: 1.7rem 0 .7rem; color: var(--ink); }

/* ---------- Hero ---------- */
.hero { position: relative; overflow: hidden; border-radius: 24px; padding: 2.1rem 2.3rem; margin-bottom: 1.5rem;
        background: linear-gradient(120deg, #4F46E5 0%, #7C3AED 55%, #C026D3 100%);
        box-shadow: 0 18px 40px rgba(79,70,229,.28); }
.hero:before { content: ""; position: absolute; right: -60px; top: -90px; width: 270px; height: 270px;
               border-radius: 50%; background: rgba(255,255,255,.12); }
.hero:after { content: ""; position: absolute; right: 150px; bottom: -110px; width: 210px; height: 210px;
              border-radius: 50%; background: rgba(255,255,255,.08); }
.hero-title { position: relative; z-index: 1; font-size: 2.1rem; font-weight: 800; letter-spacing: -.02em; color: #fff; }
.hero-text { position: relative; z-index: 1; color: rgba(255,255,255,.88); margin-top: .3rem; }
.hero-date { position: relative; z-index: 1; display: inline-block; margin-top: 1rem; padding: .3rem .85rem;
             border-radius: 99px; background: rgba(255,255,255,.18); color: #fff; font-size: .82rem; font-weight: 600; }

/* ---------- Cards ---------- */
.stat { background: #fff; border: 1px solid var(--line); border-radius: 20px; padding: 1.2rem 1.3rem;
        box-shadow: 0 6px 24px rgba(30,27,75,.05); display: flex; align-items: center; gap: 1rem; }
.stat-ic { width: 50px; height: 50px; border-radius: 15px; display: flex; align-items: center;
           justify-content: center; font-size: 1.45rem; flex-shrink: 0; }
.stat-num { font-size: 1.65rem; font-weight: 800; line-height: 1.1; color: var(--ink); }
.stat-num.small { font-size: 1.15rem; }
.stat-lbl { font-size: .82rem; color: var(--muted); font-weight: 600; }

.panel { background: #fff; border: 1px solid var(--line); border-radius: 20px; padding: 1.3rem 1.5rem;
         box-shadow: 0 6px 24px rgba(30,27,75,.05); min-height: 100%; }
.panel-title { font-weight: 800; font-size: 1.05rem; margin-bottom: .8rem; color: var(--ink); }

.row { display: flex; align-items: center; gap: .85rem; padding: .6rem 0; border-bottom: 1px dashed var(--line); }
.row:last-child { border-bottom: 0; }
.grow { flex: 1; min-width: 0; }
.nm { font-weight: 700; color: var(--ink); }
.sub { font-size: .78rem; color: var(--muted); }
.score { font-weight: 800; color: var(--ink); }

.av { width: 40px; height: 40px; border-radius: 50%; color: #fff; font-weight: 700; font-size: .85rem;
      display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.av-lg { width: 76px; height: 76px; font-size: 1.7rem; }

.bar { height: 7px; border-radius: 99px; background: var(--line); overflow: hidden; margin-top: .4rem; }
.bar > span { display: block; height: 100%; border-radius: 99px; background: linear-gradient(90deg, #6366F1, #A855F7); }

.chip { display: inline-block; padding: .22rem .75rem; border-radius: 99px; font-size: .78rem; font-weight: 700;
        background: #EEF2FF; color: #4338CA; margin: .2rem .35rem .2rem 0; }
.chip.green { background: #ECFDF5; color: #047857; }

.profile { display: flex; align-items: center; gap: 1.3rem; background: #fff; border: 1px solid var(--line);
           border-radius: 24px; padding: 1.5rem 1.7rem; box-shadow: 0 8px 30px rgba(30,27,75,.06); margin: .6rem 0 1.2rem; }
.pname { font-size: 1.45rem; font-weight: 800; letter-spacing: -.01em; color: var(--ink); margin-bottom: .2rem; }

.ring { width: 94px; height: 94px; border-radius: 50%; display: flex; align-items: center;
        justify-content: center; flex-shrink: 0; }
.ring-in { width: 74px; height: 74px; border-radius: 50%; background: #fff; display: flex;
           flex-direction: column; align-items: center; justify-content: center; }
.ring-in b { font-size: 1.4rem; font-weight: 800; line-height: 1; color: var(--ink); }
.ring-in span { font-size: .65rem; color: var(--muted); font-weight: 600; }

.grade-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: .9rem; }
.gcard { background: #fff; border: 1px solid var(--line); border-radius: 16px; padding: 1rem 1.1rem;
         display: flex; align-items: center; gap: .9rem; box-shadow: 0 4px 16px rgba(30,27,75,.04); }
.badge { width: 38px; height: 38px; border-radius: 11px; font-weight: 800; display: flex;
         align-items: center; justify-content: center; flex-shrink: 0; }
.badge.a { background: #D1FAE5; color: #047857; }
.badge.b { background: #E0E7FF; color: #4338CA; }
.badge.c { background: #FEF3C7; color: #B45309; }
.badge.d { background: #FFE4E6; color: #BE123C; }

.empty { text-align: center; padding: 2.4rem 1rem; border: 2px dashed #D5D8EE; border-radius: 20px;
         color: var(--muted); background: rgba(255,255,255,.6); }
.empty .big { font-size: 2rem; }
.empty b { display: block; color: var(--ink); font-size: 1.05rem; margin: .4rem 0 .2rem; }

/* ---------- Forms and inputs ---------- */
[data-testid="stForm"] { background: #fff; border: 1px solid var(--line); border-radius: 20px;
                         padding: 1.6rem; box-shadow: 0 8px 30px rgba(30,27,75,.06); }
div[data-baseweb="input"], div[data-baseweb="base-input"], div[data-baseweb="select"] > div {
    background: #fff !important; border-radius: 12px !important; }
div[data-baseweb="input"], div[data-baseweb="select"] > div { border: 1px solid var(--line) !important; }
div[data-baseweb="input"]:focus-within, div[data-baseweb="select"] > div:focus-within {
    border-color: var(--indigo) !important; box-shadow: 0 0 0 3px rgba(79,70,229,.15); }
.stTextInput input, .stNumberInput input { color: var(--ink) !important; }
div[data-baseweb="select"] * { color: var(--ink) !important; }

.stButton > button, [data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(135deg, var(--indigo), var(--violet)); color: #fff; border: 0;
    border-radius: 12px; padding: .6rem 1.7rem; font-weight: 700;
    box-shadow: 0 6px 16px rgba(79,70,229,.3); transition: transform .15s, box-shadow .15s; }
.stButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover {
    color: #fff; transform: translateY(-1px); box-shadow: 0 10px 22px rgba(79,70,229,.38); }
.stButton > button p, [data-testid="stFormSubmitButton"] button p { color: #fff !important; }

.stTabs [data-baseweb="tab-list"] { gap: .4rem; border-bottom: 1px solid var(--line); }
.stTabs [data-baseweb="tab"] { font-weight: 700; }
.stTabs [aria-selected="true"] { color: var(--indigo); }
.stTabs [data-baseweb="tab-highlight"] { background: var(--indigo); }

@media (max-width: 640px) {
    .profile { flex-wrap: wrap; }
    .hero { padding: 1.5rem; }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# UI helpers
# ----------------------------------------------------------------------------
GRADIENTS = [("#6366F1", "#A855F7"), ("#06B6D4", "#3B82F6"), ("#F59E0B", "#EF4444"),
             ("#10B981", "#06B6D4"), ("#EC4899", "#F43F5E"), ("#8B5CF6", "#6366F1")]


def h(markup):
    """Collapse HTML to one line so Markdown never treats indented lines as code."""
    return " ".join(line.strip() for line in markup.splitlines()).strip()


def show(markup):
    st.markdown(h(markup), unsafe_allow_html=True)


def page_header(title, subtitle):
    show(f'<div class="page-title">{esc(title)}</div><div class="page-sub">{esc(subtitle)}</div>')


def avatar(name, size_class="av"):
    name = str(name)
    start, end = GRADIENTS[sum(map(ord, name)) % len(GRADIENTS)]
    initials = "".join(w[0] for w in name.split()[:2]).upper() or "?"
    return (f'<div class="{size_class}" style="background:linear-gradient(135deg,{start},{end})">'
            f'{esc(initials)}</div>')


def avg_of(student):
    grades = student["grades"]
    return sum(grades.values()) / len(grades) if grades else None


def letter(marks):
    if marks >= 85:
        return "A"
    if marks >= 70:
        return "B"
    if marks >= 50:
        return "C"
    return "D"


def stat_card(col, icon, label, value, bg, small=False):
    size = " small" if small else ""
    col.markdown(h(
        f'<div class="stat"><div class="stat-ic" style="background:{bg}">{icon}</div>'
        f'<div><div class="stat-num{size}">{esc(str(value))}</div>'
        f'<div class="stat-lbl">{esc(label)}</div></div></div>'), unsafe_allow_html=True)


def empty_state(icon, title, text):
    show(f'<div class="empty"><div class="big">{icon}</div><b>{esc(title)}</b>{esc(text)}</div>')


def grade_grid(grades):
    cards = ""
    for subject, marks in sorted(grades.items(), key=lambda kv: kv[1], reverse=True):
        pct = max(0, min(100, marks))
        grade = letter(marks)
        cards += (f'<div class="gcard"><div class="badge {grade.lower()}">{grade}</div>'
                  f'<div class="grow"><div class="nm">{esc(str(subject))}</div>'
                  f'<div class="bar"><span style="width:{pct:.0f}%"></span></div></div>'
                  f'<div class="score">{marks:g}</div></div>')
    show(f'<div class="grade-grid">{cards}</div>')


def student_label(s):
    return f"{s['name']} (Roll {s['roll_no']})"


def pick_student(data, key):
    options = {s["roll_no"]: s for s in data["students"]}
    roll = st.selectbox("Choose a student", list(options),
                        format_func=lambda r: student_label(options[r]), key=key)
    return options[roll]


def finish(result):
    """On success, remember a toast and reload so every page shows fresh data."""
    ok, message = result
    if ok:
        st.session_state["flash"] = message
        st.rerun()
    else:
        st.error(message)


# ----------------------------------------------------------------------------
# Pages
# ----------------------------------------------------------------------------
def page_dashboard(data):
    students, teachers = data["students"], data["teachers"]
    marks = [m for s in students for m in s["grades"].values()]
    school_avg = f"{sum(marks) / len(marks):.1f}" if marks else "-"
    subjects = {sub for s in students for sub in s["grades"]}
    today = datetime.now().strftime("%A, %d %B %Y")

    show(f'<div class="hero"><div class="hero-title">Welcome back 👋</div>'
         f'<div class="hero-text">Here is how your school is doing today.</div>'
         f'<div class="hero-date">{today}</div></div>')

    cols = st.columns(4)
    stat_card(cols[0], "🎓", "Students", len(students), "#EEF2FF")
    stat_card(cols[1], "👩‍🏫", "Teachers", len(teachers), "#FDF2F8")
    stat_card(cols[2], "📚", "Subjects graded", len(subjects), "#ECFDF5")
    stat_card(cols[3], "⭐", "School average", school_avg, "#FFFBEB")

    st.write("")
    left, right = st.columns(2)

    with left:
        ranked = sorted([(avg_of(s), s) for s in students if s["grades"]],
                        key=lambda x: x[0], reverse=True)[:5]
        if ranked:
            rows = ""
            for avg, s in ranked:
                rows += (f'<div class="row">{avatar(s["name"])}<div class="grow">'
                         f'<div class="nm">{esc(str(s["name"]))}</div>'
                         f'<div class="bar"><span style="width:{min(avg, 100):.0f}%"></span></div></div>'
                         f'<div class="score">{avg:.1f}</div></div>')
        else:
            rows = '<div class="sub">Grades will rank your students here.</div>'
        show(f'<div class="panel"><div class="panel-title">🏆 Top performers</div>{rows}</div>')

    with right:
        recent = [("Student", s["name"], f"Roll {s['roll_no']}") for s in reversed(students[-3:])]
        recent += [("Teacher", t["name"], t["subject"] or "No subject yet") for t in reversed(teachers[-3:])]
        if recent:
            rows = ""
            for role, name, sub in recent:
                chip = "chip green" if role == "Teacher" else "chip"
                rows += (f'<div class="row">{avatar(name)}<div class="grow">'
                         f'<div class="nm">{esc(str(name))}</div><div class="sub">{esc(str(sub))}</div></div>'
                         f'<span class="{chip}">{role}</span></div>')
        else:
            rows = '<div class="sub">New registrations will appear here.</div>'
        show(f'<div class="panel"><div class="panel-title">🆕 Recently added</div>{rows}</div>')

    by_subject = {}
    for s in students:
        for subject, m in s["grades"].items():
            by_subject.setdefault(subject, []).append(m)
    if by_subject:
        show('<div class="section-title">📊 Average marks by subject</div>')
        chart = pd.Series({k: sum(v) / len(v) for k, v in by_subject.items()}, name="Average")
        st.bar_chart(chart, color="#6366F1")


def page_register_student(data):
    page_header("Register a student", "Roll numbers must be unique.")
    with st.form("student_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("Full name", placeholder="e.g. Aarav Sharma")
        roll_no = c2.text_input("Roll number", placeholder="e.g. 101")
        email = c1.text_input("Email", placeholder="name@example.com")
        age = c2.number_input("Age", min_value=3, max_value=100, value=15, step=1)
        if st.form_submit_button("Register student"):
            finish(student_service.register(data, name, int(age), email, roll_no))


def page_register_teacher(data):
    page_header("Register a teacher", "Employee IDs must be unique.")
    with st.form("teacher_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("Full name", placeholder="e.g. Meera Das")
        emp_id = c2.text_input("Employee ID", placeholder="e.g. T-204")
        email = c1.text_input("Email", placeholder="name@example.com")
        age = c2.number_input("Age", min_value=18, max_value=100, value=30, step=1)
        subject = st.text_input("Subject taught", placeholder="e.g. Mathematics")
        if st.form_submit_button("Register teacher"):
            finish(teacher_service.register(data, name, int(age), email, subject, emp_id))


def page_add_grades(data):
    page_header("Add grades", "Saving a subject that already exists updates its marks.")
    if not data["students"]:
        empty_state("🎓", "No students yet", "Register a student first, then come back to add grades.")
        return

    student = pick_student(data, "grade_student")
    if student["grades"]:
        show('<div class="section-title">Current grades</div>')
        grade_grid(student["grades"])
        st.write("")

    with st.form("grade_form", clear_on_submit=True):
        c1, c2 = st.columns([2, 1])
        subject = c1.text_input("Subject", placeholder="e.g. Physics")
        marks = c2.number_input("Marks (out of 100)", min_value=0.0, max_value=100.0, value=0.0, step=0.5)
        if st.form_submit_button("Save grade"):
            finish(student_service.add_grade(data, student["roll_no"], subject, marks))


def page_student_details(data):
    page_header("Student details", "Profile, grades and average.")
    if not data["students"]:
        empty_state("🎓", "No students yet", "Registered students will show up here.")
        return

    s = pick_student(data, "detail_student")
    avg = avg_of(s)
    chips = (f'<span class="chip">Roll {esc(str(s["roll_no"]))}</span>'
             f'<span class="chip">Age {esc(str(s["age"]))}</span>'
             f'<span class="chip">{esc(str(s["email"]))}</span>')
    ring = ""
    if avg is not None:
        ring = (f'<div class="ring" style="background:conic-gradient(#6366F1 {min(avg, 100) * 3.6:.0f}deg,#E7E8F3 0)">'
                f'<div class="ring-in"><b>{avg:.0f}</b><span>average</span></div></div>')
    show(f'<div class="profile">{avatar(s["name"], "av av-lg")}<div class="grow">'
         f'<div class="pname">{esc(str(s["name"]))}</div><div>{chips}</div></div>{ring}</div>')

    grades = s["grades"]
    if not grades:
        empty_state("📝", "No grades yet", "Add grades for this student to see their results.")
        return

    best = max(grades, key=grades.get)
    lowest = min(grades, key=grades.get)
    c1, c2, c3 = st.columns(3)
    stat_card(c1, "📚", "Subjects", len(grades), "#EEF2FF")
    stat_card(c2, "🥇", "Strongest subject", f"{best} ({grades[best]:g})", "#ECFDF5", small=True)
    stat_card(c3, "🎯", "Needs attention", f"{lowest} ({grades[lowest]:g})", "#FFF1F2", small=True)

    show('<div class="section-title">Grades</div>')
    grade_grid(grades)


def page_teacher_details(data):
    page_header("Teacher details", "Profile and subject.")
    if not data["teachers"]:
        empty_state("👩‍🏫", "No teachers yet", "Registered teachers will show up here.")
        return

    options = {t["emp_id"]: t for t in data["teachers"]}
    emp_id = st.selectbox("Choose a teacher", list(options), key="detail_teacher",
                          format_func=lambda e: f"{options[e]['name']} (ID {e})")
    t = options[emp_id]
    chips = (f'<span class="chip green">{esc(t["subject"] or "No subject yet")}</span>'
             f'<span class="chip">ID {esc(str(t["emp_id"]))}</span>'
             f'<span class="chip">Age {esc(str(t["age"]))}</span>'
             f'<span class="chip">{esc(str(t["email"]))}</span>')
    show(f'<div class="profile">{avatar(t["name"], "av av-lg")}<div class="grow">'
         f'<div class="pname">{esc(str(t["name"]))}</div><div>{chips}</div></div></div>')


def page_directory(data):
    page_header("Directory", "Everyone on record. Search by name or ID.")
    query = st.text_input("Search", placeholder="Type a name, roll number or employee ID").strip().lower()
    tab_students, tab_teachers = st.tabs(["🎓 Students", "👩‍🏫 Teachers"])

    def matches(df, *columns):
        if not query or df.empty:
            return df
        mask = pd.Series(False, index=df.index)
        for col in columns:
            mask |= df[col].astype(str).str.lower().str.contains(query, regex=False)
        return df[mask]

    with tab_students:
        df = pd.DataFrame(
            [{"Roll no": s["roll_no"], "Name": s["name"], "Age": s["age"], "Email": s["email"],
              "Average": avg_of(s)} for s in data["students"]],
            columns=["Roll no", "Name", "Age", "Email", "Average"])
        df = matches(df, "Name", "Roll no")
        if df.empty:
            empty_state("🔍", "No students found", "Try a different search or register a new student.")
        else:
            st.dataframe(df, hide_index=True, column_config={
                "Average": st.column_config.ProgressColumn("Average", min_value=0, max_value=100, format="%.1f")})

    with tab_teachers:
        df = pd.DataFrame(
            [{"Emp ID": t["emp_id"], "Name": t["name"], "Subject": t["subject"], "Age": t["age"],
              "Email": t["email"]} for t in data["teachers"]],
            columns=["Emp ID", "Name", "Subject", "Age", "Email"])
        df = matches(df, "Name", "Emp ID")
        if df.empty:
            empty_state("🔍", "No teachers found", "Try a different search or register a new teacher.")
        else:
            st.dataframe(df, hide_index=True)


# ----------------------------------------------------------------------------
# Navigation
# ----------------------------------------------------------------------------
PAGES = {
    "🏠  Dashboard": page_dashboard,
    "🎓  Register student": page_register_student,
    "👩‍🏫  Register teacher": page_register_teacher,
    "📝  Add grades": page_add_grades,
    "📄  Student details": page_student_details,
    "🧾  Teacher details": page_teacher_details,
    "📚  Directory": page_directory,
}

data = load_data()

with st.sidebar:
    show('<div class="brand"><div class="brand-logo">🎓</div><div><div class="brand-name">School Manager</div>'
         '<div class="brand-sub">Students and teachers</div></div></div>')
    choice = st.radio("Go to", list(PAGES), label_visibility="collapsed")

if "flash" in st.session_state:
    st.toast(st.session_state.pop("flash"), icon="✅")

PAGES[choice](data)

with st.sidebar:
    show(f'<div class="side-foot"><div><b>{len(data["students"])}</b> students</div>'
         f'<div><b>{len(data["teachers"])}</b> teachers</div></div>')
