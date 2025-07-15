from flask import Flask, redirect, render_template, request, session, flash
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from cs50 import SQL

from helpers import login_required, usd

app = Flask(__name__)

# Configurar la configuración de la aplicación
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.jinja_env.filters["usd"] = usd
Session(app)

# Configurar la base de datos
db = SQL("sqlite:///gasto.db")

@app.route("/")
@login_required
def index() -> str:
    user_id: int = session["user_id"]

    # Obtener información del usuario
    user = db.execute("SELECT username, cash FROM users WHERE id = ?", user_id)[0]
    username: str = user["username"]
    cash: float = float(user["cash"])

    return render_template("index.html", username=username, cash=cash)

@app.route("/register", methods=["GET", "POST"])
def register():
    # Si el usuario envía el formulario
    if request.method == "POST":
        username: str = request.form.get("username", "").strip()
        password: str = request.form.get("password", "")
        confirmation: str = request.form.get("confirmation", "")

        # Validar campos
        if not username or not password or not confirmation:
            flash("All fields are required.")
            return render_template("register.html")

        if password != confirmation:
            flash("Passwords do not match.")
            return render_template("register.html")

        # Hashear la contraseña
        password_hash: str = generate_password_hash(password)

        # Intentar registrar al usuario
        try:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, password_hash)
        except Exception:
            flash("Username already exists.")
            return render_template("register.html")

        flash("Account created successfully! Please log in.")
        return redirect("/login")

    # Si el usuario llega con GET
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login() :
    # Limpiar cualquier sesión previa
    session.clear()

    if request.method == "POST":
        username: str = request.form.get("username", "").strip()
        password: str = request.form.get("password", "")

        # Validar campos
        if not username or not password:
            flash("Username and password are required.")
            return render_template("login.html")

        # Buscar usuario en la base de datos
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Verificar usuario y contraseña
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            flash("Invalid username or password.")
            return render_template("login.html")

        # Iniciar sesión guardando el user_id
        session["user_id"] = rows[0]["id"]

        flash("Welcome back!")
        return redirect("/")

    return render_template("login.html")

@app.route("/logout")
def logout():
    # Borrar todos los datos de sesión
    session.clear()

    # Notificar al usuario
    flash("You have been logged out.")

    # Redirigir al login
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)
