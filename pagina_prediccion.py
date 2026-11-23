"""
pagina_prediccion.py
Página 3 del dashboard (Persona 3): ¿Qué explica la demanda y qué tan confiable es el modelo?

Esta página MIRA HACIA ATRÁS y explica. Lo que mira hacia adelante (El Niño, escenarios, MW,
meses críticos) está en la página 4, para que las dos páginas no repitan información.

Contenido:
  - selector del periodo de entrenamiento (2018–2024 / 2018–2025): cambia indicadores, gráficos y tabla
  - ¿Qué tan bien predice el modelo? (serie real vs. modelo + tabla por año, con 2025 resaltado)
  - ¿Por qué creció la demanda? (cascada)
  - ¿Qué factor mueve más la demanda? (tornado) y ¿qué tan estable es el efecto? (periodo vs. periodo)

Módulo de Shiny para Python:
    from pagina_prediccion import prediccion_ui, prediccion_server
    ui.nav_panel("Predicción", prediccion_ui("pred"))   /   prediccion_server("pred")
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from faicons import icon_svg
from shiny import module, reactive, render, ui

import modelo_demanda as md
from tema import (ACENTO, ARENA, AZUL, CIAN, FONDO, GRIS, GRIS_CLARO, TEXTO2, VERDE_CLARO, kpi_icono,
                  pagina_titulo)


def f(x, dec=1, signo=False):
    """Número en formato español: 1.234,5"""
    s = f"{x:+,.{dec}f}" if signo else f"{x:,.{dec}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


# ------------------------------------------------------------ cálculos (una sola vez)
PERIODOS = {"valid": "2018–2024", "todo": "2018–2025"}
_D = md.cargar_base()
_TRAIN, _TEST = md.separar(_D)
_MODELOS = {"valid": md.ajustar(_TRAIN),   # 2018-2024: 2025 queda como prueba
            "todo": md.ajustar(_D)}        # 2018-2025: todos los datos
_PRED = {k: pd.Series(md.predecir_gwh(m, _D).values, index=_D.index) for k, m in _MODELOS.items()}
_ES25 = (_D.anio == 2025).values


def _mape(k, mascara):
    return md.metricas(_D.demanda_gwh[mascara], _PRED[k][mascara])


_MET25 = {k: _mape(k, _ES25) for k in _MODELOS}                 # error en 2025 con cada modelo
_ERR_HIST = _mape("valid", ~_ES25)["MAPE_%"]                    # error 2018-2024 (el modelo sí vio esos años)
_ERR_TODO = _mape("todo", np.ones(len(_D), bool))["MAPE_%"]
_NINO = md.episodio_nino(_D)
_TEMP = {k: {c: md.efecto_temperatura(m, 1, c) for c in ("coef", "inf", "sup")} for k, m in _MODELOS.items()}
_ISE = {k: {c: md.efecto_ise(m, 1, c) for c in ("coef", "inf", "sup")} for k, m in _MODELOS.items()}


def _tabla_anual(k):
    t = _D.assign(modelo=_PRED[k]).groupby("anio").agg(real=("demanda_gwh", "sum"), modelo=("modelo", "sum"))
    t["error"] = (t.real - t.modelo) / t.real * 100          # >0: el modelo se queda corto
    return t


_TABLAS = {k: _tabla_anual(k) for k in _MODELOS}


def _encabezado(titulo, subtitulo):
    return ui.card_header(ui.div(ui.div(titulo, class_="fw-semibold"),
                                 ui.div(subtitulo, class_="small text-muted fw-normal")))


@module.ui
def prediccion_ui():
    return ui.div(
        pagina_titulo(3, "¿Qué explica la demanda y qué tan confiable es el modelo?",
                      "Mira hacia atrás: qué pasó entre 2018 y 2025 y qué tan bien lo reproduce el modelo."),
        # ---- selector de periodo (cambia todos los gráficos de la página)
        ui.card(
            ui.layout_columns(
                ui.input_radio_buttons(
                    "periodo", "Periodo de entrenamiento del modelo",
                    {"valid": "2018–2024 (2025 queda como prueba)", "todo": "2018–2025 (todos los datos)"},
                    selected="todo", inline=True),
                ui.div(ui.output_text("nota_periodo", inline=True), class_="small text-muted align-self-center"),
                col_widths=(6, 6), fill=False,
            ),
            fill=False,
        ),
        # ---- titulares
        ui.layout_columns(
            ui.value_box("Confiabilidad del modelo", ui.output_text("kpi_err"),
                         ui.p(ui.output_text("kpi_err_nota", inline=True), class_="small"),
                         showcase=kpi_icono(icon_svg("circle-check"), "azul"), class_="kpi kpi-azul"),
            ui.value_box("Si la temperatura sube 1 °C", ui.output_text("kpi_temp"),
                         ui.p(ui.output_text("kpi_temp_nota", inline=True), class_="small"),
                         showcase=kpi_icono(icon_svg("temperature-high"), "verde"), class_="kpi kpi-verde"),
            ui.value_box("Si la economía crece 1 %", ui.output_text("kpi_ise"),
                         ui.p("de demanda eléctrica (ISE)", class_="small"),
                         showcase=kpi_icono(icon_svg("chart-line"), "cian"), class_="kpi kpi-cian"),
            fill=False,
        ),
        # ---- ¿qué tan bien predice? serie + tabla
        ui.layout_columns(
            ui.card(
                _encabezado("¿Qué tan bien predice el modelo?", ui.output_text("sub_serie", inline=True)),
                ui.output_plot("serie", height="300px", fill=False),
                full_screen=True,
            ),
            ui.card(
                _encabezado("Demanda real contra modelo, año por año", ui.output_text("sub_tabla", inline=True)),
                ui.output_ui("tabla"),
                full_screen=True,
            ),
            col_widths=(7, 5),
        ),
        # ---- ¿por qué creció?
        ui.card(
            _encabezado(ui.output_text("tit_cascada", inline=True), ui.output_text("sub_cascada", inline=True)),
            ui.output_plot("cascada", height="300px", fill=False),
            full_screen=True,
        ),
        # ---- ¿qué factor pesa más? y ¿qué tan estable?
        ui.layout_columns(
            ui.card(
                _encabezado("¿Qué factor mueve más la demanda?", ui.output_text("sub_tornado", inline=True)),
                ui.layout_columns(
                    ui.input_slider("d_temp", "Temperatura (± °C)", 0.5, 2.0, 1.0, step=0.5),
                    ui.input_slider("d_ise", "Actividad económica (± %)", 1, 10, 5, step=1),
                ),
                ui.output_plot("tornado", height="330px", fill=False),
                full_screen=True,
            ),
            ui.card(
                _encabezado("¿Qué tan estable es el efecto?", ui.output_text("sub_estable", inline=True)),
                ui.output_plot("estable", height="410px", fill=False),
                full_screen=True,
            ),
            col_widths=(6, 6),
        ),
        ui.p("Para ver qué pasaría con un El Niño y cuánta potencia habría que sumar, ve a la página 4. "
             "Detalles técnicos (coeficientes, supuestos, pruebas) en el documento.", class_="small text-muted"),
    )


@module.server
def prediccion_server(input, output, session):

    @reactive.calc
    def k():
        return input.periodo()

    @reactive.calc
    def modelo():
        return _MODELOS[k()]

    @reactive.calc
    def fin():
        return 2024 if k() == "valid" else 2025

    # ------------------------------------------------------------ selector y titulares
    @render.text
    def nota_periodo():
        if k() == "valid":
            return "El modelo no ve 2025: sirve para comprobar qué tan bien predice un año nuevo."
        return ("El modelo ve todos los años: son los valores que usan la página 4 y el documento. "
                "Elige 2018–2024 para ver cómo le fue prediciendo 2025.")

    @render.text
    def kpi_err():
        # Siempre el error fuera de muestra (2025 sin haberlo visto): es la medida honesta de confiabilidad
        return f"± {f(_MET25['valid']['MAPE_%'])} %"

    @render.text
    def kpi_err_nota():
        if k() == "valid":
            return f"Error promedio al predecir 2025, un año que el modelo no vio (2018–2024: ± {f(_ERR_HIST)} %)."
        return (f"Error al predecir 2025 sin haberlo visto. Con 2025 dentro del entrenamiento baja a "
                f"± {f(_MET25['todo']['MAPE_%'])} %, pero ya no es una prueba.")

    @render.text
    def kpi_temp():
        return f"{f(_TEMP[k()]['coef'], signo=True)} %"

    @render.text
    def kpi_temp_nota():
        otro = "todo" if k() == "valid" else "valid"
        return f"de demanda eléctrica ({f(_TEMP[otro]['coef'], signo=True)} % con {PERIODOS[otro]})"

    @render.text
    def kpi_ise():
        return f"{f(_ISE[k()]['coef'], 2, signo=True)} %"

    # ------------------------------------------------------------ serie real vs. modelo
    @render.text
    def sub_serie():
        if k() == "valid":
            return (f"En 2025 la demanda real superó al modelo en todos los meses "
                    f"(en promedio {f(_MET25['valid']['Sesgo_%'])} %).")
        return "Con 2025 dentro del entrenamiento el modelo sigue la demanda de cerca, también en 2025."

    @render.plot
    def serie():
        fig, ax = plt.subplots(layout="constrained")
        if k() == "valid":
            ax.axvspan(_TEST.fecha.min(), _TEST.fecha.max() + pd.offsets.MonthEnd(0), color=VERDE_CLARO, alpha=.35, lw=0)
            ax.text(_TEST.fecha.min() + pd.Timedelta(days=15), 0.03, "2025\n(no vista)", transform=ax.get_xaxis_transform(),
                    va="bottom", color=TEXTO2, fontsize=9)
        ax.axvspan(_NINO["inicio"], _NINO["fin"] + pd.offsets.MonthEnd(0), color=FONDO, lw=0)
        ax.text(_NINO["inicio"] + pd.Timedelta(days=15), 0.03, "El Niño\n2023–24",
                transform=ax.get_xaxis_transform(), va="bottom", color=TEXTO2, fontsize=9)
        ax.plot(_D.fecha, _D.demanda_gwh, color=AZUL, label="Demanda real")
        ax.plot(_D.fecha, _PRED[k()].values, color=ACENTO, ls="--", label="Lo que esperaba el modelo")
        ax.set_ylabel("GWh por mes")
        ax.yaxis.set_major_formatter(lambda v, _: f(v, 0))
        ax.legend(frameon=False, loc="upper left")
        return fig

    # ------------------------------------------------------------ tabla por año
    @render.text
    def sub_tabla():
        t = _TABLAS[k()]
        if k() == "valid":
            return (f"2018–2024: error entre {f(t.error.loc[:2024].abs().min())} y {f(t.error.loc[:2024].abs().max())} %. "
                    f"En 2025 salta a {f(t.error.loc[2025])} %.")
        return (f"Error de ajuste entre {f(t.error.abs().min())} y {f(t.error.abs().max())} %. "
                f"Con 2025 incluido el modelo ya no la subestima tanto ({f(t.error.loc[2025])} %).")

    @render.ui
    def tabla():
        t = _TABLAS[k()]
        filas = []
        for anio, r in t.iterrows():
            nueva = (anio == 2025 and k() == "valid")
            etiqueta = ui.span("Predicción", class_="tag pr") if nueva else ui.span("Ajuste", class_="tag aj")
            filas.append(ui.tags.tr(
                ui.tags.td(str(anio)), ui.tags.td(f(r.real, 0)), ui.tags.td(f(r.modelo, 0)),
                ui.tags.td(f"{f(r.error, 1, True)} %"), ui.tags.td(etiqueta),
                class_="fila-2025" if anio == 2025 else None))
        return ui.div(
            ui.tags.table(
                ui.tags.thead(ui.tags.tr(ui.tags.th("Año"), ui.tags.th("Real (GWh)"), ui.tags.th("Modelo (GWh)"),
                                         ui.tags.th("Error %"), ui.tags.th("Tipo"))),
                ui.tags.tbody(*filas), class_="tabla-mod"),
            ui.p("Error % = (real − modelo) ÷ real. Positivo: el modelo se queda corto. "
                 "«Ajuste»: año que el modelo vio al entrenarse; «Predicción»: año que no vio.",
                 class_="small text-muted mt-2 mb-0"),
        )

    # ------------------------------------------------------------ cascada
    @reactive.calc
    def cascada_t():
        # Fija en 2018-2025 con el modelo de todos los datos: responde "¿por qué creció?", no depende del selector.
        # (Terminar en 2024, año de El Niño, inflaría el peso del calor.)
        return md.descomposicion_crecimiento(_MODELOS["todo"], _D, 2018, 2025)

    @render.text
    def tit_cascada():
        return "¿Por qué creció la demanda 2018–2025?"

    @render.text
    def sub_cascada():
        t = cascada_t().set_index("factor")["proporcion_%"]
        aporte = t.loc[["Crecimiento estructural", "Actividad económica"]].sum()
        return (f"El crecimiento estructural y la economía explican el {f(aporte, 0)} %; la temperatura, el "
                f"{f(t.loc['Temperatura'], 0)} %. Siempre con el periodo completo y todos los datos.")

    @render.plot
    def cascada():
        t = cascada_t()
        ini, fn = t.attrs["gwh_inicio"], t.attrs["gwh_fin"]
        etiquetas = [str(t.attrs["anio_ini"])] + [x.replace(" ", "\n", 1) for x in t.factor] + [str(t.attrs["anio_fin"])]
        fig, ax = plt.subplots(layout="constrained")
        x = np.arange(len(etiquetas))
        ax.bar(x[0], ini, color=AZUL, width=0.6)
        base = ini
        for i, (g, fac) in enumerate(zip(t.gwh, t.factor), start=1):
            color = ARENA if fac == "No explicado" else (ACENTO if fac == "Temperatura" else CIAN)
            ax.bar(x[i], g, bottom=base, color=color, width=0.6)
            ax.text(x[i], base + max(g, 0) + 250, f"{f(g, 0, True)}", ha="center", fontsize=9)
            ax.plot([x[i] - 0.7, x[i] - 0.3], [base, base], color=GRIS, lw=0.8)
            base += g
        ax.bar(x[-1], fn, color=AZUL, width=0.6)
        ax.text(x[0], ini + 250, f(ini, 0), ha="center", fontsize=9)
        ax.text(x[-1], fn + 250, f(fn, 0), ha="center", fontsize=9, fontweight="bold")
        ax.set_xticks(x, etiquetas, fontsize=8.5)
        ax.set_ylim(ini * 0.8, fn * 1.06)
        ax.set_ylabel("GWh por año")
        ax.yaxis.set_major_formatter(lambda v, _: f(v, 0))
        ax.grid(axis="x", visible=False)
        return fig

    # ------------------------------------------------------------ tornado
    @reactive.calc
    def tabla_torn():
        return md.tabla_tornado(modelo(), delta_temp=input.d_temp(), delta_ise=input.d_ise())

    @render.text
    def sub_tornado():
        t = tabla_torn().set_index("variable")["rango"]
        temp = t[[i for i in t.index if i.startswith("Temperatura")][0]]
        eco = t[[i for i in t.index if i.startswith("Actividad")][0]]
        if temp >= eco:
            return f"Con estos rangos, la temperatura pesa {f(temp / eco)} veces más que la economía."
        return f"Con estos rangos, la economía pesa {f(eco / temp)} veces más que la temperatura."

    @render.plot
    def tornado():
        t = tabla_torn()
        fig, ax = plt.subplots(layout="constrained")
        y = np.arange(len(t))
        ax.barh(y, t["alto"], color=ACENTO, height=0.5, label="Aumento")
        ax.barh(y, t["bajo"], color=ARENA, height=0.5, label="Disminución")
        ax.axvline(0, color=GRIS, lw=1)
        ax.set_yticks(y, t["variable"])
        lim = max(abs(t["bajo"]).max(), t["alto"].max()) * 1.35
        ax.set_xlim(-lim, lim)
        for i, r in t.iterrows():
            ax.text(r["alto"] + lim * 0.02, i, f"{f(r['alto'], signo=True)} %", va="center", fontsize=9)
            ax.text(r["bajo"] - lim * 0.02, i, f"{f(r['bajo'], signo=True)} %", va="center", ha="right", fontsize=9)
        ax.set_xlabel("Cambio en la demanda (%)")
        ax.grid(axis="y", visible=False)
        ax.legend(frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, fontsize=9)
        return fig

    # ------------------------------------------------------------ estabilidad del efecto (periodo contra periodo)
    @render.text
    def sub_estable():
        a, b = _TEMP["valid"]["coef"], _TEMP["todo"]["coef"]
        return (f"El efecto de +1 °C es {f(a)} % con {PERIODOS['valid']} y {f(b)} % con {PERIODOS['todo']}: "
                f"agregar 2025 lo reduce. Las barras son el rango probable (IC 95 %).")

    @render.plot
    def estable():
        fig, axes = plt.subplots(2, 1, layout="constrained")
        for ax, (titulo, datos, unidad) in zip(axes, [("Temperatura: +1 °C", _TEMP, 1), ("Economía: +1 % del ISE", _ISE, 2)]):
            for i, clave in enumerate(["valid", "todo"]):
                d = datos[clave]
                resaltado = clave == k()
                color = AZUL if clave == "valid" else ACENTO
                ax.errorbar(d["coef"], i, xerr=[[d["coef"] - d["inf"]], [d["sup"] - d["coef"]]], fmt="o", color=color,
                            ms=10 if resaltado else 7, capsize=5, lw=3 if resaltado else 1.8,
                            alpha=1 if resaltado else .55)
                ax.text(d["coef"], i + 0.28, f"{f(d['coef'], unidad, True)} %", ha="center", fontsize=9, color=color,
                        fontweight="bold")
            ax.set_yticks([0, 1], [f"Entrenado con\n{PERIODOS['valid']}", f"Entrenado con\n{PERIODOS['todo']}"])
            ax.set_ylim(-0.6, 1.7)
            ax.set_title(titulo, fontsize=10, loc="left")
            ax.set_xlabel("Cambio en la demanda (%)")
            ax.grid(axis="y", visible=False)
            ax.axvline(0, color=GRIS, lw=1)
            ax.margins(x=0.15)
        return fig
