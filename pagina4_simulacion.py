"""
pagina4_simulacion.py
Página 4 del dashboard (Persona 4): ¿Qué pasaría y qué hacemos?

Esta página MIRA HACIA ADELANTE y decide. La parte que explica el pasado (qué factor pesa más, qué tan
confiable es el modelo) está en la página 3; aquí no se repite.

Contenido:
  - escenarios A, B y C (El Niño moderado, fuerte y fuerte + economía alta)
  - simulador (temperatura y ISE) y MW adicionales por escenario
  - rejilla de MW según clima y economía
  - ¿Cuándo llega El Niño? (temporada alta mayo–agosto o baja): MW por mes
  - recomendación

Módulo de Shiny para Python. Necesita en la misma carpeta: escenarios.py, modelo_demanda.py, tema.py y
base_demanda_caribe_2018_2025.xlsx
"""
import matplotlib.pyplot as plt
import numpy as np
from faicons import icon_svg
from matplotlib.colors import LinearSegmentedColormap
from shiny import module, reactive, render, ui

import escenarios as es
import modelo_demanda as md
from escenarios import f
from tema import (ACENTO, ARENA, AZUL, CIAN, GRIS, GRIS_CLARO, TEXTO, TEXTO2, VERDE_CLARO, ESTILO_GLOBAL,
                  pagina_titulo)

# ------------------------------------------------------------ cálculos (una sola vez)
_TAB = es.tabla_escenarios().set_index("escenario")
_A, _B, _C = (_TAB.loc[k] for k in "ABC")
_TORN = md.tabla_tornado(es.M, 1.0, 5.0)          # solo para la recomendación; el gráfico está en la página 3
_PERFIL = md.perfil_mensual(es.M, es.D)
_TOP = _PERFIL.nlargest(3, "vs_promedio_%").sort_index()["mes"].tolist()
_MESES_LARGO = dict(zip(md.MESES, ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
                                   "agosto", "septiembre", "octubre", "noviembre", "diciembre"]))
_TOP_TXT = ", ".join(_MESES_LARGO[m] for m in _TOP[:-1]) + " y " + _MESES_LARGO[_TOP[-1]]
_SESGO = es.sesgo_2025()
_T_ROW = _TORN.set_index("variable")["rango"]
_RANGO_TEMP = _T_ROW[[i for i in _T_ROW.index if i.startswith("Temperatura")][0]]
_RANGO_ECO = _T_ROW[[i for i in _T_ROW.index if i.startswith("Actividad")][0]]
_B_ALTA, _B_BAJA = es.resumen_temporada(_B.pct, "alta"), es.resumen_temporada(_B.pct, "baja")
_B_MESES = es.adicional_por_mes(_B.pct)
_COLOR_ESC = {"A": CIAN, "B": AZUL, "C": ACENTO}
_MAPA = LinearSegmentedColormap.from_list("mar", ["#F4FAF3", VERDE_CLARO, CIAN, AZUL])


def _encabezado(titulo, subtitulo):
    return ui.card_header(ui.div(ui.div(titulo, class_="fw-semibold"),
                                 ui.div(subtitulo, class_="small text-muted fw-normal")))


_CSS = ui.tags.style(f"""
.sim .esc-letra {{ display: inline-block; width: 1.9rem; height: 1.9rem; line-height: 1.9rem; text-align: center;
                  border-radius: 50%; color: #fff; font-weight: 700; margin-right: 8px; }}
.sim .esc-A {{ background: {CIAN}; }} .sim .esc-B {{ background: {AZUL}; }} .sim .esc-C {{ background: {ACENTO}; }}
.sim .card-esc-A {{ border-top: 5px solid {CIAN} !important; }}
.sim .card-esc-B {{ border-top: 5px solid {AZUL} !important; }}
.sim .card-esc-C {{ border-top: 5px solid {ACENTO} !important; }}
.sim .esc-mw {{ font-size: 1.9rem; font-weight: 700; line-height: 1.2; color: {TEXTO}; }}
.sim .esc-nota {{ font-size: .78rem; color: #6B7F8F; }}
.sim .recom li {{ margin-bottom: .5rem; }}
.sim .recom li::marker {{ color: {ACENTO}; }}
""")


