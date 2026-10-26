from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
from cachelib import FileSystemCache
import pymysql
import bcrypt
import os
import math
from dotenv import load_dotenv
import re
from werkzeug.utils import secure_filename


# =====================================================
# 1. FLASK CONFIGURATION
# =====================================================

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

if not app.config["SECRET_KEY"]:
    raise RuntimeError("SECRET_KEY is missing from .env")

app.config["SESSION_TYPE"] = "cachelib"
app.config["SESSION_CACHELIB"] = FileSystemCache(
    cache_dir="session_cache",
    threshold=500,
)
app.config["SESSION_PERMANENT"] = False

Session(app)
# Image upload configuration
app.config["UPLOAD_FOLDER"] = os.path.join(
    app.root_path, "static", "uploads"
)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

def allowed_image(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_IMAGE_EXTENSIONS
    )


# =====================================================
# 2. MYSQL DATABASE CONNECTION
# =====================================================

def get_db():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        cursorclass=pymysql.cursors.DictCursor,
    )


# =====================================================
# 3. HOME PAGE
# =====================================================

@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("library"))
    return redirect(url_for("login"))


# =====================================================
# 4. USER REGISTRATION
# =====================================================

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", errors=[])

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    errors = []

    if not name:
        errors.append("Name is required")
    
    if not email:
        errors.append("Email is required")
    elif not re.fullmatch(
        r"[A-Za-z0-9._%+-]+@gmail\.com",
        email,
        re.IGNORECASE
    ):
        errors.append(
            "Please enter a valid Gmail address ending in @gmail.com"
        )

    if not password:
        errors.append("Password is required")
    if not confirm_password:
        errors.append("Confirm password is required")
    if password and confirm_password and password != confirm_password:
        errors.append("Passwords do not match")

    if errors:
        return render_template("register.html", errors=errors)

    hashed_password = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")

    connection = get_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (email, name, password_hash)
                VALUES (%s, %s, %s)
                """,
                (email, name, hashed_password),
            )
            user_id = cursor.lastrowid

        connection.commit()

    except pymysql.err.IntegrityError as error:
        connection.rollback()
        if error.args[0] == 1062:
            return render_template(
                "register.html",
                errors=["Email Already Exists"],
            )
        raise
    finally:
        connection.close()

    session.clear()
    session["user_id"] = user_id
    session["name"] = name
    return redirect(url_for("library"))


# =====================================================
# 5. USER LOGIN
# =====================================================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", errors=[])

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    errors = []
    if not email:
        errors.append("Email is required")
    if not password:
        errors.append("Password is required")

    if errors:
        return render_template("login.html", errors=errors)

    connection = get_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT user_id, name, password_hash
                FROM users
                WHERE email = %s
                """,
                (email,),
            )
            user = cursor.fetchone()
    finally:
        connection.close()

    if not user:
        return render_template(
            "login.html",
            errors=["Invalid email or password"],
        )

    try:
        password_correct = bcrypt.checkpw(
            password.encode("utf-8"),
            user["password_hash"].encode("utf-8"),
        )
    except (ValueError, TypeError):
        password_correct = False

    if not password_correct:
        return render_template(
            "login.html",
            errors=["Invalid email or password"],
        )

    session.clear()
    session["user_id"] = user["user_id"]
    session["name"] = user["name"]
    return redirect(url_for("library"))


# =====================================================
# 6. USER LOGOUT
# =====================================================

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))


# =====================================================
# 7. LIBRARY: DISPLAY AUTHORS AND BOOKS
# =====================================================

@app.route("/library")
def library():
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db()
    try:
        with connection.cursor() as cursor:
            
            cursor.execute(
                """
                SELECT author_id, name, country, photo_filename
                FROM AUTHOR
                ORDER BY author_id
                """
            )
            authors = cursor.fetchall()


            
            cursor.execute(
                """
                SELECT book_id, title, price, author_id, cover_filename
                FROM BOOK
                ORDER BY book_id
                """
            )
            books = cursor.fetchall()

    finally:
        connection.close()

    return render_template(
        "library.html",
        name=session["name"],
        authors=authors,
        books=books,
    )


# =====================================================
# 8. ADD AUTHOR
# =====================================================


