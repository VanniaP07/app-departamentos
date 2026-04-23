import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Rentas Pro", layout="centered")

# CONEXIÓN AL EXCEL (GOOGLE SHEETS)
conn = st.connection("gsheets", type=GSheetsConnection)
URL_EXCEL = "https://docs.google.com/spreadsheets/d/1zPLXT_SW0j3ztNT85TkR898lWVXwOjJqqYHfxTgVc1Y/edit?usp=sharing" # <--- ¡PEGA TU LINK AQUÍ!

if 'pagina' not in st.session_state:
    st.session_state.pagina = "menu"

def ir_a(pagina):
    st.session_state.pagina = pagina

# --- 1. MENÚ PRINCIPAL ---
if st.session_state.pagina == "menu":
    st.title("🏨 MENÚ PRINCIPAL")
    if st.button("📝 REALIZAR NUEVA RESERVA", use_container_width=True):
        ir_a("registro")
        st.rerun()
    if st.button("📋 ADMINISTRACIÓN GENERAL", use_container_width=True):
        ir_a("admin_Todos")
        st.rerun()
    st.markdown("---")
    st.write("🔍 **VER POR TRABAJADOR:**")
    c1, c2, c3 = st.columns(3)
    if c1.button("👤 Jaky", use_container_width=True): ir_a("admin_Jaky"); st.rerun()
    if c2.button("👤 Miriam", use_container_width=True): ir_a("admin_Miriam"); st.rerun()
    if c3.button("👤 Pepillo", use_container_width=True): ir_a("admin_Pepillo"); st.rerun()

# --- 2. PANTALLA DE REGISTRO ---
elif st.session_state.pagina == "registro":
    if st.button("⬅ Volver al Menú"): ir_a("menu"); st.rerun()
    st.header("📝 Nueva Reservación")
    
    dueño = st.selectbox("Asignar a:", ["Jaky", "Miriam", "Pepillo"])
    cliente = st.text_input("Nombre del cliente")
    depa = st.text_input("Departamento / Casa")
    precio = st.number_input("Precio por noche ($)", min_value=0, step=1)
    col1, col2 = st.columns(2)
    llegada = col1.date_input("Llegada")
    salida = col2.date_input("Salida")
    transporte = st.checkbox("Transporte Internacional (+$100)")
    
    noches = (salida - llegada).days
    total = (max(0, noches) * precio) + (100 if transporte else 0)
    
    if noches > 0:
        st.success(f"🌙 Noches: {noches} | 💰 TOTAL: ${total}")

    if st.button("💾 GUARDAR AHORA", use_container_width=True, type="primary"):
        if cliente and depa and noches > 0:
            # LEER DATOS ACTUALES
            df_actual = conn.read(spreadsheet=URL_EXCEL)
            # CREAR NUEVA FILA
            nueva = pd.DataFrame([{
                "Dueño": dueño, "Cliente": cliente, "Propiedad": depa,
                "Inicio": llegada.strftime("%d/%m/%y"), 
                "Fin": salida.strftime("%d/%m/%y"), "Total": f"${total}"
            }])
            # UNIR Y GUARDAR
            df_final = pd.concat([df_actual, nueva], ignore_index=True)
            conn.update(spreadsheet=URL_EXCEL, data=df_final)
            st.toast("✅ ¡Guardado en la Nube!")
            ir_a("menu")
            st.rerun()
        else:
            st.error("⚠️ Revisa los datos")

# --- 3. PANTALLA DE ADMINISTRACIÓN ---
elif st.session_state.pagina.startswith("admin_"):
    filtro = st.session_state.pagina.replace("admin_", "")
    if st.button("⬅ Volver al Menú"): ir_a("menu"); st.rerun()
    st.header(f"📋 Reservas de {filtro}")
    
    # LEER DIRECTO DESDE EL EXCEL
    df = conn.read()
    if not df.empty:
        if filtro != "Todos":
            df = df[df["Dueño"] == filtro]
        st.table(df)
    else:
        st.write("No hay datos en el Excel.")
