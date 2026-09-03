import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
import os, io
import urllib.parse

st.set_page_config(page_title="COGRAL", layout="wide")

# ========== USUARIOS Y CLAVES - TU LOS CAMBIAS ACA ==========
USUARIOS = {
    "tatiana": {"clave": "cogral2026", "rol": "Jefe de Bodega", "nombre": "Tatiana - Jefa"},
    "secretaria": {"clave": "secre123", "rol": "Secretaria", "nombre": "Secretaria"},
    "auxiliar": {"clave": "aux123", "rol": "Auxiliar de Bodega", "nombre": "Auxiliar"},
    "miron": {"clave": "miron123", "rol": "Miron", "nombre": "Mirón"},
    "conductor": {"clave": "cond123", "rol": "Conductor", "nombre": "Conductor"}
}

if "bodegas" not in st.session_state:
    st.session_state.bodegas = ["Bodega 1", "Bodega 2", "Bodega 3", "Bodega Principal"]
if "distribuidores" not in st.session_state:
    st.session_state.distribuidores = ["Agrosur", "Cogral", "Ferreteria Central"]

FILE_DESCARGUES = "descargues.xlsx"
FILE_DESPACHOS = "despachos.xlsx"
FILE_REVISION = "revision.xlsx"
FILE_ARREGLOS = "arreglos.xlsx"
FILE_STOCK = "stock.xlsx"

def guardar_excel(archivo, df_new):
    if os.path.exists(archivo):
        df_old = pd.read_excel(archivo)
        df_final = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df_final = df_new
    df_final.to_excel(archivo, index=False)

