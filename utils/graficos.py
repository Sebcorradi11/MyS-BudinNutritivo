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