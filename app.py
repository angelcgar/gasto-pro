# python
from decimal import Decimal, InvalidOperation

# flask
from flask import Flask, jsonify, redirect, render_template, request, session, flash
from flask_session import Session
# werkzeug
from werkzeug.security import generate_password_hash, check_password_hash
# cs50
from cs50 import SQL

# openai
from openai import OpenAI

# Configuración de la app
from helpers import login_required, usd
from constants import secret_key, database_url, debug_mode, openai_api_key

app = Flask(__name__)

# Configurar la configuración de la aplicación
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

@app.route("/transaction", methods=["GET", "POST"])
@login_required
def transaction():
    if request.method == "POST":
        description: str = request.form.get("description", "").strip()
        amount_str: str = request.form.get("amount", "").strip()
        category: str = request.form.get("category", "").strip()
        type_: str = request.form.get("type", "")

        # todo: hacerlo mas flexible para el usuario
        if not description or not amount_str or not category or type_ not in ("income", "expense"):
            flash("All fields are required.")
            return render_template("transaction.html")

        try:
            amount = Decimal(amount_str)
            if amount <= 0:
                raise InvalidOperation
        except InvalidOperation:
            flash("Invalid amount.")
            return render_template("transaction.html")

        user_id = session["user_id"]

        # Insertar la transacción
        db.execute(
            "INSERT INTO transactions (user_id, description, amount, category, type) VALUES (?, ?, ?, ?, ?)",
            session["user_id"], description, str(amount), category, type_
        )

        # Actualizar el cash del usuario
        # todo: quitar los string mágicos
        if type_ == "income":
            db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", str(amount), user_id)
        elif type_ == "expense":
            db.execute("UPDATE users SET cash = cash - ? WHERE id = ?", str(amount), user_id)


        flash("Transaction recorded successfully!")
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

    # Agrupar los datos
    income_total = sum(float(row["amount"]) for row in rows if row["type"] == "income")
    expense_total = sum(float(row["amount"]) for row in rows if row["type"] == "expense")
    total = income_total + expense_total

    # Porcentaje de ingresos vs gastos
    income_pct = round(income_total / total * 100, 2) if total else 0
    expense_pct = round(expense_total / total * 100, 2) if total else 0

    # Gasto por categoría
    category_totals = {}
    for row in rows:
        if row["type"] == "expense":
            category_totals[row["category"]] = category_totals.get(row["category"], 0) + float(row["amount"])

    # Total de gastos para porcentajes por categoría
    total_expense = sum(category_totals.values())
    category_percentages = {
        category: round(amount / total_expense * 100, 2)
        for category, amount in category_totals.items()
    } if total_expense else {}

    # Prompt para IA
    prompt = f"""
    Resume los gastos de este mes. Total ingresos: ${income_total:.2f}, total gastos: ${expense_total:.2f}.
    Porcentajes de gasto por categoría: {category_percentages}.
    Proporciona un consejo financiero corto en español.
    """

    # Obtener respuesta de la IA (OpenAI)
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=openai_api_key
    )
    ai_message = None
    try:
        response = client.chat.completions.create(
            model="openai/gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.7,
        )
        ai_message = response.choices[0].message.content
    except Exception as e:
        ai_message = "La IA no está disponible en este momento."

    return render_template("analysis.html",
                            income_pct=income_pct,
                            expense_pct=expense_pct,
                            category_percentages=category_percentages,
                            income_total=income_total,
                            expense_total=expense_total)

@app.route("/analysis/ai")
@login_required
def analysis_ai():
    user_id = session["user_id"]

    rows = db.execute("""
        SELECT amount, category, type, timestamp
        FROM transactions
        WHERE user_id = ?
          AND strftime('%Y-%m', timestamp) = strftime('%Y-%m', 'now')
    """, user_id)

    from decimal import Decimal
    income_total = sum(Decimal(row["amount"]) for row in rows if row["type"] == "income")
    expense_total = sum(Decimal(row["amount"]) for row in rows if row["type"] == "expense")

    category_totals = {}
    for row in rows:
        if row["type"] == "expense":
            category_totals[row["category"]] = category_totals.get(row["category"], 0) + Decimal(row["amount"])

    total_expense = sum(category_totals.values())
    category_percentages = {
        cat: round(amt / total_expense * 100, 2)
        for cat, amt in category_totals.items()
    } if total_expense else {}

    # Generar respuesta IA
    prompt = f"""
    Resume los gastos de este mes. Total ingresos: ${income_total:.2f}, total gastos: ${expense_total:.2f}.
    Porcentajes de gasto por categoría: {category_percentages}.
    Proporciona un consejo financiero corto en español.
    """

    # Obtener respuesta de la IA (OpenAI)
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=openai_api_key
    )
    ai_message = None

    try:
        import openai
        import os
        openai.api_key = os.getenv("OPENAI_API_KEY")
        response = client.chat.completions.create(
            model="openai/gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.7,
        )
        ai_message = response.choices[0].message.content
    except Exception as e:
        ai_message = "La IA no está disponible en este momento."

    return jsonify({"message": ai_message})

if __name__ == "__main__":
    app.run(debug=True)
