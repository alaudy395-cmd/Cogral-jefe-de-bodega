import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
import os, io, glob, zipfile
from PIL import Image
import numpy as np

st.set_page_config(page_title="COGRAL - FINAL COMPLETO", layout="wide", initial_sidebar_state="expanded")

# ============ CONFIG FOTOS COMPRIMIDAS 300KB + 7 DIAS ============
CARPETA_FOTOS = "fotos"
os.makedirs(CARPETA_FOTOS, exist_ok=True)
os.makedirs(f"{CARPETA_FOTOS}/importantes", exist_ok=True)

def guardar_foto_comprimida(archivo, es_importante=False):
    if not archivo:
        return "NO", ""
    try:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        carpeta = f"{CARPETA_FOTOS}/importantes" if es_importante else CARPETA_FOTOS
        nombre_base = archivo.name.rsplit('.',1)[0][:20].replace(" ", "_")
        nombre = f"{ts}_{nombre_base}.jpg"
        ruta = os.path.join(carpeta, nombre)
        img = Image.open(archivo)
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")
        img.thumbnail((1024, 1024))
        img.save(ruta, "JPEG", optimize=True, quality=50)
        return "SI", ruta
    except Exception as e:
        return "NO", ""

def limpiar_fotos_7dias():
    limite = datetime.now() - timedelta(days=7)
    b=0
    for f in glob.glob(f"{CARPETA_FOTOS}/*.*"):
        if os.path.isfile(f) and datetime.fromtimestamp(os.path.getmtime(f)) < limite:
            try: os.remove(f); b+=1
            except: pass
    return b

def crear_zip_todo():
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        for a in ["stock.xlsx","revision.xlsx","descargues.xlsx","despachos.xlsx","arreglos.xlsx"]:
            if os.path.exists(a): z.write(a)
        for f in glob.glob(f"{CARPETA_FOTOS}/**/*.*", recursive=True):
            if os.path.isfile(f): z.write(f)
    return out.getvalue()

def guardar_excel(archivo, df_new):
    if os.path.exists(archivo):
        try:
            old=pd.read_excel(archivo)
            for col in df_new.columns:
                if col not in old.columns:
                    old[col] = ""
            final=pd.concat([old, df_new], ignore_index=True)
        except:
            final=df_new
    else:
        final=df_new
    final.to_excel(archivo,index=False)

def to_excel_download(df):
    out=io.BytesIO()
    with pd.ExcelWriter(out, engine='openpyxl') as w:
        df.to_excel(w,index=False)
    return out.getvalue()

if "limpieza_hecha" not in st.session_state:
    limpiar_fotos_7dias()
    st.session_state.limpieza_hecha=True

# ============ USUARIOS - LOGIN SIN CLAVES VISIBLES ============
USUARIOS = {
    "tatiana": {"clave":"cogral2026","rol":"Jefe de Bodega","nombre":"Tatiana - Jefa"},
    "secretaria": {"clave":"secre123","rol":"Secretaria","nombre":"Secretaria"},
    "auxiliar": {"clave":"aux123","rol":"Auxiliar de Bodega","nombre":"Auxiliar"},
    "miron": {"clave":"miron123","rol":"Miron","nombre":"Mirón"},
    "conductor": {"clave":"cond123","rol":"Conductor","nombre":"Conductor"},
}
if "bodegas" not in st.session_state:
    st.session_state.bodegas=["Bodega 1","Bodega 2","Bodega 3","Bodega Principal"]
if "distribuidores" not in st.session_state:
    st.session_state.distribuidores=["Agrosur","Cogral","Ferreteria Central","Coagronorte","Urea Dist"]

FILE_STOCK="stock.xlsx"
FILE_REVISION="revision.xlsx"
FILE_DESCARGUES="descargues.xlsx"
FILE_DESPACHOS="despachos.xlsx"
FILE_ARREGLOS="arreglos.xlsx"

if "login" not in st.session_state:
    st.session_state.login=False

