import streamlit as st
import math
from datetime import date, timedelta
from fpdf import FPDF
import pandas as pd

# ==============================
# 0. CONFIGURACIÓN DE PÁGINA Y ESTILOS
# ==============================
st.set_page_config(page_title="Calculadora Pediátrica", page_icon="💊")

st.markdown("""
<style>
    body {
        background-color: #FFF0F5;
    }
    .main-title {
        font-size: 48px;
        text-align: center;
        color: #FF1493;
        font-family: 'Brush Script MT', cursive;
        margin-bottom: 0px;
    }
    .sub-title {
        text-align: center;
        color: #8B008B;
        font-size: 22px;
        margin-top: -15px;
    }
    .result-box {
        background: #FFFFFF;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 6px 12px rgba(255,105,180,0.3);
        border-left: 8px solid #FFB6C1;
    }
    .stButton > button {
        background-color: #FF69B4;
        color: white;
        border-radius: 30px;
        padding: 12px 30px;
        font-size: 18px;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton > button:hover {
        background-color: #FF1493;
    }
    .red-label {
        color: red;
        font-weight: bold;
    }
    .alerta-adulto {
        background-color: #FFC0CB;
        color: darkred;
        padding: 15px;
        border-radius: 12px;
        font-weight: bold;
        border: 2px solid red;
    }
</style>
""", unsafe_allow_html=True)

# ==============================
# 1. BASE DE DATOS DE MEDICAMENTOS
# ==============================
DB_MEDICAMENTOS = {
    # FAVORITOS
    "Amoxicilina": {
        "tipo": "mgkgdia", "dosis": 50, "dosis_max_dia": 90,
        "frecuencias": [8,12], "categoria": "Antibiótico"
    },
    "Paracetamol": {
        "tipo": "mgkgdosis", "dosis": 15, "dosis_max_toma": 15, "dosis_max_dia": 75,
        "frecuencias": [6,8], "categoria": "Analgésico/Antipirético"
    },
    "Ibuprofeno": {
        "tipo": "mgkgdosis", "dosis": 10, "dosis_max_toma": 10, "dosis_max_dia": 40,
        "frecuencias": [6,8], "categoria": "Analgésico/Antipirético"
    },
    "Azitromicina": {
        "tipo": "mgkgdia", "dosis": 10, "dosis_max_dia": 10,
        "frecuencias": [24], "categoria": "Antibiótico"
    },
    "Clorfenamina": {
        "tipo": "edad", "por_edad": {(0,1):1.0, (2,5):2.0, (6,11):4.0},
        "frecuencias": [6,8], "categoria": "Antialérgico"
    },
    "Loratadina": {
        "tipo": "edad", "por_edad": {(2,5):5.0, (6,11):10.0},
        "frecuencias": [24], "categoria": "Antialérgico"
    },
    "Hierro (elemental)": {
        "tipo": "mgkgdia", "dosis": 3, "dosis_max_dia": 6,
        "frecuencias": [24], "categoria": "Suplemento"
    },
    "Sulfato Ferroso": {
        "tipo": "mgkgdia", "dosis": 6, "dosis_max_dia": 12,
        "frecuencias": [24], "categoria": "Suplemento"
    },
    "Simeticona": {
        "tipo": "edad", "por_edad": {(0,2):20, (2,12):40},
        "frecuencias": [6,8], "categoria": "Gastrointestinal"
    },
    "Albendazol": {
        "tipo": "edad", "por_edad": {(1,2):200, (2,18):400},
        "frecuencias": [24], "categoria": "Antiparasitario"
    },
    # RESTO
    "Eritromicina": {
        "tipo": "mgkgdia", "dosis": 40, "frecuencias": [6,8,12],
        "categoria": "Antibiótico"
    },
    "Claritromicina": {
        "tipo": "mgkgdia", "dosis": 15, "dosis_max_dia": 20,
        "frecuencias": [12], "categoria": "Antibiótico"
    },
    "TMP/SMX": {
        "tipo": "mgkgdia", "dosis": 8, "frecuencias": [12],
        "categoria": "Antibiótico"
    },
    "Metronidazol": {
        "tipo": "mgkgdia", "dosis": 30, "frecuencias": [8],
        "categoria": "Antibiótico"
    },
    "Nitrofurantoína": {
        "tipo": "mgkgdia", "dosis": 5, "frecuencias": [6],
        "categoria": "Antibiótico"
    },
    "Cefalexina": {
        "tipo": "mgkgdia", "dosis": 50, "dosis_max_dia": 100,
        "frecuencias": [6,8,12], "categoria": "Antibiótico"
    },
    "Amoxicilina + Clavulanato": {
        "tipo": "mgkgdia", "dosis": 45, "frecuencias": [8,12],
        "categoria": "Antibiótico"
    },
    "Salbutamol": {
        "tipo": "edad", "por_edad": {(0,4):0.1}, "frecuencias": [6],
        "categoria": "Respiratorio"
    },
    "Prednisolona": {
        "tipo": "mgkgdosis", "dosis": 1, "frecuencias": [24],
        "categoria": "Respiratorio"
    },
    "Dexametasona": {
        "tipo": "mgkgdosis", "dosis": 0.15, "frecuencias": [6],
        "categoria": "Respiratorio"
    },
    "Subsalicilato de bismuto": {
        "tipo": "edad", "por_edad": {(2,3):262, (4,5):350, (6,8):525, (9,11):700},
        "frecuencias": [8], "categoria": "Gastrointestinal"
    },
    "Hidróxido de aluminio + magnesio": {
        "tipo": "edad", "por_edad": {(0,1):2.5, (2,5):5},
        "frecuencias": [6,8], "categoria": "Gastrointestinal"
    },
    "Ondansetrón": {
        "tipo": "mgkgdosis", "dosis": 0.15, "dosis_max_toma": 4,
        "frecuencias": [8], "categoria": "Gastrointestinal"
    },
    "Mebendazol": {
        "tipo": "edad", "por_edad": {(2,18):100},
        "frecuencias": [12], "categoria": "Antiparasitario"
    },
    "Zinc": {
        "tipo": "edad", "por_edad": {(0,6):10, (7,12):20},
        "frecuencias": [24], "categoria": "Suplemento"
    },
    "Vitamina C": {
        "tipo": "edad", "por_edad": {(0,3):125, (4,8):250, (9,13):375},
        "frecuencias": [24], "categoria": "Suplemento"
    }
}

