"""
escenarios.py · Escenarios y capacidad adicional (Persona 4).

Usa el modelo de la Persona 3 (modelo_demanda.py) y lo traduce a decisiones:
cuánta energía (GWh/año) y cuánta potencia (MW, día pico) hay que sumar si hace más calor
(El Niño) y/o si la economía crece más.

Lo usan la página 4 del tablero (pagina4_simulacion.py) y el documento técnico,
así los números coinciden en los dos lugares.

Convención (la misma de la tabla de El Niño del documento, Persona 3):
    GWh adicionales = demanda real 2025 x % de aumento
    MW adicionales  = potencia del día de mayor demanda de 2025 x % de aumento
    (promedio del día pico, no el pico horario)
El modelo es log-lineal, así que los efectos de temperatura y economía se multiplican:
    % total = (1 + %temperatura) x (1 + %economía) - 1
"""
import numpy as np
import pandas as pd

import modelo_demanda as md

# ---------------------------------------------------------------- datos y modelo
D = md.cargar_base()
M = md.ajustar(D)                       # 2018-2025, igual que la sensibilidad de la Persona 3
NINO = md.episodio_nino(D)              # El Niño 2023-24: anomalía promedio y máxima
BASE25 = D[D.anio == 2025]
GWH_2025 = float(BASE25.demanda_gwh.sum())
MW_2025 = float(md.mw_dia_pico(BASE25.demanda_max_dia_gwh.max()))

# Crecimiento económico alto del escenario C: ISE +3 % (el mejor año reciente sin rebote del
# COVID fue 2019, con +3,1 %; en 2025 fue +2,6 %). El control del tablero llega hasta +10 %.
ISE_ALTO = 3.0
T_PROM = round(NINO["anom_prom"], 2)    # +0,75 °C
T_PICO = round(NINO["anom_max"], 2)     # +1,33 °C

def f(x, dec=1, signo=False):
    """Número en formato español: 1.234,5"""
    s = f"{x:+,.{dec}f}" if signo else f"{x:,.{dec}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


ESCENARIOS = {
    "A": {"nombre": "El Niño moderado", "dT": T_PROM, "dISE": 0.0,
          "desc": f"Como El Niño 2023–24 en promedio (+{f(T_PROM, 2)} °C), economía igual"},
    "B": {"nombre": "El Niño fuerte", "dT": T_PICO, "dISE": 0.0,
          "desc": f"Como el pico de 2023–24 (+{f(T_PICO, 2)} °C), economía igual"},
    "C": {"nombre": "El Niño fuerte + economía alta", "dT": T_PICO, "dISE": ISE_ALTO,
          "desc": f"Pico de El Niño (+{f(T_PICO, 2)} °C) y ISE +{f(ISE_ALTO, 0)} %"},
}


def resultado(dT: float, dISE: float = 0.0, usar: str = "coef") -> dict:
    """Efecto de subir dT °C la anomalía de temperatura y dISE % la actividad económica.
    usar: 'coef' (lo más probable), 'inf' o 'sup' (límites del IC 95 %)."""
    p_t = md.efecto_temperatura(M, dT, usar) / 100
    p_e = md.efecto_ise(M, dISE, usar) / 100
    p = (1 + p_t) * (1 + p_e) - 1
    return {"dT": dT, "dISE": dISE, "pct": p * 100, "pct_temp": p_t * 100, "pct_eco": p_e * 100,
            "gwh": GWH_2025 * p, "mw": MW_2025 * p}


def con_intervalo(dT: float, dISE: float = 0.0) -> dict:
    r = resultado(dT, dISE)
    lo, hi = resultado(dT, dISE, "inf"), resultado(dT, dISE, "sup")
    r.update({"pct_inf": lo["pct"], "pct_sup": hi["pct"], "mw_inf": lo["mw"], "mw_sup": hi["mw"],
              "gwh_inf": lo["gwh"], "gwh_sup": hi["gwh"]})
    return r


def tabla_escenarios() -> pd.DataFrame:
    filas = []
    for k, e in ESCENARIOS.items():
        r = con_intervalo(e["dT"], e["dISE"])
        filas.append({"escenario": k, "nombre": e["nombre"], "dT": e["dT"], "dISE": e["dISE"],
                      "pct": r["pct"], "pct_inf": r["pct_inf"], "pct_sup": r["pct_sup"],
                      "gwh": r["gwh"], "gwh_inf": r["gwh_inf"], "gwh_sup": r["gwh_sup"],
                      "mw": r["mw"], "mw_inf": r["mw_inf"], "mw_sup": r["mw_sup"]})
    return pd.DataFrame(filas)


def rejilla(temps=None, ises=None) -> pd.DataFrame:
    """MW adicionales para cada combinación de temperatura y crecimiento económico."""
    temps = np.arange(0, 2.01, 0.25) if temps is None else temps
    ises = np.arange(0, 10.1, 2) if ises is None else ises
    return pd.DataFrame([[resultado(t, e)["mw"] for t in temps] for e in ises],
                        index=[f"+{e:g} %" for e in ises], columns=[f"+{t:g}" for t in temps])


# Temporadas según el mes en que ocurriría El Niño (página 4)
TEMPORADAS = {
    "todo": ("Cualquier mes", md.MESES),
    "alta": ("Temporada alta (mayo a agosto)", ["May", "Jun", "Jul", "Ago"]),
    "baja": ("Temporada baja (septiembre a abril)", ["Sep", "Oct", "Nov", "Dic", "Ene", "Feb", "Mar", "Abr"]),
}


def adicional_por_mes(pct: float) -> pd.DataFrame:
    """GWh adicionales en cada mes de 2025 para un aumento de pct %. En el modelo log-lineal
    el aumento porcentual es el mismo todos los meses; pesa más en los meses de más demanda."""
    t = pd.DataFrame({"mes": md.MESES, "gwh_base": BASE25.demanda_gwh.values})
    t["gwh_extra"] = t["gwh_base"] * pct / 100
    # potencia: promedio del día de mayor demanda de cada mes de 2025 (no el pico horario)
    t["mw_base"] = [md.mw_dia_pico(v) for v in BASE25.demanda_max_dia_gwh.values]
    t["mw_extra"] = t["mw_base"] * pct / 100
    return t


def resumen_temporada(pct: float, clave: str) -> dict:
    """MW y GWh adicionales si El Niño ocurre en una temporada: la potencia es la del mes más exigente
    de la temporada; la energía es la suma de los meses de la temporada."""
    t = adicional_por_mes(pct)
    s = t[t["mes"].isin(TEMPORADAS[clave][1])]
    i = s["mw_extra"].idxmax()
    return {"mw": float(s.loc[i, "mw_extra"]), "mes_pico": s.loc[i, "mes"], "mw_prom": float(s["mw_extra"].mean()),
            "gwh": float(s["gwh_extra"].sum()), "meses": list(s["mes"])}


def sesgo_2025() -> float:
    """Cuánto subestimó el modelo la demanda real de 2025 (% promedio, entrenado con 2018-2024)."""
    tr, te = md.separar(D)
    mv = md.ajustar(tr)
    return md.metricas(te.demanda_gwh, md.predecir_gwh(mv, te))["Sesgo_%"]


if __name__ == "__main__":
    pd.set_option("display.width", 200)
    print(tabla_escenarios().round(1).to_string(index=False))
    print(rejilla().round(0))
    print("sesgo 2025:", round(sesgo_2025(), 2))
