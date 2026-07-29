import streamlit as st
import pandas as pd

st.set_page_config(page_title="Buscador UUID", layout="wide")

st.title("🔎 Buscador de Facturas por UUID")

# --- Subir archivo ---
uploaded_file = st.file_uploader("Selecciona tu archivo Excel", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
else:
    st.warning("Por favor selecciona un archivo Excel para continuar.")
    st.stop()


st.title("🔎 Buscador de Facturas por UUID")

# --- Input del usuario ---
uuid_input = st.text_input("Ingresa el UUID:")

# --- Contenedor de líneas dinámicas ---
if "lineas" not in st.session_state:
    st.session_state.lineas = []

# --- Función para añadir línea ---
def add_line():
    st.session_state.lineas.append({"uuid": "", "deducible": False})

st.button("➕ Añadir línea", on_click=add_line)

# --- Mostrar cada línea ---
for idx, linea in enumerate(st.session_state.lineas):
    st.subheader(f"Línea {idx + 1}")

    col1, col2 = st.columns([3, 1])

    with col1:
        uuid_val = st.text_input(f"UUID línea {idx+1}", key=f"uuid_{idx}", value=linea["uuid"])
        linea["uuid"] = uuid_val

    with col2:
        deducible_btn = st.checkbox("Deducibilidad 8.5%", key=f"ded_{idx}")
        linea["deducible"] = deducible_btn

    # --- Buscar en el Excel ---
    if uuid_val:
        row = df[df["UUID"] == uuid_val]

        if row.empty:
            st.warning("UUID no encontrado en la base.")
        else:
            factura = row.iloc[0]

            fecha = factura["Fecha"]
            subtotal = factura["Subtotal"]
            iva = factura["IVA"]
            isr = factura["ISR"]
            ret = factura["Retenciones"]
            desc = factura["Descuentos"]
            total = factura["Total"]
            concepto = factura["Concepto"]

            # --- Cálculo deducible ---
            deducible = total * 0.085 if deducible_btn else 0

            st.write("### Datos de la factura")
            st.write(f"**Fecha:** {fecha}")
            st.write(f"**Subtotal:** {subtotal:,.2f}")
            st.write(f"**IVA:** {iva:,.2f}")
            st.write(f"**ISR:** {isr:,.2f}")
            st.write(f"**Retenciones:** {ret:,.2f}")
            st.write(f"**Descuentos:** {desc:,.2f}")
            st.write(f"**Total:** {total:,.2f}")
            st.write(f"**Concepto:** {concepto}")

            if deducible_btn:
                st.success(f"Deducible (8.5%): {deducible:,.2f}")
