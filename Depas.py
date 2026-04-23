import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN Y ESTILO ---
st.set_page_config(page_title="Rentas Pro", layout="centered")

# Simulación de base de datos en memoria
if 'reservas' not in st.session_state:
    st.session_state.reservas = []
if 'pagina' not in st.session_state:
    st.session_state.pagina = "menu"

# --- FUNCIONES DE NAVEGACIÓN ---
def ir_a(pagina):
    st.session_state.pagina = pagina

# --- MENÚ PRINCIPAL ---
if st.session_state.pagina == "menu":
    st.title("MENÚ PRINCIPAL")
    st.subheader("Seleccione una opción:")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 REALIZAR RESERVA", use_container_width=True):
            ir_a("registro")
    with col2:
        if st.button("📋 ADMIN. GENERAL", use_container_width=True):
            ir_a("admin_Todos")

    st.markdown("---")
    st.write("**VER POR TRABAJADOR:**")
    
    c1, c2, c3 = st.columns(3)
    if c1.button("👤 Jaky", use_container_width=True): ir_a("admin_Jaky")
    if c2.button("👤 Miriam", use_container_width=True): ir_a("admin_Miriam")
    if c3.button("👤 Pepillo", use_container_width=True): ir_a("admin_Pepillo")

# --- PANTALLA DE REGISTRO ---
elif st.session_state.pagina == "registro":
    if st.button("⬅ Volver al Menú"): ir_a("menu")
    
    st.header("📝 Nueva Reservación")
    
    with st.form("form_reserva", clear_on_submit=True):
        dueño = st.selectbox("Asignar a:", ["Jaky", "Miriam", "Pepillo"])
        cliente = st.text_input("Nombre del cliente")
        depa = st.text_input("Departamento / Casa")
        precio = st.number_input("Precio por noche ($)", min_value=0)
        
        col1, col2 = st.columns(2)
        llegada = col1.date_input("Llegada")
        salida = col2.date_input("Salida")
        
        transporte = st.checkbox("Transporte Internacional (+$100)")
        
        # Cálculos
        noches = (salida - llegada).days
        total = (noches * precio) + (100 if transporte else 0)
        
        if noches >= 0:
            st.write(f"🌙 **Noches:** {noches} | 💰 **TOTAL:** ${total}")
        
        if st.form_submit_button("GUARDAR RESERVA"):
            if cliente and depa and noches >= 0:
                nueva = {
                    "Dueño": dueño, "Cliente": cliente, "Propiedad": depa,
                    "Inicio": llegada.strftime("%d/%m/%y"), 
                    "Fin": salida.strftime("%d/%m/%y"), "Total": f"${total}"
                }
                st.session_state.reservas.append(nueva)
                st.success("✅ ¡Guardado con éxito!")
                st.balloons()
            else:
                st.error("Error: Revisa los datos y las fechas.")

# --- PANTALLA DE ADMINISTRACIÓN ---
elif st.session_state.pagina.startswith("admin_"):
    filtro = st.session_state.pagina.replace("admin_", "")
    if st.button("⬅ Volver al Menú"): ir_a("menu")
    
    st.header(f"📋 Reservas: {filtro}")
    
    if st.session_state.reservas:
        df = pd.DataFrame(st.session_state.reservas)
        if filtro != "Todos":
            df = df[df["Dueño"] == filtro]
        
        if not df.empty:
            st.table(df) # Se ve mejor en celular que el dataframe interactivo
            if st.button("🗑️ Borrar Historial"):
                st.session_state.reservas = []
                st.rerun()
        else:
            st.info(f"No hay reservas para {filtro}")
    else:
        st.write("No hay datos registrados.")
