import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# ─────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Simulador - Budín Nutritivo",
    page_icon="🍞",
    layout="wide"
)

# ─────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────
st.title("🍞 Simulador de Producción Masiva")
st.subheader("Budín Nutritivo de Lentejas, Manzana y Zucchini")
st.caption("Universidad de la Cuenca del Plata · ISI 4to Año · Modelos y Simulación · Grupo 3 · 2026")
st.divider()

# ─────────────────────────────────────────
# TABS
# ─────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "👥 Flujo de Personas",
    "📦 Stock de Porciones",
    "💰 Viabilidad Comercial"
])

with tab1:
    st.header("Simulador de Flujo de Personas y Formulario Digital")
    st.info("Próximamente")

with tab2:
    st.header("Simulador de Stock de Porciones")
    st.info("Próximamente")

with tab3:
    st.header("Simulador de Viabilidad Productiva y Comercial")
    st.info("Próximamente")