import pytest
from simuladores.stock_porciones import simular_stock, escenarios_stock


PARAMS_BASE = dict(
    comensales_esperados=60,
    pct_consumo_min=0.70,
    pct_consumo_max=0.90,
    budines_por_lote=2,
    porciones_por_budin=10,
    lotes_preparados=3,
    iteraciones=500,
)


# ── Estructura de salida ───────────────────────────────────────────────────────

def test_retorna_dataframe_y_dict():
    import pandas as pd
    df, met = simular_stock(**PARAMS_BASE)
    assert isinstance(df, pd.DataFrame)
    assert isinstance(met, dict)

def test_dataframe_tiene_n_iteraciones():
    df, _ = simular_stock(**PARAMS_BASE)
    assert len(df) == PARAMS_BASE["iteraciones"]

def test_metricas_tienen_claves_esperadas():
    _, met = simular_stock(**PARAMS_BASE)
    claves = {"total_porciones", "demanda_promedio", "prob_quiebre",
              "desperdicio_promedio", "porciones_recomendadas",
              "lotes_recomendados", "recomendacion"}
    assert claves.issubset(set(met.keys()))


# ── Cálculo de porciones ──────────────────────────────────────────────────────

def test_total_porciones_correcto():
    """total = lotes × budines_por_lote × porciones_por_budin."""
    _, met = simular_stock(**PARAMS_BASE)
    esperado = (PARAMS_BASE["lotes_preparados"]
                * PARAMS_BASE["budines_por_lote"]
                * PARAMS_BASE["porciones_por_budin"])
    assert met["total_porciones"] == esperado

def test_total_porciones_escala_con_lotes():
    params_pocos = {**PARAMS_BASE, "lotes_preparados": 1}
    params_muchos = {**PARAMS_BASE, "lotes_preparados": 10}
    _, met1 = simular_stock(**params_pocos)
    _, met10 = simular_stock(**params_muchos)
    assert met10["total_porciones"] == met1["total_porciones"] * 10


# ── Lógica de quiebre y desperdicio ──────────────────────────────────────────

def test_quiebre_alto_con_pocos_lotes():
    """Con 1 lote (20 porciones) y 60 comensales esperamos quiebre casi seguro."""
    params = {**PARAMS_BASE, "lotes_preparados": 1}
    _, met = simular_stock(**params)
    assert met["prob_quiebre"] > 50

def test_sin_quiebre_con_muchos_lotes():
    """Con 20 lotes (400 porciones) y 60 comensales no debe haber quiebre."""
    params = {**PARAMS_BASE, "lotes_preparados": 20}
    _, met = simular_stock(**params)
    assert met["prob_quiebre"] == 0

def test_quiebre_y_desperdicio_no_simultaneos():
    """En cada iteración no puede haber quiebre Y desperdicio a la vez."""
    df, _ = simular_stock(**PARAMS_BASE)
    simultaneos = ((df["Quiebre (porciones)"] > 0) & (df["Desperdicio (porciones)"] > 0)).sum()
    assert simultaneos == 0

def test_prob_quiebre_entre_0_y_100():
    _, met = simular_stock(**PARAMS_BASE)
    assert 0 <= met["prob_quiebre"] <= 100

def test_lotes_recomendados_en_rango_razonable():
    """lotes_recomendados debe ser similar a lotes_preparados, no igual a la demanda en porciones."""
    _, met = simular_stock(**PARAMS_BASE)
    # Con 60 comensales y 70-90% consumo el P90 de demanda son ~50 porciones
    # dividido por budines_por_lote(2) × porciones_por_budin(10) = 20 → ~3 lotes
    assert met["lotes_recomendados"] <= 10, (
        f"lotes_recomendados={met['lotes_recomendados']} es irrazonablemente alto "
        "(probable división incorrecta: olvidó porciones_por_budin)"
    )


# ── Reproducibilidad ──────────────────────────────────────────────────────────

def test_misma_semilla_mismo_resultado():
    _, met1 = simular_stock(**PARAMS_BASE, semilla=42)
    _, met2 = simular_stock(**PARAMS_BASE, semilla=42)
    assert met1["prob_quiebre"] == met2["prob_quiebre"]


# ── Escenarios ────────────────────────────────────────────────────────────────

def test_escenarios_retorna_tres_claves():
    esc = escenarios_stock()
    assert set(esc.keys()) == {"optimista", "esperado", "pesimista"}

def test_escenarios_son_ejecutables():
    from datos.parametros import CAPACIDAD
    for clave, esc in escenarios_stock().items():
        params = {k: v for k, v in esc.items() if k not in ("nombre", "descripcion")}
        params["budines_por_lote"] = CAPACIDAD["budines_por_lote"]
        params["porciones_por_budin"] = CAPACIDAD["porciones_por_budin"]
        _, met = simular_stock(**params)
        assert 0 <= met["prob_quiebre"] <= 100, f"Escenario {clave} falló"

def test_optimista_menor_quiebre_que_pesimista():
    from datos.parametros import CAPACIDAD
    resultados = {}
    for clave, esc in escenarios_stock().items():
        params = {k: v for k, v in esc.items() if k not in ("nombre", "descripcion")}
        params["budines_por_lote"] = CAPACIDAD["budines_por_lote"]
        params["porciones_por_budin"] = CAPACIDAD["porciones_por_budin"]
        _, met = simular_stock(**params)
        resultados[clave] = met["prob_quiebre"]
    assert resultados["optimista"] <= resultados["pesimista"]
