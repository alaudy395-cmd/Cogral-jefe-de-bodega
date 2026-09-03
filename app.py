import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
import os, io
import urllib.parse

st.set_page_config(page_title="COGRAL - 4 USUARIOS FINAL", layout="wide")

if "bodegas" not in st.session_state:
    st.session_state.bodegas = ["Bodega 1", "Bodega 2", "Bodega 3", "Bodega Principal"]
if "distribuidores" not in st.session_state:
    st.session_state.distribuidores = ["Agrosur", "Cogral", "Ferreteria Central", "Coagronorte", "Distribuidor Urea"]

FILE_DESCARGUES = "descargues.xlsx"
FILE_DESPACHOS = "despachos.xlsx"
FILE_REVISION = "revision.xlsx"
FILE_ARREGLOS = "arreglos.xlsx"
FILE_STOCK = "stock.xlsx"
FILE_INGRESOS = "ingresos.xlsx"

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

def limpieza_7_dias(archivo):
    if not os.path.exists(archivo): return 0
    df = pd.read_excel(archivo)
    if df.empty or "Fecha" not in df.columns: return 0
    if "Importante" not in df.columns: df["Importante"]="NO"
    try:
        df["Fecha_dt"] = pd.to_datetime(df["Fecha"], errors='coerce')
        limite = datetime.now() - timedelta(days=7)
        a_borrar = (df["Fecha_dt"] < limite) & (df["Importante"]!="SI")
        borrados = a_borrar.sum()
        if borrados>0:
            df = df[~a_borrar].drop(columns=["Fecha_dt"], errors='ignore')
            df.to_excel(archivo, index=False)
        return borrados
    except: return 0

def ejecutar_limpieza():
    total=0
    for arch in [FILE_DESCARGUES, FILE_DESPACHOS, FILE_REVISION, FILE_ARREGLOS]:
        total+=limpieza_7_dias(arch)
    return total

# LOGIN 4 USUARIOS
st.sidebar.title("🏭 COGRAL")
rol = st.sidebar.selectbox("Ingresar como:", ["Jefe de Bodega", "Secretaria", "Auxiliar de Bodega", "Miron"])
es_jefa = (rol=="Jefe de Bodega")

if es_jefa:
    borrados = ejecutar_limpieza()
    if borrados>0: st.sidebar.warning(f"🧹 {borrados} viejos borrados (>7 días)")
    st.sidebar.success("👑 Tatiana - JEFA - Puede borrar y marcar importante")