if not st.session_state.login:
    st.title("🏭 COGRAL - Ingreso")
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        u=st.text_input("Usuario")
        p=st.text_input("Clave", type="password")
        if st.button("Entrar", type="primary", use_container_width=True):
            if u in USUARIOS and USUARIOS[u]["clave"]==p:
                st.session_state.login=True
                st.session_state.rol=USUARIOS[u]["rol"]
                st.session_state.usuario=u
                st.session_state.nombre=USUARIOS[u]["nombre"]
                st.rerun()
            else:
                st.error("Usuario o clave incorrecta")
    st.stop()

rol=st.session_state.rol
nombre=st.session_state.nombre
st.sidebar.write(f"👤 {nombre} - {rol}")
if st.sidebar.button("Cerrar sesión"):
    st.session_state.login=False
    st.rerun()

if rol=="Jefe de Bodega":
    if st.sidebar.button("🧹 Limpiar fotos >7 días ahora"):
        b=limpiar_fotos_7dias()
        st.sidebar.success(f"Borradas {b} fotos")

MUNICIPIOS=["Tunja","Duitama","Sogamoso","Paipa","Chiquinquira","Villa de Leyva","Moniquira","Garagoa","Miraflores","Puerto Boyaca","Samaca","Ventaquemada","Nobsa","Tibasosa","Santa Rosa de Viterbo","Soata","El Cocuy","Guateque","Ramiriqui","Turmeque","Toca","Combita","Oicata","Sora","Sotaquira","Tuta","Chivata","Soraca","Siachoque","Tibana","Jenesano","Nuevo Colon","Boyaca","Vira Cacha","Cienega","Ramiriqui","Zetaquira","Berbeo","Miraflores","Paez","San Eduardo","Paya","Pisba"]