@app.route("/authors/add", methods=["GET", "POST"])
def add_author():
    if "user_id" not in session:
        return redirect(url_for("login"))

    errors = []

    if request.method == "POST":
        author_id_input = request.form.get("author_id", "").strip()
        author_name = request.form.get("name", "").strip()
        country = request.form.get("country", "").strip()

        photo = request.files.get("author_photo")
        has_photo = photo is not None and bool(photo.filename.strip())

        if not author_id_input.isdigit() or int(author_id_input) < 1:
            errors.append("Author ID must be a positive number.")

        if not author_name:
            errors.append("Author name is required.")
        elif len(author_name) > 100:
            errors.append("Author name cannot exceed 100 characters.")

        if not country:
            errors.append("Country is required.")
        elif len(country) > 50:
            errors.append("Country cannot exceed 50 characters.")

        safe_name = None

        if has_photo:
            if not allowed_image(photo.filename):
                errors.append(
                    "Photo must be JPG, JPEG, PNG, or WebP."
                )
            else:
                safe_name = secure_filename(photo.filename)
                if not safe_name:
                    errors.append("Invalid photo filename.")

        if not errors:
            connection = get_db()
            saved_path = None

            try:
                photo_filename = None

                if has_photo:
                    photo_filename = (
                        f"{os.urandom(8).hex()}_{safe_name}"
                    )
                    saved_path = os.path.join(
                        app.config["UPLOAD_FOLDER"],
                        photo_filename,
                    )
                    photo.save(saved_path)

                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO AUTHOR
                            (author_id, name, country, photo_filename)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (
                            int(author_id_input),
                            author_name,
                            country,
                            photo_filename,
                        ),
                    )

                connection.commit()
                return redirect(url_for("library"))

            except pymysql.err.IntegrityError as error:
                connection.rollback()

                if saved_path and os.path.isfile(saved_path):
                    os.remove(saved_path)

                if error.args[0] == 1062:
                    error_message = str(error.args[1])

                    if "uq_author_name" in error_message:
                        errors.append("An author with this name already exists.")
                    else:
                        errors.append("This Author ID already exists.")
                else:
                    errors.append("Could not add the author.")

            except Exception:
                connection.rollback()

                if saved_path and os.path.isfile(saved_path):
                    os.remove(saved_path)

                raise

            finally:
                connection.close()

    return render_template("add_author.html", errors=errors)



# =====================================================
# 9. EDIT AUTHOR
# =====================================================


@app.route("/authors/<int:author_id>/edit", methods=["GET", "POST"])
def edit_author(author_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    errors = []
    connection = get_db()
    saved_path = None

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM AUTHOR WHERE author_id = %s",
                (author_id,),
            )
            author = cursor.fetchone()

        if not author:
            return "Author not found", 404

        if request.method == "POST":
            name = request.form.get("name", "").strip()
            country = request.form.get("country", "").strip()

            photo = request.files.get("author_photo")
            has_photo = (
                photo is not None and bool(photo.filename.strip())
            )

            if not name:
                errors.append("Author name is required.")
            elif len(name) > 100:
                errors.append("Author name cannot exceed 100 characters.")

            if not country:
                errors.append("Country is required.")
            elif len(country) > 50:
                errors.append("Country cannot exceed 50 characters.")

            photo_filename = author.get("photo_filename")

            if has_photo:
                if not allowed_image(photo.filename):
                    errors.append(
                        "Photo must be JPG, JPEG, PNG, or WebP."
                    )
                else:
                    safe_name = secure_filename(photo.filename)

                    if not safe_name:
                        errors.append("Invalid photo filename.")
                    else:
                        photo_filename = (
                            f"{os.urandom(8).hex()}_{safe_name}"
                        )

            if not errors:
                try:
                    if has_photo:
                        saved_path = os.path.join(
                            app.config["UPLOAD_FOLDER"],
                            photo_filename,
                        )
                        photo.save(saved_path)

                    with connection.cursor() as cursor:
                        cursor.execute(
                            """
                            UPDATE AUTHOR
                            SET name = %s,
                                country = %s,
                                photo_filename = %s
                            WHERE author_id = %s
                            """,
                            (name, country, photo_filename, author_id),
                        )

                    connection.commit()
                    return redirect(url_for("library"))

                except pymysql.err.IntegrityError as error:
                    connection.rollback()

                    if saved_path and os.path.isfile(saved_path):
                        os.remove(saved_path)

                    if error.args[0] == 1062:
                        errors.append(
                            "An author with this name already exists."
                        )
                    else:
                        errors.append("Could not update the author.")

                except Exception:
                    connection.rollback()

                    if saved_path and os.path.isfile(saved_path):
                        os.remove(saved_path)

                    raise

            author["name"] = name
            author["country"] = country

    finally:
        connection.close()

    return render_template(
        "edit_author.html",
        author=author,
        errors=errors,
    )

