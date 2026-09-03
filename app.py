import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="COGRAL - Bodega", layout="wide", page_icon="🌱")

# --- ESTILO BONITO ---
st.markdown("""
<style>
  .stApp { background-color: #f8fdf8; }
    h1, h2, h3 { color: #2e7d32!important; }
  .stButton>button { background-color: #43a047; color: white; border-radius: 8px; font-weight: bold; }
    [data-testid="stSidebar"] { background-color: #e8f5e9; }
  .card { background: white; padding: 15px; border-radius: 15px; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.08); border-top: 4px solid #4caf50; margin-bottom: 10px; }
  .card img { border-radius: 50%; }
  .card h4 { margin: 10px 0 5px 0; color: #2e7d32; }
  .card p { font-size: 13px; color: #666; }
</style>
""", unsafe_allow_html=True)

USUARIOS = {"tatiana": {"pass": "tatiana2024", "rol": "Jefa de Bodega"}, "maria": {"pass": "maria2024", "rol": "Asistente"}}

if "login" not in st.session_state: st.session_state.login = False
if not st.session_state.login:
    st.title("🏭 COGRAL")
    st.subheader("Sistema de Bodega")
    u = st.text_input("Usuario").lower().strip()
    p = st.text_input("Contraseña", type="password")
    if st.button("Entrar", use_container_width=True):
        if u in USUARIOS and USUARIOS[u]["pass"] == p:
            st.session_state.login = True
            st.session_state.user = u
            st.session_state.rol = USUARIOS[u]["rol"]
            st.rerun()
        else: st.error("Datos incorrectos")
    st.stop()

# --- SIDEBAR ---
try:
    st.sidebar.image("IMG-20260902-WA2077.jpg", width=200)
except:
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/236/236831.png", width=150)

st.sidebar.markdown(f"### 👷‍♀️ {st.session_state.user.capitalize()}")
st.sidebar.caption(st.session_state.rol)
if st.sidebar.button("Cerrar sesión"): st.session_state.login=False; st.rerun()

if "productos" not in st.session_state: st.session_state.productos = ["Urea", "Maíz", "Cemento"]
if "inventario" not in st.session_state: st.session_state.inventario = []

st.title("📦 COGRAL - Control de Bodega")

tab1, tab2, tab3, tab4 = st.tabs(["🏠 Inicio Equipo", "➕ Registrar", "📊 Movimientos", "📦 Stock"])

# --- TAB 1: CUADRITOS BONITOS QUE QUIERES ---
with tab1:
    st.subheader("✨ Nuestro Equipo COGRAL")
    st.caption("Toca cada perfil para ver su función")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="card">
            <img src="https://cdn-icons-png.flaticon.com/512/4140/4140048.png" width="80">
            <h4>Secretaria</h4>
            <p>📋 Control de pedidos<br>Atención al cliente</p>
            <small>💚 Activa</small>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="card">
            <img src="https://cdn-icons-png.flaticon.com/512/4140/4140047.png" width="80">
            <h4>Revisora</h4>
            <p>🔍 Revisa calidad<br>Control de entradas</p>
            <small>💚 Activa</small>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="card">
            <img src="https://cdn-icons-png.flaticon.com/512/4140/4140037.png" width="80">
            <h4>Auxiliar de Bodega</h4>
            <p>📦 Organiza inventario<br>Carga y descarga</p>
            <small>💚 Activo</small>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="card">
            <img src="https://cdn-icons-png.flaticon.com/512/4140/4140051.png" width="80">
            <h4>Distribuidores</h4>
            <p>🚚 Entregas a campo<br>Rutas y clientes</p>
            <small>💚 En ruta</small>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    st.subheader("👩‍💼 Jefatura")
    c1, c2 = st.columns([1,3])
    with c1:
        try:
            st.image