# ============ APLICACION ============
if rol=="Jefe de Bodega":
    st.title(f"Bienvenida {nombre} 👑 - App Completa")
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📦 STOCK","📥 DESCARGUES","🚚 DESPACHOS","🔍 REVISIONES","📊 INFORMES","🗃️ BORRAR/CERO"])

    with tab1:
        st.subheader("📦 STOCK - Producto, Físico, Sistema, Proveedor, Vencimiento, Bodega - Foto OPCIONAL")
        with st.form("stock_form", clear_on_submit=True):
            prod=st.text_input("Producto *")
            c1,c2=st.columns(2)
            with c1: fis=st.number_input("Cantidad FÍSICO",0,100000,0)
            with c2: sis=st.number_input("Cantidad SISTEMA",0,100000,0)
            prov=st.selectbox("Proveedor", st.session_state.distribuidores)
            nuevo_prov=st.text_input("Nuevo proveedor? Escríbelo aquí")
            if nuevo_prov: prov=nuevo_prov
            if nuevo_prov and nuevo_prov not in st.session_state.distribuidores:
                st.session_state.distribuidores.append(nuevo_prov)
            c3,c4=st.columns(2)
            with c3: bod=st.selectbox("Bodega", st.session_state.bodegas)
            with c4: ven=st.date_input("Fecha Vencimiento", value=date.today())
            obs=st.text_area("Observaciones")
            foto=st.file_uploader("📸 Foto OPCIONAL - si quieres (se comprime a 300KB)", type=["jpg","jpeg","png"])
            imp=st.checkbox("⭐ IMPORTANTE - Esta foto NO se borra a los 7 días")
            if fis>0 and fis<=30:
                st.error(f"⚠️ ALERTA BAJITO: Solo {fis} unidades")
            if st.form_submit_button("💾 GUARDAR STOCK", type="primary", use_container_width=True):
                if not prod:
                    st.error("Falta producto")
                else:
                    tf, ruta = guardar_foto_comprimida(foto, imp)
                    err = fis - sis
                    df=pd.DataFrame([{
                        "Producto":prod,"Cantidad_Fisica":fis,"Cantidad_Sistema":sis,"Error":err,
                        "Proveedor":prov,"Bodega":bod,"Vencimiento":str(ven),"Observaciones":obs,
                        "Foto":tf,"Ruta_Foto":ruta,"Importante":"SI" if imp else "NO",
                        "Estado":"Pendiente" if err!=0 or fis<=30 else "OK",
                        "Alerta_Bajo":"SI" if fis<=30 else "NO",
                        "Fecha":str(date.today()),
                        "Borra_en": str(date.today()+timedelta(days=7)) if not imp else "NUNCA"
                    }])
                    guardar_excel(FILE_STOCK, df)
                    guardar_excel(FILE_REVISION, df)
                    st.success("Guardado - Con o sin foto funciona")
                    st.balloons()
        if os.path.exists(FILE_STOCK):
            st.dataframe(pd.read_excel(FILE_STOCK), use_container_width=True)

    with tab2:
        st.subheader("📥 DESCARGUES - Nombre, Tipo Sencillo/Mula, Peso 1-40000, Toneladas, Proveedor, Conductor - Foto OPCIONAL")
        with st.form("desc_form", clear_on_submit=True):
            nd=st.text_input("Nombre Descargue *")
            c1,c2=st.columns(2)
            with c1: tipo=st.selectbox("Tipo",["Sencillo","Mula"])
            with c2: peso=st.number_input("Peso kg 1-40000",1,40000,1000)
            st.caption(f"{peso/1000:.2f} toneladas")
            prov=st.selectbox("Proveedor", st.session_state.distribuidores, key="prov_desc")
            cond=st.text_input("Conductor")
            foto=st.file_uploader("📸 Foto OPCIONAL", type=["jpg","jpeg","png"], key="foto_desc")
            imp=st.checkbox("⭐ IMPORTANTE", key="imp_desc")
            if st.form_submit_button("💾 Guardar Descargue", type="primary", use_container_width=True):
                if not nd:
                    st.error("Falta nombre")
                else:
                    tf,ruta=guardar_foto_comprimida(foto, imp)
                    df=pd.DataFrame([{"Nombre_Descargue":nd,"Tipo":tipo,"Peso":peso,"Toneladas":peso/1000,"Proveedor":prov,"Conductor":cond,"Foto":tf,"Ruta_Foto":ruta,"Importante":"SI" if imp else "NO","Fecha":str(date.today())}])
                    guardar_excel(FILE_DESCARGUES, df)
                    st.success("Guardado")
        if os.path.exists(FILE_DESCARGUES):
            st.dataframe(pd.read_excel(FILE_DESCARGUES), use_container_width=True)

    with tab3:
        st.subheader("🚚 DESPACHOS FURGONES - Carro, Destino Boyacá, Peso 1-10000, Clientes, Productos, Conductor, Firma con dedo - Foto OPCIONAL")
        with st.form("desp_form", clear_on_submit=True):
            carro=st.selectbox("Carro furgón",["NK 482","NK 866","NL 288","Otro"])
            dest=st.selectbox("Destino Boyacá", MUNICIPIOS)
            c1,c2=st.columns(2)
            with c1: peso=st.number_input("Peso kg 1-10000",1,10000,1000)
            with c2: cli=st.number_input("No. Clientes 1-100",1,100,1)
            prods=st.text_area("Productos que lleva *")
            foto=st.file_uploader("📸 Foto furgón OPCIONAL - ya no bloquea", type=["jpg","jpeg","png"], key="foto_desp")
            nom=st.text_input("Nombre conductor")
            imp=st.checkbox("⭐ IMPORTANTE", key="imp_desp")
            if st.form_submit_button("💾 DESPACHAR - Conductor firmará luego", type="primary", use_container_width=True):
                if not prods:
                    st.error("Falta productos")
                else:
                    tf,ruta=guardar_foto_comprimida(foto, imp)
                    df=pd.DataFrame([{"Carro":carro,"Destino":dest,"Peso":peso,"Clientes":cli,"Productos":prods,"Foto":tf,"Ruta_Foto":ruta,"Importante":"SI" if imp else "NO","Nombre_Conductor":nom,"Firma":"NO","Ruta_Firma":"","Estado_Check":"Pendiente firma","Fecha":str(date.today()),"Hora":datetime.now().strftime("%H:%M")}])
                    guardar_excel(FILE_DESPACHOS, df)
                    st.success("Despachado - Sin foto también guarda")
                    st.balloons()
        if os.path.exists(FILE_DESPACHOS):
            df=pd.read_excel(FILE_DESPACHOS)
            st.dataframe(df, use_container_width=True)
            if "Ruta_Firma" in df.columns:
                for i,row in df.iterrows():
                    rf=str(row.get("Ruta_Firma",""))
                    if rf and os.path.exists(rf):
                        st.write(f"✍️ Firma: {row.get('Nombre_Conductor','')} - {row.get('Destino','')} - {row.get('Fecha','')}")
                        st.image(rf, width=250)

    with tab4:
        st.subheader("🔍 REVISIONES")
        if os.path.exists(FILE_REVISION):
            df=pd.read_excel(FILE_REVISION)
            st.dataframe(df, use_container_width=True)
            st.download_button("📥 Exportar Revisiones", to_excel_download(df), "revisiones.xlsx")
        else:
            st.info("No hay revisiones aún")

    with tab5:
        st.title("📊 INFORMES - 20 revisados, 10 con error, etc + carros por municipio")
        c1,c2=st.columns(2)
        with c1: fi=st.date_input("Desde", value=date.today()-timedelta(days=7))
        with c2: ff=st.date_input("Hasta", value=date.today())

        if os.path.exists(FILE_REVISION):
            df=pd.read_excel(FILE_REVISION)
            try:
                df["Fecha_dt"]=pd.to_datetime(df["Fecha"], errors='coerce')
                mask=(df["Fecha_dt"]>=pd.to_datetime(fi)) & (df["Fecha_dt"]<=pd.to_datetime(ff))
                dff=df[mask]
            except: dff=df
            total=len(dff)
            con_err=len(dff[dff["Error"]!=0]) if "Error" in dff.columns and not dff.empty else 0
            bien=total-con_err
            bajos=len(dff[dff["Cantidad_Fisica"]<=30]) if "Cantidad_Fisica" in dff.columns and not dff.empty else 0

            st.subheader("📦 Inventario Semana")
            m1,m2,m3,m4=st.columns(4)
            m1.metric("Revisados", total)
            m2.metric("Con Error", con_err)
            m3.metric("Bien", bien)
            m4.metric("Bajitos <=30", bajos)
            st.write(f"Ejemplo: En la semana se revisaron {total} productos, {con_err} con error, {bien} bien")
            if not dff.empty:
                st.dataframe(dff, use_container_width=True)
                st.download_button("📥 Exportar Inventario Semana", to_excel_download(dff), f"informe_inv_{fi}_{ff}.xlsx")

        if os.path.exists(FILE_DESPACHOS):
            st.divider()
            st.subheader("🚚 Carros por Municipio - Ejemplo Duitama tantas veces")
            df=pd.read_excel(FILE_DESPACHOS)
            try:
                df["Fecha_dt"]=pd.to_datetime(df["Fecha"], errors='coerce')
                mask=(df["Fecha_dt"]>=pd.to_datetime(fi)) & (df["Fecha_dt"]<=pd.to_datetime(ff))
                dff=df[mask]
            except: dff=df
            if not dff.empty:
                res=dff.groupby("Destino").agg(Veces=("Destino","count"), Peso_Total_kg=("Peso","sum"), Clientes_Total=("Clientes","sum")).reset_index().sort_values("Veces", ascending=False)
                st.dataframe(res, use_container_width=True)
                st.bar_chart(res.set_index("Destino")["Veces"])
                st.download_button("📥 Exportar Despachos", to_excel_download(dff), f"informe_desp_{fi}_{ff}.xlsx")

    with tab6:
        st.title("🗃️ BORRAR / CERO - Para TODOS - App nunca se llena")
        st.warning("⚠️ Lo que borres aquí se borra para SECRETARIA, AUXILIAR, MIRON Y CONDUCTOR. Todos quedan en cero.")
        if st.button("📦 EXPORTAR TODO EN ZIP (Respaldo Año/Mes)", type="primary", use_container_width=True):
            z=crear_zip_todo()
            st.download_button("⬇️ DESCARGAR ZIP FINAL", z, f"COGRAL_RESPALDO_{date.today()}.zip", "application/zip", use_container_width=True)

        st.divider()
        st.subheader("🔧 Si te da error de Ruta_Firma")
        if st.button("🔧 ARREGLAR ARCHIVOS VIEJOS - CLIC AQUÍ", use_container_width=True):
            for arch in [FILE_DESPACHOS, FILE_STOCK, FILE_REVISION]:
                if os.path.exists(arch):
                    try:
                        df=pd.read_excel(arch)
                        if "Ruta_Firma" not in df.columns: df["Ruta_Firma"]=""
                        if "Firma" not in df.columns: df["Firma"]="NO"
                        if "Ruta_Foto" not in df.columns: df["Ruta_Foto"]=""
                        df.to_excel(arch, index=False)
                    except:
                        if os.path.exists(arch): os.remove(arch)
            st.success("Arreglado - Ya puedes firmar")

        st.divider()
        col1,col2=st.columns(2)
        with col1:
            if st.button("🗑️ Borrar MES actual para TODOS", use_container_width=True):
                st.session_state["cm"]=True
            if st.session_state.get("cm"):
                if st.button("✅ Sí borrar MES para TODOS", type="primary"):
                    for arch in [FILE_STOCK, FILE_REVISION, FILE_DESCARGUES, FILE_DESPACHOS]:
                        if os.path.exists(arch):
                            try:
                                df=pd.read_excel(arch)
                                df["Fecha_dt"]=pd.to_datetime(df["Fecha"], errors='coerce')
                                df=df[df["Fecha_dt"].dt.month!=datetime.now().month]
                                df.to_excel(arch,index=False)
                            except:
                                if os.path.exists(arch): os.remove(arch)
                    st.success("Mes borrado para TODOS")
                    st.session_state["cm"]=False
        with col2:
            if st.button("🗑️ Borrar TODO EL AÑO para TODOS", use_container_width=True):
                st.session_state["ca"]=True
            if st.session_state.get("ca"):
                txt=st.text_input("Escribe BORRAR TODO para confirmar")
                if txt=="BORRAR TODO":
                    if st.button("✅ BORRAR TODO Y ARRANCAR EN CERO", type="primary", use_container_width=True):
                        for arch in [FILE_STOCK, FILE_REVISION, FILE_DESCARGUES, FILE_DESPACHOS, FILE_ARREGLOS]:
                            if os.path.exists(arch): os.remove(arch)
                        for f in glob.glob(f"{CARPETA_FOTOS}/**/*.*", recursive=True):
                            if os.path.isfile(f): os.remove(f)
                        st.success("TODO borrado para TODOS - App liviana")
                        st.balloons()
                        st.session_state["ca"]=False

