"""
pagina2_factores.py
Página 2 del dashboard (Persona 2): factores que se relacionan con la demanda eléctrica del Caribe.

Módulo de Shiny para Python con el mismo estilo de la página 3 (pagina_prediccion.py). Para integrarlo en la app del equipo:

    from pagina2_factores import factores_ui, factores_server
    ...
    ui.nav_panel("Factores", factores_ui("fact"))
    ...
    def server(input, output, session):
        factores_server("fact")

Necesita en la misma carpeta: graficos_factores.py y base_demanda_caribe_2018_2025.xlsx
"""
from faicons import icon_svg
from shiny import module, render, ui

import graficos_factores as g
from graficos_factores import f
from tema import kpi_icono, pagina_titulo

# ------------------------------------------------------------ cálculos (una sola vez)
_BASE, _DEP = g.cargar()
_R = {c: g.corr_con_demanda(_BASE, c) for c in g.MATRIZ if c != g.Y}
_N_IDEAM_BAJO = int((_BASE["ideam_confiable"] == 0).sum())


def _encabezado(titulo, subtitulo):
    return ui.card_header(ui.div(ui.div(titulo, class_="fw-semibold"),
                                 ui.div(subtitulo, class_="small text-muted fw-normal")))


FASES_OPC = {"Todas": "Todas (colorear por fase)", "El Niño": "El Niño", "La Niña": "La Niña", "Neutral": "Neutral"}


@module.ui
def factores_ui():
    anios = ["Todos"] + [str(a) for a in range(2018, 2026)]
    return ui.div(
        pagina_titulo(2, "¿Con qué se relaciona la demanda?",
                      "Mira los datos: qué factores se mueven junto con la demanda y cuáles no."),
        # ---- titulares (estáticos)
        ui.layout_columns(
            ui.value_box("Actividad económica (ISE)", f"r = {f(_R['ise'], 2, True)}",
                         ui.p("relación clara: con más actividad, más demanda", class_="small"),
                         showcase=kpi_icono(icon_svg("chart-line"), "azul"), class_="kpi kpi-azul"),
            ui.value_box("Temperatura", f"r = {f(_R['temperatura_c'], 2, True)}",
                         ui.p(f"relación moderada (con la anomalía, r = {f(_R['temp_anom_c'], 2, True)})", class_="small"),
                         showcase=kpi_icono(icon_svg("temperature-high"), "verde"), class_="kpi kpi-verde"),
            ui.value_box("Índice El Niño (ONI)", f"r = {f(_R['oni'], 2, True)}",
                         ui.p("sin relación clara por sí solo: El Niño actúa a través del calor", class_="small"),
                         showcase=kpi_icono(icon_svg("cloud-sun"), "cian"), class_="kpi kpi-cian"),
            fill=False,
        ),
        # ---- dispersión y correlaciones
        ui.layout_columns(
            ui.card(
                _encabezado("¿Con qué se mueve la demanda?", ui.output_text("sub_disp", inline=True)),
                ui.layout_columns(
                    ui.input_radio_buttons("fase", "Fase climática (El Niño / La Niña / Neutral)", FASES_OPC,
                                           selected="Todas", inline=True),
                    ui.input_select("anio", "Resaltar un año", anios, selected="Todos", width="200px"),
                    col_widths=(9, 3), fill=False,
                ),
                ui.output_plot("dispersion", height="460px", fill=False),
                full_screen=True,
            ),
            ui.card(
                _encabezado("¿Cómo se relacionan entre sí?",
                            "Azul: suben juntas. Arena: una sube cuando la otra baja."),
                ui.output_plot("correlacion", height="430px", fill=False),
                full_screen=True,
            ),
            col_widths=(7, 5),
        ),
        # ---- departamentos y limpieza
        ui.layout_columns(
            ui.card(
                _encabezado("Comparación por departamento", ui.output_text("sub_dep", inline=True)),
                ui.input_radio_buttons("metrica", None, g.METRICAS, selected="var", inline=True),
                ui.output_plot("departamentos", height="300px", fill=False),
                full_screen=True,
            ),
            ui.card(
                _encabezado("Limpieza: vacíos de temperatura del IDEAM",
                            f"{_N_IDEAM_BAJO} meses con menos de 5 estaciones; por eso la temperatura principal es NASA POWER."),
                ui.output_plot("ideam", height="340px", fill=False),
                full_screen=True,
            ),
            col_widths=(6, 6),
        ),
        ui.p("Una correlación no prueba causa: la actividad económica y la demanda crecen con los años, "
             "y el modelo de la página 3 separa el efecto de cada factor. "
             "Fuentes: XM, DANE, NASA POWER, IDEAM y NOAA.", class_="small text-muted"),
        class_="fact",
    )


@module.server
def factores_server(input, output, session):

    @render.text
    def sub_disp():
        extra = "" if input.anio() == "Todos" else f" Con círculo, los meses de {input.anio()}."
        if input.fase() == "Todas":
            return (f"Cada punto es un mes, coloreado por fase climática. Círculo vacío: aislamiento por "
                    f"COVID-19 (mar–ago 2020).{extra}")
        k, n = g.pendiente(_BASE, input.fase())
        k_all, _ = g.pendiente(_BASE, "Todas")
        return (f"Solo {input.fase()} ({n} meses): cada +1 °C de anomalía va con {f(k, 2, True)} GWh/día, "
                f"frente a {f(k_all, 2, True)} con todos los meses.{extra}")

    @render.plot
    def dispersion():
        return g.fig_dispersion(_BASE, input.anio(), input.fase())

    @render.plot
    def correlacion():
        return g.fig_correlacion(_BASE)

    @render.text
    def sub_dep():
        return {"var": "Atlántico, Córdoba y Magdalena crecieron más; Cesar y La Guajira quedaron por debajo de 2018.",
                "covid": "En 2020 La Guajira y Cesar fueron los más golpeados.",
                "temp": "Las capitales difieren hasta 1,1 °C. Cesar no tiene serie de temperatura."}[input.metrica()]

    @render.plot
    def departamentos():
        return g.fig_departamentos(_DEP, input.metrica())

    @render.plot
    def ideam():
        return g.fig_ideam(_BASE)
