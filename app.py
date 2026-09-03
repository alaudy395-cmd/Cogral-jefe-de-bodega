import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
import os, io, glob, zipfile
from PIL import Image
import numpy as np

st.set_page_config(page_title="COGRAL - FIRMA", layout="wide")

# ============ FOTOS 7 DÍAS + COMPRIMIDAS 300KB ============
CARPETA_FOTOS = "fotos"
os.makedirs(CARPETA_FOTOS, exist_ok=True)
os.makedirs(f"{CARPETA_FOTOS}/importantes", exist_ok=True)

def guardar_foto_comprimida(archivo, es_importante=False):
    if not archivo: return "NO", ""
    try:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        carpeta = f"{CARPETA_FOTOS}/importantes" if es_importante else CARPETA_FOTOS
        nombre = f"{ts}_{archivo.name.rsplit('.',1)[0][:20]}.jpg"
        ruta = os.path.join(carpeta, nombre)
        img = Image.open(archivo)
        if img.mode in ("RGBA","P","LA"): img = img.convert("RGB")
        img.thumbnail((1024,1024))
        img.save(ruta, "JPEG", optimize=True, quality=50)
        kb = os.path.getsize(ruta)/1024
        return "SI", f"{ruta} ({kb:.0f}KB)"
    except:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        carpeta = f"{CARPETA_FOTOS}/importantes" if es_importante else CARPETA_FOTOS
        ruta = os.path.join(carpeta, f"{ts}_{archivo.name}")
        with open(ruta,"wb") as f: f.write(archivo.getbuffer())
        return "SI", ruta

def limpiar_fotos_7dias():
    limite = datetime.now() - timedelta(days=7)
    b=0
    for f in glob.glob(f"{CARPETA_FOTOS}/*.*"):
        if os.path.isfile(f) and datetime.fromtimestamp(os.path.getmtime(f)) < limite:
            os.remove(f); b+=1
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
            final=pd.concat([old, df_new], ignore_index=True)
        except: final=df_new
    else: final=df_new
    final.to_excel(archivo,index=False)

def to_excel_download(df):
    out=io.BytesIO()
    with pd.ExcelWriter(out, engine='openpyxl') as w: df.to_excel(w,index=False)
    return out.getvalue()

if "limpieza_hecha" not in st.session_state:
    limpiar_fotos_7dias()
    st.session_state.limpieza_hecha=True

# ============ LOGIN SIN CLAVES VISIBLES ============
USUARIOS = {
    "tatiana": {"clave":"cogral2026","rol":"Jefe de Bodega","nombre":"Tatiana - Jefa"},
    "secretaria": {"clave":"secre123","rol":"Secretaria","nombre":"Secretaria"},
    "auxiliar": {"clave":"aux123","rol":"Auxiliar de Bodega","nombre":"Auxiliar"},
    "miron": {"clave":"miron123","rol":"Miron","nombre":"Mirón"},
    "conductor": {"clave":"cond123","rol":"Conductor","nombre":"Conductor"},
}
if "bodegas" not in st.session_state: st.session_state.bodegas=["Bodega 1","Bodega 2","Bodega 3","Bodega Principal"]
if "distribuidores" not in st.session_state: st.session_state.distribuidores=["Agrosur","Cogral","Ferreteria Central","Coagronorte","Urea Dist"]

FILE_STOCK="stock.xlsx"; FILE_REVISION="revision.xlsx"; FILE_DESCARGUES="descargues.xlsx"; FILE_DESPACHOS="despachos.xlsx"; FILE_ARREGLOS="arreglos.xlsx"

if "login" not in st.session_state: st.session_state.login=False
if not st.session_state.login:
    st.title("🏭 COGRAL - Ingreso")
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        u=st.text_input("Usuario")
        p=st.text_input("Clave", type="password")
        if st.button("Entrar", type="primary", use_container_width=True):
            if u in USUARIOS and USUARIOS[u]["clave"]==p:
                st.session_state.login=True; st.session_state.rol=USUARIOS[u]["rol"]; st.session_state.usuario=u; st.session_state.nombre=USUARIOS[u]["nombre"]; st.rerun()
            else: st.error("Usuario o clave incorrecta")
    st.stop()

rol=st.session_state.rol; nombre=st.session_state.nombre
st.sidebar.write(f"👤 {nombre} - {rol}")
if st.sidebar.button("Cerrar sesión"): st.session_state.login=False; st.rerun()
if rol=="Jefe de Bodega" and st.sidebar.button("🧹 Limpiar fotos >7 días"): b=limpiar_fotos_7dias(); st.sidebar.success(f"Borradas {b}")