# ============ OTROS ROLES ============
elif rol=="Secretaria":
    st.title("📝 Secretaria - Foto OPCIONAL")
    with st.form("rev", clear_on_submit=True):
        prod=st.text_input("Producto *")
        c1,c2=st.columns(2)
        with c1: fis=st.number_input("FÍSICO",0,100000,0)
        with c2: sis=st.number_input("SISTEMA",0,100000,0)
        prov=st.selectbox("Proveedor", st.session_state.distribuidores)
        bod=st.selectbox("Bodega", st.session_state.bodegas)
        ven=st.date_input("Vencimiento", value=date.today())
        obs=st.text_area("Observaciones")
        foto=st.file_uploader("📸 Foto OPCIONAL", type=["jpg","jpeg","png"])
        imp=st.checkbox("⭐ IMPORTANTE")
        if fis>0 and fis<=30: st.error(f"BAJITO {fis}")
        if st.form_submit_button("📤 Enviar a Jefa", type="primary", use_container_width=True):
            tf,ruta=guardar_foto_comprimida(foto, imp)
            df=pd.DataFrame([{"Producto":prod,"Cantidad_Fisica":fis,"Cantidad_Sistema":sis,"Error":fis-sis,"Proveedor":prov,"Bodega":bod,"Vencimiento":str(ven),"Observaciones":obs,"Foto":tf,"Ruta_Foto":ruta,"Importante":"SI" if imp else "NO","Fecha":str(date.today())}])
            guardar_excel(FILE_REVISION, df); guardar_excel(FILE_STOCK, df); st.success("Enviado")

