import streamlit as st
import numpy as np
import pandas as pd

from datos.parametros import EVENTO, CAPACIDAD, COMERCIAL
from simuladores.flujo_personas import simular_flujo, escenarios_flujo
from simuladores.stock_porciones import simular_stock, escenarios_stock
from simuladores.viabilidad import simular_viabilidad, escenarios_viabilidad, calcular_costo_materia_prima
from utils.verificacion import verificar_tiempos, verificar_positivo, mostrar_errores
from utils.graficos import (
    grafico_histograma,
    grafico_barras,
    grafico_escenarios,
    grafico_punto_equilibrio,
    COLORES,
)
from utils.informe import generar_informe

# ─────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Simulador — Budín Nutritivo",
    page_icon="🍞",
    layout="wide",
)

# ─────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────
st.title("🍞 Simulador de Producción Masiva")
st.subheader("Budín Nutritivo de Lentejas, Manzana y Zucchini")
st.caption("Universidad de la Cuenca del Plata · ISI 4to Año · Modelos y Simulación · Grupo 3 · 2026")
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
tab1, tab2, tab3 = st.tabs([
    "👥 Flujo de Personas",
    "📦 Stock de Porciones",
    "💰 Viabilidad Comercial",
])


# ═════════════════════════════════════════
# TAB 1 — FLUJO DE PERSONAS
# ═════════════════════════════════════════
with tab1:
    st.header("Simulador de Flujo de Personas y Formulario Digital")
    st.markdown("**Modelo:** Simulación de eventos discretos · Estima saturación del sistema durante el evento.")

    col_params, col_resultados = st.columns([1, 2])

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
        c1, c2 = st.columns(2)
        tasa_min = c1.number_input("Mín", min_value=0.1, max_value=20.0,
                                    value=float(EVENTO["tasa_llegada_personas_min"]),
                                    step=0.5, key="tasa_min")
        tasa_max = c2.number_input("Máx", min_value=0.1, max_value=20.0,
                                    value=float(EVENTO["tasa_llegada_personas_max"]),
                                    step=0.5, key="tasa_max")

        st.markdown("**Tiempo de degustación (min)**")
        c3, c4 = st.columns(2)
        deg_min = c3.number_input("Mín", min_value=0.5, max_value=30.0,
                                   value=float(EVENTO["tiempo_degustacion_min"]),
                                   step=0.5, key="deg_min")
        deg_max = c4.number_input("Máx", min_value=0.5, max_value=30.0,
                                   value=float(EVENTO["tiempo_degustacion_max"]),
                                   step=0.5, key="deg_max")

        st.markdown("**Tiempo de formulario QR (min)**")
        c5, c6 = st.columns(2)
        form_min = c5.number_input("Mín", min_value=0.5, max_value=30.0,
                                    value=float(EVENTO["tiempo_formulario_min"]),
                                    step=0.5, key="form_min")
        form_max = c6.number_input("Máx", min_value=0.5, max_value=30.0,
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

                # Métricas principales
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Duración evento", f"{met_flujo['tiempo_total_evento']} min")
                m2.metric("Tiempo prom. sistema", f"{met_flujo['tiempo_promedio_sistema']} min")
                m3.metric("Con espera", f"{met_flujo['comensales_con_espera']} personas")
                m4.metric("Saturación", met_flujo["saturacion"],
                          delta=f"{met_flujo['pct_saturacion']}%",
                          delta_color="inverse")

                st.info(f"💡 {met_flujo['recomendacion']}")

                # Gráfico distribución tiempos
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
                gc1, gc2 = st.columns(2)
                gc1.plotly_chart(fig_deg, use_container_width=True)
                gc2.plotly_chart(fig_form, use_container_width=True)

                # Tabla detalle (colapsable)
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
        sc1, sc2 = st.columns(2)
        sc1.plotly_chart(fig_sat, use_container_width=True)
        sc2.plotly_chart(fig_dur, use_container_width=True)


# ═════════════════════════════════════════
# TAB 2 — STOCK DE PORCIONES
# ═════════════════════════════════════════
with tab2:
    st.header("Simulador de Stock de Porciones")
    st.markdown("**Modelo:** Monte Carlo · Estima probabilidad de quiebre de stock y desperdicio.")

    col_params2, col_resultados2 = st.columns([1, 2])

    with col_params2:
        st.subheader("Parámetros")

        comensales_esp = st.number_input(
            "Comensales esperados", min_value=10, max_value=500,
            value=EVENTO["comensales_esperados"], step=5, key="s_com",
        )
        budines_lote = st.number_input(
            "Budines por lote", min_value=1, max_value=50,
            value=CAPACIDAD["budines_por_lote"], step=1, key="s_bl",
        )
        lotes_preparados = st.number_input(
            "Lotes a preparar", min_value=1, max_value=200,
            value=15, step=1, key="s_lp",
        )

        st.markdown("**% de consumo esperado**")
        cs1, cs2 = st.columns(2)
        pct_min = cs1.slider("Mín %", min_value=10, max_value=100, value=70, step=5, key="pct_min") / 100
        pct_max = cs2.slider("Máx %", min_value=10, max_value=100, value=90, step=5, key="pct_max") / 100

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
                    lotes_preparados=lotes_preparados,
                    iteraciones=iteraciones_s,
                )
                with st.spinner("Simulando..."):
                    df_stock, met_stock = simular_stock(**params2)

                st.session_state["metricas_stock"] = met_stock
                st.session_state["params_stock"] = params2

                # Métricas principales
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Porciones disponibles", met_stock["total_porciones"])
                m2.metric("Demanda promedio", f"{met_stock['demanda_promedio']} uds")
                m3.metric("Prob. quiebre", f"{met_stock['prob_quiebre']}%",
                          delta_color="inverse")
                m4.metric("Lotes recomendados", met_stock["lotes_recomendados"])

                viabilidad_color = "success" if met_stock["prob_quiebre"] < 10 else \
                                   "warning" if met_stock["prob_quiebre"] < 30 else "error"
                getattr(st, viabilidad_color)(f"💡 {met_stock['recomendacion']}")

                # Histogramas
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
                gc1, gc2 = st.columns(2)
                gc1.plotly_chart(fig_dem, use_container_width=True)
                gc2.plotly_chart(fig_desp, use_container_width=True)

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
        sc1, sc2 = st.columns(2)
        sc1.plotly_chart(fig_pq, use_container_width=True)
        sc2.plotly_chart(fig_dp, use_container_width=True)