# Mapeo para el selectbox con favoritos marcados
def generar_opciones_medicamentos():
    # Favoritos primero, con estrella
    favoritos = ["Amoxicilina", "Paracetamol", "Ibuprofeno", "Azitromicina",
                 "Clorfenamina", "Loratadina", "Hierro (elemental)", "Sulfato Ferroso",
                 "Simeticona", "Albendazol"]
    # Crear lista con estrellas
    lista = [f"⭐ {med}" for med in favoritos if med in DB_MEDICAMENTOS]
    lista.append("──────────")
    # Agrupar por categoría
    categorias = {}
    for nombre, datos in DB_MEDICAMENTOS.items():
        if nombre not in favoritos:
            cat = datos.get("categoria", "Otro")
            categorias.setdefault(cat, []).append(nombre)
    for cat in categorias:
        lista.append(f"── {cat} ──")
        for med in categorias[cat]:
            lista.append(med)
    return lista

# Mapa display -> clave real
def obtener_clave_real(display_name):
    if display_name.startswith("⭐ "):
        return display_name[2:]
    elif display_name.startswith("──"):
        return None  # Es un separador
    else:
        return display_name

# ==============================
# 2. FUNCIONES AUXILIARES
# ==============================
def calcular_edad(fecha_nac):
    hoy = date.today()
    años = hoy.year - fecha_nac.year
    if (hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day):
        años -= 1
    # Meses
    if hoy.month >= fecha_nac.month:
        meses = hoy.month - fecha_nac.month
    else:
        meses = 12 + hoy.month - fecha_nac.month
    if hoy.day < fecha_nac.day:
        meses -= 1
        if meses < 0:
            meses += 12
    # Días
    if hoy.day >= fecha_nac.day:
        dias = hoy.day - fecha_nac.day
    else:
        # Último día del mes anterior
        if hoy.month == 1:
            mes_anterior = 12
            año_anterior = hoy.year - 1
        else:
            mes_anterior = hoy.month - 1
            año_anterior = hoy.year
        ultimo_dia_mes_anterior = (date(año_anterior, mes_anterior, 1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        dias = ultimo_dia_mes_anterior.day - fecha_nac.day + hoy.day
    return años, meses, dias

def obtener_dosis_por_toma(peso, edad_años, medicamento, frecuencia_h):
    info = DB_MEDICAMENTOS[medicamento]
    tipo = info["tipo"]
    mg_por_toma = 0

    if tipo == "mgkgdosis":
        mg_por_toma = info["dosis"] * peso
    elif tipo == "mgkgdia":
        dosis_diaria_total = info["dosis"] * peso
        tomas_por_dia = 24 / frecuencia_h
        mg_por_toma = dosis_diaria_total / tomas_por_dia
    elif tipo == "edad":
        # Buscar rango de edad (años cumplidos)
        for (rango_min, rango_max), dosis_edad in info.get("por_edad", {}).items():
            if rango_min <= edad_años <= rango_max:
                mg_por_toma = dosis_edad
                break
        if mg_por_toma == 0:
            st.warning("Edad fuera de los rangos definidos para este fármaco.")

    # Límites de seguridad (convertir a mg)
    if "dosis_max_toma" in info and info["dosis_max_toma"] is not None:
        max_toma_mg = info["dosis_max_toma"] * peso
        if mg_por_toma > max_toma_mg:
            st.error(f"⚠️ ¡SOBREDOSIS POR TOMA! Dosis calculada ({mg_por_toma:.1f} mg) supera el máximo de {max_toma_mg:.1f} mg.")
    if "dosis_max_dia" in info and info["dosis_max_dia"] is not None:
        tomas_por_dia = 24 / frecuencia_h
        dosis_diaria_calc = mg_por_toma * tomas_por_dia
        max_dia_mg = info["dosis_max_dia"] * peso
        if dosis_diaria_calc > max_dia_mg:
            st.error(f"⚠️ ¡SOBREDOSIS DIARIA! Dosis diaria calculada ({dosis_diaria_calc:.1f} mg) supera el máximo de {max_dia_mg:.1f} mg.")

    return mg_por_toma

def buscar_frecuencia_optima(peso, edad, medicamento, conc_tableta_mg, frecuencia_actual, mg_toma_actual):
    """Si la dosis en comprimido no es 'bonita', busca otra frecuencia válida que sí lo sea."""
    info = DB_MEDICAMENTOS[medicamento]
    frecuencias_validas = info.get("frecuencias", [])
    alternativas = []
    for f in frecuencias_validas:
        if f == frecuencia_actual:
            continue
        mg = obtener_dosis_por_toma(peso, edad, medicamento, f)
        tablets = mg / conc_tableta_mg
        # Consideramos "bonito" si tabletas es múltiplo de 0.5 o entero
        if abs(tablets - round(tablets)) < 0.01 or abs(tablets % 0.5) < 0.01:
            # Verificar que no exceda máximos (ya se chequea dentro de obtener_dosis_por_toma, pero podríamos omitir)
            # Para no duplicar alertas, confiamos en que la función ya las lanza; si no hay errores, es válida.
            alternativas.append((f, tablets))
    return alternativas

def generar_horario(frecuencia_h, hora_inicio=6):
    tomas = 24 // frecuencia_h
    horarios = []
    h = hora_inicio
    for _ in range(tomas):
        horarios.append(f"{h:02d}:00")
        h += frecuencia_h
    return horarios

def generar_pdf(nombre_paciente, edad_str, peso, medicamento, presentacion, detalle_presentacion,
                frecuencia, duracion, frasco_ml_o_unidades, mg_por_toma, dosis_por_toma_str,
                ml_dia_o_mg_dia, total_tratamiento_str, frascos_o_unidades, alertas):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Receta Pediátrica", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Paciente: {nombre_paciente}", ln=True)
    pdf.cell(0, 8, f"Edad: {edad_str}", ln=True)
    pdf.cell(0, 8, f"Peso: {peso} kg", ln=True)
    pdf.ln(5)
    pdf.cell(0, 8, f"Medicamento: {medicamento}", ln=True)
    pdf.cell(0, 8, f"Presentación: {presentacion} - {detalle_presentacion}", ln=True)
    pdf.cell(0, 8, f"Dosis por toma: {mg_por_toma:.1f} mg = {dosis_por_toma_str}", ln=True)
    pdf.cell(0, 8, f"Frecuencia: cada {frecuencia} horas", ln=True)
    pdf.cell(0, 8, f"Duración: {duracion} días", ln=True)
    if presentacion == "Jarabe":
        pdf.cell(0, 8, f"Total diario: {ml_dia_o_mg_dia:.2f} mL", ln=True)
        pdf.cell(0, 8, f"Total tratamiento: {total_tratamiento_str}", ln=True)
        pdf.cell(0, 8, f"Frascos de {frasco_ml_o_unidades} mL: {frascos_o_unidades}", ln=True)
    else:
        pdf.cell(0, 8, f"Total diario: {ml_dia_o_mg_dia:.1f} mg", ln=True)
        pdf.cell(0, 8, f"Total tratamiento: {total_tratamiento_str}", ln=True)
        pdf.cell(0, 8, f"Unidades totales: {frascos_o_unidades} tabletas/cápsulas", ln=True)
    if alertas:
        pdf.set_text_color(255,0,0)
        for alerta in alertas:
            pdf.cell(0, 8, alerta, ln=True)
        pdf.set_text_color(0,0,0)
    pdf.ln(10)
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 8, "Gracias por confiar.", ln=True, align="C")
    salida_pdf = pdf.output(dest="S")
    
    # Si usas PyFPDF clásico (devuelve un string), lo pasamos a bytes
    if isinstance(salida_pdf, str):
        return salida_pdf.encode('latin-1')
        
    # Si usas FPDF2 (devuelve un bytearray), lo convertimos a bytes estándar
    return bytes(salida_pdf)