def to_excel_download(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# ========== LOGIN ==========
if "login" not in st.session_state:
    st.session_state.login = False
    st.session_state.rol = ""
    st.session_state.usuario = ""

if not st.session_state.login:
    st.title("🏭 COGRAL - Ingreso")
    col1,col2,col3 = st.columns([1,2,1])
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/3064/3064197.png", width=100)
        usuario = st.text_input("Usuario")
        clave = st.text_input("Clave", type="password")
        if st.button("Entrar", type="primary", use_container_width=True):
            if usuario in USUARIOS and USUARIOS[usuario]["clave"] == clave:
                st.session_state.login = True
                st.session_state.rol = USUARIOS[usuario]["rol"]
                st.session_state.usuario = usuario
                st.session_state.nombre = USUARIOS[usuario]["nombre"]
                st.rerun()
            else:
                st.error("Usuario o clave incorrecta")
        st.caption("Usuarios: tatiana / secretaria / auxiliar / miron / conductor")
    st.stop()

# ========== YA LOGUEADO ==========
rol = st.session_state.rol
nombre = st.session_state.nombre

st.sidebar.title(f"COGRAL")
st.sidebar.write(f"👤 {nombre}")
st.sidebar.write(f"Rol: {rol}")
if st.sidebar.button("Cerrar sesión"):
    st.session_state.login = False
    st.rerun()

# LIMPIEZA SILENCIOSA (no se muestra)
def limpieza_silenciosa():
    for arch in [FILE_DESCARGUES, FILE_DESPACHOS, FILE_REVISION, FILE_ARREGLOS]:
        if os.path.exists(arch):
            try:
                df=pd.read_excel(arch)
                if "Fecha" in df.columns and "Importante" in df.columns:
                    df["Fecha_dt"]=pd.to_datetime(df["Fecha"], errors='coerce')
                    limite=datetime.now()-timedelta(days=7)
                    df=df[~((df["Fecha_dt"]<limite) & (df["Importante"]!="SI"))].drop(columns=["Fecha_dt"], errors='ignore')
                    df.to_excel(arch, index=False)
            except: pass
if rol=="Jefe de Bodega":
    limpieza_silenciosa()

# ========== INTERFACES POR ROL ==========

# ---- JEFA - TODO ----
if rol=="Jefe de Bodega":
    st.title(f"Bienvenida {nombre} 👑 - Panel Central")
    t1,t2,t3,t4,t5 = st.tabs(["📦 STOCK E INGRESOS", "📥 DESCARGUES", "🚚 DESPACHOS + WHATSAPP", "🔍 REVISION SECRETARIA", "👷 AUXILIAR"])

    with t1:
        st.subheader("Ingresos y Stock")
        if "lista_ingreso" not in st.session_state: st.session_state.lista_ingreso=[]
        c1,c2=st.columns(2)
        with c1:
            prod=st.text_input("Producto")
            cant=st.number_input("Cantidad",1,100000,10)
            dist=st.selectbox("Distribuidor", st.session_state.distribuidores)
        with c2:
            bod=st.selectbox("Bodega", st.session_state.bodegas)
            fec=st.date_input("Fecha", value=date.today())
            imp=st.checkbox("Marcar como IMPORTANTE")
        foto=st.file_uploader("Foto", type=["jpg","png","jpeg"], key="ing")
        if st.button("Agregar a lista"):
            if prod:
                st.session_state.lista_ingreso.append({"Producto":prod,"Cantidad":cant,"Distribuidor":dist,"Bodega":bod,"Fecha":str(fec),"Importante":"SI" if imp else "NO","Foto":"SI" if foto else "NO"})
                st.success("Agregado")
        if st.session_state.lista_ingreso:
            st.dataframe(pd.DataFrame(st.session_state.lista_ingreso))
            if st.button("GUARDAR TODO EN STOCK", type="primary"):
                guardar_excel(FILE_STOCK, pd.DataFrame(st.session_state.lista_ingreso))
                st.session_state.lista_ingreso=[]; st.rerun()
        if os.path.exists(FILE_STOCK):
            df=pd.read_excel(FILE_STOCK)
            st.dataframe(df, use_container_width=True)
            st.download_button("Exportar Stock", to_excel_download(df), "stock.xlsx")

    with t2:
        st.subheader("Descargues Sencillo / Mula 1-40.000kg")
        with st.form("desc"):
            tipo=st.selectbox("Tipo", ["Sencillo","Mula"])
            peso=st.number_input("Peso kg",1,40000,1000)
            prods=st.text_input("Productos que trae")
            cond=st.text_input("Conductor")
            foto=st.file_uploader("Foto descargue", type=["jpg","png","jpeg"], key="desc")
            imp=st.checkbox("IMPORTANTE")
            if st.form_submit_button("Guardar Descargue", type="primary"):
                df=pd.DataFrame([{"Tipo":tipo,"Peso":peso,"Toneladas":peso/1000,"Productos":prods,"Conductor":cond,"Importante":"SI" if imp else "NO","Foto":"SI" if foto else "NO","Fecha":str(date.today())}])
                guardar_excel(FILE_DESCARGUES, df); st.success("Guardado")
        if os.path.exists(FILE_DESCARGUES): st.dataframe(pd.read_excel(FILE_DESCARGUES))

    with t3:
        st.subheader("Despachos Furgones NK 482 / 866 / NL 288")
        with st.form("desp"):
            carro=st.selectbox("Carro furgón", ["NK 482","NK 866","NL 288","Otro"])
            dest=st.selectbox("Destino Boyacá", ["Tunja","Duitama","Sogamoso","Chiquinquirá","Paipa","Otro"])
            peso=st.number_input("Peso kg 1-10000",1,10000,1000)
            clientes=st.number_input("No. Clientes 1-100",1,100,1)
            prods=st.text_area("Productos que lleva")
            dist=st.selectbox("Distribuidor", st.session_state.distribuidores)
            tel=st.text_input("WhatsApp conductor (57...)")
            nom=st.text_input("Nombre conductor")
            foto=st.file_uploader("Foto furgón OBLIGATORIA", type=["jpg","png","jpeg"], key="despacho")
            c1,c2=st.columns(2)
            with c1: ck_peso=st.checkbox("Peso OK")
            with c2: ck_clientes=st.checkbox("Clientes OK")
            firma=st.checkbox("Recibí completo y me hago responsable")
            imp=st.checkbox("IMPORTANTE")
            if st.form_submit_button("Guardar Despacho", type="primary"):
                if not firma: st.error("Debe firmar")
                elif not foto: st.error("Foto obligatoria")
                else:
                    df=pd.DataFrame([{"Carro":carro,"Destino":dest,"Peso":peso,"Clientes":clientes,"Productos":prods,"Distribuidor":dist,"WhatsApp":tel,"PesoOK":ck_peso,"ClientesOK":ck_clientes,"Importante":"SI" if imp else "NO","Foto":"SI","Nombre":nom,"Firma":"SI","Fecha":str(date.today())}])
                    guardar_excel(FILE_DESPACHOS, df)
                    st.session_state["ult"]={"carro":carro,"dest":dest,"peso":peso,"cli":clientes,"prods":prods,"tel":tel,"nom":nom,"ck1":ck_peso,"ck2":ck_clientes,"dist":dist}
                    st.success("Despacho guardado")
        if "ult" in st.session_state and st.session_state["ult"]:
            d=st.session_state["ult"]
            if d["tel"]:
                raw=f"COGRAL DESPACHO\nCarro:{d['carro']}\nDestino:{d['dest']}\nPeso:{d['peso']}kg\nClientes:{d['cli']}\nProductos:{d['prods']}\nConductor:{d['nom']}\nFirma: Recibi completo\nFecha:{date.today()}\nResponde CONFIRMO"
                link=f"https://wa.me/{d['tel']}?text={urllib.parse.quote(raw)}"
                st.link_button(f"📲 Enviar confirmación WhatsApp a {d['tel']}", link, type="primary", use_container_width=True)
        if os.path.exists(FILE_DESPACHOS): st.dataframe(pd.read_excel(FILE_DESPACHOS))

    with t4:
        st.subheader("Revisiones de Secretaria - Para Aprobar")
        if os.path.exists(FILE_REVISION):
            df=pd.read_excel(FILE_REVISION)
            st.dataframe(df)
            for idx,row in df.iterrows():
                if row.get("Estado")=="Pendiente Jefa":
                    with st.container(border=True):
                        st.write(row.to_dict())
                        mot=st.text_input("Motivo", key=f"mot{idx}")
                        c1,c2=st.columns(2)
                        if c1.button("Aprobar", key=f"ap{idx}"):
                            df.loc[idx,"Estado"]="Aprobado"; df.to_excel(FILE_REVISION,index=False); st.rerun()
                        if c2.button("Devolver", key=f"de{idx}"):
                            df.loc[idx,"Estado"]="Corregir"; df.to_excel(FILE_REVISION,index=False); st.rerun()
        else: st.info("Sin revisiones")

    with t5:
        st.subheader("Arreglos Auxiliar")
        if os.path.exists(FILE_ARREGLOS): st.dataframe(pd.read_excel(FILE_ARREGLOS))

# ---- SECRETARIA - SOLO SU INTERFAZ ----
elif rol=="Secretaria":
    st.title("📝 Secretaria - Revisión de Bodega")
    st.info("Tu revisión le llega a la Jefa Tatiana para aprobar")
    with st.form("rev", clear_on_submit=True):
        bod=st.selectbox("Bodega", st.session_state.bodegas)
        prod=st.text_input("Producto")
        fis=st.number_input("Física contada", 0.0)
        sis=st.number_input("Sistema", 0.0)
        obs=st.text_area("Observaciones")
        foto=st.file_uploader("Foto evidencia", type=["jpg","png","jpeg"])
        if st.form_submit_button("Enviar a Jefa Tatiana", type="primary", use_container_width=True):
            error=fis-sis
            estado="Pendiente Jefa" if error!=0 else "OK"
            df=pd.DataFrame([{"Bodega":bod,"Producto":prod,"Fisica":fis,"Sistema":sis,"Error":error,"Observaciones":obs,"Foto":"SI" if foto else "NO","Estado":estado,"Fecha":str(date.today()),"Usuario":st.session_state.usuario}])
            guardar_excel(FILE_REVISION, df)
            if error!=0: st.error(f"Error {error} enviado a Jefa")
            else: st.success("Enviado OK")
    if os.path.exists(FILE_REVISION):
        st.subheader("Mis revisiones")
        df=pd.read_excel(FILE_REVISION)
        df=df[df["Usuario"]==st.session_state.usuario] if "Usuario" in df.columns else df
        st.dataframe(df)

# ---- AUXILIAR - SOLO SU INTERFAZ ----
elif rol=="Auxiliar de Bodega":
    st.title("🔧 Auxiliar - Arreglos y Observaciones")
    with st.form("aux", clear_on_submit=True):
        bod=st.selectbox("Bodega", st.session_state.bodegas)
        maq=st.text_input("Máquina / Área")
        que=st.text_area("Qué arreglé")
        obs=st.text_area("Observaciones", height=150)
        f1=st.file_uploader("Foto ANTES", type=["jpg","png","jpeg"])
        f2=st.file_uploader("Foto DESPUÉS", type=["jpg","png","jpeg"])
        if st.form_submit_button("Guardar Arreglo", type="primary", use_container_width=True):
            if not obs: st.error("Observaciones obligatorias")
            else:
                df=pd.DataFrame([{"Bodega":bod,"Maquina":maq,"Arreglo":que,"Observaciones":obs,"FotoAntes":"SI" if f1 else "NO","FotoDespues":"SI" if f2 else "NO","Fecha":str(date.today()),"Usuario":st.session_state.usuario}])
                guardar_excel(FILE_ARREGLOS, df); st.success("Guardado")
    if os.path.exists(FILE_ARREGLOS): st.dataframe(pd.read_excel(FILE_ARREGLOS))

# ---- MIRON ----
elif rol=="Miron":
    st.title("👀 Solo Vista")
    for arch in [FILE_STOCK, FILE_DESCARGUES, FILE_DESPACHOS, FILE_REVISION, FILE_ARREGLOS]:
        if os.path.exists(arch):
            st.subheader(arch.upper())
            st.dataframe(pd.read_excel(arch))

# ---- CONDUCTOR ----
elif rol=="Conductor":
    st.title("🚚 Conductor - Mis Despachos")
    st.info("Aquí ves tus despachos asignados y confirmas por WhatsApp")
    if os.path.exists(FILE_DESPACHOS):
        df=pd.read_excel(FILE_DESPACHOS)
        st.dataframe(df)
        tel=st.text_input("Tu WhatsApp para confirmar (57...)")
        if tel and not df.empty:
            d=df.iloc[-1].to_dict()
            raw=f"CONFIRMO DESPACHO {d.get('Carro')} Dest {d.get('Destino')} {d.get('Peso')}kg Fecha {date.today()}"
            link=f"https://wa.me/573001111111?text={urllib.parse.quote(raw)}"
            st.link_button("CONFIRMAR RECEPCIÓN POR WHATSAPP A JEFA", link, type="primary")
