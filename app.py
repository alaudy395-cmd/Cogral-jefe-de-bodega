import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="COGRAL - Bodega", layout="wide", page_icon="🌱")
st.markdown("""<style>.stApp{background:#f8fdf8} h1,h2,h3{color:#2e7d32!important}.stButton>button{background:#43a047;color:white;border-radius:8px;font-weight:bold;width:100%} [data-testid="stSidebar"]{background:#e8f5e9}.card{background:white;padding:15px;border-radius:15px;text-align:center;box-shadow:0 4px 8px rgba(0,0,0,0.08);border-top:4px solid #4caf50;height:230px;margin-bottom:10px}.card-jefa{background:linear-gradient(135deg,#fff9c4 0%,#ffffff 100%);padding:15px;border-radius:15px;text-align:center;box-shadow:0 4px 12px rgba(0,0,0,0.15);border-top:4px solid #f9a825;height:230px;margin-bottom:10px}</style>""", unsafe_allow_html=True)

USUARIOS = {"tatiana": {"pass": "tatiana2024", "rol": "Jefa de Bodega"}, "maria": {"pass": "maria2024", "rol": "Asistente"}}
if "login" not in st.session_state: st.session_state.login=False
if not st.session_state.login:
    st.title("🏭 COGRAL"); st.subheader("Sistema de Bodega")
    u=st.text_input("Usuario").lower().strip(); p=st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        if u in USUARIOS and USUARIOS[u]["pass"]==p:
            st.session_state.login=True; st.session_state.user=u; st.session_state.rol=USUARIOS[u]["rol"]; st.rerun()
        else: st.error("Datos mal")
    st.stop()

st.sidebar.title("COGRAL")
try: st.sidebar.image("IMG-20260902-WA2077.jpg", width=200)
except: st.sidebar.warning("Foto no encontrada")
st.sidebar.markdown(f"### 👷‍♀️ {st.session_state.user.capitalize()}"); st.sidebar.caption(st.session_state.rol)
if st.sidebar.button("Cerrar sesión"): st.session_state.login=False; st.rerun()

if "productos" not in st.session_state: st.session_state.productos=["Urea","Maíz","Cemento","Triple 15"]
if "inventario" not in st.session_state: st.session_state.inventario=[]

st.title("📦 COGRAL - Control de Bodega")
tab1,tab2,tab3=st.tabs(["🏠 Inicio Equipo","➕ Registrar","📊 Stock"])

with tab1:
    st.subheader("✨ Nuestro Equipo COGRAL")
    col1,col2,col3,col4=st.columns(4)
    with col1:
        st.markdown('<div class="card-jefa">', unsafe_allow_html=True)
        try: st.image("IMG-20260902-WA2077.jpg", width=90)
        except: st.image("https://cdn-icons-png.flaticon.com/512/236/236831.png", width=90)
        st.markdown("<h4>👑 JEFA DE BODEGA</h4><p><b>Tatiana</b><br>Supervisión</p><small>⭐ Eres tú</small></div>", unsafe_allow_html=True)
    with col2: st.markdown('<div class="card"><img src="https://cdn-icons-png.flaticon.com/512/4140/4140048.png" width="80"><h4>Secretaria</h4><p>📋 Pedidos</p><small>💚 Activa</small></div>', unsafe_allow_html=True)
    with col3: st.markdown('<div class="card"><img src="https://cdn-icons-png.flaticon.com/512/4140/4140047.png" width="80"><h4>Revisora</h4><p>🔍 Calidad</p><small>💚 Activa</small></div>', unsafe_allow_html=True)
    with col4: st.markdown('<div class="card"><img src="https://cdn-icons-png.flaticon.com/512/4140/4140037.png" width="80"><h4>Auxiliar</h4><p>📦 Bodega</p><small>💚 Activo</small></div>', unsafe_allow_html=True)

with tab2:
    nuevo=st.text_input("✏️ Escribe el producto", placeholder="Ej: Alambre...")
    if nuevo and nuevo not in st.session_state.productos: st.session_state.productos.append(nuevo)
    prod_final=nuevo if nuevo else st.selectbox("O elige uno", st.session_state.productos)
    cant=st.number_input("Cantidad",1,10000,1); tipo=st.radio("Tipo",["Entrada","Salida"],horizontal=True); fecha=st.date_input("Fecha",date.today())
    if st.button("💾 Guardar",type="primary"):
        if prod_final:
            st.session_state.inventario.append({"Fecha":str(fecha),"Producto":prod_final,"Tipo":tipo,"Cantidad":cant})
            st.success(f"Guardado {prod_final}"); st.balloons()

with tab3:
    if st.session_state.inventario:
        df=pd.DataFrame(st.session_state.inventario); st.dataframe(df,use_container_width=True)
        stock=[]
        for p in df["Producto"].unique():
            e=df[(df["Producto"]==p)&(df["Tipo"]=="Entrada")]["Cantidad"].sum(); s=df[(df["Producto"]==p)&(df["Tipo"]=="Salida")]["Cantidad"].sum()
            stock.append({"Producto":p,"Stock":e-s})
        st.dataframe(pd.DataFrame(stock),use_container_width=True)
        st.download_button("📥 Descargar Excel",df.to_csv(index=False).encode('utf-8'),"bodega.csv","text/csv")
    else: st.info("Aún no hay datos")