# =====================================================
# 10. DELETE AUTHOR
# =====================================================

@app.route("/authors/<int:author_id>/delete", methods=["POST"])
def delete_author(author_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM AUTHOR WHERE author_id = %s",
                (author_id,),
            )
        connection.commit()
    except pymysql.err.IntegrityError:
        connection.rollback()
        return (
            "Cannot delete this author because related books exist. "
            "Check that the BOOK foreign key uses ON DELETE CASCADE.",
            409,
        )
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

    return redirect(url_for("library"))


# =====================================================
# 11. ADD BOOK
# =====================================================


@app.route("/books/add", methods=["GET", "POST"])
def add_book():
    if "user_id" not in session:
        return redirect(url_for("login"))

    errors = []
    connection = get_db()
    saved_path = None

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT author_id, name FROM AUTHOR ORDER BY author_id"
            )
            authors = cursor.fetchall()

        if request.method == "POST":
            book_id_input = request.form.get("book_id", "").strip()
            title = request.form.get("title", "").strip()
            price_input = request.form.get("price", "").strip()
            author_input = request.form.get("author_id", "").strip()

            cover_upload = request.files.get("cover_image")
            has_cover = (
                cover_upload is not None
                and bool(cover_upload.filename.strip())
            )

            safe_cover_name = None

            if not book_id_input.isdigit() or int(book_id_input) < 1:
                errors.append("Book ID must be a positive number.")

            if not title:
                errors.append("Book title is required.")
            elif len(title) > 100:
                errors.append("Book title cannot exceed 100 characters.")

            price = None

            if not price_input:
                errors.append("Price is required.")
            else:
                try:
                    price = float(price_input)

                    if not math.isfinite(price):
                        errors.append("Enter a valid price.")
                    elif price < 0:
                        errors.append("Price cannot be negative.")

                except ValueError:
                    errors.append("Enter a valid price.")

            valid_author_ids = {
                author["author_id"] for author in authors
            }

            if not author_input.isdigit():
                errors.append("Please select a valid author.")
            elif int(author_input) not in valid_author_ids:
                errors.append("Selected author does not exist.")

            # Validate the optional cover image.
            if has_cover:
                if not allowed_image(cover_upload.filename):
                    errors.append(
                        "Cover must be a JPG, JPEG, PNG, or WebP image."
                    )
                else:
                    safe_cover_name = secure_filename(
                        cover_upload.filename
                    )

                    if not safe_cover_name:
                        errors.append("Invalid image filename.")

            if not errors:
                cover_filename = None

                try:
                    # Save the image using a unique filename.
                    if has_cover:
                        cover_filename = (
                            f"{os.urandom(8).hex()}_{safe_cover_name}"
                        )

                        saved_path = os.path.join(
                            app.config["UPLOAD_FOLDER"],
                            cover_filename,
                        )

                        cover_upload.save(saved_path)

                    with connection.cursor() as cursor:
                        cursor.execute(
                            """
                            INSERT INTO BOOK
                                (book_id, title, price, author_id,
                                 cover_filename)
                            VALUES (%s, %s, %s, %s, %s)
                            """,
                            (
                                int(book_id_input),
                                title,
                                price,
                                int(author_input),
                                cover_filename,
                            ),
                        )

                    connection.commit()
                    return redirect(url_for("library"))

                except pymysql.err.IntegrityError as error:
                    connection.rollback()

                    if saved_path and os.path.isfile(saved_path):
                        os.remove(saved_path)

                    if error.args[0] == 1062:
                        error_message = str(error.args[1])
                        if "uq_book_title" in error_message:
                            errors.append("A book with this title already exists.")
                        else:
                            errors.append("This Book ID already exists.")
                    else:
                         errors.append(
        "Could not add the book. Check the selected author."
    )

                except Exception:
                    connection.rollback()

                    if saved_path and os.path.isfile(saved_path):
                        os.remove(saved_path)

                    raise

    finally:
        connection.close()

    return render_template(
        "add_book.html",
        errors=errors,
        authors=authors,
    )
