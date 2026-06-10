import streamlit as st
import pandas as pd

from datos.parametros import EVENTO, CAPACIDAD, COMERCIAL, TIEMPOS, RECETA
from simuladores.flujo_personas import simular_flujo, escenarios_flujo
from simuladores.stock_porciones import simular_stock, escenarios_stock
from simuladores.viabilidad import simular_viabilidad, escenarios_viabilidad, calcular_costo_materia_prima
from utils.verificacion import verificar_tiempos, verificar_positivo, mostrar_errores
from utils.graficos import (
    grafico_histograma,
    grafico_barras,
    grafico_escenarios,
    grafico_punto_equilibrio,
    grafico_flujo_produccion,
    COLORES,
)
from utils.informe import generar_informe

# ─────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Budín Nutritivo — Simulador",
    page_icon="🍞",
    layout="wide",
)

# ─────────────────────────────────────────
# ESTILOS PERSONALIZADOS
# ─────────────────────────────────────────
st.markdown("""
<style>
/* Fondo general */
.stApp { background-color: #FAF6F1; }

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #F0E8DC;
    border-right: 1px solid #E2D3C0;
}

/* Tarjetas / expanders */
[data-testid="stExpander"] {
    background-color: #FFFFFF;
    border: 1px solid #E2D3C0;
    border-radius: 10px;
}

/* Botón primario */
.stButton > button[kind="primary"] {
    background-color: #2C1810;
    color: #FAF6F1;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    letter-spacing: 0.03em;
}
.stButton > button[kind="primary"]:hover {
    background-color: #3D2418;
    color: #FAF6F1;
}

/* Botón secundario */
.stButton > button[kind="secondary"] {
    background-color: transparent;
    color: #2C1810;
    border: 1.5px solid #2C1810;
    border-radius: 8px;
}

/* Métricas */
[data-testid="stMetric"] {
    background-color: #FFFFFF;
    border: 1px solid #E2D3C0;
    border-radius: 10px;
    padding: 0.75rem 1rem;
}
[data-testid="stMetricLabel"] { color: #6B4F3A; font-size: 0.8rem; }
[data-testid="stMetricValue"] { color: #2C1810; font-weight: 700; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background-color: #F0E8DC;
    border-radius: 10px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    color: #6B4F3A;
    font-weight: 500;
}
.stTabs [aria-selected="true"] {
    background-color: #2C1810 !important;
    color: #FAF6F1 !important;
}

/* Inputs */
input, textarea, [data-baseweb="input"] {
    background-color: #FFFFFF !important;
    border-color: #D4C4B0 !important;
    border-radius: 8px !important;
}

/* Sliders — track */
[data-testid="stSlider"] [role="slider"] {
    background-color: #2C1810 !important;
}

/* Divisor */
hr { border-color: #E2D3C0; }

/* Info / success / warning boxes */
[data-testid="stAlert"] { border-radius: 10px; }

/* Badges del header */
.badge-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background-color: #2C1810;
    color: #FAF6F1;
    border-radius: 20px;
    padding: 5px 14px;
    font-size: 0.82rem;
    font-weight: 600;
    margin-right: 8px;
    letter-spacing: 0.02em;
}

/* Etiqueta de sección tipo small-caps */
.section-label {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #C9952A;
    margin-bottom: 2px;
}

/* Tarjeta de etapa productiva */
.etapa-card {
    background: #FFFFFF;
    border: 1px solid #E2D3C0;
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 12px;
}
.etapa-num {
    background-color: #2C1810;
    color: #FAF6F1;
    border-radius: 50%;
    width: 26px;
    height: 26px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.78rem;
    font-weight: 700;
    flex-shrink: 0;
}
.etapa-info { flex: 1; }
.etapa-nombre { font-weight: 600; color: #2C1810; font-size: 0.9rem; }
.etapa-tiempo { color: #6B4F3A; font-size: 0.78rem; }
.etapa-dur { color: #C9952A; font-weight: 700; font-size: 0.88rem; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────
col_titulo, col_badges = st.columns([3, 2])
with col_titulo:
    st.markdown('<p class="section-label">Simulador de Producción Alimentaria</p>', unsafe_allow_html=True)
    st.title("🍞 Budín Nutritivo")
    st.caption("Universidad de la Cuenca del Plata · ISI 4to Año · Modelos y Simulación · Grupo 3 · 2026")
with col_badges:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<span class="badge-pill">🧪 3 simuladores</span>'
        '<span class="badge-pill">🥚 10 ingredientes</span>'
        '<span class="badge-pill">⚙️ 6 etapas</span>',
        unsafe_allow_html=True,
    )
st.divider()

# ─────────────────────────────────────────
# ESTADO GLOBAL — resultados para el informe
# ─────────────────────────────────────────
if "metricas_flujo" not in st.session_state:
    st.session_state["metricas_flujo"] = None
if "metricas_stock" not in st.session_state:
    st.session_state["metricas_stock"] = None
if "metricas_viabilidad" not in st.session_state:
    st.session_state["metricas_viabilidad"] = None
if "params_flujo" not in st.session_state:
    st.session_state["params_flujo"] = None
if "params_stock" not in st.session_state:
    st.session_state["params_stock"] = None
if "params_viabilidad" not in st.session_state:
    st.session_state["params_viabilidad"] = None

# ─────────────────────────────────────────
# TABS
# ─────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "👥 Flujo de Personas",
    "📦 Stock de Porciones",
    "💰 Viabilidad Comercial",
    "🏭 Línea de Producción",
])


# ═════════════════════════════════════════
# TAB 1 — FLUJO DE PERSONAS
# ═════════════════════════════════════════
with tab1:
    st.markdown('<p class="section-label">Simulador 1 · Eventos Discretos</p>', unsafe_allow_html=True)
    st.header("Flujo de Personas y Formulario Digital")
    st.markdown("Estima saturación del sistema, tiempos de espera y carga del formulario QR durante el evento.")

    col_params, col_resultados = st.columns([1, 2], gap="large")

    with col_params:
        st.subheader("Parámetros")

        comensales = st.number_input(
            "Cantidad de comensales", min_value=10, max_value=500,
            value=EVENTO["comensales_esperados"], step=5,
        )
        capacidad_sistema = st.number_input(
            "Capacidad simultánea del sistema", min_value=1, max_value=100,
            value=15, step=1,
        )
        st.markdown("**Tasa de llegada (personas/min)**")
        tasa_min = st.number_input("Tasa mínima", min_value=0.1, max_value=20.0,
                                   value=float(EVENTO["tasa_llegada_personas_min"]),
                                   step=0.5, key="tasa_min")
        tasa_max = st.number_input("Tasa máxima", min_value=0.1, max_value=20.0,
                                   value=float(EVENTO["tasa_llegada_personas_max"]),
                                   step=0.5, key="tasa_max")

        st.markdown("**Tiempo de degustación (min)**")
        deg_min = st.number_input("Degustación mínima", min_value=0.5, max_value=30.0,
                                  value=float(EVENTO["tiempo_degustacion_min"]),
                                  step=0.5, key="deg_min")
        deg_max = st.number_input("Degustación máxima", min_value=0.5, max_value=30.0,
                                  value=float(EVENTO["tiempo_degustacion_max"]),
                                  step=0.5, key="deg_max")

        st.markdown("**Tiempo de formulario QR (min)**")
        form_min = st.number_input("Formulario mínimo", min_value=0.5, max_value=30.0,
                                   value=float(EVENTO["tiempo_formulario_min"]),
                                   step=0.5, key="form_min")
        form_max = st.number_input("Formulario máximo", min_value=0.5, max_value=30.0,
                                   value=float(EVENTO["tiempo_formulario_max"]),
                                   step=0.5, key="form_max")

        ejecutar_flujo = st.button("▶ Simular flujo", use_container_width=True, type="primary")

    with col_resultados:
        if ejecutar_flujo:
            errores = []
            ok, msg = verificar_tiempos(tasa_min, tasa_max, "tasa de llegada")
            if not ok:
                errores.append(msg)
            ok, msg = verificar_tiempos(deg_min, deg_max, "degustación")
            if not ok:
                errores.append(msg)
            ok, msg = verificar_tiempos(form_min, form_max, "formulario")
            if not ok:
                errores.append(msg)
            ok, msg = verificar_positivo(comensales, "comensales")
            if not ok:
                errores.append(msg)

            if errores:
                mostrar_errores(errores)
            else:
                params = dict(
                    comensales=comensales,
                    tasa_llegada_min=tasa_min,
                    tasa_llegada_max=tasa_max,
                    t_degustacion_min=deg_min,
                    t_degustacion_max=deg_max,
                    t_formulario_min=form_min,
                    t_formulario_max=form_max,
                    capacidad_sistema=capacidad_sistema,
                )
                with st.spinner("Simulando..."):
                    df_flujo, met_flujo = simular_flujo(**params)

                st.session_state["metricas_flujo"] = met_flujo
                st.session_state["params_flujo"] = params

                pico = met_flujo["pico_concurrencia"]
                cap  = met_flujo["capacidad_sistema"]

                # Información contextual sobre concurrencia real vs capacidad configurada
                if cap > pico:
                    st.info(
                        f"Con los parámetros actuales, el **pico de concurrencia fue {pico} personas simultáneas** "
                        f"(capacidad configurada: {cap}). "
                        f"Si el evento tiene llegadas más masivas o tiempos más largos, "
                        f"la saturación puede aumentar significativamente."
                    )
                elif cap <= pico:
                    st.warning(
                        f"**La capacidad del sistema fue superada.** "
                        f"El pico de concurrencia fue {pico} personas simultáneas "
                        f"con capacidad de {cap}. Hay comensales que esperaron."
                    )

                # Métricas principales — 2x2
                ma1, ma2 = st.columns(2)
                mb1, mb2 = st.columns(2)
                ma1.metric("Duración evento", f"{met_flujo['tiempo_total_evento']} min")
                ma2.metric("Tiempo prom. sistema", f"{met_flujo['tiempo_promedio_sistema']} min")
                mb1.metric("Con espera", f"{met_flujo['comensales_con_espera']} personas")
                mb2.metric("Saturación", met_flujo["saturacion"],
                           delta=f"{met_flujo['pct_saturacion']}%",
                           delta_color="inverse")
                st.caption(f"Pico de concurrencia real: **{pico} personas simultáneas** · Capacidad configurada: {cap}")

                # ── Diagnóstico de saturación ─────────────────────────
                st.markdown('<p class="section-label" style="margin-top:16px">¿Por qué este resultado?</p>',
                            unsafe_allow_html=True)

                intervalo_prom = round(2 / (tasa_min + tasa_max), 1)
                t_servicio_prom = round((deg_min + deg_max + form_min + form_max) / 2, 1)
                pico = met_flujo["pico_concurrencia"]

                if met_flujo["saturacion"] == "Alta":
                    st.warning(
                        f"**Causa: la tasa de llegada supera la capacidad de atencion del sistema.** "
                        f"En promedio llega 1 persona cada {intervalo_prom} min, pero el tiempo promedio de "
                        f"atencion (degustacion + formulario) es de {t_servicio_prom} min. "
                        f"Esto genera acumulacion: el pico fue de {pico} personas simultaneas "
                        f"con capacidad configurada de {capacidad_sistema}. "
                        f"El {met_flujo['pct_saturacion']}% de los comensales tuvo que esperar. "
                        f"Recomendacion: {met_flujo['recomendacion']}"
                    )
                elif met_flujo["saturacion"] == "Media":
                    st.info(
                        f"**El sistema opera con saturacion moderada.** "
                        f"El tiempo promedio de atencion ({t_servicio_prom} min) es relativamente alto "
                        f"respecto al intervalo de llegada ({intervalo_prom} min), "
                        f"lo que genera colas en momentos pico. "
                        f"El pico de concurrencia fue {pico} personas sobre una capacidad de {capacidad_sistema}. "
                        f"Recomendacion: {met_flujo['recomendacion']}"
                    )
                else:
                    st.success(
                        f"**El sistema funciona con baja saturacion.** "
                        f"La capacidad de {capacidad_sistema} lugares simultaneos es suficiente "
                        f"para el flujo de {comensales} comensales con llegadas cada {intervalo_prom} min "
                        f"y atencion promedio de {t_servicio_prom} min. "
                        f"El pico maximo registrado fue de {pico} personas simultaneas. "
                        f"No se requieren medidas adicionales."
                    )

                # Gráficos apilados verticalmente para que tengan ancho completo
                fig_deg = grafico_histograma(
                    datos=df_flujo["Degustación (min)"].tolist(),
                    titulo="Distribución de tiempos de degustación",
                    etiqueta_x="Minutos",
                    color=COLORES["principal"],
                )
                fig_form = grafico_histograma(
                    datos=df_flujo["Formulario (min)"].tolist(),
                    titulo="Distribución de tiempos de formulario",
                    etiqueta_x="Minutos",
                    color=COLORES["secundario"],
                )
                st.plotly_chart(fig_deg, use_container_width=True)
                st.plotly_chart(fig_form, use_container_width=True)

                with st.expander("Ver tabla de eventos"):
                    st.dataframe(df_flujo, use_container_width=True)

        elif st.session_state["metricas_flujo"] is None:
            st.info("Configurá los parámetros y presioná **▶ Simular flujo**.")

    # Comparación de escenarios
    st.divider()
    st.subheader("Comparación de Escenarios")
    if st.button("▶ Comparar los 3 escenarios", key="cmp_flujo"):
        escenarios = escenarios_flujo()
        nombres, sat_pct, espera_prom, dur_evento = [], [], [], []

        for clave, esc in escenarios.items():
            p = {k: v for k, v in esc.items() if k not in ("nombre", "descripcion")}
            _, m = simular_flujo(**p)
            nombres.append(esc["nombre"])
            sat_pct.append(m["pct_saturacion"])
            espera_prom.append(m["espera_promedio"])
            dur_evento.append(m["tiempo_total_evento"])

        fig_sat = grafico_barras(
            categorias=nombres, valores=sat_pct,
            titulo="% Saturación por escenario",
            etiqueta_y="% comensales con espera",
            colores=[COLORES["optimista"], COLORES["esperado"], COLORES["pesimista"]],
        )
        fig_dur = grafico_barras(
            categorias=nombres, valores=dur_evento,
            titulo="Duración total del evento (min)",
            etiqueta_y="Minutos",
            colores=[COLORES["optimista"], COLORES["esperado"], COLORES["pesimista"]],
        )
        st.plotly_chart(fig_sat, use_container_width=True)
        st.plotly_chart(fig_dur, use_container_width=True)


# ═════════════════════════════════════════
# TAB 2 — STOCK DE PORCIONES
# ═════════════════════════════════════════
with tab2:
    st.markdown('<p class="section-label">Simulador 2 · Monte Carlo</p>', unsafe_allow_html=True)
    st.header("Stock de Porciones")
    st.markdown("Estima probabilidad de quiebre de stock, desperdicio y cantidad óptima de lotes a preparar.")

    col_params2, col_resultados2 = st.columns([1, 2], gap="large")

    with col_params2:
        st.subheader("Parámetros")

        comensales_esp = st.number_input(
            "Comensales esperados", min_value=10, max_value=500,
            value=EVENTO["comensales_esperados"], step=5, key="s_com",
        )
        budines_lote = st.number_input(
            "Budines por lote (hornada)", min_value=1, max_value=50,
            value=CAPACIDAD["budines_por_lote"], step=1, key="s_bl",
            help="Cuántos budines salen de cada hornada. Dato real del equipo de nutrición: 2 budines por lote.",
        )
        porciones_budin = st.number_input(
            "Porciones por budín", min_value=1, max_value=50,
            value=CAPACIDAD["porciones_por_budin"], step=1, key="s_pb",
            help="Cuántas porciones (tajadas) rinde cada budín. Dato real: 10 porciones por budín.",
        )
        lotes_preparados = st.number_input(
            "Lotes a preparar", min_value=1, max_value=200,
            value=3, step=1, key="s_lp",
            help="Cuántas hornadas se van a producir para el evento. Determina el stock total disponible.",
        )

        total_prev = lotes_preparados * budines_lote * porciones_budin
        st.info(
            f"**{lotes_preparados} lotes × {budines_lote} budines × {porciones_budin} porciones "
            f"= {total_prev} porciones disponibles**"
        )

        pct_min = st.slider("% consumo mínimo", min_value=10, max_value=100,
                            value=70, step=5, key="pct_min",
                            help="Porcentaje mínimo de comensales que se estima consumirán una porción.") / 100
        pct_max = st.slider("% consumo máximo", min_value=10, max_value=100,
                            value=90, step=5, key="pct_max",
                            help="Porcentaje máximo de comensales que se estima consumirán una porción.") / 100
        iteraciones_s = st.select_slider(
            "Iteraciones Monte Carlo",
            options=[100, 500, 1000, 5000, 10000],
            value=1000, key="iter_s",
        )

        ejecutar_stock = st.button("▶ Simular stock", use_container_width=True, type="primary")

    with col_resultados2:
        if ejecutar_stock:
            errores2 = []
            ok, msg = verificar_tiempos(pct_min, pct_max, "% de consumo")
            if not ok:
                errores2.append(msg)
            ok, msg = verificar_positivo(lotes_preparados, "lotes preparados")
            if not ok:
                errores2.append(msg)

            if errores2:
                mostrar_errores(errores2)
            else:
                params2 = dict(
                    comensales_esperados=comensales_esp,
                    pct_consumo_min=pct_min,
                    pct_consumo_max=pct_max,
                    budines_por_lote=budines_lote,
                    porciones_por_budin=porciones_budin,
                    lotes_preparados=lotes_preparados,
                    iteraciones=iteraciones_s,
                )
                with st.spinner("Simulando..."):
                    df_stock, met_stock = simular_stock(**params2)

                st.session_state["metricas_stock"] = met_stock
                st.session_state["params_stock"] = params2

                # Métricas 2x2
                ma1, ma2 = st.columns(2)
                mb1, mb2 = st.columns(2)
                ma1.metric("Porciones disponibles", met_stock["total_porciones"])
                ma2.metric("Demanda promedio", f"{met_stock['demanda_promedio']} uds")
                mb1.metric("Prob. quiebre", f"{met_stock['prob_quiebre']}%",
                           delta_color="inverse")
                mb2.metric("Lotes recomendados", met_stock["lotes_recomendados"])

                # ── Diagnóstico de stock ──────────────────────────────
                st.markdown('<p class="section-label" style="margin-top:16px">¿Por qué este resultado?</p>',
                            unsafe_allow_html=True)

                pct_desperdicio = (met_stock["desperdicio_promedio"] / met_stock["total_porciones"] * 100
                                   if met_stock["total_porciones"] > 0 else 0)

                if met_stock["prob_quiebre"] > 30:
                    st.error(
                        f"**Causa: el stock preparado es insuficiente para la demanda esperada.** "
                        f"Las {met_stock['total_porciones']} porciones disponibles "
                        f"({lotes_preparados} lotes x {budines_lote} budines x {porciones_budin} porciones) "
                        f"no alcanzan para cubrir la demanda en el {met_stock['prob_quiebre']}% de los escenarios simulados. "
                        f"La demanda promedio fue de {met_stock['demanda_promedio']} porciones y en el peor caso "
                        f"llego a {met_stock['demanda_maxima']}. "
                        f"Recomendacion: preparar al menos {met_stock['lotes_recomendados']} lotes "
                        f"({met_stock['lotes_recomendados'] * budines_lote * porciones_budin} porciones) "
                        f"para cubrir el 90% de los escenarios."
                    )
                elif met_stock["prob_quiebre"] > 10:
                    st.warning(
                        f"**Hay riesgo moderado de quedarse sin stock.** "
                        f"Con {met_stock['total_porciones']} porciones y una demanda promedio de "
                        f"{met_stock['demanda_promedio']} porciones, en el {met_stock['prob_quiebre']}% de los casos "
                        f"el stock se agota antes de atender a todos. "
                        f"Recomendacion: agregar 1-2 lotes adicionales como margen de seguridad."
                    )
                elif pct_desperdicio > 30:
                    st.info(
                        f"**Hay stock de sobra, pero el desperdicio es elevado.** "
                        f"En promedio {met_stock['desperdicio_promedio']:.0f} porciones ({pct_desperdicio:.0f}% del stock) "
                        f"quedan sin consumir porque la demanda real es menor al stock preparado. "
                        f"Con los niveles de consumo estimados ({int(pct_min*100)}-{int(pct_max*100)}%), "
                        f"alcanzaria con preparar {met_stock['lotes_recomendados']} lotes."
                    )
                else:
                    st.success(
                        f"**El stock esta bien dimensionado.** "
                        f"Las {met_stock['total_porciones']} porciones cubren la demanda en el "
                        f"{100 - met_stock['prob_quiebre']:.0f}% de los escenarios, "
                        f"con un desperdicio promedio de solo {met_stock['desperdicio_promedio']:.0f} porciones. "
                        f"La cantidad de lotes planificada ({lotes_preparados}) es adecuada para este evento."
                    )

                fig_dem = grafico_histograma(
                    datos=df_stock["Demanda (porciones)"].tolist(),
                    titulo="Distribución de demanda (Monte Carlo)",
                    etiqueta_x="Porciones demandadas",
                    color=COLORES["principal"],
                    linea_vertical=met_stock["total_porciones"],
                    etiqueta_linea="Stock disponible",
                )
                fig_desp = grafico_histograma(
                    datos=df_stock["Desperdicio (porciones)"].tolist(),
                    titulo="Distribución de desperdicio",
                    etiqueta_x="Porciones desperdiciadas",
                    color=COLORES["esperado"],
                )
                st.plotly_chart(fig_dem, use_container_width=True)
                st.plotly_chart(fig_desp, use_container_width=True)

                with st.expander("Ver tabla de iteraciones (primeras 100)"):
                    st.dataframe(df_stock.head(100), use_container_width=True)

        elif st.session_state["metricas_stock"] is None:
            st.info("Configurá los parámetros y presioná **▶ Simular stock**.")

    # Comparación de escenarios
    st.divider()
    st.subheader("Comparación de Escenarios")
    if st.button("▶ Comparar los 3 escenarios", key="cmp_stock"):
        escenarios2 = escenarios_stock()
        nombres2, prob_q, desp_prom, por_rec = [], [], [], []

        for clave, esc in escenarios2.items():
            p = {k: v for k, v in esc.items() if k not in ("nombre", "descripcion")}
            p["budines_por_lote"] = CAPACIDAD["budines_por_lote"]
            p["porciones_por_budin"] = CAPACIDAD["porciones_por_budin"]
            _, m = simular_stock(**p)
            nombres2.append(esc["nombre"])
            prob_q.append(m["prob_quiebre"])
            desp_prom.append(m["desperdicio_promedio"])
            por_rec.append(m["porciones_recomendadas"])

        fig_pq = grafico_barras(
            categorias=nombres2, valores=prob_q,
            titulo="Probabilidad de quiebre por escenario (%)",
            etiqueta_y="%",
            colores=[COLORES["optimista"], COLORES["esperado"], COLORES["pesimista"]],
        )
        fig_dp = grafico_barras(
            categorias=nombres2, valores=desp_prom,
            titulo="Desperdicio promedio por escenario (porciones)",
            etiqueta_y="Porciones",
            colores=[COLORES["optimista"], COLORES["esperado"], COLORES["pesimista"]],
        )
        st.plotly_chart(fig_pq, use_container_width=True)
        st.plotly_chart(fig_dp, use_container_width=True)


# ═════════════════════════════════════════
# TAB 3 — VIABILIDAD COMERCIAL
# ═════════════════════════════════════════
with tab3:
    st.markdown('<p class="section-label">Simulador 3 · Monte Carlo Económico</p>', unsafe_allow_html=True)
    st.header("Viabilidad Productiva y Comercial")
    st.markdown("Estima rentabilidad mensual, punto de equilibrio y probabilidad de viabilidad a escala organizacional.")

    # Costo base de materia prima (informativo)
    costo_mp_base, desglose_mp = calcular_costo_materia_prima()
    st.info(
        f"Costo de materia prima por budin: ${costo_mp_base:,.0f} ARS "
        f"(receta y precios de referencia). "
        f"Cada budin rinde {CAPACIDAD['porciones_por_budin']} porciones "
        f"-> ${costo_mp_base / CAPACIDAD['porciones_por_budin']:,.0f} ARS por porcion."
    )

    col_params3, col_resultados3 = st.columns([1, 2], gap="large")

    with col_params3:
        st.subheader("Parámetros")

        st.markdown('<p class="section-label">Capacidad productiva</p>', unsafe_allow_html=True)

        lotes_dia = st.number_input(
            "Lotes por día", min_value=1, max_value=50,
            value=COMERCIAL["lotes_por_dia"], step=1, key="v_ld",
            help=(
                f"Cuántas hornadas se producen por día. "
                f"Cada lote rinde {CAPACIDAD['budines_por_lote']} budines. "
                f"Con un ciclo de ~{CAPACIDAD['jornada_horas']*60//119} hs por lote y jornada de "
                f"{CAPACIDAD['jornada_horas']} hs, el máximo real es ~4 lotes/día."
            ),
        )
        dias_mes = st.number_input(
            "Días de producción por mes", min_value=1, max_value=31,
            value=COMERCIAL["dias_produccion_mes"], step=1, key="v_dm",
            help=(
                "Días hábiles de producción mensual. "
                "Para escala pequeña/evento: 1–5 días. "
                "Para producción regular: 10–15 días. "
                "Para producción continua: ~22 días hábiles."
            ),
        )

        st.markdown('<p class="section-label" style="margin-top:12px">Economía</p>', unsafe_allow_html=True)

        precio_venta = st.number_input(
            "Precio de venta por porción ($)", min_value=50, max_value=10000,
            value=450, step=50, key="v_pv",
            help=(
                f"Precio al que se vende cada porción (tajada) del budín. "
                f"Cada budín rinde {CAPACIDAD['porciones_por_budin']} porciones, "
                f"por lo que el ingreso por budín = precio × {CAPACIDAD['porciones_por_budin']}. "
                f"Ejemplo: $450/porción → $4.500 por budín completo."
            ),
        )
        costos_fijos = st.number_input(
            "Costos fijos mensuales ($)", min_value=0, max_value=1000000,
            value=COMERCIAL["costos_fijos_mensuales"], step=5000, key="v_cf",
            help=(
                "Gastos que se pagan siempre, independientemente de cuánto se produzca: "
                "alquiler, servicios, amortización de equipos, habilitaciones, etc. "
                "Se reparten entre todos los budines vendidos en el mes."
            ),
        )
        costo_mo = st.number_input(
            "Costo de mano de obra por budín ($)", min_value=0, max_value=50000,
            value=COMERCIAL["costo_mano_obra_budin"], step=50, key="v_mo",
            help=(
                "Cuánto cuesta en mano de obra producir 1 budín. "
                "Incluye el tiempo de todos los operarios del equipo. "
                "Ejemplo: si el equipo cobra ARS 20.000 por día y produce 40 budines, "
                "el costo por budín es ARS 500."
            ),
        )

        st.markdown('<p class="section-label" style="margin-top:12px">Incertidumbre Monte Carlo</p>', unsafe_allow_html=True)

        margen_var = st.slider(
            "Variación de costos ±%", min_value=0, max_value=50,
            value=15, step=1, key="v_mv",
            help="Porcentaje de variación aleatoria de los costos de materia prima en cada iteración, simulando fluctuaciones de precios de mercado.",
        )
        aceptacion = st.slider(
            "Aceptación sensorial esperada (%)", min_value=10, max_value=100,
            value=65, step=5, key="v_as",
            help=(
                "Porcentaje de budines producidos que encontrará comprador. "
                "65% = de cada 10 budines producidos, se venden ~6-7. "
                "El resto no se vende (desperdicio o devolucion). "
                "Este parámetro reduce tanto los ingresos como los costos variables."
            ),
        )

        iteraciones_v = st.select_slider(
            "Iteraciones Monte Carlo",
            options=[100, 500, 1000, 5000, 10000],
            value=1000, key="iter_v",
            help="Cantidad de escenarios aleatorios que el modelo simula para estimar la distribución de resultados.",
        )

        ejecutar_viab = st.button("▶ Simular viabilidad", use_container_width=True, type="primary")

    with col_resultados3:
        if ejecutar_viab:
            errores3 = []
            ok, msg = verificar_positivo(precio_venta, "precio de venta")
            if not ok:
                errores3.append(msg)
            ok, msg = verificar_positivo(lotes_dia, "lotes por día")
            if not ok:
                errores3.append(msg)

            if errores3:
                mostrar_errores(errores3)
            else:
                params3 = dict(
                    lotes_por_dia=lotes_dia,
                    budines_por_lote=CAPACIDAD["budines_por_lote"],
                    porciones_por_budin=CAPACIDAD["porciones_por_budin"],
                    dias_produccion_mes=dias_mes,
                    precio_venta=float(precio_venta),
                    costos_fijos_mensuales=float(costos_fijos),
                    costo_mano_obra_budin=float(costo_mo),
                    margen_variacion_costos_pct=float(margen_var),
                    aceptacion_sensorial_pct=float(aceptacion),
                    iteraciones=iteraciones_v,
                )
                with st.spinner("Simulando..."):
                    df_viab, met_viab = simular_viabilidad(**params3)

                st.session_state["metricas_viabilidad"] = met_viab
                st.session_state["params_viabilidad"] = params3

                # Métricas 2x2
                ma1, ma2 = st.columns(2)
                mb1, mb2 = st.columns(2)
                ma1.metric("Viabilidad", met_viab["viabilidad"])
                ma2.metric("Prob. viable", f"{met_viab['prob_viabilidad']}%")
                ganancia_prom = met_viab["ganancia_promedio"]
                mb1.metric("Ganancia prom./mes",
                           f"${ganancia_prom:,.0f}",
                           delta_color="normal" if ganancia_prom >= 0 else "inverse")
                mb2.metric("Punto de equilibrio", f"{met_viab['punto_equilibrio_promedio']:,.0f} uds")

                # ── Desglose de costos por budín ──────────────────────────
                st.caption(
                    f"**Costo por budín:** "
                    f"ARS {met_viab['costo_mp_base']:,.0f} materias primas "
                    f"+ ARS {met_viab['costo_mo_por_budin']:,.0f} mano de obra "
                    f"= **ARS {met_viab['costo_total_budin']:,.0f}/budín** "
                    f"→ **ARS {met_viab['costo_total_porcion']:,.0f}/porción**"
                )

                # ── Diagnóstico: por qué este resultado ──────────────────
                st.markdown('<p class="section-label" style="margin-top:16px">¿Por qué este resultado?</p>',
                            unsafe_allow_html=True)

                ppp = CAPACIDAD["porciones_por_budin"]
                costo_por_porcion = met_viab["costo_total_porcion"]
                margen_por_porcion = precio_venta - costo_por_porcion
                margen_por_budin = margen_por_porcion * ppp
                budines_vendidos_mes = int(met_viab["budines_por_mes"] * aceptacion / 100)

                if margen_por_porcion <= 0:
                    st.error(
                        f"**Causa: el costo por porcion supera el precio de venta por porcion.** "
                        f"Producir 1 budin cuesta ARS {met_viab['costo_total_budin']:,.0f} "
                        f"(ARS {met_viab['costo_mp_base']:,.0f} materias primas + "
                        f"ARS {met_viab['costo_mo_por_budin']:,.0f} mano de obra). "
                        f"Dividido en {ppp} porciones: ARS {costo_por_porcion:,.0f} por porcion. "
                        f"El precio de venta es ARS {precio_venta:,} por porcion. "
                        f"Cada porcion vendida genera una perdida de ARS {abs(margen_por_porcion):,.0f}. "
                        f"El precio debe superar ARS {costo_por_porcion:,.0f} por porcion para ser viable."
                    )
                else:
                    pe_budines = int(costos_fijos / margen_por_budin) + 1 if margen_por_budin > 0 else 0
                    if budines_vendidos_mes < pe_budines:
                        st.warning(
                            f"**Causa: el volumen vendido no alcanza el punto de equilibrio.** "
                            f"El margen por porcion es ARS {margen_por_porcion:,.0f} "
                            f"(ARS {precio_venta:,} precio - ARS {costo_por_porcion:,.0f} costo). "
                            f"Por budin completo ({ppp} porciones): ARS {margen_por_budin:,.0f} de margen. "
                            f"Para cubrir costos fijos de ARS {costos_fijos:,.0f}/mes "
                            f"se necesitan vender **{pe_budines} budines/mes**. "
                            f"Con {met_viab['budines_por_mes']} budines producidos y {aceptacion}% de aceptacion "
                            f"se venden solo **{budines_vendidos_mes}** "
                            f"(faltan {pe_budines - budines_vendidos_mes} budines para el equilibrio). "
                            f"Aumentar dias de produccion, precio por porcion o aceptacion sensorial mejoraria el resultado."
                        )
                    else:
                        st.success(
                            f"**El producto es rentable en estas condiciones.** "
                            f"Margen de ARS {margen_por_porcion:,.0f} por porcion "
                            f"(ARS {margen_por_budin:,.0f} por budin completo). "
                            f"Se venden {budines_vendidos_mes} budines/mes. "
                            f"Los costos fijos se cubren con {pe_budines} budines "
                            f"y los {budines_vendidos_mes - pe_budines} restantes son ganancia neta."
                        )

                st.info(f"Recomendacion: {met_viab['recomendacion']}")

                # Histograma de ganancia
                fig_gan = grafico_histograma(
                    datos=df_viab["Ganancia ($)"].tolist(),
                    titulo="Distribución de ganancia mensual (Monte Carlo)",
                    etiqueta_x="Ganancia ($)",
                    color=COLORES["principal"],
                    linea_vertical=0,
                    etiqueta_linea="Punto de corte (0)",
                )

                # Punto de equilibrio visual
                max_uds = int(met_viab["budines_por_mes"] * 1.5) or 1000
                uds_range = list(range(0, max_uds, max(1, max_uds // 100)))
                costo_total_unit = met_viab["costo_total_budin"]
                ingresos_range = [u * precio_venta * CAPACIDAD["porciones_por_budin"] for u in uds_range]
                costos_range = [u * costo_total_unit + costos_fijos for u in uds_range]
                pe_val = met_viab["punto_equilibrio_promedio"]

                fig_pe = grafico_punto_equilibrio(
                    unidades=uds_range,
                    ingresos=ingresos_range,
                    costos=costos_range,
                    punto_equilibrio=pe_val,
                )

                st.plotly_chart(fig_gan, use_container_width=True)
                st.plotly_chart(fig_pe, use_container_width=True)

                # Desglose de costos de materia prima
                with st.expander("Ver desglose de costo de materia prima"):
                    df_mp = pd.DataFrame({
                        "Ingrediente": list(desglose_mp.keys()),
                        "Costo ($)": [round(v, 2) for v in desglose_mp.values()],
                    }).sort_values("Costo ($)", ascending=False)
                    st.dataframe(df_mp, use_container_width=True)

                with st.expander("Ver tabla de iteraciones (primeras 100)"):
                    st.dataframe(df_viab.head(100), use_container_width=True)

        elif st.session_state["metricas_viabilidad"] is None:
            st.info("Configurá los parámetros y presioná **▶ Simular viabilidad**.")

    # Comparación de escenarios
    st.divider()
    st.subheader("Comparación de Escenarios")
    if st.button("▶ Comparar los 3 escenarios", key="cmp_viab"):
        escenarios3 = escenarios_viabilidad()
        nombres3, ingresos_esc, costos_esc, ganancias_esc = [], [], [], []

        for clave, esc in escenarios3.items():
            p = {k: v for k, v in esc.items() if k not in ("nombre", "descripcion")}
            p["budines_por_lote"] = CAPACIDAD["budines_por_lote"]
            p["porciones_por_budin"] = CAPACIDAD["porciones_por_budin"]
            p["dias_produccion_mes"] = COMERCIAL["dias_produccion_mes"]
            p["costo_mano_obra_budin"] = COMERCIAL["costo_mano_obra_budin"]
            _, m = simular_viabilidad(**p)
            nombres3.append(esc["nombre"])
            budines_mes = m["budines_por_mes"]
            budines_vendidos = budines_mes * esc["aceptacion_sensorial_pct"] / 100
            # ingreso = porciones vendidas × precio por porción
            ingreso_prom = budines_vendidos * CAPACIDAD["porciones_por_budin"] * esc["precio_venta"]
            costo_var = budines_vendidos * m["costo_total_budin"]
            ingresos_esc.append(round(ingreso_prom))
            costos_esc.append(round(costo_var + esc["costos_fijos_mensuales"]))
            ganancias_esc.append(round(m["ganancia_promedio"]))

        fig_esc = grafico_escenarios(
            escenarios=nombres3,
            ingresos=ingresos_esc,
            costos=costos_esc,
            ganancias=ganancias_esc,
        )
        st.plotly_chart(fig_esc, use_container_width=True)

        # Tabla resumen
        df_resumen = pd.DataFrame({
            "Escenario": nombres3,
            "Ingreso estimado ($)": ingresos_esc,
            "Costo total ($)": costos_esc,
            "Ganancia prom. ($)": ganancias_esc,
        })
        st.dataframe(df_resumen, use_container_width=True)


# ═════════════════════════════════════════
# TAB 4 — LÍNEA DE PRODUCCIÓN
# ═════════════════════════════════════════
with tab4:
    st.markdown('<p class="section-label">Proceso Productivo · Budín Nutritivo</p>', unsafe_allow_html=True)
    st.header("Línea de Producción")
    st.markdown("Visualización del flujo productivo: etapas del proceso, tiempos y capacidad por jornada.")

    col_gantt, col_etapas = st.columns([2, 1], gap="large")

    # Etapas del proceso con tiempos desde parametros.py
    ETAPAS = [
        ("Preparación",      TIEMPOS["preparacion_min"],       TIEMPOS["preparacion_max"],       "🔪"),
        ("Cocción lentejas", TIEMPOS["coccion_lentejas_min"],  TIEMPOS["coccion_lentejas_max"],  "🫕"),
        ("Mezclado",         TIEMPOS["mezclado_min"],          TIEMPOS["mezclado_max"],          "🥣"),
        ("Horneado",         TIEMPOS["horneado_min"],          TIEMPOS["horneado_max"],          "🔥"),
        ("Enfriado",         TIEMPOS["enfriado_min"],          TIEMPOS["enfriado_max"],          "❄️"),
        ("Envasado",         TIEMPOS["envasado_min"],          TIEMPOS["envasado_max"],          "📦"),
    ]

    with col_etapas:
        st.markdown('<p class="section-label">Etapas del proceso</p>', unsafe_allow_html=True)
        tiempo_total_prom = 0
        for i, (nombre, t_min, t_max, icono) in enumerate(ETAPAS, 1):
            prom = (t_min + t_max) / 2
            tiempo_total_prom += prom
            st.markdown(f"""
            <div class="etapa-card">
                <div class="etapa-num">{i}</div>
                <div class="etapa-info">
                    <div class="etapa-nombre">{icono} {nombre}</div>
                    <div class="etapa-tiempo">{t_min}–{t_max} min</div>
                </div>
                <div class="etapa-dur">{prom:.0f} min</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        ma, mb = st.columns(2)
        ma.metric("Tiempo total prom.", f"{tiempo_total_prom:.0f} min")
        mb.metric("Budines por lote", CAPACIDAD["budines_por_lote"])

        st.markdown('<p class="section-label" style="margin-top:16px">Ingredientes</p>', unsafe_allow_html=True)
        ingredientes_labels = {
            "lentejas_cocidas_g": "Lentejas cocidas",
            "harina_avena_g": "Harina de avena",
            "zucchini_rallado_g": "Zucchini rallado",
            "manzana_rallada_g": "Manzana rallada",
            "huevos_unidades": "Huevos",
            "cacao_amargo_g": "Cacao amargo",
            "miel_g": "Miel / azúcar mascabo",
            "polvo_hornear_g": "Polvo de hornear",
            "esencia_vainilla_ml": "Esencia de vainilla",
            "aceite_ml": "Aceite vegetal",
        }
        unidades = {
            "lentejas_cocidas_g": "g", "harina_avena_g": "g", "zucchini_rallado_g": "g",
            "manzana_rallada_g": "g", "huevos_unidades": "ud", "cacao_amargo_g": "g",
            "miel_g": "g", "polvo_hornear_g": "g", "esencia_vainilla_ml": "ml", "aceite_ml": "ml",
        }
        for clave, label in ingredientes_labels.items():
            valor = RECETA[clave]
            ud = unidades[clave]
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;padding:5px 0;
                        border-bottom:1px solid #E2D3C0;font-size:0.85rem;">
                <span style="color:#2C1810;">{label}</span>
                <span style="color:#C9952A;font-weight:700;">{valor} {ud}</span>
            </div>""", unsafe_allow_html=True)

    with col_gantt:
        st.markdown('<p class="section-label">Flujo del proceso productivo</p>', unsafe_allow_html=True)

        fig_flujo = grafico_flujo_produccion([
            {"nombre": nombre, "tiempo_min": t_min, "tiempo_max": t_max, "icono": icono}
            for nombre, t_min, t_max, icono in ETAPAS
        ])
        st.plotly_chart(fig_flujo, use_container_width=True)

        # Tabla de tiempos por etapa
        st.markdown('<p class="section-label" style="margin-top:16px">Tiempos por etapa</p>',
                    unsafe_allow_html=True)
        df_tiempos = pd.DataFrame([
            {
                "Etapa": f"{icono} {nombre}",
                "Mín (min)": t_min,
                "Máx (min)": t_max,
                "Promedio (min)": round((t_min + t_max) / 2, 1),
            }
            for nombre, t_min, t_max, icono in ETAPAS
        ])
        st.dataframe(df_tiempos, use_container_width=True, hide_index=True)

        # Métricas de capacidad
        st.markdown('<p class="section-label" style="margin-top:16px">Capacidad productiva</p>',
                    unsafe_allow_html=True)
        tiempo_ciclo = sum((t_min + t_max) / 2 for _, t_min, t_max, _ in ETAPAS)
        lotes_por_jornada = int((CAPACIDAD["jornada_horas"] * 60) / tiempo_ciclo)
        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("Tiempo de ciclo", f"{tiempo_ciclo:.0f} min")
        mc2.metric("Lotes / jornada", lotes_por_jornada)
        mc3.metric("Budines / jornada", lotes_por_jornada * CAPACIDAD["budines_por_lote"])


# ─────────────────────────────────────────
# SIDEBAR — DESCARGA DE INFORME
# ─────────────────────────────────────────
with st.sidebar:
    st.header("📄 Informe Académico")
    st.markdown("Generá y descargá el informe Markdown con los resultados de las simulaciones ejecutadas.")

    sims_ejecutadas = sum([
        st.session_state["metricas_flujo"] is not None,
        st.session_state["metricas_stock"] is not None,
        st.session_state["metricas_viabilidad"] is not None,
    ])

    if sims_ejecutadas == 0:
        st.info("Ejecutá al menos una simulación para habilitar el informe.")
    else:
        st.success(f"{sims_ejecutadas}/3 simuladores ejecutados.")

        informe_md = generar_informe(
            metricas_flujo=st.session_state["metricas_flujo"],
            metricas_stock=st.session_state["metricas_stock"],
            metricas_viabilidad=st.session_state["metricas_viabilidad"],
            params_flujo=st.session_state["params_flujo"],
            params_stock=st.session_state["params_stock"],
            params_viabilidad=st.session_state["params_viabilidad"],
        )

        st.download_button(
            label="⬇️ Descargar informe (.md)",
            data=informe_md.encode("utf-8"),
            file_name="informe_budin_nutritivo.md",
            mime="text/markdown",
            use_container_width=True,
        )

    st.divider()
    st.caption("Grupo 3 · UCP · 2026")
    st.caption("Modelos y Simulación / ISI III")