MUNICIPIOS=["Tunja","Almeida","Aquitania","Arcabuco","Belen","Berbeo","Beteitiva","Boavita","Boyaca","Briceño","Buenavista","Busbanza","Caldas","Campohermoso","Cerinza","Chinavita","Chiquinquira","Chiscas","Chita","Chitaraque","Chivata","Chivor","Cienega","Combita","Coper","Corrales","Covarachia","Cubara","Cucaita","Cuitiva","Duitama","El Cocuy","El Espino","Firavitoba","Floresta","Gachantiva","Gameza","Garagoa","Guacamayas","Guateque","Guayata","Guican","Iza","Jenesano","Jerico","La Capilla","La Uvita","La Victoria","Labranzagrande","Macanal","Maripi","Miraflores","Mongua","Mongui","Moniquira","Motavita","Muzo","Nobsa","Nuevo Colon","Oicata","Otanche","Pachavita","Paez","Paipa","Pajarito","Panqueba","Pauna","Paya","Paz de Rio","Pesca","Pisba","Puerto Boyaca","Quipama","Ramiriqui","Raquira","Rondon","Saboya","Sachica","Samaca","San Eduardo","San Jose de Pare","San Luis de Gaceno","San Mateo","San Miguel de Sema","San Pablo de Borbur","Santa Maria","Santa Rosa de Viterbo","Santa Sofia","Santana","Sativanorte","Sativasur","Siachoque","Soata","Socha","Socota","Sogamoso","Somondoco","Sora","Soraca","Sotaquira","Susacon","Sutamarchan","Sutatenza","Tasco","Tenza","Tibana","Tibasosa","Tinjaca","Tipacoque","Toca","Togui","Topaga","Tota","Tunungua","Turmeque","Tuta","Tutaza","Umbita","Ventaquemada","Villa de Leyva","Viracacha","Zetaquira"]

