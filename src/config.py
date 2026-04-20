from pathlib import Path

APP_TITLE = "Dashboard Retail + IA"
APP_SUBTITLE = "Día 6 · Introducción a APIs y seguridad básica"

EXPECTED_SHEETS = ("Customers", "Products", "Stores", "Transactions")

VIEWS = (
    "Resumen ejecutivo",
    "Tendencias comerciales",
    "Análisis de productos",
    "Clientes y segmentos",
    "Exploración tabular",
    "API y seguridad básica",
)

DEFAULT_TOP_N = 10
MIN_TOP_N = 5
MAX_TOP_N = 20

DEFAULT_GEMINI_MODEL = "gemini-3-flash-preview"

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "raw" / "retail_sales_dataset.xlsx"