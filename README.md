[README.md](https://github.com/user-attachments/files/33908180/README.md)
# Excel Form App – Library Catalogue Manager

A Django web application built during my internship to manage the book catalogue of the **Sparta Library**. It replaces a manually maintained Excel file with a database-backed system: staff can import existing Excel catalogues, resolve duplicate records, add new books and browse or print the full catalogue.

## Features

- **User accounts** – sign up (unique email required), log in and log out. All catalogue pages require authentication.
- **Excel import** (`/upload/`) – upload an `.xlsx` file and bulk-insert the records into the database.
  - Rows without an accession number are skipped.
  - Duplicate accession numbers inside the same file are skipped.
  - A summary page shows how many records were added, skipped and flagged as duplicates.
- **Duplicate resolution** (`/duplicates/`) – when an imported accession number already exists in the database, the old and new records are shown side by side. You can edit the existing record, skip the duplicate, or skip all of them at once.
- **Catalogue view** (`/people/`) – table of all records sorted numerically by accession number, with filters and a print-friendly layout.
- **Add / edit records** – a form for adding a new book (the next accession number is generated automatically) and a form for editing existing ones.
- **Upload history** – every import is logged (user, file name, time, rows added) and visible in the Django admin.

## Tech stack

- Python 3, Django
- PostgreSQL
- pandas + openpyxl (Excel import)
- Django templates (HTML/CSS)

## Project structure

```
excel_form_app/
├── manage.py
├── excel_form_app/        # project settings and root URLs
├── main/                  # the application
│   ├── models.py          # Person (book record) and UploadLog
│   ├── views.py           # import, duplicates, catalogue, add/edit
│   ├── forms.py
│   ├── urls.py
│   ├── migrations/
│   └── templates/
└── templates/             # base layout, home page, login / signup
```

> The model is named `Person` for historical reasons; each record represents a book.

## Getting started

### Prerequisites

- Python 3.12 or newer
- PostgreSQL

### 1. Clone the repository

```bash
git clone <repository-url>
cd excel_form_app
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install django pandas openpyxl psycopg2-binary
```

### 3. Create the database

Create an empty PostgreSQL database named `mydatabase` (for example with pgAdmin, or `createdb mydatabase`).

### 4. Configure the database connection

In `excel_form_app/settings.py`, update the `DATABASES` section with your own PostgreSQL credentials:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mydatabase',
        'USER': 'postgres',
        'PASSWORD': 'your-password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

Do not commit real credentials. For anything beyond local development, load the password and `SECRET_KEY` from environment variables and set `DEBUG = False`.

### 5. Apply migrations and create an admin user

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Run the development server

```bash
python manage.py runserver
```

Open <http://127.0.0.1:8000>, log in, and go to `/upload/` to import your Excel file.

## Excel file format

The importer reads the following column headers (in Greek):

| Column | Meaning |
|---|---|
| ΑΡΙΘΜΟΣ ΕΙΣΑΓΩΓΗΣ | Accession number (required, unique) |
| ΗΜΕΡΟΜΗΝΙΑ ΕΙΣΑΓΩΓΗΣ | Date of acquisition |
| ΣΥΓΓΡΑΦΕΑΣ | Author |
| ΣΥΓΓΡΑΦΕΑΣ KOHA | Author (Koha format) |
| ΤΙΤΛΟΣ | Title |
| ΕΚΔΟΤΗΣ | Publisher |
| ΕΚΔΟΣΗ | Edition |
| ΕΤΟΣ ΕΚΔΟΣΗΣ | Year of publication |
| ΤΟΠΟΣ  ΕΚΔΟΣΗΣ | Place of publication (note the double space) |
| ΣΧΗΜΑ | Format |
| ΣΕΛΙΔΕΣ | Pages |
| ΤΟΜΟΣ | Volume |
| ΤΡΟΠΟΣ ΠΡΟΜΗΘΕΙΑΣ ΠΑΡΑΤΗΡΗΣΕΙΣ | Acquisition method / notes |
| ISBN | ISBN |
| Στήλη1, Στήλη2 | Extra columns |

Missing columns are imported as empty values.

## Main routes

| URL | Description |
|---|---|
| `/` | Home page |
| `/signup/`, `/accounts/login/` | Registration and login |
| `/upload/` | Import an Excel file |
| `/duplicates/` | Resolve duplicate records |
| `/people/` | Browse and print the catalogue |
| `/add-person/` | Add a new record |
| `/person/edit/<id>/` | Edit a record |
| `/admin/` | Django admin (upload history) |

## Known limitations

- Skipping a duplicate does not overwrite the existing record; to change it, use the edit option.
- Adding a record manually relies on PostgreSQL's `REGEXP_REPLACE`, so it does not work on SQLite.
- Database settings are currently stored in `settings.py` rather than environment variables.

## Author

Created by me and my colegues as part of an internship project.