elif rol=="Conductor":
    st.title("🚚 Conductor - Firma con el dedo - Foto NO obligatoria")
    try:
        from streamlit_drawable_canvas import st_canvas
        CANVAS_OK=True
    except:
        CANVAS_OK=False
        st.error("Falta librería, agrega streamlit-drawable-canvas a requirements.txt")

    if os.path.exists(FILE_DESPACHOS):
        df=pd.read_excel(FILE_DESPACHOS)
        if "Ruta_Firma" not in df.columns: df["Ruta_Firma"]=""
        if "Firma" not in df.columns: df["Firma"]="NO"
        if "Estado_Check" not in df.columns: df["Estado_Check"]="Pendiente"
        df.to_excel(FILE_DESPACHOS, index=False)

        st.dataframe(df, use_container_width=True)
        idx=st.number_input("Fila de tu despacho (0,1,2...)", 0, len(df)-1, 0)
        st.info(f"Vas a firmar: {df.loc[idx,'Carro']} -> {df.loc[idx,'Destino']} | {df.loc[idx,'Peso']}kg")

        if CANVAS_OK:
            st.subheader("✍️ Firma aquí con el dedo en el cuadro blanco")
            canvas_result = st_canvas(
                fill_color="rgba(255,255,255,0)",
                stroke_width=3,
                stroke_color="#000000",
                background_color="#FFFFFF",
                height=200,
                width=350,
                drawing_mode="freedraw",
                key="firma_canvas",
            )
            col1,col2=st.columns(2)
            with col1:
                if st.button("🗑️ Borrar firma", use_container_width=True):
                    st.rerun()
            with col2:
                if st.button("✅ CONFIRMO Y FIRMO - PESO OK CLIENTES OK", type="primary", use_container_width=True):
                    if canvas_result.image_data is not None and np.mean(canvas_result.image_data[:,:,0:3]) < 250:
                        img = Image.fromarray(canvas_result.image_data.astype(np.uint8))
                        ts=datetime.now().strftime("%Y%m%d_%H%M%S")
                        ruta_firma=f"{CARPETA_FOTOS}/firma_{ts}.png"
                        img.save(ruta_firma)
                        df.loc[idx,"Firma"]="SI"
                        df.loc[idx,"Ruta_Firma"]=ruta_firma
                        df.loc[idx,"Estado_Check"]="FIRMADO"
                        df.to_excel(FILE_DESPACHOS, index=False)
                        st.success("¡FIRMADO! Jefa ya ve tu firma")
                        st.image(ruta_firma, width=300)
                        st.balloons()
                    else:
                        st.error("Firma primero con el dedo en el cuadro blanco")
    else:
        st.warning("No hay despachos aún")

elif rol=="Auxiliar de Bodega":
    st.title("🔧 Auxiliar - Foto OPCIONAL")
    with st.form("aux", clear_on_submit=True):
        bod=st.selectbox("Bodega", st.session_state.bodegas)
        obs=st.text_area("Observaciones")
        foto=st.file_uploader("📸 Foto OPCIONAL", type=["jpg","jpeg","png"])
        imp=st.checkbox("⭐ IMPORTANTE")
        if st.form_submit_button("Guardar", type="primary"):
            tf,ruta=guardar_foto_comprimida(foto, imp)
            df=pd.DataFrame([{"Bodega":bod,"Observaciones":obs,"Foto":tf,"Ruta_Foto":ruta,"Importante":"SI" if imp else "NO","Fecha":str(date.today())}])
            guardar_excel(FILE_ARREGLOS, df); st.success("OK")

elif rol=="Miron":
    st.title("👀 Mirón - Solo vista")
    for f in [FILE_STOCK, FILE_DESCARGUES, FILE_DESPACHOS, FILE_REVISION]:
        if os.path.exists(f):
            st.subheader(f)
            st.dataframe(pd.read_excel(f), use_container_width=True)
