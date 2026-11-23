"""
tema.py · Paleta, estilos y piezas comunes del tablero (portada + 4 páginas).

Paleta tomada de la imagen de referencia (playa del Caribe):
    azul intenso, azul cian, verde claro, verde oscuro y arena rosada.

Uso en las páginas:
    from tema import AZUL, CIAN, VERDE_CLARO, ACENTO, ARENA, GRIS, GRIS_CLARO, FONDO, TEXTO2, aplicar_mpl
"""
import matplotlib.pyplot as plt
from shiny import ui

# ---------------------------------------------------------------- paleta
AZUL = "#0A74F0"          # azul intenso: demanda real, valores principales
CIAN = "#169FDB"          # azul cian: apoyo, intervalos, 2.º elemento
VERDE_CLARO = "#93D68F"   # verde claro: fondos suaves y resaltes
ACENTO = "#3A7D26"        # verde oscuro: calor / El Niño / aumento / escenario propio
ARENA = "#B8938F"         # arena rosada: disminución, "no explicado", La Niña
TEXTO = "#12304A"         # azul muy oscuro para títulos y texto
TEXTO2 = "#4A6275"
SUAVE = "#6B7F8F"
GRIS = "#8FA3B0"
GRIS_CLARO = "#CFDDE3"
FONDO = "#E6F2F4"         # franjas de fondo en los gráficos
REJILLA = "#E3ECEF"

# versiones translúcidas para franjas (rgba)
RGBA_NINO = "rgba(58,125,38,0.18)"
RGBA_NINA = "rgba(184,147,143,0.25)"


def aplicar_mpl():
    """Estilo común de matplotlib para todos los gráficos del tablero."""
    plt.rcParams.update({
        "figure.dpi": 96, "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
        "grid.color": REJILLA, "axes.edgecolor": "#B7C7D0", "lines.linewidth": 2, "font.size": 10,
        "axes.axisbelow": True, "xtick.color": TEXTO2, "ytick.color": TEXTO2, "axes.labelcolor": TEXTO2,
        "axes.titlecolor": TEXTO, "text.color": TEXTO, "figure.facecolor": "white", "axes.facecolor": "white",
    })


aplicar_mpl()

