# Database Systems Lab 2 & Lab 3 — Login, To-Do & Library Application

## 1. Project Information

- **University:** Alexandria National University
- **Faculty:** Faculty of Engineering
- **Course:** Database Systems
- **Assignments:** Lab 2 — Login & To-Do Application; Lab 3 — Foreign Keys and Simple SQL
- **Student Name:** Omar Sherif Mahmoud
- **Student ID:** 2304021

## 2. Project Description

This project is a web application developed using Python Flask and MySQL.

Lab 2 implements user registration, secure login, and personal task management.

Lab 3 extends the existing application with a Library Management system for managing authors and books. Users can view, add, edit, and delete library records through the website.

The application uses MySQL to store data and enforce relationships between tables.

## 3. Technologies Used

- **Backend:** Python and Flask
- **Frontend:** HTML, CSS, JavaScript, Bootstrap 5
- **Database:** MySQL
- **Database Connector:** PyMySQL
- **Password Security:** bcrypt
- **Session Management:** Flask-Session
- **Environment Configuration:** python-dotenv
- **Version Control:** Git and GitHub
- **SQL Development:** MySQL Workbench
- **Code Editor:** Visual Studio Code

## 4. Application Features

### Lab 2 — Login and To-Do Application

- User registration with duplicate-email detection
- Secure login and logout
- Password hashing using bcrypt
- Private task lists for each user
- Add, edit, and delete tasks
- Mark tasks as completed or pending
- Optional task due dates
- Client-side and server-side validation
- Parameterized SQL queries
- Responsive interface
- Dark Mode / Light Mode on the Login, Registration, and To-Do pages

### Lab 3 — Library Management

- Display all authors and books
- Add new authors
- Edit existing authors
- Delete authors
- Add new books
- Edit existing books
- Delete books
- Display each book's author ID
- Validate required author names, countries, book titles, and prices in the application
- Validate numeric IDs and prices
- Use primary keys and foreign keys to maintain referential integrity
- Automatically delete an author's books when that author is deleted, using `ON DELETE CASCADE`
- Require login to access the Library pages

## 5. Installation and Setup

### Step 1 — Install the Requirements

Install:

- Python
- MySQL Server
- MySQL Workbench
- Visual Studio Code
- Git

### Step 2 — Open the Project

Clone the GitHub repository or open the existing project folder in Visual Studio Code.

### Step 3 — Create a Virtual Environment

From the project directory, create a virtual environment:

```bash
python -m venv .venv
```

### Step 4 — Install Dependencies

On Windows, run:

