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


def inject_custom_style() -> None:
    st.markdown(
        """
        <style>
        .main-title {
            font-size: 2.1rem;
            font-weight: 700;
            margin-bottom: 0.3rem;
        }

        .subtitle {
            color: #6b7280;
            margin-bottom: 1.5rem;
        }

        .section-title {
            font-size: 1.35rem;
            font-weight: 600;
            margin-top: 0.5rem;
            margin-bottom: 0.75rem;
        }

        .info-box {
            background-color: #f7f9fc;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 1rem 1.1rem;
            margin-bottom: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def render_header() -> None:
    st.markdown('<div class="main-title">Dashboard Retail + IA</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Día 3 · Diseño visual y navegación básica del dashboard</div>',
        unsafe_allow_html=True
    )


def render_executive_view(df: pd.DataFrame) -> None:
    st.markdown('<div class="section-title">Resumen ejecutivo</div>', unsafe_allow_html=True)

    total_transactions = df["TransactionID"].nunique()
    total_net_sales = df["net_sales"].sum()
    total_profit = df["profit"].sum()
    average_ticket = df["net_sales"].mean()

    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    kpi_col1.metric("Transacciones", f"{total_transactions:,}")
    kpi_col2.metric("Ventas netas", f"${total_net_sales:,.2f}")
    kpi_col3.metric("Utilidad", f"${total_profit:,.2f}")
    kpi_col4.metric("Ticket promedio", f"${average_ticket:,.2f}")

    monthly_sales = (
        df.groupby("year_month", as_index=False)["net_sales"]
        .sum()
        .sort_values("year_month")
    )

    payment_method_sales = (
        df.groupby("PaymentMethod", as_index=False)["net_sales"]
        .sum()
        .sort_values("net_sales", ascending=False)
    )

    fig_monthly_sales = px.line(
        monthly_sales,
        x="year_month",
        y="net_sales",
        markers=True,
        title="Tendencia mensual de ventas netas"
    )

    fig_payment_method = px.bar(
        payment_method_sales,
        x="PaymentMethod",
        y="net_sales",
        title="Ventas netas por método de pago"
    )

    chart_col1, chart_col2 = st.columns(2)
    chart_col1.plotly_chart(fig_monthly_sales, use_container_width=True)
    chart_col2.plotly_chart(fig_payment_method, use_container_width=True)

    st.markdown(
        """
        <div class="info-box">
        Esta vista concentra el panorama general del negocio y permite identificar rápidamente
        el comportamiento agregado de ventas, utilidad y ticket promedio.
        </div>
        """,
        unsafe_allow_html=True
    )


def render_trends_view(df: pd.DataFrame) -> None:
    st.markdown('<div class="section-title">Tendencias comerciales</div>', unsafe_allow_html=True)

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

    monthly_profit = (
        df.groupby("year_month", as_index=False)["profit"]
        .sum()
        .sort_values("year_month")
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

    fig_monthly_profit = px.line(
        monthly_profit,
        x="year_month",
        y="profit",
        markers=True,
        title="Utilidad mensual"
    )

    chart_col1, chart_col2 = st.columns(2)
    chart_col1.plotly_chart(fig_category_sales, use_container_width=True)
    chart_col2.plotly_chart(fig_region_profit, use_container_width=True)

    st.plotly_chart(fig_monthly_profit, use_container_width=True)


def render_products_view(df: pd.DataFrame) -> None:
    st.markdown('<div class="section-title">Análisis de productos</div>', unsafe_allow_html=True)

    top_products = (
        df.groupby("ProductName", as_index=False)["net_sales"]
        .sum()
        .sort_values("net_sales", ascending=False)
        .head(10)
    )

    subcategory_sales = (
        df.groupby("SubCategory", as_index=False)["net_sales"]
        .sum()
        .sort_values("net_sales", ascending=False)
        .head(10)
    )

    quantity_by_category = (
        df.groupby("Category", as_index=False)["Quantity"]
        .sum()
        .sort_values("Quantity", ascending=False)
    )

    fig_top_products = px.bar(
        top_products.sort_values("net_sales"),
        x="net_sales",
        y="ProductName",
        orientation="h",
        title="Top 10 productos por ventas netas"
    )

    fig_subcategory_sales = px.bar(
        subcategory_sales.sort_values("net_sales"),
        x="net_sales",
        y="SubCategory",
        orientation="h",
        title="Top 10 subcategorías por ventas netas"
    )

    fig_quantity_by_category = px.bar(
        quantity_by_category,
        x="Category",
        y="Quantity",
        title="Cantidad vendida por categoría"
    )

    chart_col1, chart_col2 = st.columns(2)
    chart_col1.plotly_chart(fig_top_products, use_container_width=True)
    chart_col2.plotly_chart(fig_subcategory_sales, use_container_width=True)

    st.plotly_chart(fig_quantity_by_category, use_container_width=True)


def render_table_view(df: pd.DataFrame) -> None:
    st.markdown('<div class="section-title">Exploración tabular</div>', unsafe_allow_html=True)

    summary_col1, summary_col2, summary_col3 = st.columns(3)
    summary_col1.metric("Filas", f"{df.shape[0]:,}")
    summary_col2.metric("Columnas", f"{df.shape[1]:,}")
    summary_col3.metric("Productos únicos", f"{df['ProductID'].nunique():,}")

    st.dataframe(df.head(50), use_container_width=True)

    st.markdown(
        """
        <div class="info-box">
        Esta vista permite inspeccionar la estructura integrada del dataset y verificar
        cómo conviven en una misma tabla los atributos de cliente, producto, tienda y transacción.
        </div>
        """,
        unsafe_allow_html=True
    )


st.set_page_config(
    page_title="Dashboard Retail + IA",
    page_icon="📊",
    layout="wide"
)

inject_custom_style()
render_header()

try:
    source_tables = load_source_tables(DATA_FILE)
    df = build_analytical_dataset(source_tables)

    st.sidebar.header("Navegación")
    selected_view = st.sidebar.radio(
        "Selecciona una sección",
        (
            "Resumen ejecutivo",
            "Tendencias comerciales",
            "Análisis de productos",
            "Exploración tabular"
        )
    )

    st.sidebar.markdown("---")
    st.sidebar.write("Estado del proyecto")
    st.sidebar.success("Datos cargados correctamente")
    st.sidebar.write(f"Registros integrados: {df.shape[0]:,}")
    st.sidebar.write(f"Columnas analíticas: {df.shape[1]:,}")

    if selected_view == "Resumen ejecutivo":
        render_executive_view(df)
    elif selected_view == "Tendencias comerciales":
        render_trends_view(df)
    elif selected_view == "Análisis de productos":
        render_products_view(df)
    else:
        render_table_view(df)

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