# ---------------------------------------------------------------- CSS global
CSS = f"""
:root {{ --azul:{AZUL}; --cian:{CIAN}; --verde-claro:{VERDE_CLARO}; --verde:{ACENTO}; --arena:{ARENA};
        --texto:{TEXTO}; --suave:{SUAVE}; }}
body {{ background: #F3F9FA; color: {TEXTO}; }}

/* barra de navegación */
.navbar {{ background: linear-gradient(90deg, {AZUL} 0%, {CIAN} 70%, {ACENTO} 135%) !important;
          box-shadow: 0 2px 12px rgba(18,48,74,.18); }}
.navbar .navbar-brand, .navbar .nav-link, .navbar .navbar-brand * {{ color: #fff !important; font-weight: 500; }}
.navbar .nav-link {{ opacity: .85; border-bottom: 3px solid transparent; padding-bottom: .35rem; }}
.navbar .nav-link:hover {{ opacity: 1; }}
.navbar .nav-link.active {{ opacity: 1; font-weight: 700; border-bottom-color: {VERDE_CLARO}; }}
.navbar-toggler {{ background: rgba(255,255,255,.85); }}

/* tarjetas */
.card {{ border: 0 !important; border-radius: 14px !important; box-shadow: 0 2px 12px rgba(18,48,74,.08); }}
.card-header {{ background: #fff !important; border-bottom: 1px solid {REJILLA} !important;
               border-radius: 14px 14px 0 0 !important; border-left: 5px solid {CIAN}; }}
.card-header .fw-semibold {{ color: {TEXTO}; }}
.card-header .small {{ color: {SUAVE} !important; }}

/* indicadores (value boxes) */
.bslib-value-box.kpi {{ background: #fff !important; color: {TEXTO} !important; border-radius: 14px;
                       border: 0 !important; box-shadow: 0 2px 12px rgba(18,48,74,.08); }}
.bslib-value-box.kpi .value-box-title {{ color: {TEXTO2} !important; font-size: .9rem; font-weight: 500; }}
.bslib-value-box.kpi .value-box-value {{ color: {TEXTO} !important; font-weight: 700; }}
.bslib-value-box.kpi p {{ color: {SUAVE} !important; margin: 0; }}
.bslib-value-box.kpi .value-box-showcase {{ color: #fff !important; }}
.kpi-azul {{ border-left: 6px solid {AZUL} !important; }}
.kpi-cian {{ border-left: 6px solid {CIAN} !important; }}
.kpi-verde {{ border-left: 6px solid {ACENTO} !important; }}
.kpi-arena {{ border-left: 6px solid {ARENA} !important; }}
.kpi-ico {{ width: 56px; height: 56px; border-radius: 50%; display: flex; align-items: center;
           justify-content: center; color: #fff; }}
.kpi-ico svg {{ width: 26px !important; height: 26px !important; fill: currentColor; }}
.kpi-ico.azul {{ background: {AZUL}; }} .kpi-ico.cian {{ background: {CIAN}; }}
.kpi-ico.verde {{ background: {ACENTO}; }} .kpi-ico.arena {{ background: {ARENA}; }}

/* encabezado de página */
.pag-cab {{ display:flex; align-items:center; gap:14px; margin: 1rem 0 1rem 0; flex-wrap: wrap; }}
.pag-num {{ width: 46px; height: 46px; border-radius: 12px; color:#fff; font-weight: 700; font-size: 1.3rem;
           display:flex; align-items:center; justify-content:center;
           background: linear-gradient(135deg, {AZUL}, {ACENTO}); }}
.pag-tit {{ font-size: 1.45rem; font-weight: 700; color: {TEXTO}; margin: 0; line-height: 1.2; }}
.pag-sub {{ color: {SUAVE}; margin: 0; font-size: .92rem; }}

/* botones y controles */
.btn-outline-secondary {{ color: {AZUL}; border-color: {AZUL}; }}
.btn-outline-secondary:hover {{ background: {AZUL}; border-color: {AZUL}; color: #fff; }}
.form-check-input:checked {{ background-color: {AZUL}; border-color: {AZUL}; }}
.irs--shiny .irs-bar {{ background: {CIAN}; border-color: {CIAN}; }}
.irs--shiny .irs-handle {{ border-color: {AZUL}; }}
.irs--shiny .irs-single, .irs--shiny .irs-from, .irs--shiny .irs-to {{ background: {AZUL}; }}

/* mini indicadores */
.mini-kpi {{ background: #EEF7F9; border-radius: 10px; padding: 10px 12px; height: 100%;
            border-top: 3px solid {CIAN}; }}
.mini-tit {{ font-size: .8rem; color: {TEXTO2}; display: block; text-align: left; }}
.mini-tit svg {{ margin-right: 6px; vertical-align: -0.1em; fill: {CIAN}; }}
.mini-val {{ font-size: 1.5rem; font-weight: 700; line-height: 1.3; margin-top: 2px; color: {TEXTO}; }}
.mini-nota {{ font-size: .75rem; color: {SUAVE}; }}

/* tabla de precisión del modelo */
.tabla-mod {{ width: 100%; border-collapse: collapse; font-size: .92rem; }}
.tabla-mod th {{ text-align: right; color: {TEXTO2}; font-weight: 600; padding: 7px 10px;
                border-bottom: 2px solid {CIAN}; }}
.tabla-mod td {{ text-align: right; padding: 6px 10px; border-bottom: 1px solid {REJILLA}; }}
.tabla-mod th:first-child, .tabla-mod td:first-child {{ text-align: left; font-weight: 600; }}
.tabla-mod tr.fila-2025 td {{ background: {VERDE_CLARO}66; font-weight: 700; border-bottom: 2px solid {ACENTO}; }}
.tabla-mod .tag {{ display:inline-block; padding: 1px 9px; border-radius: 20px; font-size: .75rem; }}
.tabla-mod .tag.aj {{ background: #E3EEF4; color: {TEXTO2}; }}
.tabla-mod .tag.pr {{ background: {ACENTO}; color: #fff; }}
"""

ESTILO_GLOBAL = ui.tags.style(CSS)


def kpi_icono(icono_svg, color="azul"):
    return ui.div(icono_svg, class_=f"kpi-ico {color}")


def pagina_titulo(num, titulo, subtitulo):
    """Encabezado de cada página: número, pregunta que responde y una línea de apoyo."""
    return ui.div(
        ui.div(str(num), class_="pag-num"),
        ui.div(ui.h3(titulo, class_="pag-tit"), ui.p(subtitulo, class_="pag-sub")),
        class_="pag-cab",
    )
