import streamlit as st
import pandas as pd

st.set_page_config(page_title="Buscador UUID", layout="wide")
st.title("🔎 Buscador de Facturas por UUID")

# -------------------------------
# CARGA DE ARCHIVO
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

    st.write("### Columnas detectadas:")
    st.write(list(df.columns))
else:
    st.warning("Por favor selecciona un archivo para continuar.")
    st.stop()

# -------------------------------
# ESTADO GLOBAL
# -------------------------------
if "tabla" not in st.session_state:
    st.session_state.tabla = pd.DataFrame(columns=[
        "Emisión", "Subtotal", "Retención", "ISR", "IVA Retenido",
        "Total Original XML", "Lugar Expedición", "Concepto"
    ])

# -------------------------------
# FUNCIÓN PARA LIMPIAR NÚMEROS
# -------------------------------
def limpiar_numero(valor):
    try:
        if isinstance(valor, str):
            valor = valor.replace(",", "").strip()
        return float(valor)
    except:
        return 0.0

# -------------------------------
# SECCIÓN SUPERIOR: AÑADIR LÍNEA
# -------------------------------
st.header("➕ Añadir nueva factura por UUID")

uuid_input = st.text_input("Ingresa el UUID:")

if st.button("Guardar factura"):

    if uuid_input == "":
        st.error("Debes ingresar un UUID.")
    else:
        if "UUID" not in df.columns:
            st.error("El archivo no contiene la columna 'UUID'.")
        else:
            row = df[df["UUID"] == uuid_input]

            if row.empty:
                st.error("El UUID no existe en el archivo.")
            else:
                factura = row.iloc[0]

                # Extraer y limpiar valores
                emision = factura.get("Emisión", "")
                subtotal = limpiar_numero(factura.get("SubTotal", 0))
                isr = limpiar_numero(factura.get("ISR Retenido", 0))
                iva_ret = limpiar_numero(factura.get("IVA Retenido", 0))
                retencion = isr + iva_ret
                total_xml = limpiar_numero(factura.get("Total Original XML", 0))
                lugar_exp = factura.get("Emisor Lugar Expedición", "")
                concepto = factura.get("Conceptos Descripción", "")

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

                st.success("Factura agregada correctamente.")

# -------------------------------
# TOTALES SUPERIORES
# -------------------------------
st.header("📊 Totales acumulados")

if not st.session_state.tabla.empty:
    totales = st.session_state.tabla.sum(numeric_only=True)

    st.write(f"**Subtotal acumulado:** {totales['Subtotal']:.2f}")
    st.write(f"**Retención acumulada:** {totales['Retención']:.2f}")
    st.write(f"**ISR acumulado:** {totales['ISR']:.2f}")
    st.write(f"**IVA Retenido acumulado:** {totales['IVA Retenido']:.2f}")
    st.write(f"**Total Original XML acumulado:** {totales['Total Original XML']:.2f}")
else:
    st.info("Aún no hay facturas agregadas.")

st.markdown("---")

# -------------------------------
# TABLA FINAL
# -------------------------------
st.header("📄 Facturas agregadas")

if st.session_state.tabla.empty:
    st.info("Aún no hay facturas agregadas.")
else:
    st.dataframe(st.session_state.tabla.style.format("{:.2f}"))
