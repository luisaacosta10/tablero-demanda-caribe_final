"""
modelo_demanda.py
Modelo de regresión lineal de la demanda eléctrica de la región Caribe (Persona 3).

Lo usan el notebook (análisis) y la app de Shiny (página 3 y escenarios de la Persona 4).

Modelo final (log-lineal, datos mensuales):
    log(D_t) = b0 + b1*TempAnom_t + b2*log(ISE_t) + sum(g_m*Mes_m) + b3*t + e_t

- Los coeficientes se leen como porcentajes: +1 °C de anomalía -> (exp(b1) - 1)*100 % de demanda.
- Errores estándar HAC (Newey-West) porque los residuos están autocorrelacionados.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

RUTA_BASE = Path(__file__).parent / "base_demanda_caribe_2018_2025.xlsx"

FORMULA_FINAL = "log_demanda ~ temp_anom_c + log_ise + C(mes) + tendencia"
FORMULA_COMPLETA = "log_demanda ~ temp_anom_c + log_ise + dias_habiles + C(mes) + covid + tendencia"

ANIO_PRUEBA = 2025   # entrenamiento 2018-2024, prueba 2025
LAGS_HAC = 6         # rezagos de Newey-West (datos mensuales)


def cargar_base(ruta=RUTA_BASE) -> pd.DataFrame:
    d = pd.read_excel(ruta, sheet_name="base_mensual")
    return d.sort_values("fecha").reset_index(drop=True)


def ajustar(datos: pd.DataFrame, formula: str = FORMULA_FINAL):
    """Ajusta MCO con errores robustos HAC (Newey-West)."""
    return smf.ols(formula, datos).fit(cov_type="HAC", cov_kwds={"maxlags": LAGS_HAC})


def separar(d: pd.DataFrame, anio_prueba: int = ANIO_PRUEBA):
    return d[d.anio < anio_prueba].copy(), d[d.anio == anio_prueba].copy()


def metricas(y, y_pred) -> dict:
    y, y_pred = np.asarray(y, float), np.asarray(y_pred, float)
    e = y - y_pred
    return {
        "RMSE_GWh": float(np.sqrt(np.mean(e ** 2))),
        "MAE_GWh": float(np.mean(np.abs(e))),
        "MAPE_%": float(np.mean(np.abs(e) / y) * 100),
        "Sesgo_%": float(np.mean(e / y) * 100),   # >0: el modelo subestima
    }


def predecir_gwh(modelo, datos: pd.DataFrame) -> pd.Series:
    """Predicción en GWh (deshace el log)."""
    return np.exp(modelo.predict(datos))


# ---------------------------------------------------------------- sensibilidad
def efecto_temperatura(modelo, delta_c, usar="coef") -> float:
    """% de cambio en la demanda si la anomalía de temperatura sube delta_c °C.
    usar: 'coef', 'inf' o 'sup' (límites del IC 95 %)."""
    b = _coef(modelo, "temp_anom_c", usar)
    return (np.exp(b * delta_c) - 1) * 100


def efecto_ise(modelo, cambio_pct, usar="coef") -> float:
    """% de cambio en la demanda si la actividad económica (ISE) cambia cambio_pct %."""
    b = _coef(modelo, "log_ise", usar)
    return ((1 + cambio_pct / 100) ** b - 1) * 100


def _coef(modelo, nombre, usar):
    if usar == "coef":
        return modelo.params[nombre]
    ic = modelo.conf_int().loc[nombre]
    return ic.iloc[0] if usar == "inf" else ic.iloc[1]


def tabla_tornado(modelo, delta_temp=1.0, delta_ise=5.0) -> pd.DataFrame:
    """Impacto (% de demanda) de mover cada variable hacia abajo y hacia arriba."""
    filas = [
        {"variable": f"Temperatura ±{delta_temp:g} °C",
         "bajo": efecto_temperatura(modelo, -delta_temp),
         "alto": efecto_temperatura(modelo, delta_temp)},
        {"variable": f"Actividad económica (ISE) ±{delta_ise:g} %",
         "bajo": efecto_ise(modelo, -delta_ise),
         "alto": efecto_ise(modelo, delta_ise)},
        {"variable": "Crecimiento estructural ±1 año",
         "bajo": (np.exp(-12 * modelo.params["tendencia"]) - 1) * 100,
         "alto": (np.exp(12 * modelo.params["tendencia"]) - 1) * 100},
    ]
    t = pd.DataFrame(filas)
    t["rango"] = t["alto"] - t["bajo"]
    return t.sort_values("rango").reset_index(drop=True)


def predecir_escenario(modelo, datos: pd.DataFrame, delta_temp=0.0, delta_ise_pct=0.0) -> pd.Series:
    """Demanda (GWh) predicha si a cada mes se le suma delta_temp °C de anomalía y
    el ISE cambia delta_ise_pct %. Útil para los escenarios de El Niño (Persona 4)."""
    esc = datos.copy()
    esc["temp_anom_c"] = esc["temp_anom_c"] + delta_temp
    esc["log_ise"] = np.log(esc["ise"] * (1 + delta_ise_pct / 100))
    return predecir_gwh(modelo, esc)


def descomposicion_crecimiento(modelo, d: pd.DataFrame, anio_ini=2018, anio_fin=2025) -> pd.DataFrame:
    """Cuánto aporta cada factor al crecimiento de la demanda anual entre dos años (en GWh).
    Como el modelo es log-lineal, el cambio en log se reparte entre factores y luego se
    expresa como proporción del crecimiento total en GWh."""
    a, b = d[d.anio == anio_ini], d[d.anio == anio_fin]
    gwh_a, gwh_b = a.demanda_gwh.sum(), b.demanda_gwh.sum()
    total_log = np.log(gwh_b / gwh_a)
    p = modelo.params
    aportes = {
        "Crecimiento estructural": p["tendencia"] * (b.tendencia.mean() - a.tendencia.mean()),
        "Actividad económica": p["log_ise"] * (b.log_ise.mean() - a.log_ise.mean()),
        "Temperatura": p["temp_anom_c"] * (b.temp_anom_c.mean() - a.temp_anom_c.mean()),
    }
    aportes["No explicado"] = total_log - sum(aportes.values())
    t = pd.DataFrame({"factor": list(aportes), "aporte_log": list(aportes.values())})
    t["proporcion_%"] = t["aporte_log"] / total_log * 100
    t["gwh"] = t["aporte_log"] / total_log * (gwh_b - gwh_a)
    t.attrs.update(gwh_inicio=gwh_a, gwh_fin=gwh_b, anio_ini=anio_ini, anio_fin=anio_fin)
    return t


MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]


def perfil_mensual(modelo, d: pd.DataFrame, anio=2025) -> pd.DataFrame:
    """Demanda diaria esperada por mes con clima normal (anomalía 0), dejando fijos la
    economía y la tendencia: aísla el efecto de la estacionalidad.
    Devuelve el % por encima o por debajo del promedio del año."""
    b = d[d.anio == anio].copy()
    b["temp_anom_c"] = 0.0
    b["tendencia"] = b["tendencia"].mean()
    b["log_ise"] = b["log_ise"].mean()
    gwh_dia = predecir_gwh(modelo, b).values / b["dias_mes"].values
    t = pd.DataFrame({"mes": MESES, "gwh_dia": gwh_dia})
    t["vs_promedio_%"] = (t["gwh_dia"] / t["gwh_dia"].mean() - 1) * 100
    return t


def episodio_nino(d: pd.DataFrame, desde=2023) -> dict:
    """Datos del El Niño fuerte 2023-24 (meses con el_nino = 1 desde `desde`):
    inicio, fin, anomalía de temperatura promedio y máxima."""
    n = d[(d.el_nino == 1) & (d.anio >= desde)]
    return {"inicio": n.fecha.min(), "fin": n.fecha.max(),
            "anom_prom": float(n.temp_anom_c.mean()), "anom_max": float(n.temp_anom_c.max()),
            "fecha_max": n.loc[n.temp_anom_c.idxmax(), "fecha"]}


def mw_dia_pico(gwh_dia: float) -> float:
    """Potencia promedio (MW) del día de mayor demanda. No es el pico horario."""
    return gwh_dia * 1000 / 24
