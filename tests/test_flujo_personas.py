import pytest
from simuladores.flujo_personas import simular_flujo, escenarios_flujo


PARAMS_BASE = dict(
    comensales=60,
    tasa_llegada_min=1,
    tasa_llegada_max=3,
    t_degustacion_min=3,
    t_degustacion_max=7,
    t_formulario_min=2,
    t_formulario_max=5,
    capacidad_sistema=15,
)


# ── Estructura de salida ───────────────────────────────────────────────────────

def test_retorna_dataframe_y_dict():
    import pandas as pd
    df, met = simular_flujo(**PARAMS_BASE)
    assert isinstance(df, pd.DataFrame)
    assert isinstance(met, dict)

def test_dataframe_tiene_columnas_esperadas():
    df, _ = simular_flujo(**PARAMS_BASE)
    columnas = {"Comensal", "Llegada (min)", "Espera (min)",
                "Degustación (min)", "Formulario (min)",
                "Tiempo total (min)", "Salida (min)"}
    assert columnas.issubset(set(df.columns))

def test_dataframe_tiene_fila_por_comensal():
    df, _ = simular_flujo(**PARAMS_BASE)
    assert len(df) == PARAMS_BASE["comensales"]

def test_metricas_tienen_claves_esperadas():
    _, met = simular_flujo(**PARAMS_BASE)
    claves = {"comensales", "tiempo_total_evento", "tiempo_promedio_sistema",
              "tiempo_promedio_formulario", "comensales_con_espera",
              "pct_saturacion", "saturacion", "recomendacion",
              "pico_concurrencia", "capacidad_sistema"}
    assert claves.issubset(set(met.keys()))

def test_pico_concurrencia_no_supera_comensales_minus_one():
    # El pico es cuántos estaban antes que el que llega; máximo comensales-1
    _, met = simular_flujo(**PARAMS_BASE)
    assert met["pico_concurrencia"] <= PARAMS_BASE["comensales"] - 1

def test_pico_alto_con_llegada_rapida_y_servicio_lento():
    """Alta tasa de llegada + servicio largo = pico de concurrencia alto."""
    params = {**PARAMS_BASE,
              "tasa_llegada_min": 10, "tasa_llegada_max": 15,
              "t_degustacion_min": 10, "t_degustacion_max": 15,
              "t_formulario_min": 8, "t_formulario_max": 12,
              "capacidad_sistema": 999}
    _, met = simular_flujo(**params)
    assert met["pico_concurrencia"] > 10, "Con llegada rápida y servicio lento el pico debe ser alto"

def test_pico_concurrencia_positivo():
    _, met = simular_flujo(**PARAMS_BASE)
    assert met["pico_concurrencia"] >= 1

def test_pico_no_supera_capacidad_con_espera():
    """Si hay esperas, el pico debe haber alcanzado la capacidad."""
    params = {**PARAMS_BASE, "capacidad_sistema": 3}
    _, met = simular_flujo(**params)
    if met["comensales_con_espera"] > 0:
        assert met["pico_concurrencia"] >= 3


# ── Corrección del bug de intervalo de llegada ─────────────────────────────────

def test_duracion_evento_razonable():
    """Con 60 comensales y tasa 1-3/min el evento debe durar menos de 120 min."""
    _, met = simular_flujo(**PARAMS_BASE)
    assert met["tiempo_total_evento"] < 120, (
        f"Duración {met['tiempo_total_evento']} min es demasiado larga (bug de intervalo)"
    )

def test_duracion_evento_no_negativa():
    _, met = simular_flujo(**PARAMS_BASE)
    assert met["tiempo_total_evento"] > 0

def test_llegadas_son_crecientes():
    """Los tiempos de llegada deben ser estrictamente crecientes."""
    df, _ = simular_flujo(**PARAMS_BASE)
    llegadas = df["Llegada (min)"].tolist()
    assert all(llegadas[i] < llegadas[i + 1] for i in range(len(llegadas) - 1))


# ── Saturación ────────────────────────────────────────────────────────────────

def test_saturacion_alta_con_capacidad_minima():
    """Con capacidad=1 casi todos deberían esperar."""
    params = {**PARAMS_BASE, "capacidad_sistema": 1}
    _, met = simular_flujo(**params)
    assert met["comensales_con_espera"] > 0, "Con capacidad=1 debe haber esperas"
    assert met["pct_saturacion"] > 0

def test_sin_espera_con_capacidad_maxima():
    """Con capacidad enorme nadie debería esperar."""
    params = {**PARAMS_BASE, "capacidad_sistema": 9999}
    df, met = simular_flujo(**params)
    assert met["comensales_con_espera"] == 0
    assert all(df["Espera (min)"] == 0)

def test_saturacion_clasificada_correctamente():
    _, met = simular_flujo(**PARAMS_BASE)
    assert met["saturacion"] in ("Alta", "Media", "Baja")


# ── Reproducibilidad ──────────────────────────────────────────────────────────

def test_misma_semilla_mismo_resultado():
    _, met1 = simular_flujo(**PARAMS_BASE, semilla=42)
    _, met2 = simular_flujo(**PARAMS_BASE, semilla=42)
    assert met1["tiempo_total_evento"] == met2["tiempo_total_evento"]

def test_distinta_semilla_distinto_resultado():
    _, met1 = simular_flujo(**PARAMS_BASE, semilla=42)
    _, met2 = simular_flujo(**PARAMS_BASE, semilla=99)
    assert met1["tiempo_total_evento"] != met2["tiempo_total_evento"]


# ── Escenarios ────────────────────────────────────────────────────────────────

def test_escenarios_retorna_tres_claves():
    esc = escenarios_flujo()
    assert set(esc.keys()) == {"optimista", "esperado", "pesimista"}

def test_escenarios_son_ejecutables():
    for clave, esc in escenarios_flujo().items():
        params = {k: v for k, v in esc.items() if k not in ("nombre", "descripcion")}
        df, met = simular_flujo(**params)
        assert len(df) == params["comensales"], f"Escenario {clave} falló"