# ==============================
# 3. INTERFAZ PRINCIPAL
# ==============================
st.markdown("<div class='main-title'>NN</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>💖 Calculadora Pediátrica de Dosis 💖</div>", unsafe_allow_html=True)
st.write("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("👶 Datos del paciente")
    nombre = st.text_input("Nombre", "Angel")
    fecha_nacimiento = st.date_input("Fecha de nacimiento", value=date(2024, 7, 1),
                                     min_value=date(2000,1,1), max_value=date.today())
    if fecha_nacimiento:
        años, meses, dias = calcular_edad(fecha_nacimiento)
        edad_str = f"{años} año(s) {meses} mes(es) {dias} día(s)"
        st.markdown(f"**Edad calculada:** {edad_str}")
    else:
        años, meses, dias = 0,0,0
    peso = st.number_input("Peso (kg)", min_value=1.0, max_value=150.0, value=13.8, step=0.1)

with col2:
    st.subheader("💊 Medicamento y presentación")
    opciones_med = generar_opciones_medicamentos()
    seleccion_display = st.selectbox("Selecciona el medicamento", opciones_med)
    medicamento_clave = obtener_clave_real(seleccion_display)
    if medicamento_clave is None:
        st.warning("Selecciona un medicamento válido.")
        medicamento_clave = ""
    else:
        # Forma farmacéutica
        forma = st.radio("Forma farmacéutica", ["Jarabe", "Tableta/Cápsula"], index=0)
        if forma == "Jarabe":
            # Etiqueta en rojo
            st.markdown('<p class="red-label">Datos del jarabe</p>', unsafe_allow_html=True)
            conc_mg = st.number_input("mg del fármaco en el jarabe", min_value=1, value=100)
            conc_ml = st.number_input("mL de la solución", min_value=1, value=5)
            modo_presentacion = st.radio("¿Cómo se administra?", ["Jeringa (mL)", "Gotero (gotas)"])
            if modo_presentacion == "Gotero (gotas)":
                gotas_por_ml = st.number_input("Gotas por mL (habitual 20)", min_value=1, value=20)
            else:
                gotas_por_ml = None
        else:  # Tableta/Cápsula
            conc_tableta = st.number_input("Miligramos por tableta/cápsula", min_value=1, value=500)

with st.expander("⏰ Esquema terapéutico", expanded=True):
    col_f1, col_f2, col_f3 = st.columns(3)
    # Frecuencias válidas según medicamento
    if medicamento_clave and medicamento_clave in DB_MEDICAMENTOS:
        frecuencias_validas = DB_MEDICAMENTOS[medicamento_clave].get("frecuencias", [6,8,12,24])
    else:
        frecuencias_validas = [6,8,12,24]
    with col_f1:
        frecuencia = st.selectbox("Cada cuántas horas", frecuencias_validas)
    with col_f2:
        duracion = st.number_input("Días de tratamiento", min_value=1, value=3)
    with col_f3:
        if forma == "Jarabe":
            frasco_ml = st.number_input("Volumen del frasco (mL)", min_value=10, value=60)
        else:
            frasco_ml = None  # No se usa

# --- CÁLCULOS Y RESULTADOS ---
if st.button("💊 Calcular dosis", type="primary"):
    if not medicamento_clave:
        st.error("Debe seleccionar un medicamento.")
    else:
        # 1. Obtener dosis en mg por toma
        mg_toma = obtener_dosis_por_toma(peso, años, medicamento_clave, frecuencia)

        # 2. Convertir a unidades prácticas
        if forma == "Jarabe":
            if conc_ml > 0:
                ml_toma = mg_toma * conc_ml / conc_mg
            else:
                ml_toma = 0
            tomas_dia = 24 / frecuencia
            ml_dia = ml_toma * tomas_dia
            ml_total = ml_dia * duracion
            frascos = math.ceil(ml_total / frasco_ml) if frasco_ml else 0
            # Detalle por toma
            if modo_presentacion == "Gotero (gotas)" and gotas_por_ml:
                gotas_toma = ml_toma * gotas_por_ml
                dosis_str = f"{gotas_toma:.0f} gotas"
            else:
                dosis_str = f"{ml_toma:.2f} mL"
            total_tratamiento_str = f"{ml_total:.2f} mL"
        else:  # Tableta/Cápsula
            tablets_toma = mg_toma / conc_tableta
            tomas_dia = 24 / frecuencia
            tablets_dia = tablets_toma * tomas_dia
            tablets_total = tablets_dia * duracion
            frascos_o_unidades = math.ceil(tablets_total)
            dosis_str = f"{tablets_toma:.2f} tableta(s)"
            total_tratamiento_str = f"{tablets_total:.2f} tabletas/cápsulas"
            ml_dia = None

        # 3. Alertas de adulto
        alertas_list = []
        if peso >= 40:
            alertas_list.append(f"⚠️ ALERTA: El paciente pesa {peso} kg.")
        if años >= 12:
            alertas_list.append(f"⚠️ ALERTA: El paciente tiene {años} años.")
        if alertas_list:
            alertas_list.append("Verifique si corresponde utilizar presentaciones y dosis de adulto.")
            st.markdown('<div class="alerta-adulto">' + "<br>".join(alertas_list) + '</div>', unsafe_allow_html=True)

        # 4. Sugerencia gotas si <2 años y jarabe en mL
        if forma == "Jarabe" and modo_presentacion != "Gotero (gotas)" and años < 2:
            st.warning("💡 Para niños menores de 2 años se recomienda usar gotero (gotas) para mayor precisión.")

        # 5. Resultados principales
        st.success("### ✨ Resultados")
        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            st.metric("mg por toma", f"{mg_toma:.1f} mg")
        with col_r2:
            if forma == "Jarabe":
                st.metric("mL/gotas por toma", dosis_str)
            else:
                st.metric("Tabletas por toma", dosis_str)
        with col_r3:
            if forma == "Jarabe":
                st.metric("Frascos necesarios", f"{frascos} ud(s)")
            else:
                st.metric("Unidades totales", f"{frascos_o_unidades} ud(s)")

        # 6. Equivalencias para jarabe
        if forma == "Jarabe":
            st.markdown("#### 🥄 Equivalencias prácticas")
            if modo_presentacion == "Gotero (gotas)":
                st.info(f"💧 **{gotas_toma:.0f} gotas** por toma")
            else:
                if ml_toma >= 5:
                    cucharaditas = ml_toma / 5
                    st.info(f"🥄 **{cucharaditas:.1f} cucharaditas** (1 cdita = 5 mL)")
                if ml_toma >= 15:
                    cucharadas = ml_toma / 15
                    st.info(f"🍲 **{cucharadas:.1f} cucharadas** (1 cda = 15 mL)")
                if ml_toma < 5 and ml_toma > 0:
                    st.info(f"💧 Dosis pequeña: {ml_toma:.2f} mL (usar jeringa dosificadora)")

        # 7. Volúmenes totales
        st.markdown("#### 📊 Totales del tratamiento")
        if forma == "Jarabe":
            col_t1, col_t2, col_t3 = st.columns(3)
            with col_t1:
                st.metric("mL por día", f"{ml_dia:.2f} mL")
            with col_t2:
                st.metric("mL total", f"{ml_total:.2f} mL")
            with col_t3:
                st.metric(f"Frascos de {frasco_ml} mL", frascos)
        else:
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                st.metric("mg por día", f"{mg_toma * tomas_dia:.1f} mg")
            with col_t2:
                st.metric("Total tabletas/cápsulas", f"{tablets_total:.2f}")

        # 8. Alerta por dosis en comprimido no redonda
        if forma == "Tableta/Cápsula":
            if abs(tablets_toma - round(tablets_toma)) > 0.1 and abs(tablets_toma % 0.5) > 0.05:
                st.warning("⚠️ La dosis no coincide bien con la presentación seleccionada.")
                # Buscar sugerencia automática
                alternativas = buscar_frecuencia_optima(peso, años, medicamento_clave, conc_tableta, frecuencia, mg_toma)
                if alternativas:
                    sugerencias = []
                    for f_alt, tab_alt in alternativas:
                        sugerencias.append(f"- Cada {f_alt} horas: {tab_alt:.2f} tableta(s) por toma")
                    st.info("💡 Existen esquemas válidos que podrían ajustarse mejor:\n" + "\n".join(sugerencias) +
                            "\nVerifique si es clínicamente apropiado.")

        # 9. Horario
        st.markdown("#### 🕒 Horario orientativo")
        horarios = generar_horario(frecuencia)
        df_horario = pd.DataFrame({"Hora": horarios, "Dosis": [dosis_str]*len(horarios)})
        st.table(df_horario)

        # 10. PDF
        detalle_presentacion = f"{conc_mg}mg/{conc_ml}mL" if forma=="Jarabe" else f"{conc_tableta} mg"
        pdf_bytes = generar_pdf(nombre, edad_str, peso, medicamento_clave, forma, detalle_presentacion,
                                frecuencia, duracion,
                                frasco_ml if forma=="Jarabe" else "",
                                mg_toma, dosis_str,
                                ml_dia if forma=="Jarabe" else (mg_toma * tomas_dia),
                                total_tratamiento_str,
                                frascos if forma=="Jarabe" else frascos_o_unidades,
                                alertas_list if alertas_list else [])
        st.download_button(
            label="📄 Descargar receta en PDF",
            data=pdf_bytes,
            file_name=f"receta_{nombre.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
        st.balloons()
else:
    st.info("Completa los datos y pulsa el botón para ver el resultado.")

# Pie
st.markdown("---")
st.markdown("<center><small>Hecho NN</small></center>", unsafe_allow_html=True)
