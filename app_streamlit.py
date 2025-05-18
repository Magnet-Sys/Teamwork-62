import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Cargar datos
@st.cache_data
def load_data():
    df = pd.read_csv("data.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    df["Hour"] = pd.to_datetime(df["Time"], format="%H:%M").dt.hour
    return df

plt.style.use("ggplot")      
plt.style.use("fivethirtyeight")  
plt.style.use("bmh")      

df = load_data()

# Título
st.title("Análisis de Ventas - Supermercado")

# Sidebar con filtros
with st.sidebar:
    st.header("Filtros")

    # Filtros binarios SIEMPRE visibles
    genders = st.radio("Género", options=["Todos"] + df["Gender"].unique().tolist(), horizontal=True)
    customers = st.radio("Tipo de Cliente", options=["Todos"] + df["Customer type"].unique().tolist(), horizontal=True)
    date_range = st.date_input("Rango de Fechas", [df["Date"].min(), df["Date"].max()])

    # Ciudad

    all_cities = sorted(df["City"].unique().tolist())
    city_options = ["Seleccionar todos"] + all_cities
    selected_cities = st.multiselect("Ciudad", city_options, default=[])

    if "Seleccionar todos" in selected_cities and len(selected_cities) > 1:
        selected_cities = [c for c in selected_cities if c != "Seleccionar todos"]

    if "Seleccionar todos" in selected_cities:
        cities = all_cities
    elif selected_cities:
        cities = selected_cities
    else:
        cities = []  # No selection

    # Línea de producto

    all_products = sorted(df["Product line"].unique().tolist())
    product_options = ["Seleccionar todos"] + all_products
    selected_products = st.multiselect("Línea de Producto", product_options, default=[])

    if "Seleccionar todos" in selected_products and len(selected_products) > 1:
        selected_products = [p for p in selected_products if p != "Seleccionar todos"]

    if "Seleccionar todos" in selected_products:
        products = all_products
    elif selected_products:
        products = selected_products
    else:
        products = []  # No selection



# Construir condiciones de filtro
filtered_df = df.copy()

if cities:
    filtered_df = filtered_df[filtered_df["City"].isin(cities)]

if products:
    filtered_df = filtered_df[filtered_df["Product line"].isin(products)]

if genders != "Todos":
    filtered_df = filtered_df[filtered_df["Gender"] == genders]

if customers != "Todos":
    filtered_df = filtered_df[filtered_df["Customer type"] == customers]

filtered_df = filtered_df[
    (filtered_df["Date"] >= pd.to_datetime(date_range[0])) &
    (filtered_df["Date"] <= pd.to_datetime(date_range[1]))
]

# Crear resumen de filtros
filtros = []

# Género
if genders != "Todos":
    filtros.append(f"{genders.lower()}s")
else:
    filtros.append("personas de todos los géneros")

# Tipo de cliente
if customers != "Todos":
    filtros.append(f"clientes {customers.lower()}")
else:
    filtros.append("clientes de todos los tipos")

# Ciudades
if cities and len(cities) == 1:
    filtros.append(f"de la ciudad de {cities[0]}")
elif cities and len(cities) > 1:
    filtros.append(f"de las ciudades: {', '.join(cities)}")
else:
    filtros.append("de todas las ciudades")

# Producto
if products and len(products) == 1:
    filtros.append(f"en la categoría {products[0]}")
elif products and len(products) > 1:
    filtros.append(f"en las categorías: {', '.join(products)}")
else:
    filtros.append("de todas las categorías de productos")

# Rango de fechas
fecha_inicio = date_range[0].strftime("%d/%m/%Y")
fecha_fin = date_range[1].strftime("%d/%m/%Y")
filtros.append(f"entre el {fecha_inicio} y el {fecha_fin}")

# Mostrar resumen
st.markdown(f"**Datos filtrados para:** {', '.join(filtros)}.")


# Mostrar resultados si hay datos
if not filtered_df.empty:

    st.metric("Total de Ventas ($)", f'{filtered_df["Total"].sum():,.2f}')
    st.metric("Unidades Vendidas", int(filtered_df["Quantity"].sum()))
    st.metric("Promedio por Transacción", f'{filtered_df["Total"].mean():,.2f}')

    st.subheader("Ventas por Línea de Producto")
    product_sales = filtered_df.groupby("Product line")["Total"].sum().sort_values()

    fig1, ax1 = plt.subplots(figsize=(10, 12))
    bars = ax1.barh(product_sales.index, product_sales.values, color="#1f77b4", edgecolor="black")

    for bar in bars:
        width = bar.get_width()
        label_x_pos = width * 0.5 
        ax1.text(label_x_pos, bar.get_y() + bar.get_height()/2,
                f"${width:,.0f}", va='center', ha='right', color="white", fontsize=20)

    ax1.set_xlabel("Ventas ($)", fontsize=12)
    ax1.set_ylabel("Línea de Producto", fontsize=12)
    ax1.spines["right"].set_visible(False)
    ax1.spines["top"].set_visible(False)
    st.pyplot(fig1)


    st.subheader("Ventas por Fecha")
    daily_sales = filtered_df.groupby("Date")["Total"].sum()

    fig2, ax2 = plt.subplots(figsize=(10, 4))  # más ancho ayuda
    ax2.plot(daily_sales.index, daily_sales.values, marker='o', color="#ff7f0e", linewidth=2)

    # Mejoras estéticas
    ax2.set_ylabel("Ventas ($)", fontsize=12)
    ax2.set_xlabel("Fecha", fontsize=12)
    ax2.grid(True, linestyle="--", alpha=0.5)
    ax2.spines["right"].set_visible(False)
    ax2.spines["top"].set_visible(False)

    # Rotar y formatear fechas
    ax2.tick_params(axis='x', rotation=45)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))

    st.pyplot(fig2)





    st.subheader("Ventas por Horas del Día")
    sales_by_hour = filtered_df.groupby("Hour")["Total"].sum()
    fig3, ax = plt.subplots()
    sales_by_hour.plot(kind="bar", ax=ax)
    ax.set_xlabel("Hora")
    ax.set_ylabel("Ventas ($)")
    st.pyplot(fig3)
    

    st.subheader("Distribución de Métodos de Pago")
    payment_counts = filtered_df["Payment"].value_counts()
    fig4, ax = plt.subplots()
    payment_counts.plot(kind="pie", autopct='%1.1f%%', ax=ax)
    ax.set_ylabel("")  
    st.pyplot(fig4)

    st.subheader("Distribución de Calificaciones por Tipo de Cliente")

    fig5, ax = plt.subplots(figsize=(8, 4))

    # Histogramas para cada tipo de cliente
    colors = {"Member": "#1f77b4", "Normal": "#ff7f0e"}
    for customer_type in filtered_df["Customer type"].unique():
        subset = filtered_df[filtered_df["Customer type"] == customer_type]
        ax.hist(subset["Rating"], bins=20, alpha=0.3, label=customer_type ,color=colors[customer_type])

    ax.set_xlabel("Rating (1 a 10)")
    ax.set_ylabel("Frecuencia")
    ax.legend(title="Tipo de Cliente",loc="lower right")
    st.pyplot(fig5)

    # st.subheader("Distribución de Calificaciones por Tipo de Cliente")
    # fig5, ax = plt.subplots()
    # filtered_df.boxplot(column="Rating", by="Customer type", ax=ax, grid=False)
    # ax.set_title("Distribución de Calificaciones")
    # ax.set_xlabel("Tipo de Cliente")
    # ax.set_ylabel("Rating (1 a 10)")
    # plt.suptitle("") 
    # st.pyplot(fig5)

    # st.subheader("Datos Filtrados")
    # st.dataframe(filtered_df)
else:
    st.warning("⚠️ No hay datos para mostrar con los filtros seleccionados.")




