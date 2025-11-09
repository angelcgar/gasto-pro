from flask import redirect, session
from functools import wraps
from decimal import Decimal

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def usd(value: float) -> str:
    """Formatea el valor como USD"""
    return f"${value:,.2f}"

def calculate_monthly_analysis(rows):
    """
    Calcula el análisis mensual de transacciones.

    Args:
        rows: Lista de transacciones con campos amount, category, type

    Returns:
        dict con income_total, expense_total, income_pct, expense_pct, category_percentages
    """
    # Agrupar los datos usando Decimal para precisión
    income_total = sum(Decimal(row["amount"]) for row in rows if row["type"] == "income")
    expense_total = sum(Decimal(row["amount"]) for row in rows if row["type"] == "expense")
    total = income_total + expense_total

    # Porcentaje de ingresos vs gastos
    income_pct = round(float(income_total / total * 100), 2) if total else 0
    expense_pct = round(float(expense_total / total * 100), 2) if total else 0

    # Gasto por categoría
    category_totals = {}
    for row in rows:
        if row["type"] == "expense":
            category_totals[row["category"]] = category_totals.get(row["category"], Decimal(0)) + Decimal(row["amount"])

    # Total de gastos para porcentajes por categoría
    total_expense = sum(category_totals.values())
    category_percentages = {
        category: round(float(amount / total_expense * 100), 2)
        for category, amount in category_totals.items()
    } if total_expense else {}

    return {
        "income_total": float(income_total),
        "expense_total": float(expense_total),
        "income_pct": income_pct,
        "expense_pct": expense_pct,
        "category_percentages": category_percentages
    }

def generate_ai_prompt(income_total, expense_total, category_percentages):
    """
    Genera el prompt para el análisis de IA.

    Args:
        income_total: Total de ingresos
        expense_total: Total de gastos
        category_percentages: Diccionario con porcentajes por categoría

    Returns:
        str: Prompt formateado para la IA
    """
    return f"""
Resume los gastos de este mes. Total ingresos: ${income_total:.2f}, total gastos: ${expense_total:.2f}.
Porcentajes de gasto por categoría: {category_percentages}.
Proporciona un consejo financiero corto en español.
"""

def get_ai_response(client, prompt):
    """
    Obtiene respuesta de la IA usando OpenAI.

    Args:
        client: Cliente de OpenAI configurado
        prompt: Texto del prompt

    Returns:
        str: Respuesta de la IA o mensaje de error
    """
    try:
        response = client.chat.completions.create(
            model="openai/gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return "La IA no está disponible en este momento."
