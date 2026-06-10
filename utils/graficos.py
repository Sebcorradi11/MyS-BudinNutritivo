# utils/graficos.py
# Funciones reutilizables para generar gráficos con Plotly
# Universidad de la Cuenca del Plata · ISI 4to Año · Grupo 3 · 2026

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

# ─────────────────────────────────────────
# PALETA DE COLORES DEL PROYECTO
# ─────────────────────────────────────────
COLORES = {
    "optimista": "#27AE60",
    "esperado": "#F39C12",
    "pesimista": "#E74C3C",
    "principal": "#3498DB",
    "secundario": "#9B59B6",
    "neutro": "#95A5A6",
    "fondo": "#F8F9FA",
}

COLORES_ETAPAS = {
    "Preparación": "#3498DB",
    "Cocción": "#E67E22",
    "Mezclado": "#2ECC71",
    "Espera": "#95A5A6",
    "Horneado": "#E74C3C",
    "Enfriado": "#9B59B6",
    "Envasado": "#1ABC9C",
}

# ─────────────────────────────────────────
# GRÁFICO DE BARRAS
# ─────────────────────────────────────────
def grafico_barras(
    categorias: list,
    valores: list,
    titulo: str,
    etiqueta_x: str = "",
    etiqueta_y: str = "",
    colores: list = None,
) -> go.Figure:
    """
    Gráfico de barras simple.
    """
    fig = go.Figure(data=[
        go.Bar(
            x=categorias,
            y=valores,
            marker_color=colores or COLORES["principal"],
            text=[f"{v:,.0f}" for v in valores],
            textposition="outside",
        )
    ])
    fig.update_layout(
        title=titulo,
        xaxis_title=etiqueta_x,
        yaxis_title=etiqueta_y,
        height=400,
        margin=dict(l=20, r=20, t=50, b=40),
        plot_bgcolor=COLORES["fondo"],
    )
    return fig


