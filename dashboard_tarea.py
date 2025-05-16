import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- Configuración de la Página ---
st.set_page_config(layout="wide", page_title="Dashboard")

# --- Cargar y Preprocesar Datos ---
@st.cache_data # Cache para mejorar rendimiento
def load_data():
    df = pd.read_csv('data.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    df['Time'] = pd.to_datetime(df['Time'], format='%H:%M').dt.time
    df['Month'] = df['Date'].dt.month_name()
    df['Year'] = df['Date'].dt.year
    return df

df = load_data()

# --- Barra Lateral de Filtros ---
st.sidebar.header("Filtros del Dashboard")

# Filtro de Rango de Fechas
min_date = df['Date'].min()
max_date = df['Date'].max()
date_range = st.sidebar.date_input("Selecciona Rango de Fechas:",
                                   value=(min_date, max_date),
                                   min_value=min_date,
                                   max_value=max_date)

# Filtrar DataFrame por rango de fechas
if len(date_range) == 2:
    start_date, end_date = date_range
    df_filtered = df[(df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))]
else:
    df_filtered = df.copy() # Usar todos los datos si el rango no está completo


# Filtro de Sucursal
selected_branch = st.sidebar.multiselect("Selecciona Sucursal(es):",
                                         options=df['Branch'].unique(),
                                         default=df['Branch'].unique())
if selected_branch:
    df_filtered = df_filtered[df_filtered['Branch'].isin(selected_branch)]

# Filtro de Tipo de Cliente
selected_customer_type = st.sidebar.multiselect("Selecciona Tipo de Cliente:",
                                               options=df['Customer type'].unique(),
                                               default=df['Customer type'].unique())
if selected_customer_type:
    df_filtered = df_filtered[df_filtered['Customer type'].isin(selected_customer_type)]

# Filtro de Ciudad
selected_city = st.sidebar.multiselect("Selecciona Ciudad(es):",
                                       options=df['City'].unique(),
                                       default=df['City'].unique())
if selected_city:
    df_filtered = df_filtered[df_filtered['City'].isin(selected_city)]


# --- Layout Principal del Dashboard ---
st.title("Análisis de Ventas y Comportamiento de Clientes")
st.markdown("Este dashboard interactivo presenta un análisis de los datos de ventas de la cadena de tiendas de conveniencia.")

if df_filtered.empty:
    st.warning("No hay datos disponibles para los filtros seleccionados.")
