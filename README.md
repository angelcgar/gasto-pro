# 💸 Gasto Pro – CS50 Final Project

Gasto Pro es una aplicación web de control de gastos personales creada como proyecto final para CS50x 2025. Permite a los usuarios registrar ingresos y egresos, visualizar su historial financiero, analizar sus gastos mensuales y recibir sugerencias generadas por inteligencia artificial.

---

## 🚀 Características

- Registro y login de usuarios
- Agregar ingresos y gastos por categoría
- Historial con desglose por tipo y categoría
- Análisis mensual con porcentajes por categoría
- 💡 Integración de IA (OpenAI) para ofrecer recomendaciones financieras automáticas
- Interfaz amigable con Bootstrap

---

## 🧠 Inteligencia Artificial

La app incluye una sección de "GastoPro AI Advisor" que usa **OpenAI** para analizar tus gastos mensuales y ofrecerte sugerencias breves en español.
La generación se realiza bajo demanda para evitar lentitud, usando un botón interactivo.

---

## ⚙️ Tecnologías utilizadas

- **Python** con **Flask**
- SQLite como base de datos relacional
- Jinja2 para plantillas HTML
- Bootstrap 5 para estilos
- OpenAI API para integración IA

---

## 🛠️ Instalación local

1. Clona el repositorio:

```bash
git clone https://github.com/tu_usuario/gasto-pro.git
cd gasto-pro
```

2. Crea un entorno virtual e instala las dependencias

```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Crea un archivo .env y agrega tu clave API de OpenAI:

```bash
OPENAI_API_KEY=sk-...
```

4. Corre la aplicación:
```bash
flask run
```

## Archivos importantes
- app.py: lógica principal de la app

- const.py: constantes globales, incluyendo el modelo IA configurable (GPT_MODEL)

- helpers.py: funciones auxiliares como login_required

- templates/: todas las vistas HTML

- static/: estilos e íconos (si los agregas)

## Sobre el modelo IA
El modelo de OpenAI se configura desde constants.py:

```python
GPT_MODEL = "gpt-3.5-turbo"
```

## Proyecto final para CS50x
Este proyecto fue creado como parte del curso CS50's Introduction to Computer Science.

Cumple con los requisitos técnicos del proyecto final, incluyendo originalidad, complejidad, y un componente de software completo con funcionalidad real y útil.

## Futuras mejoras
- Guardar historial de recomendaciones de IA

- Modo oscuro y tema móvil

- Exportar transacciones en CSV

- Alertas de gasto automático
