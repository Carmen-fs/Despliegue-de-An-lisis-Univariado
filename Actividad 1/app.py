# Dashboard de Bitácora de Pisos y Base de Leads
# Adaptado del formato de Streamlit usado en el notebook del profesor.

import streamlit as st
import plotly.express as px
import pandas as pd

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Pisos y Leads",
    layout="wide"
)

# Función de carga de datos
@st.cache_data
def load_data():
    pisos = pd.read_csv("Bitacora_Piso_Limpia.csv")
    leads = pd.read_csv("Leads_Reales_Limpia.csv")

    pisos["Fecha"] = pd.to_datetime(pisos["Fecha"])
    pisos["Periodo"] = pisos["Fecha"].dt.strftime("%Y-%m")

    leads["Fecha"] = pd.to_datetime(leads["Periodo"] + "-01")

    return pisos, leads

# Cargamos los datos
pisos, leads = load_data()

# Barra lateral
st.sidebar.title("PISOS Y LEADS")

Base = st.sidebar.selectbox(
    label="Base de datos",
    options=["Bitácora de pisos", "Base de leads"]
)

# Selección de datos y variables según la base
if Base == "Bitácora de pisos":
    df = pisos.copy()

    Lista = [
        "Asesor",
        "Estatus_Lead",
        "Prueba_Manejo",
        "PDM",
        "SDC",
        "Venta",
        "Inter_Gerente",
        "Mes"
    ]

else:
    df = leads.copy()

    Lista = [
        "Nivel_Efectividad",
        "Año",
        "Mes",
        "Mes_Num"
    ]

Variable_Cat = st.sidebar.selectbox(
    label="Variables",
    options=Lista
)

# Filtro de periodos
Periodos = sorted(df["Periodo"].dropna().unique())

Periodos_Seleccionados = st.sidebar.multiselect(
    label="Periodo",
    options=Periodos,
    default=Periodos
)

df = df[df["Periodo"].isin(Periodos_Seleccionados)]

# Encabezado
st.title("Extracción de Características")
st.write(f"**Base seleccionada:** {Base}")

if df.empty:
    st.warning("Selecciona al menos un periodo para mostrar las gráficas.")
    st.stop()

# Indicadores principales
Indicador_A, Indicador_B, Indicador_C = st.columns(3)

if Base == "Bitácora de pisos":
    Indicador_A.metric("Registros", len(df))
    Indicador_B.metric("Ventas", int(df["Venta"].sum()))
    Indicador_C.metric(
        "Tasa de venta",
        f"{df['Venta'].mean():.1%}"
    )

    # Para el gráfico de área: registros por fecha
    Tabla_Tiempo = (
        df.groupby("Fecha")
        .size()
        .reset_index(name="frecuencia")
    )

    Titulo_Area = "Registros por día"
    Etiqueta_Y = "Registros"

else:
    Indicador_A.metric("Meses", len(df))
    Indicador_B.metric(
        "Ventas reportadas",
        f"{df['Ventas'].sum():,.0f}"
    )
    Indicador_C.metric(
        "Leads totales",
        f"{df['Total'].sum():,.2f}"
    )

    # Para el gráfico de área: ventas por mes
    Tabla_Tiempo = (
        df.groupby("Fecha", as_index=False)["Ventas"]
        .sum()
        .rename(columns={"Ventas": "frecuencia"})
    )

    Titulo_Area = "Ventas por mes"
    Etiqueta_Y = "Ventas"

# Tabla de frecuencias de la variable seleccionada
Tabla_frecuencias = (
    df[Variable_Cat]
    .fillna("Sin dato")
    .astype(str)
    .value_counts()
    .reset_index()
)

Tabla_frecuencias.columns = ["categorias", "frecuencia"]

# ============================================================
# FILA 1: GRÁFICO DE BARRAS Y GRÁFICO DE PASTEL
# ============================================================

Contenedor_A, Contenedor_B = st.columns(2)

with Contenedor_A:
    st.write("Gráfico de Barras")

    figure1 = px.bar(
        data_frame=Tabla_frecuencias,
        x="categorias",
        y="frecuencia",
        title=f"Frecuencia de {Variable_Cat}",
        color="frecuencia",
        color_continuous_scale="Reds"
    )

    figure1.update_xaxes(automargin=True)
    figure1.update_yaxes(automargin=True)
    figure1.update_layout(height=300)

    st.plotly_chart(figure1, use_container_width=True)

with Contenedor_B:
    st.write("Gráfico de Pastel")

    figure2 = px.pie(
        data_frame=Tabla_frecuencias,
        names="categorias",
        values="frecuencia",
        title=f"Distribución de {Variable_Cat}",
        color_discrete_sequence=px.colors.qualitative.Vivid
    )

    figure2.update_layout(height=300)

    st.plotly_chart(figure2, use_container_width=True)

# ============================================================
# FILA 2: GRÁFICO DE DONA Y GRÁFICO DE ÁREA
# ============================================================

Contenedor_C, Contenedor_D = st.columns(2)

with Contenedor_C:
    st.write("Gráfico de Anillo o Dona")

    figure3 = px.pie(
        data_frame=Tabla_frecuencias,
        names="categorias",
        values="frecuencia",
        hole=0.4,
        title=f"Participación de {Variable_Cat}",
        color_discrete_sequence=px.colors.qualitative.Bold
    )

    figure3.update_layout(height=300)

    st.plotly_chart(figure3, use_container_width=True)

with Contenedor_D:
    st.write("Gráfico de Área")

    figure4 = px.area(
        data_frame=Tabla_Tiempo,
        x="Fecha",
        y="frecuencia",
        title=Titulo_Area,
        color_discrete_sequence=["#C0392B"]
    )

    figure4.update_layout(
        height=300,
        xaxis_title="Fecha",
        yaxis_title=Etiqueta_Y
    )

    st.plotly_chart(figure4, use_container_width=True)

# Tablas opcionales para revisar los resultados
with st.expander("Ver tabla de frecuencias y datos filtrados"):
    st.write("Tabla de frecuencias")
    st.dataframe(Tabla_frecuencias, hide_index=True)

    st.write("Datos filtrados")
    st.dataframe(df, hide_index=True)