# ================= 1. JEFE =================
if rol=="Jefe de Bodega":
    t1,t2,t3,t4,t5,t6,t7,t8 = st.tabs(["🏠 Inicio","🏭 Bodegas","📥 Ingreso","📥 Descargues","🚚 Despachos WhatsApp","🔍 Buscador","🚨 Aprobaciones","⚙️ 7 Días"])

    with t1:
        st.title("🏭 JEFA DE BODEGA - Tatiana")
        try: st.image("IMG-20260902-WA2077.jpg", width=250)
        except: pass
        st.info("4 usuarios: Jefe, Secretaria, Auxiliar, Mirón | WhatsApp Gratis | Furgones sin carpa | 7 días auto-borra si no es IMPORTANTE")

    with t2:
        st.subheader("Control Bodegas")
        nueva=st.text_input("Nueva bodega")
        if st.button("Crear Bodega"):
            if nueva and nueva not in st.session_state.bodegas:
                st.session_state.bodegas.append(nueva); st.rerun()
        for b in st.session_state.bodegas: st.write(f"✅ {b}")

    with t3:
        st.subheader("📥 INGRESO - Varios productos + Distribuidor + Foto + Importante")
        if "lista_ingreso" not in st.session_state: st.session_state.lista_ingreso=[]
        prod=st.text_input("Producto libre", placeholder="Urea, Maiz, Alambre...")
        cant=st.number_input("Cantidad",1,100000,10)
        dist=st.selectbox("Distribuidor", st.session_state.distribuidores)
        nd=st.text_input("Nuevo distribuidor?")
        if nd and nd not in st.session_state.distribuidores: st.session_state.distribuidores.append(nd); dist=nd
        bod=st.selectbox("Bodega", st.session_state.bodegas)
        fec=st.date_input("Fecha", value=date.today())
        importante=st.checkbox("💾 Guardar como IMPORTANTE (no se borra)")
        foto=st.file_uploader("📸 Foto ingreso", type=["jpg","png","jpeg"])
        if foto: st.image(foto, width=180)
        if st.button("Agregar a lista"):
            if prod.strip():
                st.session_state.lista_ingreso.append({"Producto":prod.strip(),"Cantidad":cant,"Distribuidor":dist,"Bodega":bod,"Fecha":str(fec),"Importante":"SI" if importante else "NO","Foto":"SI" if foto else "NO","Tipo":"INGRESO"})
                st.success(f"Agregado {prod}")
        if st.session_state.lista_ingreso:
            st.dataframe(pd.DataFrame(st.session_state.lista_ingreso), use_container_width=True)
            if st.button("💾 GUARDAR TODO EN STOCK", type="primary", use_container_width=True):
                guardar_excel(FILE_INGRESOS, pd.DataFrame(st.session_state.lista_ingreso))
                guardar_excel(FILE_STOCK, pd.DataFrame(st.session_state.lista_ingreso))
                st.session_state.lista_ingreso=[]; st.rerun()
        if os.path.exists(FILE_STOCK):
            st.dataframe(pd.read_excel(FILE_STOCK), use_container_width=True)

    with t4:
        st.subheader("📥 DESCARGUES - Sencillo/Mula 1-40.000kg")
        with st.form("desc_jefa"):
            tipo=st.selectbox("Tipo", ["Sencillo","Mula"])
            peso=st.number_input("Peso 1-40000", 1, 40000, 1000)
            st.write(f"Toneladas: {peso/1000:.2f} t")
            prods=st.text_input("Productos varios")
            dist=st.selectbox("Distribuidor descargue", st.session_state.distribuidores)
            cond=st.text_input("Conductor")
            importante=st.checkbox("💾 IMPORTANTE")
            foto=st.file_uploader("📸 Foto descargue", type=["jpg","png","jpeg"])
            if st.form_submit_button("Guardar Descargue"):
                df=pd.DataFrame([{"Tipo":tipo,"Peso":peso,"Toneladas":peso/1000,"Productos":prods,"Distribuidor":dist,"Conductor":cond,"Importante":"SI" if importante else "NO","Foto":"SI" if foto else "NO","Fecha":str(date.today())}])
                guardar_excel(FILE_DESCARGUES, df); st.success("Guardado")

    with t5:
        st.subheader("🚚 DESPACHOS FURGONES - NK 482/866/NL 288 + Confirmación WhatsApp Gratis")
        st.info("Son furgones, siempre están en cargue. No se pide carpa. Solo Peso y Clientes + Foto + Firma")
        with st.form("desp_jefa_form"):
            carro=st.selectbox("Carro Furgón", ["NK 482","NK 866","NL 288","Otro"])
            destino=st.selectbox("Destino Boyacá", ["Tunja","Duitama","Sogamoso","Chiquinquirá","Paipa","Villa de Leyva","Otro"])
            peso=st.number_input("Peso kg 1-10000", 1, 10000, 1000)
            clientes=st.number_input("Clientes 1-100", 1, 100, 1)
            prods=st.text_area("Productos varios que lleva", placeholder="Urea 5 bultos, Maiz 10...")
            dist=st.selectbox("Distribuidor despacho", st.session_state.distribuidores)
            tel_conductor=st.text_input("📱 WhatsApp conductor (con indicativo 57 ej: 573001234567)", placeholder="573001234567")
            nombre=st.text_input("Nombre conductor")
            importante=st.checkbox("💾 Guardar como IMPORTANTE - no se borra a los 7 días")
            foto=st.file_uploader("📸 Foto furgón cargado - OBLIGATORIA", type=["jpg","png","jpeg"])
            if foto: st.image(foto, width=200)
            st.divider()
            st.write("✅ Check List Furgón")
            c1,c2=st.columns(2)
            with c1: ck_peso=st.checkbox("Peso OK")
            with c2: ck_clientes=st.checkbox("Clientes OK")
            firma=st.checkbox("Recibí completo y me hago responsable de la carga")
            btn=st.form_submit_button("💾 GUARDAR Despacho y Generar WhatsApp", type="primary", use_container_width=True)
            if btn:
                if not firma: st.error("Debe firmar el check de recibido")
                elif not foto: st.error("Foto obligatoria del furgón")
                else:
                    df=pd.DataFrame([{"Carro":carro,"Destino":destino,"Peso":peso,"Clientes":clientes,"Productos":prods,"Distribuidor":dist,"WhatsApp":tel_conductor,"PesoOK":ck_peso,"ClientesOK":ck_clientes,"Importante":"SI" if importante else "NO","Foto":"SI","Nombre":nombre,"Firma":"SI - Recibí completo y me hago responsable","Fecha":str(date.today()),"Hora":datetime.now().strftime("%H:%M")}])
                    guardar_excel(FILE_DESPACHOS, df)
                    st.session_state["ultimo_despacho"]={"carro":carro,"destino":destino,"peso":peso,"clientes":clientes,"prods":prods,"tel":tel_conductor,"nombre":nombre,"ck_peso":ck_peso,"ck_clientes":ck_clientes}
                    st.success("✅ Despacho guardado correctamente"); st.balloons()

        # BOTON WHATSAPP FUERA DEL FORM
        if "ultimo_despacho" in st.session_state and st.session_state["ultimo_despacho"]:
            d=st.session_state["ultimo_despacho"]
            st.divider()
            st.subheader("📲 Confirmación WhatsApp - Opción Gratis")
            if d["tel"]:
                texto = f"🚚 *COGRAL - DESPACHO FURGÓN*%0A%0A*Carro:* {d['carro']}%0A*Destino:* {d['destino']}%0A*Peso:* {d['peso']} kg%0A*Clientes:* {d['clientes']}%0A*Productos:* {d['prods']}%0A*Distribuidor:* {dist}%0A%0A✅ *Check:* Peso OK:{d['ck_peso']} | Clientes OK:{d['ck_clientes']}%0A%0A👤 *Conductor:* {d['nombre']}%0A
