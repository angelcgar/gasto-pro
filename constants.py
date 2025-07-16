from dotenv import load_dotenv
import os

load_dotenv()  # Carga el archivo .env

# Leer variables
secret_key = os.getenv("FLASK_SECRET_KEY")
database_url = os.getenv("DATABASE_URL")
debug_mode = os.getenv("DEBUG", "False") == "True"
