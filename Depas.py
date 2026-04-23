import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Rentas Pro", layout="centered")

# "Cerebro" para recordar datos y en qué pantalla estamos
if 'reservas' not in st.session_state:
    st.session_state.reservas = []
if 'pagina' not in st.session_state:
    st.session_state.pagina = "menu"

# --- FUNCIONES DE NAVEGACIÓN ---
def ir_a(pagina):
    st.session_state.pagina = pagina

# --- 1. MENÚ PRINCIPAL ---
if st.session_state.pagina == "menu":
    st.title("🏨 MENÚ PRINCIPAL")
    
    # Botones grandes de acceso directo
    if st.button("📝 REALIZAR NUEVA RESERVA", use_container_width=True):
        ir_a("registro")
        st.rerun()

    if st.button("📋 ADMINISTRACIÓN GENERAL", use_container_width=True):
        ir_a("admin_Todos")
        st.rerun()

    st.markdown("---")
    st.write("🔍 **VER POR TRABAJADOR:**")
    
    # Columnas para los trabajadores
    c1, c2, c3 = st.columns(3)
    if c1.button("👤 Jaky", use_container_width=True): 
        ir_a("admin_Jaky")
        st.rerun()
    if c2.button("👤 Miriam", use_container_width=True): 
        ir_a("admin_Miriam")
        st.rerun()
    if c3.button("👤 Pepillo", use_container_width=True): 
        ir_a("admin_Pepillo")
        st.rerun()

# --- 2. PANTALLA DE REGISTRO ---
elif st.session_state.pagina == "registro":
    if st.button("⬅ Volver al Menú"): 
        ir_a("menu")
        st.rerun()
    
    st.header("📝 Nueva Reservación")
    
    # NOTA: Quitamos el "st.form" para que los cálculos sean instantáneos al hacer clic
    dueño = st.selectbox("Asignar a:", ["Jaky", "Miriam", "Pepillo"])
    cliente = st.text_input("Nombre del cliente")
    depa = st.text_input("Departamento / Casa")
    precio = st.number_input("Precio por noche ($)", min_value=0, step=1)
    
    col1, col2 = st.columns(2)
    llegada = col1.date_input("Llegada")
    salida = col2.date_input("Salida")
    
    transporte = st.checkbox("Transporte Internacional (+$100)")
    
    # CÁLCULO INSTANTÁNEO (Sin clics extra)
    noches = (salida - llegada).days
    total = (max(0, noches) * precio) + (100 if transporte else 0)
    
    if noches > 0:
        st.success(f"🌙 Noches: {noches} | 💰 TOTAL: ${total}")
    
if st.button("💾 GUARDAR AHORA", use_container_width=True, type="primary"):
        if cliente and depa and noches > 0:
            nueva = {
                "Dueño": dueño, "Cliente": cliente, "Propiedad": depa,
                "Inicio": llegada.strftime("%d/%m/%y"), 
                "Fin": salida.strftime("%d/%m/%y"), "Total": f"${total}"
            }
            st.session_state.reservas.append(nueva)
            st.toast("✅ ¡Guardado!") # Mensaje rápido en la esquina
            ir_a("menu")
            st.rerun()
        else:
            st.error("⚠️ Datos incompletos o fechas erróneas")

# --- 3. PANTALLA DE ADMINISTRACIÓN ---
elif st.session_state.pagina.startswith("admin_"):
    filtro = st.session_state.pagina.replace("admin_", "")
    if st.button("⬅ Volver al Menú"): 
        ir_a("menu")
        st.rerun()
    
    st.header(f"📋 Reservas de {filtro}")
    
    df = pd.DataFrame(st.session_state.reservas)
    if not df.empty:
        if filtro != "Todos":
            df = df[df["Dueño"] == filtro]
        
        if not df.empty:
            st.table(df)
        else:
            st.info(f"No hay registros para {filtro}")
    else:
        st.write("Historial vacío.")