# ============ PANEL JEFA ============
if rol=="Jefe de Bodega":
    st.title(f"Bienvenida {nombre} 👑 - Con Firma")
    t1,t2,t3,t4,t6,t7,t5=st.tabs(["📦 STOCK","📥 DESCARGUES","🚚 DESPACHOS","🔍 REVISIONES","📊 INFORMES","🗃️ BORRAR/CERO","🔧 AUX"])

    with t1:
        st.subheader("📦 STOCK - Producto, Físico, Sistema, Proveedor, Vencimiento, Bodega - Foto 300KB")
        with st.form("stock", clear_on_submit=True):
            prod=st.text_input("Producto *")
            c1,c2=st.columns(2)
            with c1: fis=st.number_input("Cantidad FÍSICO",0,100000,0)
            with c2: sis=st.number_input("Cantidad SISTEMA",0,100000,0)
            prov=st.selectbox("Proveedor", st.session_state.distribuidores)
            nuevo=st.text_input("Nuevo proveedor? Escríbelo")
            if nuevo: prov=nuevo
            if nuevo and nuevo not in st.session_state.distribuidores: st.session_state.distribuidores.append(nuevo)
            c3,c4=st.columns(2)
            with c3: bod=st.selectbox("Bodega", st.session_state.bodegas)
            with c4: ven=st.date_input("Fecha Vencimiento", value=date.today())
            obs=st.text_area("Observaciones")
            foto=st.file_uploader("📸 Foto (se comprime a 300KB auto)", type=["jpg","png","jpeg"])
            imp=st.checkbox("⭐ IMPORTANTE - No se borra a los 7 días")
            if fis>0 and fis<=30: st.error(f"⚠️ BAJITO: Solo {fis}")
            if st.form_submit_button("💾 GUARDAR STOCK", type="primary", use_container_width=True):
                if not prod: st.error("Falta producto")
                else:
                    tf, ruta=guardar_foto_comprimida(foto, imp)
                    err=fis-sis
                    df=pd.DataFrame([{"Producto":prod,"Cantidad_Fisica":fis,"Cantidad_Sistema":sis,"Error":err,"Proveedor":prov,"Bodega":bod,"Vencimiento":str(ven),"Observaciones":obs,"Foto":tf,"Ruta_Foto":ruta,"Importante":"SI" if imp else "NO","Estado":"Pendiente" if err!=0 or fis<=30 else "OK","Alerta_Bajo":"SI" if fis<=30 else "NO","Fecha":str(date.today()),"Borra_en": str(date.today()+timedelta(days=7)) if not imp else "NUNCA"}])
                    guardar_excel(FILE_STOCK, df); guardar_excel(FILE_REVISION, df); st.success(f"Guardado {ruta}"); st.balloons()
        if os.path.exists(FILE_STOCK): st.dataframe(pd.read_excel(FILE_STOCK), use_container_width=True)

    with t2:
        st.subheader("📥 DESCARGUES - Nombre, Tipo Sencillo/Mula, Peso 1-40000, Toneladas, Proveedor")
        with st.form("desc", clear_on_submit=True):
            nd=st.text_input("Nombre Descargue *")
            c1,c2=st.columns(2)
            with c1: tipo=st.selectbox("Tipo",["Sencillo","Mula"])
            with c2: peso=st.number_input("Peso kg 1-40000",1,40000,1000); st.caption(f"{peso/1000:.2f} toneladas")
            prov=st.selectbox("Proveedor", st.session_state.distribuidores, key="pd")
            cond=st.text_input("Conductor")
            foto=st.file_uploader("📸 Foto (comprimida)", type=["jpg","png","jpeg"], key="fd")
            imp=st.checkbox("⭐ IMPORTANTE", key="imp_d")
            if st.form_submit_button("Guardar Descargue", type="primary", use_container_width=True):
                tf,ruta=guardar_foto_comprimida(foto, imp)
                df=pd.DataFrame([{"Nombre_Descargue":nd,"Tipo":tipo,"Peso":peso,"Toneladas":peso/1000,"Proveedor":prov,"Conductor":cond,"Foto":tf,"Ruta_Foto":ruta,"Importante":"SI" if imp else "NO","Fecha":str(date.today())}])
                guardar_excel(FILE_DESCARGUES, df); st.success("Guardado")

    with t3:
        st.subheader("🚚 DESPACHOS - Con firma del conductor")
        with st.form("desp", clear_on_submit=True):
            carro=st.selectbox("Carro furgón",["NK 482","NK 866","NL 288","Otro"])
            dest=st.selectbox("Destino Boyacá", MUNICIPIOS)
            c1,c2=st.columns(2)
            with c1: peso=st.number_input("Peso kg 1-10000",1,10000,1000)
            with c2: cli=st.number_input("No. Clientes 1-100",1,100,1)
            prods=st.text_area("Productos que lleva *")
            foto=st.file_uploader("📸 Foto furgón OBLIGATORIA", type=["jpg","png","jpeg"], key="fdf")
            nom=st.text_input("Nombre conductor")
            imp=st.checkbox("⭐ IMPORTANTE")
            if st.form_submit_button("💾 DESPACHAR - Conductor firmará en su celular", type="primary", use_container_width=True):
                if not foto: st.error("Foto obligatoria")
                else:
                    tf,ruta=guardar_foto_comprimida(foto, imp)
                    df=pd.DataFrame([{"Carro":carro,"Destino":dest,"Peso":peso,"Clientes":cli,"Productos":prods,"Foto":tf,"Ruta_Foto":ruta,"Importante":"SI" if imp else "NO","Nombre_Conductor":nom,"Firma":"NO","Ruta_Firma":"","Estado_Check":"Pendiente firma conductor","Fecha":str(date.today()),"Hora":datetime.now().strftime("%H:%M")}])
                    guardar_excel(FILE_DESPACHOS, df); st.success("Despachado - Conductor debe firmar"); st.balloons()
        if os.path.exists(FILE_DESPACHOS):
            df=pd.read_excel(FILE_DESPACHOS)
            st.dataframe(df, use_container_width=True)
            # Mostrar firmas
            if "Ruta_Firma" in df.columns:
                for i,row in df.iterrows():
                    if row["Ruta_Firma"] and os.path.exists(str(row["Ruta_Firma"])):
                        st.write(f"Firma {row['Nombre_Conductor']} - {row['Destino']}")
                        st.image(str(row["Ruta_Firma"]), width=200)

    with t4:
        if os.path.exists(FILE_REVISION): st.dataframe(pd.read_excel(FILE_REVISION), use_container_width=True)

    with t6:
        st.title("📊 INFORMES")
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
            total=len(dff); con_err=len(dff[dff["Error"]!=0]) if "Error" in dff.columns and not dff.empty else 0; bien=total-con_err; bajos=len(dff[dff["Cantidad_Fisica"]<=30]) if "Cantidad_Fisica" in dff.columns and not dff.empty else 0
            m1,m2,m3,m4=st.columns(4); m1.metric("Revisados", total); m2.metric("Con Error", con_err); m3.metric("Bien", bien); m4.metric("Bajitos", bajos)
            if not dff.empty: st.dataframe(dff, use_container_width=True); st.download_button("📥 Exportar", to_excel_download(dff), f"informe_{fi}_{ff}.xlsx")
        if os.path.exists(FILE_DESPACHOS):
            st.divider(); st.subheader("🚚 Carros por Municipio")
            df=pd.read_excel(FILE_DESPACHOS)
            try:
                df["Fecha_dt"]=pd.to_datetime(df["Fecha"], errors='coerce')
                mask=(df["Fecha_dt"]>=pd.to_datetime(fi)) & (df["Fecha_dt"]<=pd.to_datetime(ff))
                dff=df[mask]
            except: dff=df
            if not dff.empty:
                res=dff.groupby("Destino").agg(Veces=("Destino","count"), Peso_Total=("Peso","sum"), Clientes_Total=("Clientes","sum")).reset_index().sort_values("Veces", ascending=False)
                st.dataframe(res, use_container_width=True); st.bar_chart(res.set_index("Destino")["Veces"])

    with t7:
        st.title("🗃️ BORRAR / CERO - Para TODOS - App nunca se llena")
        if st.button("📦 EXPORTAR TODO EN ZIP", type="primary", use_container_width=True):
            z=crear_zip_todo(); st.download_button("⬇️ DESCARGAR ZIP", z, f"COGRAL_{date.today()}.zip", "application/zip", use_container_width=True)
        st.divider()
        col1,col2=st.columns(2)
        with col1:
            if st.button("🗑️ Borrar MES para TODOS", use_container_width=True): st.session_state["cm"]=True
            if st.session_state.get("cm") and st.button("✅ Sí borrar MES", type="primary"):
                for arch in [FILE_STOCK, FILE_REVISION, FILE_DESCARGUES, FILE_DESPACHOS]:
                    if os.path.exists(arch):
                        try:
                            df=pd.read_excel(arch); df["Fecha_dt"]=pd.to_datetime(df["Fecha"], errors='coerce')
                            df=df[df["Fecha_dt"].dt.month!=datetime.now().month]; df.to_excel(arch,index=False)
                        except:
                            if os.path.exists(arch): os.remove(arch)
                st.success("Mes borrado para TODOS"); st.session_state["cm"]=False
        with col2:
            if st.button("🗑️ Borrar TODO AÑO para TODOS", use_container_width=True): st.session_state["ca"]=True
            if st.session_state.get("ca"):
                txt=st.text_input("Escribe BORRAR TODO")
                if txt=="BORRAR TODO" and st.button("✅ BORRAR TODO", type="primary", use_container_width=True):
                    for arch in [FILE_STOCK, FILE_REVISION, FILE_DESCARGUES, FILE_DESPACHOS, FILE_ARREGLOS]:
                        if os.path.exists(arch): os.remove(arch)
                    for f in glob.glob(f"{CARPETA_FOTOS}/**/*.*", recursive=True):
                        if os.path.isfile(f): os.remove(f)
                    st.success("TODO borrado"); st.balloons(); st.session_state["ca"]=False

    with t5:
        if os.path.exists(FILE_ARREGLOS): st.dataframe(pd.read_excel(FILE_ARREGLOS))

