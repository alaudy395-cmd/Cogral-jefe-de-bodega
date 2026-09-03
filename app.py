import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
import os, io, glob, zipfile
import urllib.parse
from PIL import Image

st.set_page_config(page_title="COGRAL - FINAL HOY", layout="wide")

# ============ FOTOS 7 DÍAS + COMPRIMIDAS 300KB ============
CARPETA_FOTOS = "fotos"
os.makedirs(CARPETA_FOTOS, exist_ok=True)
os.makedirs(f"{CARPETA_FOTOS}/importantes", exist_ok=True)

def guardar_foto_comprimida(archivo, es_importante=False):
    if not archivo:
        return "NO", ""
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
    borradas=0
    for f in glob.glob(f"{CARPETA_FOTOS}/*.*"):
        if os.path.isfile(f) and datetime.fromtimestamp(os.path.getmtime(f)) < limite:
            os.remove(f); borradas+=1
    return borradas

def crear_zip_todo():
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        for a in ["stock.xlsx","revision.xlsx","descargues.xlsx","despachos.xlsx","arreglos.xlsx"]:
            if os.path.exists(a): z.write(a)
        for f in glob.glob(f"{CARPETA_FOTOS}/importantes/*.*"):
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

# ============ INICIO DE SESIÓN ARREGLADO ============
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
                st.session_state.login=True
                st.session_state.rol=USUARIOS[u]["rol"]
                st.session_state.usuario=u
                st.session_state.nombre=USUARIOS[u]["nombre"]
                st.rerun()
            else: st.error("Usuario o clave mala")
    st.stop()

rol=st.session_state.rol; nombre=st.session_state.nombre
st.sidebar.write(f"👤 {nombre} - {rol}")
if st.sidebar.button("Cerrar sesión"): st.session_state.login=False; st.rerun()
if rol=="Jefe de Bodega" and st.sidebar.button("🧹 Limpiar fotos >7 días"): b=limpiar_fotos_7dias(); st.sidebar.success(f"Borradas {b}")

MUNICIPIOS=["Tunja","Almeida","Aquitania","Arcabuco","Belen","Berbeo","Beteitiva","Boavita","Boyaca","Briceño","Buenavista","Busbanza","Caldas","Campohermoso","Cerinza","Chinavita","Chiquinquira","Chiscas","Chita","Chitaraque","Chivata","Chivor","Cienega","Combita","Coper","Corrales","Covarachia","Cubara","Cucaita","Cuitiva","Duitama","El Cocuy","El Espino","Firavitoba","Floresta","Gachantiva","Gameza","Garagoa","Guacamayas","Guateque","Guayata","Guican","Iza","Jenesano","Jerico","La Capilla","La Uvita","La Victoria","Labranzagrande","Macanal","Maripi","Miraflores","Mongua","Mongui","Moniquira","Motavita","Muzo","Nobsa","Nuevo Colon","Oicata","Otanche","Pachavita","Paez","Paipa","Pajarito","Panqueba","Pauna","Paya","Paz de Rio","Pesca","Pisba","Puerto Boyaca","Quipama","Ramiriqui","Raquira","Rondon","Saboya","Sachica","Samaca","San Eduardo","San Jose de Pare","San Luis de Gaceno","San Mateo","San Miguel de Sema","San Pablo de Borbur","Santa Maria","Santa Rosa de Viterbo","Santa Sofia","Santana","Sativanorte","Sativasur","Siachoque","Soata","Socha","Socota","Sogamoso","Somondoco","Sora","Soraca","Sotaquira","Susacon","Sutamarchan","Sutatenza","Tasco","Tenza","Tibana","Tibasosa","Tinjaca","Tipacoque","Toca","Togui","Topaga","Tota","Tunungua","Turmeque","Tuta","Tutaza","Umbita","Ventaquemada","Villa de Leyva","Viracacha","Zetaquira"]

