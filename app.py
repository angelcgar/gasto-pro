from flask import Flask, redirect, render_template, request, session, flash
from flask_session import Session
from werkzeug.security import generate_password_hash
from cs50 import SQL

app = Flask(__name__)

# Configurar la configuración de la aplicación
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configurar la base de datos
db = SQL("sqlite:///gasto.db")

@app.route("/")
def index():
    return render_template("index.html")

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

if __name__ == "__main__":
    app.run(debug=True)
