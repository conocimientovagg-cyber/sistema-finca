import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Finca 2026 Cloud", layout="wide", page_icon="🌤️")

# Conexión con tu Google Sheet
conn = st.connection("gsheets", type=GSheetsConnection)

def verificar_acceso():
    if "rol" not in st.session_state:
        st.title("🚜 Acceso al Sistema Finca")
        clave = st.text_input("Clave de terminal:", type="password")
        if st.button("Entrar"):
            if clave == "admin2026": st.session_state["rol"] = "Admin"
            elif clave == "campo2026": st.session_state["rol"] = "Cosecha"
            elif clave == "venta2026": st.session_state["rol"] = "Ventas"
            else: st.error("Clave incorrecta")
            if "rol" in st.session_state: st.rerun()
        return False
    return True

if not verificar_acceso():
    st.stop()

rol = st.session_state["rol"]

# --- LECTURA DE DATOS DESDE GOOGLE SHEETS ---
try:
    df_f = conn.read(worksheet="Frutas")
    df_t = conn.read(worksheet="Te")
except Exception as e:
    st.error("⚠️ Error de conexión: Asegúrate de conectar el enlace de Google Sheets en Streamlit Cloud.")
    st.stop()

# --- LISTA DE FRUTAS ACTUALIZADA ---
lista_frutas = [
    "Aguacate Hanania", "Aguacate booth", "Coco", "Guanaba", 
    "Mandarina", "lichis", "Naranja", "Zapote", "Pitahaya", 
    "Platano", "Guineo", "OTRA FRUTA"
]

# --- 📊 MÓDULO DE ADMINISTRACIÓN ---
if rol == "Admin":
    st.title("📊 Módulo de Administración")
    t1, t2, t3 = st.tabs(["💰 Resumen de Ventas", "📦 Existencias Bodega", "📈 Gráficas Interactivas"])
    
    with t1:
        v_df = df_f[df_f["Tipo"] == "Salida"]
        st.metric("Ventas Totales ($)", f"${v_df['Total'].sum():,.2f}")
        st.write("Ventas por Cliente:")
        st.dataframe(v_df.groupby("Cliente")["Total"].sum().reset_index())

    with t2:
        st.subheader("Stock Actual")
        ent = df_f[df_f["Tipo"] == "Entrada"].groupby(["Fruta", "Medida"])["Cantidad"].sum()
        sal = df_f[df_f["Tipo"] == "Salida"].groupby(["Fruta", "Medida"])["Cantidad"].sum()
        stock = (ent.subtract(sal, fill_value=0)).reset_index()
        st.table(stock)

    with t3:
        st.subheader("Analítica")
        v_df = df_f[df_f["Tipo"] == "Salida"]
        ver = st.selectbox("Graficar por:", ["Fruta", "Cliente", "Sector"])
        if ver == "Fruta": st.bar_chart(v_df.groupby("Fruta")["Total"].sum())
        elif ver == "Cliente": st.bar_chart(v_df.groupby("Cliente")["Total"].sum())
        else: st.bar_chart(df_f[df_f["Tipo"]=="Entrada"].groupby("Sector")["Cantidad"].sum())

# --- 📥 MÓDULO DE COSECHA ---
elif rol == "Cosecha":
    st.title("📥 Registro de Cosecha")
    with st.form("fc"):
        f = st.date_input("Fecha", datetime.now())
        s = st.selectbox("Sector", [f"Sector {i}" for i in range(1, 15)])
        fruta = st.selectbox("Fruta", lista_frutas)
        med = st.radio("Medida", ["Libras", "Unidades"], horizontal=True)
        cant = st.number_input("Cantidad", min_value=0.0)
        if st.form_submit_button("✅ Guardar"):
            st.success("Dato listo para enviarse a la nube.")

# --- 📤 MÓDULO DE VENTAS ---
elif rol == "Ventas":
    st.title("📤 Registro de Venta")
    with st.form("fv"):
        cli = st.text_input("Nombre del Cliente")
        f_v = st.selectbox("Fruta", df_f["Fruta"].unique() if not df_f.empty else ["Sin Stock"])
        n_v = st.number_input("Cantidad", min_value=0.0)
        p_u = st.number_input("Precio Unitario ($)", min_value=0.0)
        st.subheader(f"Total: ${n_v * p_u:,.2f}")
        if st.form_submit_button("💰 Confirmar Venta"):
            st.success("Venta procesada.")