elif rol=="Secretaria":
    st.title("📝 Secretaria")
    with st.form("rev", clear_on_submit=True):
        prod=st.text_input("Producto *"); c1,c2=st.columns(2)
        with c1: fis=st.number_input("FÍSICO",0,100000,0)
        with c2: sis=st.number_input("SISTEMA",0,100000,0)
        prov=st.selectbox("Proveedor", st.session_state.distribuidores); ven=st.date_input("Vencimiento", value=date.today())
        bod=st.selectbox("Bodega", st.session_state.bodegas); obs=st.text_area("Observaciones")
        foto=st.file_uploader("📸 Foto", type=["jpg","png","jpeg"]); imp=st.checkbox("⭐ IMPORTANTE")
        if fis>0 and fis<=30: st.error(f"BAJITO {fis}")
        if st.form_submit_button("📤 Enviar a Jefa", type="primary", use_container_width=True):
            tf,ruta=guardar_foto_comprimida(foto, imp)
            df=pd.DataFrame([{"Producto":prod,"Cantidad_Fisica":fis,"Cantidad_Sistema":sis,"Error":fis-sis,"Proveedor":prov,"Bodega":bod,"Vencimiento":str(ven),"Observaciones":obs,"Foto":tf,"Ruta_Foto":ruta,"Importante":"SI" if imp else "NO","Fecha":str(date.today())}])
            guardar_excel(FILE_REVISION, df); guardar_excel(FILE_STOCK, df); st.success("Enviado")