else:
    # --- KPIs Principales ---
    st.subheader("Indicadores Clave de Rendimiento (KPIs)")
    col1, col2, col3, col4 = st.columns(4)
    total_revenue = df_filtered['Total'].sum()
    avg_transaction_value = df_filtered['Total'].mean()
    total_transactions = df_filtered['Invoice ID'].nunique()
    avg_rating = df_filtered['Rating'].mean()

    col1.metric("Ingresos Totales", f"${total_revenue:,.2f}")
    col2.metric("Valor Prom. Transacción", f"${avg_transaction_value:,.2f}")
    col3.metric("Total Transacciones", f"{total_transactions:,}")
    col4.metric("Calificación Promedio", f"{avg_rating:.1f} / 10")

    st.markdown("---")

    # --- Visualizaciones ---
    col_viz1, col_viz2 = st.columns(2)

    with col_viz1:
        st.subheader("1. Evolución de las Ventas Totales")
        ventas_diarias = df_filtered.groupby('Date')['Total'].sum()
        if not ventas_diarias.empty:
            fig1, ax1 = plt.subplots(figsize=(10, 4))
            sns.lineplot(x=ventas_diarias.index, y=ventas_diarias.values, ax=ax1)
            ax1.set_title('Ventas Totales a lo largo del Tiempo')
            ax1.set_xlabel('Fecha')
            ax1.set_ylabel('Ventas Totales')
            plt.xticks(rotation=45)
            ax1.grid(True)
            st.pyplot(fig1)
        else:
            st.info("No hay datos de ventas para el periodo seleccionado.")

        st.subheader("3. Distribución de Calificación de Clientes")
        fig3, ax3 = plt.subplots(figsize=(10, 4))
        sns.histplot(df_filtered['Rating'], bins=10, kde=True, color='skyblue', ax=ax3)
        ax3.set_title('Distribución de Calificaciones')
        ax3.set_xlabel('Calificación (Rating)')
        ax3.set_ylabel('Frecuencia')
        st.pyplot(fig3)

    with col_viz2:
        st.subheader("2. Ingresos por Línea de Producto")
        ingresos_linea_producto = df_filtered.groupby('Product line')['Total'].sum().sort_values(ascending=False)
        if not ingresos_linea_producto.empty:
            fig2, ax2 = plt.subplots(figsize=(10, 4))
            sns.barplot(x=ingresos_linea_producto.index, y=ingresos_linea_producto.values, palette='viridis', ax=ax2)
            ax2.set_title('Ingresos Totales por Línea de Producto')
            ax2.set_xlabel('')
            ax2.set_ylabel('Ingresos Totales')
            plt.xticks(rotation=45, ha='right')
            st.pyplot(fig2)
        else:
            st.info("No hay datos de ingresos por línea de producto para los filtros seleccionados.")

        st.subheader("4. Gasto por Tipo de Cliente")
        fig4, ax4 = plt.subplots(figsize=(10, 4))
        sns.boxplot(x='Customer type', y='Total', data=df_filtered, palette='pastel', ax=ax4)
        ax4.set_title('Comparación del Gasto Total')
        ax4.set_xlabel('Tipo de Cliente')
        ax4.set_ylabel('Gasto Total (Total)')
        st.pyplot(fig4)

    st.markdown("---")
    col_viz3, col_viz4 = st.columns(2)

    with col_viz3:
        st.subheader("6. Métodos de Pago Preferidos")
        payment_counts = df_filtered['Payment'].value_counts()
        if not payment_counts.empty:
            fig6, ax6 = plt.subplots(figsize=(10,4))
            sns.barplot(x=payment_counts.index, y=payment_counts.values, palette='coolwarm', ax=ax6)
            ax6.set_title('Frecuencia de Métodos de Pago')
            ax6.set_xlabel('Método de Pago')
            ax6.set_ylabel('Número de Transacciones')
            st.pyplot(fig6)
        else:
            st.info("No hay datos de métodos de pago para los filtros seleccionados.")

    with col_viz4:
        st.subheader("Análisis Adicional: Gasto Promedio por Hora del Día")
        df_filtered['Hour'] = pd.to_datetime(df_filtered['Time'].astype(str)).dt.hour
        gasto_por_hora = df_filtered.groupby('Hour')['Total'].mean()
        if not gasto_por_hora.empty:
            fig_hora, ax_hora = plt.subplots(figsize=(10,4))
            sns.lineplot(x=gasto_por_hora.index, y=gasto_por_hora.values, marker='o', ax=ax_hora)
            ax_hora.set_title('Gasto Promedio por Hora del Día')
            ax_hora.set_xlabel('Hora del Día')
            ax_hora.set_ylabel('Gasto Promedio (Total)')
            ax_hora.set_xticks(range(0,24))
            ax_hora.grid(True)
            st.pyplot(fig_hora)
        else:
            st.info("No hay datos para mostrar el gasto por hora.")


    st.markdown("---")
    st.subheader("Visualización de Datos Multivariados")
    st.markdown("Mapa de calor de correlación entre variables numéricas seleccionadas:")
    variables_numericas_corr = ['Unit price', 'Quantity', 'Tax 5%', 'Total', 'cogs', 'gross income', 'Rating']
    # Solo calcular si hay suficientes datos y columnas
    if not df_filtered[variables_numericas_corr].dropna().empty and len(df_filtered[variables_numericas_corr].dropna()) > 1:
        matriz_correlacion_filtrada = df_filtered[variables_numericas_corr].corr()
        fig_corr, ax_corr = plt.subplots(figsize=(8, 6))
        sns.heatmap(matriz_correlacion_filtrada, annot=True, cmap='coolwarm', fmt=".2f", linewidths=.5, ax=ax_corr)
        ax_corr.set_title('Mapa de Calor de Correlación (Datos Filtrados)')
        st.pyplot(fig_corr)
    else:
        st.info("No hay suficientes datos para generar el mapa de calor de correlación con los filtros actuales.")


    # --- Mostrar Datos Crudos (Opcional y Expansible) ---
    if st.checkbox("Mostrar Datos Crudos Filtrados (Primeras 100 filas)"):
        st.dataframe(df_filtered.head(100))

# --- Pie de Página ---
st.markdown("---")
st.markdown("Dashboard desarrollado por: Grupo de trabajo 62")
st.markdown(f"Fecha de última actualización de datos: {df['Date'].max().strftime('%Y-%m-%d')}")