import streamlit as st
import pandas as pd
from datetime import date
st.set_page_config(page_title="COGRAL - Bodega", layout="wide")
USUARIOS = {"tatiana":{"pass":"tatiana2024","rol":"JEFA DE BODEGA"},"maria":{"pass":"maria2024","rol":"AUXILIAR"},"papa":{"pass":"papa123","rol":"GERENCIA"}}
if "login" not in st.session_state: st.session_state.login=False
if not st.session_state.login:
    st.title("🏢 COGRAL - Ingreso Bodega")
    u=st.text_input("Usuario").lower()
    p=st.text_input("Clave",type="password")
    if st.button("Entrar"):
        if u in USUARIOS and USUARIOS[u]["pass"]==p:
            st.session_state.login=True; st.session_state.rol=USUARIOS[u]["rol"]; st.session_state.user=u; st.rerun()
        else: st.error("Datos mal")
    st.stop()
st.sidebar.write(f"Rol: {st.session_state.rol}")
if st.sidebar.button("Salir"): st.session_state.login=False; st.rerun()
st.title(f"COGRAL - Bodega | Jefa: Tatiana | Rol: {st.session_state.rol}")
st.success("Sistema COGRAL funcionando - Tu eres la Jefa")
df=pd.DataFrame({"Producto":["Urea","Maiz","Cemento"],"Stock":[100,50,200]})
st.dataframe(df,use_container_width=True)
st.file_uploader("Subir foto evidencia (María cada 7 días)",type=["jpg","png"])
if st.session_state.rol=="JEFA DE BODEGA":
    if st.button("🔒 CERRAR AÑO COGRAL",type="primary"):
        st.balloons(); st.success("Cierre ejecutado por Tatiana - Jefa COGRAL")
