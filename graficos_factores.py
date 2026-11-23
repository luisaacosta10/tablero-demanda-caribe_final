"""
graficos_factores.py · Datos y gráficos de la Página 2 (Persona 2).
Solo usa pandas y matplotlib (sin Shiny), igual que las figuras de la página 3 de la Persona 3.
Los usa pagina2_factores.py y también se pueden correr solos para ver las figuras.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from tema import ACENTO, ARENA, AZUL, CIAN, FONDO, GRIS, GRIS_CLARO, TEXTO, TEXTO2, VERDE_CLARO, aplicar_mpl
RUTA_BASE = Path(__file__).parent / "base_demanda_caribe_2018_2025.xlsx"
MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]

aplicar_mpl()
FASES = {"El Niño": ACENTO, "La Niña": ARENA, "Neutral": CIAN}   # color de cada fase climática

Y = "demanda_diaria_prom_gwh"
VARIABLES = {  # columna -> (título, eje x)
    "temperatura_c": ("Temperatura", "°C"),
    "temp_anom_c": ("Anomalía de temperatura", "°C frente a lo normal del mes"),
    "ise": ("Actividad económica (ISE)", "ISE (2015 = 100)"),
    "pib_caribe_anual": ("PIB regional", "miles de millones COP"),
}
MATRIZ = {Y: "Demanda", "temperatura_c": "Temperatura", "temp_anom_c": "Anomalía", "ise": "ISE",
          "pib_caribe_anual": "PIB", "oni": "ONI", "dias_habiles": "Días hábiles"}
CAPITAL = {"ATLANTICO": "barranquilla", "BOLIVAR": "cartagena", "MAGDALENA": "santa_marta",
           "CORDOBA": "monteria", "SUCRE": "sincelejo", "LA GUAJIRA": "riohacha"}
NOMBRES = {"ATLANTICO": "Atlántico", "BOLIVAR": "Bolívar", "CESAR": "Cesar", "CORDOBA": "Córdoba",
           "LA GUAJIRA": "La Guajira", "MAGDALENA": "Magdalena", "SUCRE": "Sucre"}
METRICAS = {"var": "PIB 2018–2025", "covid": "Caída PIB 2020", "temp": "Temperatura capital"}


def f(x, dec=1, signo=False):
    """Número en formato español: 1.234,5"""
    s = f"{x:+,.{dec}f}" if signo else f"{x:,.{dec}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


# ------------------------------------------------------------------ datos
def cargar(ruta=RUTA_BASE):
    """Devuelve (base mensual, tabla por departamento)."""
    base = pd.read_excel(ruta, sheet_name="base_mensual")
    base["fecha"] = pd.to_datetime(base["fecha"])
    base["mes_txt"] = [f"{MESES[d.month - 1]} {d.year}" for d in base["fecha"]]
    base["fase"] = np.select([base["el_nino"] == 1, base["la_nina"] == 1], ["El Niño", "La Niña"], default="Neutral")
    pib = pd.read_excel(ruta, sheet_name="pib_departamentos").set_index("anio")
    temp = pd.read_excel(ruta, sheet_name="temp_ciudades").drop(columns="fecha").mean()
    dep = pd.DataFrame({"var": (pib.iloc[-1] / pib.iloc[0] - 1) * 100,
                        "covid": (pib.loc[2020] / pib.loc[2019] - 1) * 100,
                        "part": pib.iloc[-1] / pib.iloc[-1].sum() * 100})
    dep["temp"] = [temp.get(f"temp_{CAPITAL[k]}_c", np.nan) if k in CAPITAL else np.nan for k in dep.index]
    dep["nombre"] = [NOMBRES[k] for k in dep.index]
    return base, dep


def corr_con_demanda(base, col):
    return float(base[col].corr(base[Y]))


# ------------------------------------------------------------------ gráficos
def pendiente(base, fase="Todas", col="temp_anom_c"):
    """GWh/día adicionales por cada +1 °C de anomalía (pendiente de la recta) en la fase elegida."""
    d = base if fase == "Todas" else base[base["fase"] == fase]
    d = d[d["covid"] == 0]
    return float(np.polyfit(d[col], d[Y], 1)[0]), len(d)


def fig_dispersion(base, anio="Todos", fase="Todas"):
    """Dispersión demanda vs. cada factor.
    - fase = 'Todas': cada punto se colorea según la fase climática (El Niño / La Niña / Neutral).
    - fase = una fase: se resaltan solo sus meses (con su propia recta) y el resto queda en gris.
    - anio: además resalta los meses de un año (contorno)."""
    # La leyenda va en una fila propia debajo de los 4 gráficos para que no tape los títulos de los ejes
    fig = plt.figure(layout="constrained")
    gs = fig.add_gridspec(3, 2, height_ratios=[1, 1, 0.13])
    axes = np.array([[fig.add_subplot(gs[i, j]) for j in range(2)] for i in range(2)])
    ax_leyenda = fig.add_subplot(gs[2, :])
    ax_leyenda.axis("off")
    covid = base["covid"] == 1
    es_anio = (base["anio"] == int(anio)) if anio != "Todos" else pd.Series(False, index=base.index)
    es_fase = (base["fase"] == fase) if fase != "Todas" else pd.Series(True, index=base.index)
    for ax, (col, (tit, eje)) in zip(axes.ravel(), VARIABLES.items()):
        if fase == "Todas":
            for nombre, color in FASES.items():
                m = (base["fase"] == nombre) & ~covid
                ax.scatter(base.loc[m, col], base.loc[m, Y], color=color, s=24, alpha=.85, ec="white", lw=.5,
                           label=nombre, zorder=2)
        else:
            m_otro = ~es_fase & ~covid
            ax.scatter(base.loc[m_otro, col], base.loc[m_otro, Y], color=GRIS_CLARO, s=20, ec="white", lw=.5, zorder=1)
            m = es_fase & ~covid
            ax.scatter(base.loc[m, col], base.loc[m, Y], color=FASES[fase], s=34, ec="white", lw=.6, zorder=3,
                       label=fase)
        ax.scatter(base.loc[covid, col], base.loc[covid, Y], color="white", s=24, ec=GRIS, lw=1, zorder=2,
                   label="COVID-19 (mar–ago 2020)")
        if anio != "Todos":
            ax.scatter(base.loc[es_anio, col], base.loc[es_anio, Y], facecolors="none", edgecolors=TEXTO2, s=70,
                       lw=1.6, zorder=4, label=anio)
        k, i = np.polyfit(base[col], base[Y], 1)
        xs = np.array([base[col].min(), base[col].max()])
        ax.plot(xs, k * xs + i, color=GRIS, lw=1.4, ls="--", label="Todos los meses", zorder=1)
        if fase != "Todas" and es_fase.sum() > 5:
            d = base[es_fase & ~covid]
            kf, i_f = np.polyfit(d[col], d[Y], 1)
            xf = np.array([d[col].min(), d[col].max()])
            ax.plot(xf, kf * xf + i_f, color=FASES[fase], lw=2.4, zorder=4, label=f"Recta {fase}")
        ax.set_title(f"{tit} (r = {f(corr_con_demanda(base, col), 2, True)})", fontsize=9.5, loc="left")
        ax.set_xlabel(eje, fontsize=8.5)
        ax.set_ylabel("GWh por día" if ax in axes[:, 0] else "", fontsize=8.5)
        if col == "pib_caribe_anual":
            ax.xaxis.set_major_formatter(lambda v, _: f(v, 0))
    h, l = axes[0, 0].get_legend_handles_labels()
    vistos = dict(zip(l, h))
    ax_leyenda.legend(vistos.values(), vistos.keys(), loc="center", ncol=min(len(vistos), 6), frameon=False,
               fontsize=8.5)
    return fig


def fig_correlacion(base):
    c = base[list(MATRIZ)].corr()
    nombres = list(MATRIZ.values())
    fig, ax = plt.subplots(layout="constrained")
    im = ax.imshow(c.values, cmap=plt.matplotlib.colors.LinearSegmentedColormap.from_list("az_na", [ARENA, "#ffffff", AZUL]),
                   vmin=-1, vmax=1)
    ax.set_xticks(range(len(c)), nombres, rotation=40, ha="right", fontsize=9)
    ax.set_yticks(range(len(c)), nombres, fontsize=9)
    ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(False)
    for i in range(len(c)):
        for j in range(len(c)):
            ax.text(j, i, f(c.values[i, j], 2), ha="center", va="center", fontsize=8.5,
                    color="white" if abs(c.values[i, j]) > .7 else "#1f2937")
    return fig


def fig_departamentos(dep, metrica="var"):
    d = dep.dropna(subset=[metrica]).sort_values(metrica)
    fig, ax = plt.subplots(layout="constrained")
    if metrica == "temp":
        colores, lim = CIAN, (26, 29.5)
        etiquetas = [f"{f(v, 2)} °C" for v in d[metrica]]
    else:
        colores = ARENA if metrica == "covid" else [AZUL if v >= 0 else ARENA for v in d[metrica]]
        lim = (-28, 8) if metrica == "covid" else (-12, 30)
        etiquetas = [f"{f(v, 1, True)} %" for v in d[metrica]]
    ax.barh(d["nombre"], d[metrica], color=colores, height=0.6)
    for y, (v, t) in enumerate(zip(d[metrica], etiquetas)):
        pad = (lim[1] - lim[0]) * 0.015
        ax.text(v + (pad if v >= 0 or metrica == "temp" else -pad), y, t, va="center", fontsize=9,
                ha="left" if (v >= 0 or metrica == "temp") else "right")
    ax.set_xlim(*lim)
    if metrica != "temp":
        ax.axvline(0, color=GRIS, lw=1)
    ax.set_xlabel({"var": "Cambio del PIB 2018–2025 (%)", "covid": "Cambio del PIB 2020 vs. 2019 (%)",
                   "temp": "Temperatura media 2018–2025 (°C, el eje empieza en 26)"}[metrica])
    ax.grid(axis="y", visible=False)
    return fig


def fig_ideam(base):
    fig, ax = plt.subplots(layout="constrained")
    bajo = base["ideam_confiable"] == 0
    ax.bar(base["fecha"], base["n_estaciones_ideam"], width=25, color=np.where(bajo, ARENA, GRIS_CLARO))
    ax.axhline(5, color=GRIS, ls="--", lw=1)
    ax.text(base["fecha"].iloc[1], 5.4, "mínimo para confiar: 5 estaciones", fontsize=8.5, color=TEXTO2)
    ini, fin = base.loc[bajo, "fecha"].min(), base.loc[bajo, "fecha"].max()
    ax.text(ini + (fin - ini) / 2, 12.5, "17 meses\nabr-2023 a ago-2024", ha="center", va="top", fontsize=8.5, color=TEXTO2)
    ax.set_ylabel("Estaciones del IDEAM que reportan")
    ax.grid(axis="x", visible=False)
    return fig


if __name__ == "__main__":  # python graficos_factores.py -> guarda las figuras en ./vista_previa
    base, dep = cargar()
    out = Path(__file__).parent / "vista_previa"
    out.mkdir(exist_ok=True)
    for nombre, fig in [("dispersion", fig_dispersion(base)), ("correlacion", fig_correlacion(base)),
                        ("departamentos", fig_departamentos(dep)), ("ideam", fig_ideam(base))]:
        fig.savefig(out / f"{nombre}.png", dpi=110)
    print("Figuras guardadas en", out)
