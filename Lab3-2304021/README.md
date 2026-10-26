# Library Management System

## 1. Project Description

A web-based Library Management System developed using Python Flask and MySQL. The application allows users to register, log in securely, and manage authors and books through a simple web interface.

## 2. Technologies Used

- **Backend:** Python and Flask
- **Frontend:** HTML, CSS, JavaScript, Bootstrap 5
- **Database:** MySQL
- **Database Connector:** PyMySQL
- **Password Security:** bcrypt
- **Session Management:** Flask-Session
- **Version Control:** Git and GitHub

## 3. Features

- User registration and login
- Secure password hashing
- Add, view, edit, and delete authors
- Add, view, edit, and delete books
- Store an author's name and country
- Store book titles, prices, and author relationships
- Upload author profile photos
- Upload book cover images
- Prevent duplicate author names and book titles
- Validate required fields
- Confirm deletion actions
- Responsive interface with styled buttons

## 4. Requirements

Install the following before running the application:

- Python
- MySQL Server
- MySQL Workbench
- Git

## 5. Installation and Setup

### Step 1 — Open the Website Folder

Open a terminal in the project directory and run:

```powershell
cd website
```

### Step 2 — Create a Virtual Environment

```powershell
python -m venv .venv
```

### Step 3 — Install Dependencies

On Windows, run:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Step 4 — Configure the Environment

Create a local `.env` file by copying `.env.example`:

```powershell
Copy-Item .env.example .env
```

Open `.env` and configure the MySQL connection details and `SECRET_KEY` according to the example file.

Do not upload `.env` or real credentials to GitHub.

### Step 5 — Create the Database

1. Open MySQL Workbench and connect to your MySQL server.
2. Open `Database/schema.sql`.
3. Execute the SQL script.
4. Confirm that the database and required tables have been created.

### Step 6 — Start the Application

Run:

```powershell
.\.venv\Scripts\python.exe app.py
```

### Step 7 — Open the Website

Open the following address in your browser:

http://127.0.0.1:5000

Register an account or log in, then use the Library Management page to manage authors and books.

## 6. Database Structure

### AUTHOR

Stores author information, including:

- `author_id` — Primary key
- `name` — Author name
- `country` — Country
- `photo_filename` — Optional profile photo filename

### BOOK

Stores book information, including:

- `book_id` — Primary key
- `title` — Book title
- `price` — Book price
- `author_id` — Foreign key referencing `AUTHOR`
- `cover_filename` — Optional cover image filename

Each book is associated with an author through the foreign key relationship.

## 7. Security

- Passwords are stored as hashes.
- SQL queries use parameterized statements.
- Database credentials are kept in environment variables.
- Authenticated routes are protected by session management.
- Input validation is performed by the application.

## 8. Running the Project

Start MySQL, activate the configured application environment, and run `app.py` from the `website` directory. Keep the local `.env` file private and ensure all required dependencies are installed.