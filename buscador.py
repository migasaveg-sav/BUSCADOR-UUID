import streamlit as st
import pandas as pd

st.set_page_config(page_title="Buscador UUID", layout="wide")
st.title("🔎 Buscador de Facturas por UUID")

# -------------------------------
# CARGA DE ARCHIVO (XLSX o CSV)
# -------------------------------
uploaded_file = st.file_uploader(
    "Selecciona tu archivo Excel o CSV",
    type=["xlsx", "csv"]
)

if uploaded_file is not None:

    filename = uploaded_file.name.lower()

    if filename.endswith(".csv"):
        df = pd.read_csv(uploaded_file, encoding="utf-8")
    else:
        df = pd.read_excel(uploaded_file)

    st.write("### Columnas detectadas en el archivo:")
    st.write(list(df.columns))

else:
    st.warning("Por favor selecciona un archivo para continuar.")
    st.stop()

# -------------------------------
# ESTADO GLOBAL
# -------------------------------
if "lineas" not in st.session_state:
    st.session_state.lineas = []

if "totales" not in st.session_state:
    st.session_state.totales = {"subtotal": 0, "iva": 0, "total": 0}

# -------------------------------
# BOTÓN SUPERIOR + TOTALES
# -------------------------------
st.header("➕ Añadir nueva línea")

def add_line():
    st.session_state.lineas.append({"uuid": "", "deducible": False})

st.button("Añadir línea", on_click=add_line)

# Mostrar totales acumulados
st.subheader("📊 Totales acumulados")
st.write(f"**Subtotal acumulado:** {st.session_state.totales['subtotal']:,.2f}")
st.write(f"**IVA acumulado:** {st.session_state.totales['iva']:,.2f}")
st.write(f"**Total acumulado:** {st.session_state.totales['total']:,.2f}")

st.markdown("---")

# -------------------------------
# LISTA DE FACTURAS (ABAJO)
# -------------------------------
st.header("📄 Facturas agregadas")

for idx, linea in enumerate(st.session_state.lineas):

    st.subheader(f"Factura #{idx + 1}")

    col1, col2 = st.columns([3, 1])

    with col1:
        uuid_val = st.text_input(f"UUID línea {idx+1}", key=f"uuid_{idx}", value=linea["uuid"])
        linea["uuid"] = uuid_val

    with col2:
        deducible_btn = st.checkbox("Deducibilidad 8.5%", key=f"ded_{idx}")
        linea["deducible"] = deducible_btn

    if uuid_val:

        if "UUID" not in df.columns:
            st.error("El archivo no contiene la columna 'UUID'.")
            continue

        row = df[df["UUID"] == uuid_val]

        if row.empty:
            st.error("El UUID no existe en el archivo.")
            continue

        factura = row.iloc[0]

        # -------------------------------
        # DESPLIEGUE DE CAMPOS
        # -------------------------------
        st.write("### Datos de la factura")

        def mostrar(columna, nombre):
            if columna in df.columns:
                st.write(f"**{nombre}:** {factura[columna]}")
            else:
                st.write(f"**{nombre}:** (columna no encontrada)")

        mostrar("Emisión", "Fecha")
        mostrar("SubTotal", "Subtotal")
        mostrar("IVA", "IVA")
        mostrar("Total", "Total")
        mostrar("Conceptos Descripción", "Concepto")

        # -------------------------------
        # ACTUALIZAR TOTALES
        # -------------------------------
        try:
            st.session_state.totales["subtotal"] += float(factura["SubTotal"])
            st.session_state.totales["iva"] += float(factura["IVA"])
            st.session_state.totales["total"] += float(factura["Total"])
        except:
            st.warning("No se pudieron sumar los totales por formato incorrecto.")

        # -------------------------------
        # DEDUCIBILIDAD
        # -------------------------------
        if deducible_btn:
            if "Total" in df.columns:
                deducible = factura["Total"] * 0.085
                st.success(f"Deducible (8.5%): {deducible:,.2f}")
            else:
                st.warning("No se encontró la columna 'Total' para calcular deducibilidad.")