# ═════════════════════════════════════════
# TAB 3 — VIABILIDAD COMERCIAL
# ═════════════════════════════════════════
with tab3:
    st.header("Simulador de Viabilidad Productiva y Comercial")
    st.markdown("**Modelo:** Monte Carlo económico · Estima rentabilidad, punto de equilibrio y probabilidad de viabilidad.")

    # Costo base de materia prima (informativo)
    costo_mp_base, desglose_mp = calcular_costo_materia_prima()
    st.info(f"Costo base de materia prima por budín: **${costo_mp_base:,.0f} ARS** (calculado a partir de la receta y precios de referencia)")

    col_params3, col_resultados3 = st.columns([1, 2])

    with col_params3:
        st.subheader("Parámetros")

        lotes_dia = st.number_input(
            "Lotes por día", min_value=1, max_value=50,
            value=COMERCIAL["lotes_por_dia"], step=1, key="v_ld",
        )
        dias_mes = st.number_input(
            "Días de producción por mes", min_value=1, max_value=31,
            value=COMERCIAL["dias_produccion_mes"], step=1, key="v_dm",
        )
        precio_venta = st.number_input(
            "Precio de venta por budín ($)", min_value=500, max_value=50000,
            value=4500, step=100, key="v_pv",
        )
        costos_fijos = st.number_input(
            "Costos fijos mensuales ($)", min_value=0, max_value=1000000,
            value=COMERCIAL["costos_fijos_mensuales"], step=5000, key="v_cf",
        )
        costo_mo = st.number_input(
            "Costo mano de obra ($/hora)", min_value=0, max_value=50000,
            value=COMERCIAL["costo_mano_obra_hora"], step=100, key="v_mo",
        )
        margen_var = st.slider(
            "Variación de costos ±%", min_value=0, max_value=50,
            value=15, step=1, key="v_mv",
        )
        aceptacion = st.slider(
            "Aceptación sensorial esperada (%)", min_value=10, max_value=100,
            value=65, step=5, key="v_as",
        )
        iteraciones_v = st.select_slider(
            "Iteraciones Monte Carlo",
            options=[100, 500, 1000, 5000, 10000],
            value=1000, key="iter_v",
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
                    dias_produccion_mes=dias_mes,
                    precio_venta=float(precio_venta),
                    costos_fijos_mensuales=float(costos_fijos),
                    costo_mano_obra_hora=float(costo_mo),
                    margen_variacion_costos_pct=float(margen_var),
                    aceptacion_sensorial_pct=float(aceptacion),
                    iteraciones=iteraciones_v,
                )
                with st.spinner("Simulando..."):
                    df_viab, met_viab = simular_viabilidad(**params3)

                st.session_state["metricas_viabilidad"] = met_viab
                st.session_state["params_viabilidad"] = params3

                # Métricas principales
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Viabilidad", met_viab["viabilidad"])
                m2.metric("Prob. viable", f"{met_viab['prob_viabilidad']}%")
                ganancia_prom = met_viab["ganancia_promedio"]
                m3.metric("Ganancia prom./mes",
                          f"${ganancia_prom:,.0f}",
                          delta_color="normal" if ganancia_prom >= 0 else "inverse")
                m4.metric("Punto de equilibrio", f"{met_viab['punto_equilibrio_promedio']:,.0f} uds")

                st.info(f"💡 {met_viab['recomendacion']}")

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
                ingresos_range = [u * precio_venta for u in uds_range]
                costos_range = [u * costo_total_unit + costos_fijos for u in uds_range]
                pe_val = met_viab["punto_equilibrio_promedio"]

                fig_pe = grafico_punto_equilibrio(
                    unidades=uds_range,
                    ingresos=ingresos_range,
                    costos=costos_range,
                    punto_equilibrio=pe_val,
                )

                gc1, gc2 = st.columns(2)
                gc1.plotly_chart(fig_gan, use_container_width=True)
                gc2.plotly_chart(fig_pe, use_container_width=True)

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
            p["dias_produccion_mes"] = COMERCIAL["dias_produccion_mes"]
            p["costo_mano_obra_hora"] = COMERCIAL["costo_mano_obra_hora"]
            _, m = simular_viabilidad(**p)
            nombres3.append(esc["nombre"])
            budines_mes = m["budines_por_mes"]
            precio_esc = esc["precio_venta"]
            ingreso_prom = budines_mes * precio_esc * (esc["aceptacion_sensorial_pct"] / 100)
            costo_var = budines_mes * m["costo_total_budin"]
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
