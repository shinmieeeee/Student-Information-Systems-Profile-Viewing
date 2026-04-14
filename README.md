# Student Information System

A desktop application built with Python and Tkinter for managing student records. It supports full CRUD operations and student profile management (bio + photo), backed by a MySQL database.

---

## Features

- **Add, Update, Delete** student records
- **Search** students by SR Code or Full Name
- **Student Profile Panel** — view/edit student info and upload a profile picture
- **Persistent storage** via MySQL

---

## Requirements

- Python 3.8+
- MySQL Server (running locally)
- Python packages:

```
mysql-connector-python
Pillow
```

Install dependencies:

```bash
pip install mysql-connector-python Pillow
```

---

## Database Setup

1. Make sure MySQL is running on `localhost`.
2. Create the database:

```sql
CREATE DATABASE informationsystem;
```

3. The app will automatically create the required tables (`Student` and `StudentProfile`) on first run.

**Default connection settings** (edit `get_connection()` in the script if needed):

| Setting  | Value              |
|----------|--------------------|
| Host     | localhost          |
| User     | root               |
| Password | *(empty)*          |
| Database | informationsystem  |

---

## How to Run

```bash
python main.py
```

> Make sure `finalproject.jpg` is in the same directory if you want the header banner image to display. Otherwise, it falls back to a plain text header.

---

## Project Structure

```
main.py               # Main application file
finalproject.jpg      # (Optional) Header banner image
README.md
```

---

## Database Schema

**Student**

| Column     | Type         | Description        |
|------------|--------------|--------------------|
| SrCode     | VARCHAR(20)  | Primary key        |
| FullName   | VARCHAR(100) |                    |
| Department | VARCHAR(100) |                    |
| Age        | VARCHAR(10)  |                    |

**StudentProfile**

| Column  | Type      | Description                          |
|---------|-----------|--------------------------------------|
| SrCode  | VARCHAR(20) | Foreign key → Student.SrCode       |
| Info    | TEXT      | Additional info / bio                |
| Picture | LONGBLOB  | Profile picture (stored as binary)   |

---

## Usage Guide

| Action           | How to do it                                                    |
|------------------|-----------------------------------------------------------------|
| Add student      | Fill in all fields on the left panel, click **Add**            |
| Update student   | Click a student in the list, edit fields, click **Update**     |
| Delete student   | Click a student in the list, click **Delete**                  |
| Search           | Type in the search bar and click **Search**                    |
| Clear search     | Click **Clear** next to the search bar                         |
| View profile     | Click any student in the list                                  |
| Edit bio/info    | Select a student, edit the text box, click **Save Info**       |
| Upload photo     | Select a student, click **Upload Picture**, choose an image    |

---

## Notes

- Deleting a student also deletes their profile (cascading delete).
- Supported image formats for profile pictures: `.png`, `.jpg`, `.jpeg`, `.gif`
- Profile pictures are stored directly in the database as binary data (LONGBLOB).
