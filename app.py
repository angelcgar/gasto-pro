# python
from decimal import Decimal, InvalidOperation
import os

# flask
from flask import Flask, jsonify, redirect, render_template, request, session, flash
from flask_session import Session
# werkzeug
from werkzeug.security import generate_password_hash, check_password_hash
# cs50
from cs50 import SQL

# openai
from openai import OpenAI as OpenAIClient

# Configuración de la app
from helpers import login_required, usd, calculate_monthly_analysis, generate_ai_prompt, get_ai_response
from constants import secret_key, database_url, debug_mode, openai_api_key

app = Flask(__name__)

# Configurar la configuración de la aplicación
app.config["SECRET_KEY"] = secret_key or os.urandom(24)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.jinja_env.filters["usd"] = usd
Session(app)

# Configurar la base de datos
db = SQL(database_url)

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
            flash("Todos los campos son obligatorios.", "error")
            return render_template("register.html")

        if password != confirmation:
            flash("Las contraseñas no coinciden.", "error")
            return render_template("register.html")

        # Hashear la contraseña
        password_hash: str = generate_password_hash(password)

        # Intentar registrar al usuario
        try:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, password_hash)
        except Exception:
            flash("El nombre de usuario ya existe.", "error")
            return render_template("register.html")

        flash("¡Cuenta creada exitosamente! Por favor, inicia sesión.", "success")
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
            flash("El nombre de usuario y la contraseña son obligatorios.", "error")
            return render_template("login.html")

        # Buscar usuario en la base de datos
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Verificar usuario y contraseña
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            flash("Nombre de usuario o contraseña inválidos.", "error")
            return render_template("login.html")

        # Iniciar sesión guardando el user_id
        session["user_id"] = rows[0]["id"]

        flash(f"¡Bienvenido de nuevo, {username}!", "success")
        return redirect("/")

    return render_template("login.html")

@app.route("/logout")
def logout():
    # Borrar todos los datos de sesión
    session.clear()

    # Notificar al usuario
    flash("Has cerrado sesión exitosamente.", "info")

    # Redirigir al login
    return redirect("/login")

@app.route("/transaction", methods=["GET", "POST"])
@login_required
def transaction():
    if request.method == "POST":
        description: str = request.form.get("description", "").strip()
        amount_str: str = request.form.get("amount", "").strip()
        category: str = request.form.get("category", "").strip()
        type_: str = request.form.get("type", "")

        # Validar que todos los campos estén presentes
        if not description or not amount_str or not category or type_ not in ("income", "expense"):
            flash("Todos los campos son obligatorios.", "error")
            categories = db.execute("SELECT name FROM categories ORDER BY name ASC")
            return render_template("transaction.html", categories=categories)

        try:
            amount = Decimal(amount_str)
            if amount <= 0:
                raise InvalidOperation
        except InvalidOperation:
            flash("El monto debe ser un número positivo válido.", "error")
            categories = db.execute("SELECT name FROM categories ORDER BY name ASC")
            return render_template("transaction.html", categories=categories)

        user_id = session["user_id"]

        # Insertar la transacción
        db.execute(
            "INSERT INTO transactions (user_id, description, amount, category, type) VALUES (?, ?, ?, ?, ?)",
            session["user_id"], description, str(amount), category, type_
        )

        # Actualizar el cash del usuario
        if type_ == "income":
            db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", str(amount), user_id)
        elif type_ == "expense":
            db.execute("UPDATE users SET cash = cash - ? WHERE id = ?", str(amount), user_id)

        # Mensaje diferenciado según el tipo
        tipo_texto = "ingreso" if type_ == "income" else "gasto"
        flash(f"¡{tipo_texto.capitalize()} de {usd(float(amount))} registrado exitosamente!", "success")
        return redirect("/")

    # GET: obtener las categorías de la base de datos
    categories = db.execute("SELECT name FROM categories ORDER BY name ASC")
    return render_template("transaction.html", categories=categories)

@app.route("/history")
@login_required
def history():
    transactions = db.execute(
        "SELECT description, amount, category, type, timestamp FROM transactions WHERE user_id = ? ORDER BY timestamp DESC",
        session["user_id"]
    )
    return render_template("history.html", transactions=transactions)

@app.route("/analysis")
@login_required
def analysis():
    user_id = session["user_id"]

    # Transacciones del mes actual
    rows = db.execute("""
        SELECT amount, category, type, timestamp
        FROM transactions
        WHERE user_id = ?
          AND strftime('%Y-%m', timestamp) = strftime('%Y-%m', 'now')
    """, user_id)

    # Calcular análisis usando función auxiliar
    analysis_data = calculate_monthly_analysis(rows)

    return render_template("analysis.html",
                            income_pct=analysis_data["income_pct"],
                            expense_pct=analysis_data["expense_pct"],
                            category_percentages=analysis_data["category_percentages"],
                            income_total=analysis_data["income_total"],
                            expense_total=analysis_data["expense_total"])

@app.route("/analysis/ai")
@login_required
def analysis_ai():
    user_id = session["user_id"]

    # Transacciones del mes actual
    rows = db.execute("""
        SELECT amount, category, type, timestamp
        FROM transactions
        WHERE user_id = ?
          AND strftime('%Y-%m', timestamp) = strftime('%Y-%m', 'now')
    """, user_id)

    # Calcular análisis usando función auxiliar
    analysis_data = calculate_monthly_analysis(rows)

    # Generar prompt y obtener respuesta de IA
    prompt = generate_ai_prompt(
        analysis_data["income_total"],
        analysis_data["expense_total"],
        analysis_data["category_percentages"]
    )

    # Configurar cliente de OpenAI
    client = OpenAIClient(
        base_url="https://openrouter.ai/api/v1",
        api_key=openai_api_key
    )

    # Obtener respuesta de la IA
    ai_message = get_ai_response(client, prompt)

    return jsonify({"message": ai_message})

if __name__ == "__main__":
    app.run(debug=True)
