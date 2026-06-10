import pytest
from utils.verificacion import (
    verificar_parametros,
    verificar_tiempos,
    verificar_probabilidad,
    verificar_positivo,
    verificar_costos,
)


# ── verificar_parametros ───────────────────────────────────────────────────────

def test_parametros_validos():
    ok, errores = verificar_parametros({"comensales": 60, "lotes": 3})
    assert ok and errores == []

def test_parametro_negativo_falla():
    ok, errores = verificar_parametros({"comensales": -1})
    assert not ok and len(errores) == 1

def test_parametro_cero_es_valido():
    # verificar_parametros solo rechaza negativos; el cero lo maneja verificar_positivo
    ok, errores = verificar_parametros({"costos_fijos": 0})
    assert ok and errores == []


# ── verificar_tiempos ─────────────────────────────────────────────────────────

def test_tiempos_validos():
    ok, msg = verificar_tiempos(3, 7, "degustación")
    assert ok and msg == ""

def test_tiempos_iguales_validos():
    ok, _ = verificar_tiempos(5, 5, "degustación")
    assert ok

def test_tiempo_min_mayor_que_max_falla():
    ok, msg = verificar_tiempos(10, 5, "degustación")
    assert not ok and "degustación" in msg

def test_tiempos_negativos_fallan():
    ok, _ = verificar_tiempos(-1, 5, "degustación")
    assert not ok


# ── verificar_probabilidad ────────────────────────────────────────────────────

def test_probabilidad_valida():
    ok, _ = verificar_probabilidad(0.75, "consumo")
    assert ok

def test_probabilidad_cero_valida():
    ok, _ = verificar_probabilidad(0.0, "consumo")
    assert ok

def test_probabilidad_uno_valida():
    ok, _ = verificar_probabilidad(1.0, "consumo")
    assert ok

def test_probabilidad_mayor_a_uno_falla():
    ok, msg = verificar_probabilidad(1.5, "consumo")
    assert not ok and "consumo" in msg

def test_probabilidad_negativa_falla():
    ok, _ = verificar_probabilidad(-0.1, "consumo")
    assert not ok


# ── verificar_positivo ────────────────────────────────────────────────────────

def test_valor_positivo_valido():
    ok, _ = verificar_positivo(10, "precio")
    assert ok

def test_cero_falla():
    ok, msg = verificar_positivo(0, "precio")
    assert not ok and "precio" in msg

def test_negativo_falla():
    ok, _ = verificar_positivo(-5, "precio")
    assert not ok


# ── verificar_costos ──────────────────────────────────────────────────────────

def test_costos_validos():
    ok, errores = verificar_costos({"harina": 100, "huevos": 50})
    assert ok and errores == []

def test_costo_negativo_falla():
    ok, errores = verificar_costos({"harina": -10, "huevos": 50})
    assert not ok and len(errores) == 1

def test_multiples_costos_negativos():
    ok, errores = verificar_costos({"harina": -10, "huevos": -5, "miel": 30})
    assert not ok and len(errores) == 2
