"""
portada.py · Portada del tablero (antes de la página 1).
No es un módulo: el botón "Entrar al tablero" (id "ir_tablero") lo atiende app.py.
"""
from faicons import icon_svg
from shiny import ui

from tema import ACENTO, AZUL, CIAN, TEXTO, VERDE_CLARO

INTEGRANTES = [
    ("Isabel Buelvas de la Hoz", "T00077937"),
    ("Luisa Acosta Romero", "T00082202"),
    ("Maria Espitaleta Julio", "T00078486"),
    ("Lineth Villalba Dominiquett", "T00083377"),
]

PAGINAS = [
    ("1", "Contexto", "¿Qué ha pasado con la demanda?", "chart-line"),
    ("2", "Factores", "¿Con qué se relaciona?", "magnifying-glass-chart"),
    ("3", "Predicción", "¿Qué la explica y qué tan confiable es el modelo?", "bullseye"),
    ("4", "Simulación", "¿Qué pasaría y qué hacemos?", "bolt"),
]

_CSS = ui.tags.style(f"""
.portada {{ margin: -0.5rem -0.75rem 0 -0.75rem; }}
.por-hero {{ position: relative; overflow: hidden; color: #fff; padding: 4.5rem 2rem 6rem 2rem; text-align: center;
            background: linear-gradient(135deg, {AZUL} 0%, {CIAN} 55%, {VERDE_CLARO} 100%); }}
.por-hero::after {{ content: ""; position: absolute; left: 0; right: 0; bottom: -1px; height: 70px;
    background: radial-gradient(120% 100% at 50% 100%, #F3F9FA 58%, transparent 60%); }}
.por-etiqueta {{ display: inline-block; background: rgba(255,255,255,.22); border: 1px solid rgba(255,255,255,.5);
                padding: .25rem 1rem; border-radius: 30px; font-size: .85rem; letter-spacing: .08em;
                text-transform: uppercase; margin-bottom: 1.2rem; }}
.por-titulo {{ font-size: clamp(2rem, 5vw, 3.4rem); font-weight: 800; line-height: 1.1; margin: 0 auto .8rem auto;
              max-width: 900px; text-shadow: 0 2px 12px rgba(0,0,0,.18); }}
.por-sub {{ font-size: 1.15rem; max-width: 760px; margin: 0 auto 1.6rem auto; opacity: .96; }}
.por-btn {{ background: #fff !important; color: {AZUL} !important; font-weight: 700; border: 0 !important;
           padding: .7rem 2rem; border-radius: 40px; box-shadow: 0 6px 18px rgba(0,0,0,.2); }}
.por-btn:hover {{ background: {TEXTO} !important; color: #fff !important; }}
.por-cuerpo {{ max-width: 1100px; margin: -1.5rem auto 2rem auto; padding: 0 1rem; position: relative; z-index: 2; }}
.por-seccion {{ font-weight: 700; color: {TEXTO}; margin: 1.6rem 0 .8rem 0; font-size: 1.15rem; }}
.por-seccion span {{ display:inline-block; width: 34px; height: 4px; background: {ACENTO}; border-radius: 3px;
                    vertical-align: middle; margin-right: 10px; }}
.por-persona {{ background: #fff; border-radius: 14px; padding: 1.1rem 1rem; text-align: center; height: 100%;
               box-shadow: 0 2px 12px rgba(18,48,74,.10); border-top: 5px solid {CIAN}; }}
.por-persona:nth-child(2) {{ border-top-color: {AZUL}; }}
.por-persona:nth-child(3) {{ border-top-color: {ACENTO}; }}
.por-persona:nth-child(4) {{ border-top-color: #B8938F; }}
.por-avatar {{ width: 62px; height: 62px; border-radius: 50%; margin: 0 auto .7rem auto; color: #fff; font-weight: 700;
              font-size: 1.35rem; display:flex; align-items:center; justify-content:center;
              background: linear-gradient(135deg, {AZUL}, {ACENTO}); }}
.por-nombre {{ font-weight: 700; color: {TEXTO}; line-height: 1.25; }}
.por-codigo {{ color: #6B7F8F; font-size: .9rem; margin-top: .25rem; letter-spacing: .04em; }}
.por-pag {{ background: #fff; border-radius: 14px; padding: 1rem 1.1rem; height: 100%;
           box-shadow: 0 2px 12px rgba(18,48,74,.08); display: flex; gap: .9rem; align-items: center; }}
.por-pag .n {{ flex: 0 0 44px; height: 44px; border-radius: 12px; color: #fff; font-weight: 800;
              display:flex; align-items:center; justify-content:center; background: {CIAN}; }}
.por-pag b {{ color: {TEXTO}; }} .por-pag small {{ color: #6B7F8F; display:block; }}
.por-fuentes {{ text-align:center; color: #6B7F8F; font-size: .85rem; margin: 1.8rem 0 1rem 0; }}
""")


def portada_ui():
    personas = [ui.div(
        ui.div("".join(p[0] for p in n.split()[:2]), class_="por-avatar"),
        ui.div(n, class_="por-nombre"),
        ui.div(c, class_="por-codigo"),
        class_="por-persona") for n, c in INTEGRANTES]

    paginas = [ui.div(ui.div(n, class_="n"), ui.div(ui.tags.b(t), ui.tags.small(q)), class_="por-pag")
               for n, t, q, _ in PAGINAS]

    return ui.div(
        _CSS,
        ui.div(
            ui.div("Tablero de análisis y simulación", class_="por-etiqueta"),
            ui.h1("Demanda eléctrica de la región Caribe", class_="por-titulo"),
            ui.p("Qué ha pasado entre 2018 y 2025, qué la mueve (calor, economía, El Niño) y cuánta capacidad "
                 "adicional habría que sumar si el clima se pone más extremo.", class_="por-sub"),
            ui.input_action_button("ir_tablero", ui.span("Entrar al tablero  ", icon_svg("arrow-right")),
                                   class_="por-btn"),
            class_="por-hero",
        ),
        ui.div(
            ui.div(ui.span(), "Integrantes", class_="por-seccion"),
            ui.layout_columns(*personas, col_widths=[3, 3, 3, 3], fill=False),
            ui.div(ui.span(), "Qué encontrarás", class_="por-seccion"),
            ui.layout_columns(*paginas, col_widths=[6, 6, 6, 6], fill=False),
            ui.p("Departamentos: Atlántico, Bolívar, Cesar, Córdoba, La Guajira, Magdalena y Sucre. "
                 "Fuentes: XM, DANE, NASA POWER, IDEAM y NOAA.", class_="por-fuentes"),
            class_="por-cuerpo",
        ),
        class_="portada",
    )