```bash
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Step 5 — Initialize the Lab 2 Database

1. Open MySQL Workbench and connect to the local MySQL server.
2. Open `Database/schema.sql`.
3. Execute the script to create the `registration` database and the `users` and `todos` tables.

**Warning:** This script drops and recreates the `registration` database. Running it again will delete existing application data, including the Library tables.

Run this script only when setting up a fresh database or when intentionally resetting the database.

### Step 6 — Create the Library Tables

In MySQL Workbench:

1. Open `problem2_DDL.sql`.
2. Execute the script.
3. Confirm that the `AUTHOR` and `BOOK` tables exist in the `registration` database.

This script creates the Library tables without dropping the existing database.

### Step 7 — Insert Library Seed Data

In MySQL Workbench:

1. Open `problem2_DML.sql`.
2. Execute it once on a fresh Library database.
3. Verify that at least three authors and six books have been inserted.

Do not rerun the seed-data script after the same records have already been inserted, because the primary keys would be duplicated.

### Step 8 — Run Problem 1 Separately

Problem 1 uses a separate database named `company`.

In MySQL Workbench:

1. Open and execute `problem1_DDL.sql`.
2. Open and execute `problem1_DML.sql`.
3. Verify that `EMPLOYEE`, `DEPARTMENT`, and `PROJECT` each contain at least three records.

The Problem 1 scripts affect the `company` database, while the website uses the `registration` database.

**Warning:** `problem1_DDL.sql` drops and recreates `company`. Execute it only when intentionally resetting Problem 1.

### Step 9 — Configure Environment Variables

Create a `.env` file using `.env.example` as a template.

Configure the following variables with your own local values:

```text
SECRET_KEY=your_generated_secret_key
DB_HOST=localhost
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password
DB_NAME=registration
```

Use a securely generated secret key and your actual MySQL credentials. Never commit `.env` or real passwords to GitHub.

### Step 10 — Start the Flask Application

Open `app.py` in Visual Studio Code and use **Run Python File**.

Alternatively, run:

```bash
.venv\Scripts\python.exe app.py
```

Keep the application running while using the website.

### Step 11 — Open the Website

Open the following URL in your browser:

http://127.0.0.1:5000/

Register or log in using your account. After successful login, the application opens the Library page. Use the **My Tasks** link to access the To-Do application.

## 6. Database Structure

### Database: `registration`

#### Table: `users`

Stores registered user accounts.

- `user_id` — Primary key
- `email` — Unique email address
- `name` — User's name
- `password_hash` — Hashed password
- `registration_date` — Registration timestamp

#### Table: `todos`

Stores tasks belonging to users.

- `todo_id` — Primary key
- `user_id` — Foreign key referencing `users.user_id`
- `title` — Task title
- `is_done` — Completion status
- `created_at` — Creation timestamp
- `due_date` — Optional due date

**Relationship:** One user can have many tasks. Each task belongs to one user.

#### Table: `AUTHOR`

Stores author information.

- `author_id` — Primary key
- `name` — Author's name
- `country` — Author's country

#### Table: `BOOK`

Stores book information.

- `book_id` — Primary key
- `title` — Book title
- `price` — Book price
- `author_id` — Foreign key referencing `AUTHOR.author_id`

**Relationship:** One author can have multiple books. Each book references an author through `author_id`.

**Referential integrity:** The foreign key prevents a book from referencing a nonexistent author. The `ON DELETE CASCADE` constraint deletes the associated books when an author is deleted.

The application requires a country when adding an author and a price when adding or editing a book. These required-field rules are validated by the Flask application.

### Database: `company`

Problem 1 uses three related tables.

#### Table: `EMPLOYEE`

- `ssn` — Primary key
- `fname` — First name
- `lname` — Last name
- `bdate` — Birth date
- `address` — Address
- `gender` — Gender
- `salary` — Salary
- `Dno` — Foreign key referencing `DEPARTMENT.Dnumber`

#### Table: `DEPARTMENT`

- `Dnumber` — Primary key
- `Dname` — Department name
- `mgr_ssn` — Foreign key referencing `EMPLOYEE.ssn`
- `mgr_start_date` — Manager start date

#### Table: `PROJECT`

- `Pnumber` — Primary key
- `Pname` — Project name
- `Plocation` — Project location
- `Dno` — Foreign key referencing `DEPARTMENT.Dnumber`

## 7. Problem 1 — Foreign Key Questions

### Q1.1 — Deleting a Referenced Employee

Attempting to delete an employee who is referenced as a department manager is rejected by MySQL because the deletion would violate referential integrity.

Expected error: **Error 1451**.

### Q1.2 — Inserting a Project for a Nonexistent Department

Attempting to insert a project with a department number that does not exist in `DEPARTMENT` is rejected by MySQL.

Expected error: **Error 1452**.

### Q1.3 — Circular Foreign Key Dependency

If `EMPLOYEE.Dno` and `DEPARTMENT.mgr_ssn` are both `NOT NULL`, inserting the first employee and department creates a circular dependency.

One solution is to allow a foreign-key column to be `NULL` temporarily, insert the initial records, and then update the references once the related records exist. MySQL also requires care when handling circular foreign keys because it does not support deferred foreign-key constraint checking.

The SQL statements and actual results or error messages should be recorded in `problem1_Answers.txt`.

## 8. Security Features

- Passwords are stored as bcrypt hashes.
- SQL statements use parameterized queries.
- Sessions are managed using Flask-Session.
- Protected routes require authentication.
- Task operations enforce task ownership.
- User input is validated on both the client and server.
- Sensitive credentials are stored in environment variables rather than committed to the repository.

## 9. Lab 3 Deliverables

The Lab 3 submission requires the following files:

- `problem1_DDL.sql` — Creates the Problem 1 database and tables.
- `problem1_DML.sql` — Inserts Problem 1 seed data.
- `problem1_Answers.txt` — Contains the SQL and results for Q1.1–Q1.3.
- `problem2_DDL.sql` — Creates the Library tables.
- `problem2_DML.sql` — Inserts at least three authors and six books.
- `website/` — The Flask website and its supporting files.
- `README.md` — Project description and step-by-step setup instructions.

The Lab 3 SQL scripts should be run through MySQL Workbench. The Flask website runs through Python.

## 10. Version Control and Submission

1. Keep the required Lab 3 files in the repository using the folder structure specified by the assignment.
2. Do not commit `.env`, passwords, or other secrets.
3. Verify that both databases and the website work as described.
4. Commit and push the project to GitHub.
5. Submit the GitHub repository link using the submission form specified in the lab handout.