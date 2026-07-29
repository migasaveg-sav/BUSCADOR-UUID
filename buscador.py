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

if "tabla" not in st.session_state:
    st.session_state.tabla = pd.DataFrame(columns=[
        "Emisión", "Subtotal", "Retención", "ISR", "IVA Retenido",
        "Total Original XML", "Lugar Expedición", "Concepto"
    ])

# -------------------------------
# BOTÓN SUPERIOR + TOTALES
# -------------------------------
st.header("➕ Añadir nueva línea")

def add_line():
    st.session_state.lineas.append({"uuid": ""})

st.button("Añadir línea", on_click=add_line)

# Mostrar totales acumulados
if not st.session_state.tabla.empty:
    totales = st.session_state.tabla.sum(numeric_only=True)

    st.subheader("📊 Totales acumulados (sin comas)")
    st.write(f"**Subtotal acumulado:** {totales['Subtotal']:.2f}")
    st.write(f"**Retención acumulada:** {totales['Retención']:.2f}")
    st.write(f"**ISR acumulado:** {totales['ISR']:.2f}")
    st.write(f"**IVA Retenido acumulado:** {totales['IVA Retenido']:.2f}")
    st.write(f"**Total Original XML acumulado:** {totales['Total Original XML']:.2f}")

st.markdown("---")

# -------------------------------
# PROCESAR CADA LÍNEA
# -------------------------------
for idx, linea in enumerate(st.session_state.lineas):

    st.subheader(f"Línea #{idx + 1}")

    uuid_val = st.text_input(f"UUID línea {idx+1}", key=f"uuid_{idx}", value=linea["uuid"])
    linea["uuid"] = uuid_val

    if uuid_val:

        if "UUID" not in df.columns:
            st.error("El archivo no contiene la columna 'UUID'.")
            continue

        row = df[df["UUID"] == uuid_val]

        if row.empty:
            st.error("El UUID no existe en el archivo.")
            continue

        factura = row.iloc[0]

        # Extraer columnas
        emision = factura.get("Emisión", "")
        subtotal = float(factura.get("SubTotal", 0))
        isr = float(factura.get("ISR Retenido", 0))
        iva_ret = float(factura.get("IVA Retenido", 0))
        retencion = isr + iva_ret
        total_xml = float(factura.get("Total Original XML", 0))
        lugar_exp = factura.get("Emisor Lugar Expedición", "")
        concepto = factura.get("Conceptos Descripción", "")

        # Agregar a la tabla
        nueva_fila = {
            "Emisión": emision,
            "Subtotal": subtotal,
            "Retención": retencion,
            "ISR": isr,
            "IVA Retenido": iva_ret,
            "Total Original XML": total_xml,
            "Lugar Expedición": lugar_exp,
            "Concepto": concepto
        }

        st.session_state.tabla = pd.concat(
            [st.session_state.tabla, pd.DataFrame([nueva_fila])],
            ignore_index=True
        )

# -------------------------------
# TABLA FINAL
# -------------------------------
st.header("📄 Facturas agregadas (tabla)")

if st.session_state.tabla.empty:
    st.info("Aún no hay facturas agregadas.")
else:
    st.dataframe(st.session_state.tabla.style.format("{:.2f}"))
