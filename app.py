"""
Tablero completo (portada + 4 páginas) · Demanda eléctrica de la región Caribe.
Ejecutar desde esta carpeta:   shiny run app.py --launch-browser

Portada     -> portada.py             (nombres del equipo)
1. Contexto -> pagina1_contexto.py    ¿Qué ha pasado?
2. Factores -> pagina2_factores.py    ¿Con qué se relaciona?
3. Predicción -> pagina_prediccion.py ¿Qué explica la demanda y qué tan confiable es el modelo? (mira hacia atrás)
4. Simulación -> pagina4_simulacion.py ¿Qué pasaría y qué hacemos? (mira hacia adelante)
Paleta y estilos comunes: tema.py
"""
from pathlib import Path

from shiny import App, reactive, ui

from pagina1_contexto import ESTILO, cargar_base, contexto_server, contexto_ui
from pagina2_factores import factores_server, factores_ui
from pagina4_simulacion import simulacion_server, simulacion_ui
from pagina_prediccion import prediccion_server, prediccion_ui
from portada import portada_ui

base = cargar_base(Path(__file__).parent / "base_demanda_caribe_2018_2025.xlsx")

app_ui = ui.page_navbar(
    ui.nav_panel("Portada", portada_ui()),
    ui.nav_panel("1. Contexto", contexto_ui("contexto")),
    ui.nav_panel("2. Factores", factores_ui("fact")),
    ui.nav_panel("3. Predicción", prediccion_ui("pred")),
    ui.nav_panel("4. Simulación", simulacion_ui("sim")),
    id="nav",
    title="Demanda eléctrica · Región Caribe",
    header=ESTILO,
    fillable=False,
)


def server(input, output, session):
    contexto_server("contexto", base)
    factores_server("fact")
    prediccion_server("pred")
    simulacion_server("sim")

    @reactive.effect
    @reactive.event(input.ir_tablero)
    def _():
        actualizar = getattr(ui, "update_navset", None) or ui.update_navs   # nombre según la versión de Shiny
        actualizar("nav", selected="1. Contexto")


app = App(app_ui, server)