# ============ PANELES ============
if rol=="Jefe de Bodega":
    st.title(f"Bienvenida {nombre} 👑 - Versión Final Hoy")
    t1,t2,t3,t4,t6,t7,t5=st.tabs(["📦 STOCK","📥 DESCARGUES","🚚 DESPACHOS","🔍 REVISIONES","📊 INFORMES","🗃️ BORRAR/CERO","🔧 AUX"])

    with t1:
        st.subheader("📦 STOCK - Producto, Físico, Sistema, Proveedor, Vencimiento, Bodega")
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
            imp=st.checkbox("⭐ MARCAR IMPORTANTE - No se borra a los 7 días")
            if fis>0 and fis<=30: st.error(f"⚠️ ALERTA BAJITO: Solo {fis} unidades")
            if st.form_submit_button("💾 GUARDAR STOCK", type="primary", use_container_width=True):
                if not prod: st.error("Falta producto")
                else:
                    tf, ruta=guardar_foto_comprimida(foto, imp)
                    err=fis-sis
                    df=pd.DataFrame([{"Producto":prod,"Cantidad_Fisica":fis,"Cantidad_Sistema":sis,"Error":err,"Proveedor":prov,"Bodega":bod,"Vencimiento":str(ven),"Observaciones":obs,"Foto":tf,"Ruta_Foto":ruta,"Importante":"SI" if imp else "NO","Estado":"Pendiente" if err!=0 or fis<=30 else "OK","Alerta_Bajo":"SI" if fis<=30 else "NO","Fecha":str(date.today()),"Borra_en": str(date.today()+timedelta(days=7)) if not imp else "NUNCA - Importante"}])
                    guardar_excel(FILE_STOCK, df); guardar_excel(FILE_REVISION, df); st.success(f"Guardado {ruta}"); st.balloons()
        if os.path.exists(FILE_STOCK): st.dataframe(pd.read_excel(FILE_STOCK), use_container_width=True)

    with t2:
        st.subheader("📥 DESCARGUES - Nombre, Tipo, Peso, Proveedor")
        with st.form("desc", clear_on_submit=True):
            nd=st.text_input("Nombre Descargue *")
            c1,c2=st.columns(2)
            with c1: tipo=st.selectbox("Tipo",["Sencillo","Mula"])
            with c2: peso=st.number_input("Peso kg 1-40000",1,40000,1000); st.caption(f"{peso/1000:.2f} toneladas")
            prov=st.selectbox("Proveedor", st.session_state.distribuidores, key="pd")
            cond=st.text_input("Conductor")
            foto=st.file_uploader("📸 Foto (comprimida)", type=["jpg","png","jpeg"], key="fd")
            imp=st.checkbox("⭐ IMPORTANTE - No borrar", key="imp_d")
            if st.form_submit_button("Guardar Descargue", type="primary", use_container_width=True):
                tf,ruta=guardar_foto_comprimida(foto, imp)
                df=pd.DataFrame([{"Nombre_Descargue":nd,"Tipo":tipo,"Peso":peso,"Toneladas":peso/1000,"Proveedor":prov,"Conductor":cond,"Foto":tf,"Ruta_Foto":ruta,"Importante":"SI" if imp else "NO","Fecha":str(date.today()),"Borra_en": str(date.today()+timedelta(days=7)) if not imp else "NUNCA"}])
                guardar_excel(FILE_DESCARGUES, df); st.success("Guardado")

    with t3:
        st.subheader("🚚 DESPACHOS Furgones - Sin distribuidor, con municipios, con WhatsApp")
        with st.form("desp", clear_on_submit=True):
            carro=st.selectbox("Carro furgón",["NK 482","NK 866","NL 288","Otro"])
            dest=st.selectbox("Destino Boyacá", MUNICIPIOS)
            c1,c2=st.columns(2)
            with c1: peso=st.number_input("Peso kg 1-10000",1,10000,1000)
            with c2: cli=st.number_input("No. Clientes 1-100",1,100,1)
            prods=st.text_area("Productos que lleva *")
            foto=st.file_uploader("📸 Foto furgón OBLIGATORIA (se comprime)", type=["jpg","png","jpeg"], key="fdf")
            nom=st.text_input("Nombre conductor"); tel=st.text_input("WhatsApp conductor 57... Ej 573001234567")
            imp=st.checkbox("⭐ IMPORTANTE - No borrar")
            if st.form_submit_button("💾 DESPACHAR", type="primary", use_container_width=True):
                if not prods: st.error("Falta productos")
                elif not foto: st.error("Foto obligatoria")
                elif not tel: st.error("Falta WhatsApp")
                else:
                    tf,ruta=guardar_foto_comprimida(foto, imp)
                    df=pd.DataFrame([{"Carro":carro,"Destino":dest,"Peso":peso,"Clientes":cli,"Productos":prods,"Foto":tf,"Ruta_Foto":ruta,"Importante":"SI" if imp else "NO","Nombre_Conductor":nom,"WhatsApp":tel,"Estado_Check":"Pendiente conductor","Fecha":str(date.today()),"Hora":datetime.now().strftime("%H:%M"),"Borra_en": str(date.today()+timedelta(days=7)) if not imp else "NUNCA"}])
                    guardar_excel(FILE_DESPACHOS, df); st.session_state["ult"]={"carro":carro,"dest":dest,"peso":peso,"cli":cli,"prods":prods,"nom":nom,"tel":tel}; st.success("Despachado"); st.balloons()
        if "ult" in st.session_state and st.session_state["ult"]:
            d=st.session_state["ult"]; st.divider(); st.subheader("📲 BOTÓN WHATSAPP - El conductor da el OK")
            mensaje=f"🚚 *COGRAL - DESPACHO*\n*Carro:* {d['carro']}\n*Destino:* {d['dest']}\n*Peso:* {d['peso']} kg\n*Clientes:* {d['cli']}\n*Productos:* {d['prods']}\n*Conductor:* {d['nom']}\n\nConfirma:\n✅ PESO OK\n✅ CLIENTES OK\n✅ RECIBI COMPLETO\n\nResponde: *CONFIRMO*"
            link=f"https://wa.me/{d['tel']}?text={urllib.parse.quote(mensaje)}"
            st.link_button(f"📲 ENVIAR WHATSAPP A {d['nom']} - {d['tel']}", link, type="primary", use_container_width=True)
        if os.path.exists(FILE_DESPACHOS): st.dataframe(pd.read_excel(FILE_DESPACHOS), use_container_width=True)

    with t4:
        if os.path.exists(FILE_REVISION): st.subheader("🔍 Revisiones"); st.dataframe(pd.read_excel(FILE_REVISION), use_container_width=True)

    with t6:
        st.title("📊 INFORMES - Lo que más te importa Jefa")
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
            st.subheader("📦 Inventario Semana"); m1,m2,m3,m4=st.columns(4); m1.metric("Revisados", total); m2.metric("Con Error", con_err); m3.metric("Bien", bien); m4.metric("Bajitos", bajos)
            st.write(f"En la semana se revisaron {total} productos, {con_err} con error, {bien} bien")
            if not dff.empty: st.dataframe(dff, use_container_width=True); st.download_button("📥 Exportar Inventario", to_excel_download(dff), f"informe_inv_{fi}_{ff}.xlsx")
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
                st.write("Ejemplo: Salió a Duitama tantas veces con tanto peso y tantos clientes")
                st.dataframe(res, use_container_width=True); st.bar_chart(res.set_index("Destino")["Veces"])
                st.download_button("📥 Exportar Despachos", to_excel_download(dff), f"informe_desp_{fi}_{ff}.xlsx")
        if os.path.exists(FILE_DESCARGUES):
            st.divider(); st.subheader("📥 Descargues Toneladas")
            df=pd.read_excel(FILE_DESCARGUES); st.dataframe(df, use_container_width=True); st.download_button("📥 Exportar Descargues", to_excel_download(df), "informe_desc.xlsx")

    with t7:
        st.title("🗃️ BORRAR / CERO - Para TODOS")
        st.warning("Lo que borres aquí se borra para SECRETARIA, AUXILIAR, MIRON, CONDUCTOR. Todos en cero. Exporta primero.")
        if st.button("📦 EXPORTAR TODO EN ZIP - Respaldo Año/Mes", type="primary", use_container_width=True):
            z=crear_zip_todo(); st.download_button("⬇️ DESCARGAR ZIP FINAL", z, f"COGRAL_RESPALDO_{date.today()}.zip", "application/zip", use_container_width=True)
        st.divider()
        col1,col2=st.columns(2)
        with col1:
            if st.button("🗑️ Borrar MES actual para TODOS", use_container_width=True): st.session_state["cm"]=True
            if st.session_state.get("cm"):
                if st.button("✅ Sí borrar MES para todos", type="primary"):
                    for arch in [FILE_STOCK, FILE_REVISION, FILE_DESCARGUES, FILE_DESPACHOS]:
                        if os.path.exists(arch):
                            try:
                                df=pd.read_excel(arch); df["Fecha_dt"]=pd.to_datetime(df["Fecha"], errors='coerce')
                                df=df[df["Fecha_dt"].dt.month!=datetime.now().month]; df.to_excel(arch,index=False)
                            except:
                                if os.path.exists(arch): os.remove(arch)
                    st.success("Mes borrado para TODOS"); st.balloons(); st.session_state["cm"]=False
        with col2:
            if st.button("🗑️ Borrar TODO EL AÑO para TODOS", use_container_width=True): st.session_state["ca"]=True
            if st.session_state.get("ca"):
                txt=st.text_input("Escribe BORRAR TODO para confirmar")
                if txt=="BORRAR TODO" and st.button("✅ BORRAR TODO Y ARRANCAR EN CERO", type="primary", use_container_width=True):
                    for arch in [FILE_STOCK, FILE_REVISION, FILE_DESCARGUES, FILE_DESPACHOS, FILE_ARREGLOS]:
                        if os.path.exists(arch): os.remove(arch)
                    for f in glob.glob(f"{CARPETA_FOTOS}/*.*"):
                        if os.path.isfile(f): os.remove(f)
                    for f in glob.glob(f"{CARPETA_FOTOS}/importantes/*.*"):
                        if os.path.isfile(f): os.remove(f)
                    st.success("TODO borrado para TODOS - App no se llena"); st.balloons(); st.session_state["ca"]=False

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
    st.title("🚚 Conductor");
    if os.path.exists(FILE_DESPACHOS):
        df=pd.read_excel(FILE_DESPACHOS); st.dataframe(df, use_container_width=True)
        idx=st.number_input("Fila despacho",0,len(df)-1,0)
        c1,c2=st.columns(2)
        if c1.button("✅ PESO OK", use_container_width=True): df.loc[idx,"Estado_Check"]="Peso OK"; df.to_excel(FILE_DESPACHOS,index=False); st.success("Peso OK")
        if c2.button("✅ CLIENTES OK", use_container_width=True): df.loc[idx,"Estado_Check"]="Clientes OK"; df.to_excel(FILE_DESPACHOS,index=False); st.success("Clientes OK")
        if st.button("✅ CONFIRMO TODO", type="primary", use_container_width=True): df.loc[idx,"Estado_Check"]="CONFIRMADO TODO"; df.to_excel(FILE_DESPACHOS,index=False); st.success("Confirmado"); st.balloons()

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
    st.title("👀 Mirón - Solo vista")
    for f in [FILE_STOCK, FILE_DESCARGUES, FILE_DESPACHOS, FILE_REVISION]:
        if os.path.exists(f): st.subheader(f); st.dataframe(pd.read_excel(f))
