from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

EXPECTED_SHEETS = ("Customers", "Products", "Stores", "Transactions")

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "raw" / "retail_sales_dataset.xlsx"


def load_source_tables(file_path: Path) -> dict[str, pd.DataFrame]:
    if not file_path.exists():
        raise FileNotFoundError(
            "No se encontró el archivo 'retail_sales_dataset.xlsx' en 'data/raw/'."
        )

    xls = pd.ExcelFile(file_path)
    missing_sheets = [sheet for sheet in EXPECTED_SHEETS if sheet not in xls.sheet_names]

    if missing_sheets:
        raise ValueError(
            "Faltan hojas necesarias para el proyecto: " + ", ".join(missing_sheets)
        )

    return {
        "Customers": pd.read_excel(file_path, sheet_name="Customers"),
        "Products": pd.read_excel(file_path, sheet_name="Products"),
        "Stores": pd.read_excel(file_path, sheet_name="Stores"),
        "Transactions": pd.read_excel(file_path, sheet_name="Transactions")
    }


def build_analytical_dataset(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    customers = tables["Customers"].copy()
    products = tables["Products"].copy()
    stores = tables["Stores"].copy()
    transactions = tables["Transactions"].copy()

    customers["BirthDate"] = pd.to_datetime(customers["BirthDate"], errors="coerce")
    customers["JoinDate"] = pd.to_datetime(customers["JoinDate"], errors="coerce")
    transactions["Date"] = pd.to_datetime(transactions["Date"], errors="coerce")

    analytical_df = transactions.merge(customers, on="CustomerID", how="left")
    analytical_df = analytical_df.merge(products, on="ProductID", how="left")
    analytical_df = analytical_df.merge(
        stores,
        on="StoreID",
        how="left",
        suffixes=("_Customer", "_Store")
    )

    analytical_df = analytical_df.rename(
        columns={
            "Date": "TransactionDate",
            "City_Customer": "CustomerCity",
            "City_Store": "StoreCity",
            "Region": "StoreRegion"
        }
    )

    analytical_df["gross_sales"] = analytical_df["Quantity"] * analytical_df["UnitPrice"]
    analytical_df["discount_amount"] = analytical_df["gross_sales"] * analytical_df["Discount"]
    analytical_df["net_sales"] = analytical_df["gross_sales"] - analytical_df["discount_amount"]
    analytical_df["total_cost"] = analytical_df["Quantity"] * analytical_df["CostPrice"]
    analytical_df["profit"] = analytical_df["net_sales"] - analytical_df["total_cost"]

    analytical_df["year"] = analytical_df["TransactionDate"].dt.year
    analytical_df["month"] = analytical_df["TransactionDate"].dt.month
    analytical_df["year_month"] = analytical_df["TransactionDate"].dt.to_period("M").astype(str)

    return analytical_df


st.set_page_config(
    page_title="Dashboard Retail + IA",
    page_icon="📊",
    layout="wide"
)

st.title("Dashboard Retail + IA")
st.caption("Día 2 · Carga de datos y primeras visualizaciones")

try:
    source_tables = load_source_tables(DATA_FILE)
    df = build_analytical_dataset(source_tables)

    st.success("Datos cargados correctamente.")

    total_transactions = df["TransactionID"].nunique()
    total_net_sales = df["net_sales"].sum()
    total_profit = df["profit"].sum()
    average_ticket = df["net_sales"].mean()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Transacciones", f"{total_transactions:,}")
    col2.metric("Ventas netas", f"${total_net_sales:,.2f}")
    col3.metric("Utilidad", f"${total_profit:,.2f}")
    col4.metric("Ticket promedio", f"${average_ticket:,.2f}")

    st.subheader("Vista previa de la tabla analítica")
    st.dataframe(df.head(10), use_container_width=True)

    monthly_sales = (
        df.groupby("year_month", as_index=False)["net_sales"]
        .sum()
        .sort_values("year_month")
    )

    sales_by_category = (
        df.groupby("Category", as_index=False)["net_sales"]
        .sum()
        .sort_values("net_sales", ascending=False)
    )

    profit_by_region = (
        df.groupby("StoreRegion", as_index=False)["profit"]
        .sum()
        .sort_values("profit", ascending=False)
    )

    top_products = (
        df.groupby("ProductName", as_index=False)["net_sales"]
        .sum()
        .sort_values("net_sales", ascending=False)
        .head(10)
    )

    fig_monthly_sales = px.line(
        monthly_sales,
        x="year_month",
        y="net_sales",
        markers=True,
        title="Ventas netas por mes"
    )

    fig_category_sales = px.bar(
        sales_by_category,
        x="Category",
        y="net_sales",
        title="Ventas netas por categoría"
    )

    fig_region_profit = px.bar(
        profit_by_region,
        x="StoreRegion",
        y="profit",
        title="Utilidad por región"
    )

    fig_top_products = px.bar(
        top_products.sort_values("net_sales"),
        x="net_sales",
        y="ProductName",
        orientation="h",
        title="Top 10 productos por ventas netas"
    )

    st.subheader("Primeras visualizaciones")
    chart_col1, chart_col2 = st.columns(2)
    chart_col1.plotly_chart(fig_monthly_sales, use_container_width=True)
    chart_col2.plotly_chart(fig_category_sales, use_container_width=True)

    chart_col3, chart_col4 = st.columns(2)
    chart_col3.plotly_chart(fig_region_profit, use_container_width=True)
    chart_col4.plotly_chart(fig_top_products, use_container_width=True)

except FileNotFoundError as error:
    st.error(str(error))
    st.info(
        "Coloca el archivo 'retail_sales_dataset.xlsx' dentro de la carpeta 'data/raw/' "
        "y vuelve a ejecutar la aplicación."
    )

except ValueError as error:
    st.error(str(error))

except Exception as error:
    st.error(f"Ocurrió un error inesperado: {error}")