def _tarjeta_escenario(k):
    e = es.ESCENARIOS[k]
    r = _TAB.loc[k]
    return ui.card(
        ui.div(ui.span(k, class_=f"esc-letra esc-{k}"), ui.span(e["nombre"], class_="fw-semibold")),
        ui.div(e["desc"], class_="esc-nota mb-2"),
        ui.div(f"{f(r.mw, 0, True)} MW", class_="esc-mw"),
        ui.div(f"rango {f(r.mw_inf, 0)} a {f(r.mw_sup, 0)} MW", class_="esc-nota"),
        ui.div(f"{f(r.gwh, 0)} GWh/año · {f(r.pct, 1, True)} % de demanda", class_="esc-nota mb-2"),
        ui.input_action_button(f"esc_{k}", "Ver en el simulador", class_="btn-sm btn-outline-secondary"),
        class_=f"card-esc-{k}",
    )


@module.ui
def simulacion_ui():
    return ui.div(
        _CSS,
        pagina_titulo(4, "¿Qué pasaría y qué hacemos?",
                      "Mira hacia adelante: cuánta potencia habría que sumar si hace más calor y cuándo actuar."),
        # ---- titulares: escenarios A, B y C (estáticos; el botón los carga en el simulador)
        ui.layout_columns(*[_tarjeta_escenario(k) for k in "ABC"], fill=False),
        # ---- simulador
        ui.layout_columns(
            ui.card(
                _encabezado("Arma tu escenario", ui.output_text("sub_sim", inline=True)),
                ui.input_slider("dT", "Aumento de temperatura (°C)", 0.0, 2.0, es.T_PICO, step=0.05, width="100%"),
                ui.input_slider("dISE", "Crecimiento adicional de la actividad económica, ISE (%)", 0.0, 10.0, 0.0,
                                step=0.5, width="100%"),
                ui.output_ui("kpis"),
                full_screen=True,
            ),
            ui.card(
                _encabezado("Capacidad adicional por escenario",
                            "Potencia que habría que sumar (MW) y su rango probable (IC 95 %)."),
                ui.output_plot("barras", height="300px", fill=False),
                full_screen=True,
            ),
            col_widths=(5, 7),
        ),
        # ---- rejilla y temporada
        ui.layout_columns(
            ui.card(
                _encabezado("¿Cuánta potencia adicional según clima y economía?",
                            "Cada curva es una cantidad de MW. El punto de arena es tu escenario."),
                ui.output_plot("rejilla", height="360px", fill=False),
                full_screen=True,
            ),
            ui.card(
                _encabezado("¿Cuándo llega El Niño? Meses críticos", ui.output_text("sub_meses", inline=True)),
                ui.input_radio_buttons("temporada", "Mes en que ocurre El Niño",
                                       {k: v[0] for k, v in es.TEMPORADAS.items()}, selected="alta", inline=True),
                ui.output_plot("meses", height="230px", fill=False),
                ui.output_ui("kpis_temporada"),
                full_screen=True,
            ),
            col_widths=(6, 6),
        ),
        # ---- recomendación
        ui.card(
            _encabezado("Recomendación", "Con base en los escenarios y en el análisis de sensibilidad (página 3)."),
            ui.tags.ul(
                ui.tags.li(ui.tags.b("Planificar con el escenario B. "),
                           f"Un El Niño como el pico de 2023–24 exigiría cerca de {f(_B.mw, 0)} MW y "
                           f"{f(_B.gwh, 0)} GWh adicionales al año (rango probable: {f(_B.mw_inf, 0)} a "
                           f"{f(_B.mw_sup, 0)} MW)."),
                ui.tags.li(ui.tags.b("Dejar el escenario C como techo. "),
                           f"Si además la economía crece con fuerza, la necesidad sube a {f(_C.mw, 0)} MW "
                           f"(hasta {f(_C.mw_sup, 0)} MW en el extremo del rango). El escenario A "
                           f"({f(_A.mw, 0)} MW) es el piso."),
                ui.tags.li(ui.tags.b("Vigilar la temperatura antes que la economía. "),
                           f"Un cambio de ±1 °C mueve la demanda {f(_RANGO_TEMP / _RANGO_ECO)} veces más que "
                           f"uno de ±5 % en el ISE. El seguimiento del pronóstico de El Niño (ONI y temperatura) "
                           f"debe ser el aviso para activar la reserva."),
                ui.tags.li(ui.tags.b("Tener la reserva lista durante todo el episodio. "),
                           f"En el escenario B la potencia adicional es parecida en todos los meses (entre "
                           f"{f(_B_MESES['mw_extra'].min(), 0)} y {f(_B_MESES['mw_extra'].max(), 0)} MW), porque hay "
                           f"días de mucha demanda casi todo el año. Lo que se concentra es la energía: con clima "
                           f"normal, {_TOP_TXT} son los meses de mayor demanda, y un El Niño entre mayo y agosto "
                           f"sumaría {f(_B_ALTA['gwh'], 0)} GWh en esos cuatro meses."),
                ui.tags.li(ui.tags.b("Agregar margen. "),
                           f"En 2025 el modelo subestimó la demanda en promedio {f(_SESGO)} %, así que estas cifras "
                           f"son un piso, no un techo."),
                class_="recom mb-2",
            ),
            ui.div(ui.tags.b("Limitaciones: "),
                   "la potencia es el promedio del día de mayor demanda (no el pico horario); +2 °C está fuera de lo "
                   "observado (extrapolación); el ISE es nacional; la temperatura es un reanálisis de 6 capitales; "
                   "el modelo no incluye la oferta ni la respuesta de los usuarios.",
                   class_="small text-muted"),
            full_screen=True,
        ),
        class_="sim",
    )


