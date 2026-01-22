# Event Management System

This is a simple web application built using **Flask** for managing events.  
The application allows users to register, log in, access a personalized dashboard, and create or manage events through a clean and minimal interface.

It is designed with clarity and modularity in mind, making it suitable for learning, academic evaluation, and small-scale use cases.

---

## Overview

The system supports authenticated users who can manage events and track deadlines.  
The application follows a structured layout with clear separation between routing logic, templates, static assets, and configuration.

---

## Key Features

- User authentication (login and registration)
- Dashboard view after successful login
- Create, view, edit, and manage events
- Deadline and event notifications
- Reusable layout using template inheritance
- Simple and clean user interface
- SQLite database for local development

---

## Feature Summary

| Area | Description |
|-----|------------|
| Authentication | User login and registration |
| Dashboard | Central view for user activity |
| Events | Create, edit, view, and manage events |
| Notifications | Deadline and event reminders |
| UI | Reusable templates with clean styling |

---

## Technology Stack

| Component | Technology |
|---------|------------|
| Backend | Python, Flask |
| Frontend | HTML, CSS (Jinja templates) |
| Database | SQLite |
| Architecture | Modular Flask application |

---

## Prerequisites

- Python 3.7 or later  
- pip (Python package installer)

---

## Project Structure

```text
app/
├── routes/             # Authentication, dashboard, and event logic
├── templates/          # HTML templates
├── static/             # CSS files
├── models.py           # Database models
run.py                  # Application entry point
config.py               # Application configuration
requirements.txt        # Python dependencies
```


## Database

The application uses **SQLite** as its database for local development.  
The database is lightweight, file-based, and well suited for small-scale applications and learning purposes.

---

## Notes

- The application emphasizes simplicity and readability  
- Designed primarily for educational and academic use  
- The structure allows future extensions such as email notifications or external databases  

---

## Ownership

This project is developed and maintained by **Sachin Tiwari**.  
It is intended for educational and personal learning purposes.
