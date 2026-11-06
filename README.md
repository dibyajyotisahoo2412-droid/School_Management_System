# 🎓 School Manager

A lightweight, object-oriented School Management System built in Python. The project features an interactive web dashboard powered by **Streamlit** and **Pandas**, an alternate terminal-based **CLI interface**, and persistent storage using a structured **JSON database**.

---

## 📌 Table of Contents
- [Features](#-features)
- [Project Architecture](#-project-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Running the Application](#-running-the-application)
  - [Streamlit Web Interface](#1-streamlit-web-dashboard)
  - [Command-Line Interface (CLI)](#2-command-line-interface-cli)
- [Data Schema](#-data-schema)
- [OOP Implementation Details](#-oop-implementation-details)
- [License](#-license)

---

## ✨ Features

### 🌐 Web Dashboard (Streamlit)
* **Interactive Analytics & KPIs:** Track total student and teacher counts, overall school averages, and subject-wise score distributions.
* **Student & Teacher Management:** Validated registration forms ensuring uniqueness for student roll numbers and teacher employee IDs, alongside email format verification.
* **Grade Book:** Assign and update subject marks (out of 100) per student with automatic letter grade categorization (`A`, `B`, `C`, `D`).
* **Performance Insights:** Individual student report cards featuring overall average rings, strongest subjects, areas needing improvement, and visual bar charts.
* **Searchable Directory:** Unified directory tables with live keyword search across names, roll numbers, and employee IDs.
* **Top Performers & Activity Feed:** Highlights top academic ranks and recently added profiles directly on the home dashboard.

### 💻 Command-Line Interface (CLI)
* Terminal-driven interactive menu (`main.py`) for environments without browser access.
* Supports registration, grade assignment, and profile inspection via standard console input/output.

---

## 🏗 Project Architecture

The application is structured around Object-Oriented Programming (OOP) principles using Python's `abc` module:
* **`Persons` (Abstract Base Class):** Defines common abstractions (`get_roles`, `register`) and shared static utility methods such as email validation.
* **`Student` (Subclass):** Encapsulates student registration, roll number uniqueness checks, and subject grade management.
* **`Teacher` (Subclass):** Encapsulates faculty registration, employee ID uniqueness validation, and subject specialization assignments.

---

## 🛠 Tech Stack

* **Language:** Python 3.9+
* **Web Framework:** [Streamlit](https://streamlit.io/)
* **Data Processing & Analytics:** [Pandas](https://pandas.pydata.org/)
* **Database / Persistence:** JSON (`school_data.json`)
* **Styling:** Custom CSS with Google Fonts integration (`Plus Jakarta Sans` / `Bricolage Grotesque`)

---

## 📂 Project Structure

```text
├── .streamlit/
│   └── config.toml        # Streamlit visual theme configuration
├── app.py                 # Streamlit web application (standard theme)
├── school_app.py          # Streamlit web application (enhanced gradient dashboard)
├── main.py                # Command-line interface (CLI) application
├── school_data.json       # JSON-based data storage for students and teachers
└── README.md              # Project documentation