# ─────────────────────────────────────────
# GRÁFICO DE TORTA
# ─────────────────────────────────────────
def grafico_torta(
    etiquetas: list,
    valores: list,
    titulo: str,
) -> go.Figure:
    """
    Gráfico de torta con agujero (donut).
    """
    fig = go.Figure(data=[go.Pie(
        labels=etiquetas,
        values=valores,
        hole=0.4,
        textinfo="label+percent",
        marker_colors=px.colors.qualitative.Set3,
    )])
    fig.update_layout(
        title=titulo,
        height=400,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    return fig


# ─────────────────────────────────────────
# GRÁFICO DE RADAR (ANÁLISIS SENSORIAL)
# ─────────────────────────────────────────
def grafico_radar(
    descriptores: list,
    valores: list,
    titulo: str,
) -> go.Figure:
    """
    Gráfico de araña para resultados del análisis sensorial.
    Cierra el polígono repitiendo el primer valor al final.
    """
    fig = go.Figure(data=go.Scatterpolar(
        r=valores + [valores[0]],
        theta=descriptores + [descriptores[0]],
        fill="toself",
        fillcolor="rgba(52, 152, 219, 0.3)",
        line_color=COLORES["principal"],
        name="Promedio",
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
        title=titulo,
        height=400,
        margin=dict(l=40, r=40, t=50, b=40),
    )
    return fig


# ─────────────────────────────────────────
# GRÁFICO DE HISTOGRAMA (MONTE CARLO)
# ─────────────────────────────────────────
def grafico_histograma(
    datos: list,
    titulo: str,
    etiqueta_x: str = "",
    color: str = None,
    linea_vertical: float = None,
    etiqueta_linea: str = "",
) -> go.Figure:
    """
    Histograma para mostrar distribución de resultados Monte Carlo.
    Opcionalmente dibuja una línea vertical (ej: punto de equilibrio).
    """
    fig = go.Figure(data=[
        go.Histogram(
            x=datos,
            nbinsx=30,
            marker_color=color or COLORES["principal"],
            opacity=0.8,
        )
    ])

    if linea_vertical is not None:
        fig.add_vline(
            x=linea_vertical,
            line_dash="dash",
            line_color=COLORES["pesimista"],
            annotation_text=etiqueta_linea,
            annotation_position="top right",
        )

    fig.update_layout(
        title=titulo,
        xaxis_title=etiqueta_x,
        yaxis_title="Frecuencia",
        height=400,
        margin=dict(l=20, r=20, t=50, b=40),
        plot_bgcolor=COLORES["fondo"],
    )
    return fig


# ─────────────────────────────────────────
# GRÁFICO DE PUNTO DE EQUILIBRIO
# ─────────────────────────────────────────
def grafico_punto_equilibrio(
    unidades: list,
    ingresos: list,
    costos: list,
    punto_equilibrio: float,
) -> go.Figure:
    """
    Gráfico de líneas que muestra ingresos vs costos totales
    con el punto de equilibrio marcado.
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=unidades, y=ingresos,
        name="Ingresos",
        line=dict(color=COLORES["optimista"], width=2),
    ))
    fig.add_trace(go.Scatter(
        x=unidades, y=costos,
        name="Costos Totales",
        line=dict(color=COLORES["pesimista"], width=2),
    ))

    if punto_equilibrio and punto_equilibrio != float("inf"):
        pe_y = punto_equilibrio * (ingresos[-1] / unidades[-1])
        fig.add_trace(go.Scatter(
            x=[punto_equilibrio], y=[pe_y],
            mode="markers",
            name="Punto de equilibrio",
            marker=dict(size=12, color=COLORES["esperado"]),
        ))

    fig.update_layout(
        title="Punto de Equilibrio",
        xaxis_title="Unidades producidas",
        yaxis_title="Pesos ($)",
        height=400,
        margin=dict(l=20, r=20, t=50, b=40),
        plot_bgcolor=COLORES["fondo"],
    )
    return fig


# ─────────────────────────────────────────
# GRÁFICO DE COMPARACIÓN DE ESCENARIOS
# ─────────────────────────────────────────
def grafico_escenarios(
    escenarios: list,
    ingresos: list,
    costos: list,
    ganancias: list,
) -> go.Figure:
    """
    Gráfico de barras agrupadas para comparar los tres escenarios.
    """
    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="Ingresos",
        x=escenarios,
        y=ingresos,
        marker_color=COLORES["principal"],
    ))
    fig.add_trace(go.Bar(
        name="Costos Totales",
        x=escenarios,
        y=costos,
        marker_color=COLORES["pesimista"],
    ))
    fig.add_trace(go.Bar(
        name="Ganancia",
        x=escenarios,
        y=ganancias,
        marker_color=[
            COLORES["optimista"] if g > 0 else COLORES["pesimista"]
            for g in ganancias
        ],
    ))

    fig.update_layout(
        title="Comparación Financiera por Escenario",
        yaxis_title="Pesos ($)",
        barmode="group",
        height=450,
        margin=dict(l=20, r=20, t=50, b=40),
        plot_bgcolor=COLORES["fondo"],
    )
    return fig


# ─────────────────────────────────────────
# GRÁFICO GANTT (PROCESO PRODUCTIVO)
# ─────────────────────────────────────────
def grafico_gantt(df_lotes: pd.DataFrame, max_lotes: int = 10) -> go.Figure:
    """
    Diagrama de Gantt del proceso productivo por lote.
    df_lotes debe tener columnas: Lote, Inicio, y una columna por etapa.
    """
    fig = go.Figure()

    etapas = ["Preparación", "Cocción", "Mezclado", "Espera", "Horneado", "Enfriado", "Envasado"]

    for _, row in df_lotes.head(max_lotes).iterrows():
        t = row["Inicio"]
        for etapa in etapas:
            if etapa in row and row[etapa] > 0:
                fig.add_trace(go.Bar(
                    name=etapa,
                    y=[f"Lote {int(row['Lote'])}"],
                    x=[row[etapa]],
                    base=[t],
                    orientation="h",
                    marker_color=COLORES_ETAPAS[etapa],
                    showlegend=(_ == 0),
                    hovertemplate=f"<b>{etapa}</b><br>Duración: {row[etapa]:.1f} min<extra></extra>",
                ))
                t += row[etapa]

    fig.update_layout(
        barmode="stack",
        title="Diagrama de Gantt – Proceso Productivo",
        xaxis_title="Tiempo (minutos)",
        yaxis=dict(autorange="reversed"),
        height=400,
        margin=dict(l=80, r=20, t=50, b=40),
        plot_bgcolor=COLORES["fondo"],
    )
    return fig


# ─────────────────────────────────────────
# GANTT DE SIMULACIÓN DE LÍNEA
# ─────────────────────────────────────────
COLORES_ETAPAS_GANTT = {
    "Preparación":      "#3498DB",
    "Cocción lentejas": "#E67E22",
    "Mezclado":         "#2ECC71",
    "Horneado":         "#E74C3C",
    "Enfriado":         "#9B59B6",
    "Envasado":         "#1ABC9C",
}

def grafico_gantt_produccion(df: pd.DataFrame) -> go.Figure:
    """
    Gantt interactivo de la simulación de línea de producción.
    df debe tener columnas: Lote, Etapa, Inicio, Fin, Duración, Espera horno (min).
    """
    ref = pd.Timestamp("2000-01-01")
    df = df.copy()
    df["Start"] = df["Inicio"].apply(lambda x: ref + pd.Timedelta(minutes=x))
    df["Finish"] = df["Fin"].apply(lambda x: ref + pd.Timedelta(minutes=x))
    df["hover"] = df.apply(
        lambda r: (
            f"<b>{r['Etapa']}</b><br>"
            f"Inicio: {r['Inicio']:.1f} min<br>"
            f"Fin: {r['Fin']:.1f} min<br>"
            f"Duración: {r['Duración']:.1f} min"
            + (f"<br>Espera en horno: {r['Espera horno (min)']:.1f} min" if r["Espera horno (min)"] > 0 else "")
        ),
        axis=1,
    )

    fig = px.timeline(
        df,
        x_start="Start",
        x_end="Finish",
        y="Lote",
        color="Etapa",
        color_discrete_map=COLORES_ETAPAS_GANTT,
        custom_data=["hover"],
    )

    fig.update_traces(hovertemplate="%{customdata[0]}<extra></extra>")

    # Convertir etiquetas del eje X a minutos reales
    min_t = df["Inicio"].min()
    max_t = df["Fin"].max()
    tick_step = max(10, int((max_t - min_t) / 10 / 10) * 10)
    tick_vals_min = list(range(0, int(max_t) + tick_step, tick_step))
    tick_vals_dt = [ref + pd.Timedelta(minutes=m) for m in tick_vals_min]

    fig.update_xaxes(
        tickvals=tick_vals_dt,
        ticktext=[f"{m} min" for m in tick_vals_min],
        title="Tiempo desde inicio (min)",
    )
    fig.update_yaxes(autorange="reversed", title="")
    fig.update_layout(
        title="Diagrama de Gantt — Simulación de la línea de producción",
        height=max(300, 80 + df["Lote"].nunique() * 40),
        margin=dict(l=20, r=20, t=50, b=40),
        plot_bgcolor=COLORES["fondo"],
        legend_title="Etapa",
    )
    return fig


# ─────────────────────────────────────────
# DIAGRAMA DE FLUJO DEL PROCESO PRODUCTIVO
# ─────────────────────────────────────────
def grafico_flujo_produccion(etapas: list[dict]) -> go.Figure:
    """
    Pipeline horizontal del proceso productivo.
    Cada etapa es un dict con: nombre, tiempo_min, tiempo_max, icono.
    Muestra cajas conectadas con flechas, colores degradados del marrón al ámbar.
    """
    n = len(etapas)
    fig = go.Figure()

    # Paleta degradada marrón → ámbar en tonos cálidos del proyecto
    paleta = [
        "#3D2010", "#5C3317", "#7A4520", "#9A5C28",
        "#B87030", "#C9952A", "#D4A843",
    ]
    colores = [paleta[i % len(paleta)] for i in range(n)]

    box_w = 0.12      # ancho relativo de cada caja (en coordenadas 0-1)
    box_h = 0.45      # alto de cada caja
    gap   = 0.015     # espacio entre caja y flecha
    y_center = 0.5

    # Espaciado horizontal uniforme
    total = n * box_w + (n - 1) * (gap * 2 + 0.03)
    x_start = (1 - total) / 2

    posiciones = []
    x = x_start
    for i in range(n):
        posiciones.append(x)
        x += box_w + gap * 2 + 0.03

    # Cajas
    for i, (etapa, color, xp) in enumerate(zip(etapas, colores, posiciones)):
        prom = (etapa["tiempo_min"] + etapa["tiempo_max"]) / 2

        # Rectángulo relleno
        fig.add_shape(
            type="rect",
            x0=xp, x1=xp + box_w,
            y0=y_center - box_h / 2, y1=y_center + box_h / 2,
            fillcolor=color,
            line=dict(color="#FAF6F1", width=2),
            layer="below",
        )

        # Número de etapa (arriba)
        fig.add_annotation(
            x=xp + box_w / 2, y=y_center + box_h / 2 - 0.04,
            text=f"<b>{i + 1}</b>",
            showarrow=False,
            font=dict(size=11, color="#FAF6F1", family="Arial"),
            xanchor="center",
        )
        # Icono + nombre
        fig.add_annotation(
            x=xp + box_w / 2, y=y_center + 0.04,
            text=f"<b>{etapa['icono']}<br>{etapa['nombre']}</b>",
            showarrow=False,
            font=dict(size=10, color="#FAF6F1", family="Arial"),
            xanchor="center",
            align="center",
        )
        # Tiempo promedio (abajo)
        fig.add_annotation(
            x=xp + box_w / 2, y=y_center - box_h / 2 + 0.06,
            text=f"{prom:.0f} min",
            showarrow=False,
            font=dict(size=10, color="#FAD090", family="Arial"),
            xanchor="center",
        )

        # Flecha hacia la siguiente caja
        if i < n - 1:
            x_arrow_start = xp + box_w + gap
            x_arrow_end   = posiciones[i + 1] - gap
            fig.add_annotation(
                x=x_arrow_end, y=y_center,
                ax=x_arrow_start, ay=y_center,
                xref="x", yref="y", axref="x", ayref="y",
                showarrow=True,
                arrowhead=2,
                arrowsize=1.2,
                arrowwidth=2,
                arrowcolor="#C9952A",
            )

    fig.update_layout(
        xaxis=dict(visible=False, range=[0, 1]),
        yaxis=dict(visible=False, range=[0, 1]),
        plot_bgcolor="#FAF6F1",
        paper_bgcolor="#FAF6F1",
        height=220,
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
    )
    return fig