@module.server
def simulacion_server(input, output, session):

    # ------------------------------------------------------------ botones de escenario
    def _cargar(k):
        e = es.ESCENARIOS[k]
        ui.update_slider("dT", value=e["dT"])
        ui.update_slider("dISE", value=e["dISE"])

    @reactive.effect
    @reactive.event(input.esc_A)
    def _():
        _cargar("A")

    @reactive.effect
    @reactive.event(input.esc_B)
    def _():
        _cargar("B")

    @reactive.effect
    @reactive.event(input.esc_C)
    def _():
        _cargar("C")

    @reactive.calc
    def sel():
        return es.con_intervalo(input.dT(), input.dISE())

    @render.text
    def sub_sim():
        r = sel()
        if r["pct"] == 0:
            return "Mueve los controles para simular más calor o más actividad económica."
        return (f"+{f(r['dT'], 2)} °C y ISE +{f(r['dISE'], 1)} % → la demanda subiría "
                f"{f(r['pct'], 1, True)} % (rango {f(r['pct_inf'], 1)} % a {f(r['pct_sup'], 1)} %).")

    @render.ui
    def kpis():
        r = sel()

        def caja(titulo, valor, nota, icono):
            return ui.div(
                ui.p(icon_svg(icono, height="1em"), titulo, class_="mini-tit mb-0"),
                ui.div(valor, class_="mini-val"),
                ui.div(nota, class_="mini-nota"),
                class_="mini-kpi",
            )
        return ui.layout_columns(
            caja("Demanda", f"{f(r['pct'], 1, True)} %",
                 f"clima {f(r['pct_temp'], 1, True)} % · economía {f(r['pct_eco'], 1, True)} %", "arrow-trend-up"),
            caja("Energía adicional", f"{f(r['gwh'], 0)} GWh", f"por año (rango {f(r['gwh_inf'], 0)} a "
                                                              f"{f(r['gwh_sup'], 0)})", "bolt"),
            caja("Capacidad adicional", f"{f(r['mw'], 0, True)} MW", f"día pico (rango {f(r['mw_inf'], 0)} a "
                                                                      f"{f(r['mw_sup'], 0)})", "plug"),
            fill=False, gap="10px",
        )

    # ------------------------------------------------------------ barras A, B, C y el escenario propio
    @render.plot
    def barras():
        r = sel()
        nombres = ["A", "B", "C", "Tu\nescenario"]
        mw = [_A.mw, _B.mw, _C.mw, r["mw"]]
        lo = [_A.mw_inf, _B.mw_inf, _C.mw_inf, r["mw_inf"]]
        hi = [_A.mw_sup, _B.mw_sup, _C.mw_sup, r["mw_sup"]]
        colores = [CIAN, AZUL, ACENTO, ARENA]
        fig, ax = plt.subplots(layout="constrained")
        x = np.arange(4)
        ax.bar(x, mw, color=colores, width=0.55)
        ax.errorbar(x, mw, yerr=[np.array(mw) - np.array(lo), np.array(hi) - np.array(mw)], fmt="none",
                    ecolor=TEXTO2, capsize=5, lw=1.5)
        for i, v in enumerate(mw):
            ax.text(i, hi[i] + 8, f"{f(v, 0, True)} MW", ha="center", fontsize=9, fontweight="bold")
        ax.set_xticks(x, nombres)
        ax.set_ylim(0, max(hi) * 1.18)
        ax.set_ylabel("MW adicionales (día pico)")
        ax.grid(axis="x", visible=False)
        return fig

    # ------------------------------------------------------------ rejilla temperatura x economía
    @render.plot
    def rejilla():
        r = sel()
        t = np.linspace(0, 2, 81)
        e = np.linspace(0, 10, 81)
        Z = np.array([[es.resultado(a, b)["mw"] for a in t] for b in e])
        fig, ax = plt.subplots(layout="constrained")
        ax.contourf(t, e, Z, levels=np.arange(0, Z.max() + 40, 20), cmap=_MAPA)
        cs = ax.contour(t, e, Z, levels=np.arange(0, Z.max() + 40, 40), colors=TEXTO2, linewidths=0.6, alpha=.7)
        ax.clabel(cs, fmt=lambda v: f"{v:.0f} MW", fontsize=8)
        for k in "ABC":
            c = es.ESCENARIOS[k]
            ax.plot(c["dT"], c["dISE"], "o", color=_COLOR_ESC[k], ms=8, mec="white", mew=1.6, zorder=3, clip_on=False)
            ax.annotate(k, (c["dT"], c["dISE"]), xytext=(7, 7), textcoords="offset points", fontsize=10,
                        color=TEXTO, fontweight="bold")
        ax.plot(r["dT"], r["dISE"], "o", color=ARENA, ms=13, mec=TEXTO, mew=2, zorder=4, clip_on=False)
        ax.set(xlabel="Aumento de temperatura (°C)", ylabel="Crecimiento adicional del ISE (%)")
        ax.grid(False)
        return fig

    # ------------------------------------------------------------ meses críticos y temporada
    @reactive.calc
    def temp_sel():
        return es.resumen_temporada(sel()["pct"], input.temporada())

    @render.text
    def sub_meses():
        r = sel()
        if not r["pct"]:
            return "Mueve los controles de tu escenario para ver la potencia mes a mes."
        return (f"MW adicionales en cada mes de 2025 con tu escenario. Con clima normal, los meses de mayor "
                f"demanda son {_TOP_TXT}.")

    @render.plot
    def meses():
        r = sel()
        t = es.adicional_por_mes(r["pct"])
        ts = temp_sel()
        en_temp = t["mes"].isin(ts["meses"]).values
        colores = np.where(t["mes"] == ts["mes_pico"], ACENTO, np.where(en_temp, AZUL, GRIS_CLARO))
        fig, ax = plt.subplots(layout="constrained")
        ax.bar(t["mes"], t["mw_extra"], color=colores, width=0.6)
        tope = max(t["mw_extra"].max(), 10)
        for i, v in enumerate(t["mw_extra"]):
            ax.text(i, v + tope * 0.02, f(v, 0), ha="center", fontsize=8.5)
        ax.set_ylim(0, tope * 1.18)
        ax.set_ylabel("MW adicionales")
        ax.grid(axis="x", visible=False)
        return fig

    @render.ui
    def kpis_temporada():
        ts = temp_sel()

        def caja(titulo, valor, nota, icono):
            return ui.div(
                ui.p(icon_svg(icono, height="1em"), titulo, class_="mini-tit mb-0"),
                ui.div(valor, class_="mini-val"),
                ui.div(nota, class_="mini-nota"),
                class_="mini-kpi",
            )
        return ui.layout_columns(
            caja("Mes más exigente", f"{f(ts['mw'], 0, True)} MW", f"en {_MESES_LARGO[ts['mes_pico']]} (barra verde)", "plug"),
            caja("Promedio de la temporada", f"{f(ts['mw_prom'], 0, True)} MW", f"{len(ts['meses'])} meses (barras azules)",
                 "gauge-high"),
            caja("Energía en la temporada", f"{f(ts['gwh'], 0)} GWh", "si el calor dura toda la temporada", "bolt"),
            fill=False, gap="10px",
        )
