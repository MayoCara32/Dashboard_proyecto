from pathlib import Path

import pandas as pd
import streamlit as st

EXPECTED_SHEETS = ("Customers", "Products", "Stores", "Transactions")

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "raw" / "retail_sales_dataset.xlsx"


def validate_dataset(file_path: Path) -> tuple[list[str], list[str]]:
    if not file_path.exists():
        raise FileNotFoundError(
            "No se encontró el archivo 'retail_sales_dataset.xlsx' en 'data/raw/'."
        )

    xls = pd.ExcelFile(file_path)
    sheet_names = xls.sheet_names
    missing_sheets = [sheet for sheet in EXPECTED_SHEETS if sheet not in sheet_names]

    return sheet_names, missing_sheets


st.set_page_config(
    page_title="Dashboard Retail + IA",
    page_icon="📊",
    layout="wide"
)

st.title("Dashboard Retail + IA")
st.caption("Día 1 · Apertura del proyecto web y estructura base")

st.markdown(
    """
    Esta aplicación será la base del proyecto del módulo.  
    Hoy solo validamos la estructura inicial del proyecto y la presencia del dataset oficial.
    """
)

st.sidebar.header("Estado del proyecto")

try:
    sheet_names, missing_sheets = validate_dataset(DATA_FILE)

    st.sidebar.success("Proyecto listo para continuar.")
    st.sidebar.write(f"Archivo detectado: {DATA_FILE.name}")

    if missing_sheets:
        st.sidebar.warning("El archivo existe, pero faltan hojas esperadas.")
    else:
        st.sidebar.info("Todas las hojas esperadas fueron detectadas.")

    col1, col2, col3 = st.columns(3)
    col1.metric("Archivo detectado", "Sí")
    col2.metric("Hojas encontradas", len(sheet_names))
    col3.metric("Hojas esperadas", len(EXPECTED_SHEETS))

    st.subheader("Ruta del dataset")
    st.code(str(DATA_FILE))

    st.subheader("Hojas detectadas")
    st.dataframe(
        pd.DataFrame({"hoja": sheet_names}),
        use_container_width=True,
        hide_index=True
    )

    if missing_sheets:
        st.error(
            "Faltan hojas necesarias para el proyecto: "
            + ", ".join(missing_sheets)
        )
    else:
        st.success("La estructura básica del dataset es válida para iniciar el módulo.")

except FileNotFoundError as error:
    st.sidebar.error("Dataset no disponible")
    st.error(str(error))
    st.info(
        "Coloca el archivo 'retail_sales_dataset.xlsx' dentro de la carpeta 'data/raw/' "
        "y vuelve a ejecutar la aplicación."
    )

except Exception as error:
    st.sidebar.error("Ocurrió un problema al validar el dataset")
    st.error(f"Error no esperado: {error}")

st.subheader("Hoja de ruta del módulo")
st.markdown(
    """
    - **Día 1:** estructura base y validación del dataset  
    - **Día 2:** carga de datos e integración inicial de hojas  
    - **Día 3 en adelante:** visualización, interactividad, IA y despliegue  
    """
)

st.subheader("Resultado esperado al cerrar la sesión")
st.markdown(
    """
    Al finalizar hoy, el proyecto debe:
    - abrir correctamente en Streamlit
    - ubicar el dataset oficial en la ruta esperada
    - reconocer sus hojas principales
    - quedar listo para comenzar la carga de datos en la siguiente sesión
    """
)