elif rol=="Conductor":
    st.title("🚚 Conductor - Firma aquí con el dedo")
    try:
        from streamlit_drawable_canvas import st_canvas
        CANVAS_OK=True
    except:
        CANVAS_OK=False
        st.error("Instala requirements.txt con streamlit-drawable-canvas")

    if os.path.exists(FILE_DESPACHOS):
        df=pd.read_excel(FILE_DESPACHOS)
        pendientes = df[df["Estado_Check"]!="FIRMADO"] if "Estado_Check" in df.columns else df
        st.write(f"Tienes {len(pendientes)} despachos pendientes")
        st.dataframe(pendientes, use_container_width=True)
        idx=st.number_input("Fila de tu despacho (0,1,2...)", 0, len(df)-1, 0)
        st.info(f"Firma: {df.loc[idx,'Carro']} -> {df.loc[idx,'Destino']} | {df.loc[idx,'Peso']}kg | {df.loc[idx,'Productos']}")

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
                    if canvas_result.image_data is not None:
                        # Guardar firma como imagen
                        img_data = canvas_result.image_data.astype(np.uint8)
                        # Verificar que no esté vacío (todo blanco)
                        if np.mean(img_data[:,:,0:3]) < 250:
                            img = Image.fromarray(img_data)
                            ts=datetime.now().strftime("%Y%m%d_%H%M%S")
                            ruta_firma=f"{CARPETA_FOTOS}/firma_{ts}.png"
                            img.save(ruta_firma)
                            df.loc[idx,"Firma"]="SI"
                            df.loc[idx,"Ruta_Firma"]=ruta_firma
                            df.loc[idx,"Estado_Check"]="FIRMADO"
                            df.loc[idx,"Fecha_Firma"]=str(date.today())
                            df.to_excel(FILE_DESPACHOS, index=False)
                            st.success("¡FIRMADO! Jefa ya ve tu firma")
                            st.image(ruta_firma, width=300)
                            st.balloons()
                        else: st.error("Firma primero con el dedo en el cuadro blanco")
                    else: st.error("Dibuja tu firma")
        else:
            foto_firma=st.file_uploader("📸 Foto de firma / huella", type=["jpg","png","jpeg"])
            if st.button("✅ CONFIRMO CON FOTO", type="primary", use_container_width=True):
                if foto_firma:
                    tf,ruta=guardar_foto_comprimida(foto_firma, True)
                    df.loc[idx,"Firma"]="SI"; df.loc[idx,"Ruta_Firma"]=ruta; df.loc[idx,"Estado_Check"]="FIRMADO"
                    df.to_excel(FILE_DESPACHOS, index=False); st.success("Firmado")
                else: st.error("Sube foto")

elif rol=="Auxiliar de Bodega":
    st.title("🔧 Auxiliar")
    with st.form("aux", clear_on_submit=True):
        bod=st.selectbox("Bodega", st.session_state.bodegas); obs=st.text_area("Observaciones")
        foto=st.file_uploader("📸 Foto", type=["jpg","png","jpeg"]); imp=st.checkbox("⭐ IMPORTANTE")
        if st.form_submit_button("Guardar", type="primary"):
            tf,ruta=guardar_foto_comprimida(foto, imp)
            df=pd.DataFrame([{"Bodega":bod,"Observaciones":obs,"Foto":tf,"Ruta_Foto":ruta,"Importante":"SI" if imp else "NO","Fecha":str(date.today())}])
            guardar_excel(FILE_ARREGLOS, df); st.success("OK")

elif rol=="Miron":
    st.title("👀 Mirón")
    for f in [FILE_STOCK, FILE_DESCARGUES, FILE_DESPACHOS, FILE_REVISION]:
        if os.path.exists(f): st.subheader(f); st.dataframe(pd.read_excel(f))