# =====================================================
# 12. EDIT BOOK
# =====================================================
@app.route("/books/<int:book_id>/edit", methods=["GET", "POST"])
def edit_book(book_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    errors = []
    connection = get_db()
    saved_path = None

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM BOOK WHERE book_id = %s",
                (book_id,),
            )
            book = cursor.fetchone()

            if not book:
                return "Book not found", 404

            cursor.execute(
                "SELECT author_id, name FROM AUTHOR ORDER BY author_id"
            )
            authors = cursor.fetchall()

        if request.method == "POST":
            title = request.form.get("title", "").strip()
            price_input = request.form.get("price", "").strip()
            author_input = request.form.get("author_id", "").strip()

            cover = request.files.get("cover_image")
            has_cover = cover is not None and bool(cover.filename.strip())

            if not title:
                errors.append("Book title is required.")
            elif len(title) > 100:
                errors.append("Book title cannot exceed 100 characters.")

            price = None
            if not price_input:
                errors.append("Price is required.")
            else:
                try:
                    price = float(price_input)
                    if not math.isfinite(price):
                        errors.append("Enter a valid price.")
                    elif price < 0:
                        errors.append("Price cannot be negative.")
                except ValueError:
                    errors.append("Enter a valid price.")

            valid_author_ids = {a["author_id"] for a in authors}
            author_id_value = None

            if not author_input.isdigit():
                errors.append("Select a valid author.")
            elif int(author_input) not in valid_author_ids:
                errors.append("Selected author does not exist.")
            else:
                author_id_value = int(author_input)

            # Keep the existing cover unless a replacement is uploaded.
            cover_filename = book.get("cover_filename")

            if has_cover:
                if not allowed_image(cover.filename):
                    errors.append(
                        "Cover must be JPG, JPEG, PNG, or WebP."
                    )
                else:
                    safe_name = secure_filename(cover.filename)
                    if not safe_name:
                        errors.append("Invalid cover filename.")
                    else:
                        cover_filename = (
                            f"{os.urandom(8).hex()}_{safe_name}"
                        )

            if not errors:
                old_cover = book.get("cover_filename")

                try:
                    if has_cover:
                        saved_path = os.path.join(
                            app.config["UPLOAD_FOLDER"],
                            cover_filename,
                        )
                        cover.save(saved_path)

                    with connection.cursor() as cursor:
                        cursor.execute(
                            """
                            UPDATE BOOK
                            SET title = %s,
                                price = %s,
                                author_id = %s,
                                cover_filename = %s
                            WHERE book_id = %s
                            """,
                            (
                                title,
                                price,
                                author_id_value,
                                cover_filename,
                                book_id,
                            ),
                        )

                    connection.commit()

                    # Remove the old cover after the replacement is saved.
                    if has_cover and old_cover:
                        old_path = os.path.join(
                            app.config["UPLOAD_FOLDER"],
                            old_cover,
                        )
                        if os.path.isfile(old_path):
                            os.remove(old_path)

                    return redirect(url_for("library"))

                except pymysql.err.IntegrityError as error:
                    connection.rollback()

                    if saved_path and os.path.isfile(saved_path):
                        os.remove(saved_path)

                    if error.args[0] == 1062:
                        errors.append(
                            "A book with this title already exists."
                        )
                    else:
                        errors.append("Could not update the book.")

                except Exception:
                    connection.rollback()

                    if saved_path and os.path.isfile(saved_path):
                        os.remove(saved_path)

                    raise

            book["title"] = title
            book["price"] = price_input
            if author_id_value is not None:
                book["author_id"] = author_id_value

    finally:
        connection.close()

    return render_template(
        "edit_book.html",
        book=book,
        authors=authors,
        errors=errors,
    )



# =====================================================
# 13. DELETE BOOK
# =====================================================

@app.route("/books/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM BOOK WHERE book_id = %s",
                (book_id,),
            )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

    return redirect(url_for("library"))


# =====================================================
# RUN APPLICATION
# =====================================================

if __name__ == "__main__":
    app.run(debug=True)
