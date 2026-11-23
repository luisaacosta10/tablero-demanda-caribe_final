"""
Página 1 · Contexto — Demanda eléctrica de la región Caribe (Persona 1)
Módulo de Shiny para Python, listo para unir al dashboard del grupo.

Uso dentro del app del grupo:
    from pagina1_contexto import cargar_base, contexto_ui, contexto_server, ESTILO
    base = cargar_base("base_demanda_caribe_2018_2025.xlsx")
    # UI:     ui.nav_panel("Contexto", contexto_ui("contexto"))   (y header=ESTILO en page_navbar)
    # server: contexto_server("contexto", base)

Paquetes: pip install shiny shinywidgets plotly pandas openpyxl faicons
"""
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from faicons import icon_svg
from plotly.subplots import make_subplots
from shiny import module, reactive, render, ui
from shinywidgets import output_widget, render_widget

# ---------- Colores (paleta común en tema.py) ----------
import tema
C = {
    "azul": tema.AZUL,          # demanda real
    "naranja": tema.ACENTO,     # calor / aumento / El Niño (verde oscuro de la paleta; se conserva la clave)
    "gris": tema.GRIS_CLARO,    # el resto
    "texto": tema.TEXTO,
    "suave": tema.SUAVE,
    "rejilla": tema.REJILLA,
    "franja_nino": tema.RGBA_NINO,
    "franja_nina": tema.RGBA_NINA,
}
MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]

_ESTILO_P1 = ui.tags.style(f"""
  .ctx-titulo {{ font-weight: 700; margin-bottom: .15rem; }}
  .ctx-sub {{ color: {C['suave']}; }}
  .ctx-card .card-header {{ background: #FFFFFF; border-bottom: 1px solid #EEE; }}
  .ctx-card-titulo {{ font-weight: 600; font-size: 1rem; color: {C['texto']}; }}
  .ctx-card-sub {{ font-size: .82rem; color: {C['suave']}; margin-top: .1rem; }}
  .ctx-kpi .value-box-title, .ctx-kpi .value-box-title * {{ font-size: .95rem !important;
      color: {C['texto']}; margin: 0; }}
  .ctx-kpi .value-box-value {{ font-size: 1.9rem; font-weight: 700; color: {C['texto']}; }}
  .ctx-kpi p {{ font-size: .82rem; color: {C['suave']}; margin: 0; }}
  .ctx-icono {{ width: 64px; height: 64px; border-radius: 50%; display: flex;
               align-items: center; justify-content: center; }}
  .ctx-icono svg {{ width: 30px !important; height: 30px !important; fill: currentColor; }}
  .ctx-fuente {{ font-size: .82rem; color: {C['suave']}; }}
""")
ESTILO = ui.TagList(tema.ESTILO_GLOBAL, _ESTILO_P1)



# ---------- Datos ----------
def cargar_base(ruta="base_demanda_caribe_2018_2025.xlsx") -> pd.DataFrame:
    ruta = Path(ruta)
    if ruta.suffix.lower() == ".csv":
        base = pd.read_csv(ruta, encoding="utf-8-sig")
    else:
        base = pd.read_excel(ruta, sheet_name="base_mensual")
    base["fecha"] = pd.to_datetime(base["fecha"])
    base["fase_enso"] = np.select([base["el_nino"] == 1, base["la_nina"] == 1],
                                  ["El Niño", "La Niña"], default="Neutral")
    base["mes_txt"] = [f"{MESES[f.month - 1]} {f.year}" for f in base["fecha"]]
    return base


def fmt(x, dec=1):
    """Número con formato colombiano: 22.941,5"""
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def periodos_enso(df):
    """Tramos seguidos de El Niño o La Niña: [(fase, inicio, fin_exclusivo), ...]"""
    tramos, grupo = [], (df["fase_enso"] != df["fase_enso"].shift()).cumsum()
    for _, g in df.groupby(grupo):
        fase = g["fase_enso"].iloc[0]
        if fase != "Neutral":
            medio_mes = pd.Timedelta(days=15)  # los puntos van al inicio del mes: centra la franja
            tramos.append((fase, g["fecha"].iloc[0] - medio_mes, g["fecha"].iloc[-1] + medio_mes))
    return tramos


def estilo_fig(fig, alto, leyenda=False):
    fig.update_layout(
        height=alto, template="simple_white", separators=",.",
        margin=dict(l=70, r=20, t=10, b=40),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=C["texto"], size=12),
        showlegend=leyenda, hoverlabel=dict(bgcolor="white"),
        legend=dict(orientation="h", y=1.08, x=0, bgcolor="rgba(0,0,0,0)"),
    )
    fig.update_yaxes(showgrid=True, gridcolor=C["rejilla"], tickformat=",.0f")
    fig.update_xaxes(showgrid=False)
    return fig


# ---------- Piezas de la UI ----------
def kpi(titulo, valor_id, nota, icono, color):
    insignia = ui.div(icon_svg(icono), class_="ctx-icono",
                      style=f"background:{color}1F; color:{color};")
    return ui.value_box(titulo, ui.output_text(valor_id), nota,
                        showcase=insignia, showcase_layout="left center", class_="ctx-kpi kpi")


def tarjeta(titulo_id, sub_id, grafico_id):
    return ui.card(
        ui.card_header(ui.div(ui.div(ui.output_text(titulo_id), class_="ctx-card-titulo"),
                              ui.div(ui.output_text(sub_id), class_="ctx-card-sub"))),
        output_widget(grafico_id),
        class_="ctx-card",
    )


@module.ui
def contexto_ui():
    anios = ["Todos"] + [str(a) for a in range(2018, 2026)]
    return ui.div(
        ui.div(
            ui.div(
                ui.h3("Contexto: demanda eléctrica de la región Caribe", class_="ctx-titulo"),
                ui.p("Atlántico, Bolívar, Cesar, Córdoba, La Guajira, Magdalena y Sucre · 2018–2025",
                     class_="ctx-sub mb-0"),
            ),
            ui.div(ui.input_select("anio", "Año", choices=anios, selected="Todos"), style="min-width:200px;"),
            class_="d-flex justify-content-between align-items-end flex-wrap gap-3 my-3",
        ),
        ui.layout_columns(
            kpi("Demanda total", "kpi_demanda", ui.output_text("kpi_demanda_nota"), "bolt", C["azul"]),
            kpi(ui.output_text("kpi_crec_titulo"), "kpi_crec", ui.output_text("kpi_crec_nota"),
                "arrow-trend-up", tema.CIAN),
            kpi("Temperatura media", "kpi_temp", ui.output_text("kpi_temp_nota"), "temperature-high", C["naranja"]),
            kpi("Día de mayor demanda", "kpi_record", ui.output_text("kpi_record_nota"), "gauge-high", tema.ARENA),
            col_widths=[3, 3, 3, 3], fill=False,
        ),
        tarjeta("t_mensual", "s_mensual", "graf_mensual"),
        ui.layout_columns(
            tarjeta("t_anual", "s_anual", "graf_anual"),
            tarjeta("t_nino", "s_nino", "graf_nino"),
            col_widths=[6, 6], fill=False,
        ),
        ui.p("Fuentes: XM – Sinergox (demanda comercial región Caribe), NASA POWER (temperatura), "
             "NOAA CPC (índice ONI).", class_="ctx-fuente mt-2"),
    )


# ---------- Server ----------
@module.server
def contexto_server(input, output, session, base: pd.DataFrame):
    anual = base.groupby("anio", as_index=False)["demanda_gwh"].sum()
    clima_mes = base.groupby("mes")["temperatura_c"].mean()

    def demanda_anio(a):
        return float(anual.loc[anual["anio"] == a, "demanda_gwh"].iloc[0])

    @reactive.calc
    def todos():
        return input.anio() == "Todos"

    @reactive.calc
    def filtrada():
        return base if todos() else base[base["anio"] == int(input.anio())]

    # ---------------- Indicadores ----------------
    @render.text
    def kpi_demanda():
        return f"{fmt(filtrada()['demanda_gwh'].sum(), 0)} GWh"

    @render.text
    def kpi_demanda_nota():
        return "acumulado 2018–2025" if todos() else f"consumidos en {input.anio()}"

    @render.text
    def kpi_crec_titulo():
        return "Crecimiento anual promedio" if todos() else "Crecimiento vs año anterior"

    @render.text
    def kpi_crec():
        if todos():
            tasa = (demanda_anio(2025) / demanda_anio(2018)) ** (1 / 7) - 1
        else:
            a = int(input.anio())
            if a == anual["anio"].min():
                return "—"
            tasa = demanda_anio(a) / demanda_anio(a - 1) - 1
        return f"{'+' if tasa >= 0 else ''}{fmt(100 * tasa)} %"

    @render.text
    def kpi_crec_nota():
        if todos():
            return "por año, de 2018 a 2025"
        a = int(input.anio())
        return "primer año de la base" if a == anual["anio"].min() else f"frente a {a - 1}"

    @render.text
    def kpi_temp():
        return f"{fmt(filtrada()['temperatura_c'].mean())} °C"

    @render.text
    def kpi_temp_nota():
        if todos():
            return "promedio de 6 capitales"
        dif = filtrada()["temperatura_c"].mean() - base["temperatura_c"].mean()
        return f"{'+' if dif >= 0 else ''}{fmt(dif)} °C frente al promedio 2018–2025"

    @render.text
    def kpi_record():
        return f"{fmt(filtrada()['demanda_max_dia_gwh'].max())} GWh"

    @render.text
    def kpi_record_nota():
        f = filtrada()
        return f"en un solo día de {f.loc[f['demanda_max_dia_gwh'].idxmax(), 'mes_txt']}"

    # ---------------- Gráfico principal: demanda + calor ----------------
    @render.text
    def t_mensual():
        return "La demanda sube cuando hace más calor de lo normal" if todos() \
            else f"Demanda y temperatura mes a mes, {input.anio()}"

    @render.text
    def s_mensual():
        return ("Arriba: demanda diaria promedio (GWh/día). Abajo: cuánto se alejó la temperatura de lo normal "
                "para ese mes. Franjas: verde = El Niño, arena = La Niña.")

    @render_widget
    def graf_mensual():
        f = filtrada().copy()
        f["anom"] = f["temperatura_c"] - f["mes"].map(clima_mes)
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.68, 0.32],
                            vertical_spacing=0.06)
        fig.add_scatter(x=f["fecha"], y=f["demanda_diaria_prom_gwh"], mode="lines+markers" if not todos() else "lines",
                        line=dict(color=C["azul"], width=2.5), marker=dict(size=7), name="Demanda",
                        customdata=f["mes_txt"],
                        hovertemplate="%{customdata}<br><b>%{y:,.1f} GWh/día</b><extra></extra>", row=1, col=1)
        fig.add_bar(x=f["fecha"], y=f["anom"], name="Temperatura vs. lo normal",
                    marker_color=np.where(f["anom"] >= 0, C["naranja"], C["azul"]), opacity=0.85,
                    customdata=np.stack([f["mes_txt"], f["temperatura_c"]], axis=-1),
                    hovertemplate="%{customdata[0]}<br><b>%{y:+.2f} °C</b> vs. lo normal"
                                  "<br>(%{customdata[1]:.1f} °C)<extra></extra>", row=2, col=1)
        for fase, x0, x1 in periodos_enso(f):
            color = C["franja_nino"] if fase == "El Niño" else C["franja_nina"]
            for yref in ("y domain", "y2 domain"):
                fig.add_shape(type="rect", xref="x", yref=yref, x0=x0, x1=x1, y0=0, y1=1,
                              fillcolor=color, line_width=0, layer="below")
            if (x1 - x0).days > 60:
                fig.add_annotation(x=x0 + (x1 - x0) / 2, xref="x", y=1, yref="y domain", text=fase,
                                   showarrow=False, yanchor="top", font=dict(size=11, color=C["suave"]))
        estilo_fig(fig, 470)
        fig.update_layout(bargap=0.25, margin=dict(t=20))
        fig.update_yaxes(title_text="GWh/día", tickformat=",.0f", row=1, col=1)
        fig.update_yaxes(title_text="°C vs. normal", tickformat="+.1f", zeroline=True,
                         zerolinecolor=tema.GRIS, row=2, col=1)
        if not todos():
            fig.update_xaxes(tickvals=f["fecha"], ticktext=[MESES[x.month - 1] for x in f["fecha"]], row=2, col=1)
        return fig

    # ---------------- Demanda por año ----------------
    @render.text
    def t_anual():
        return "La demanda creció 31 % entre 2018 y 2025"

    @render.text
    def s_anual():
        sel = "2025" if todos() else input.anio()
        return f"GWh por año. En azul, {sel}. Solo 2020 cayó, por la pandemia."

    @render_widget
    def graf_anual():
        sel = anual["anio"].max() if todos() else int(input.anio())
        colores = [C["azul"] if a == sel else C["gris"] for a in anual["anio"]]
        fig = go.Figure(go.Bar(
            x=anual["anio"].astype(str), y=anual["demanda_gwh"], marker_color=colores, width=0.5,
            text=[fmt(v, 0) for v in anual["demanda_gwh"]], textposition="outside",
            textfont=dict(size=11, color=C["texto"]),
            hovertemplate="%{x}: <b>%{y:,.0f} GWh</b><extra></extra>"))
        estilo_fig(fig, 320)
        fig.update_yaxes(title_text="GWh por año", range=[0, 27500], dtick=5000)
        return fig

    # ---------------- El Niño 2023-24 vs año anterior ----------------
    antes = base[(base["fecha"] >= "2022-06-01") & (base["fecha"] <= "2023-05-01")].reset_index(drop=True)
    nino = base[(base["fecha"] >= "2023-06-01") & (base["fecha"] <= "2024-05-01")].reset_index(drop=True)
    var_total = nino["demanda_gwh"].sum() / antes["demanda_gwh"].sum() - 1
    var_temp = nino["temperatura_c"].mean() - antes["temperatura_c"].mean()

    @render.text
    def t_nino():
        return "Durante El Niño 2023-24 la demanda fue mayor los 12 meses"

    @render.text
    def s_nino():
        return (f"Demanda diaria promedio, junio a mayo. En total +{fmt(100 * var_total)} % "
                f"y +{fmt(var_temp)} °C frente al año anterior. No todo es El Niño: parte es crecimiento "
                f"normal; el calor explica cerca de la mitad (ver página 3).")

    @render_widget
    def graf_nino():
        meses = [MESES[f.month - 1] for f in nino["fecha"]]
        fig = go.Figure()
        fig.add_scatter(x=meses, y=antes["demanda_diaria_prom_gwh"], name="Jun-22 a may-23 (antes)",
                        mode="lines+markers", line=dict(color=tema.GRIS, width=2.5), marker=dict(size=6),
                        hovertemplate="%{x} (antes): <b>%{y:,.1f} GWh/día</b><extra></extra>")
        fig.add_scatter(x=meses, y=nino["demanda_diaria_prom_gwh"], name="Jun-23 a may-24 (El Niño)",
                        mode="lines+markers", line=dict(color=C["naranja"], width=3), marker=dict(size=7),
                        fill="tonexty", fillcolor=C["franja_nino"],
                        hovertemplate="%{x} (El Niño): <b>%{y:,.1f} GWh/día</b><extra></extra>")
        estilo_fig(fig, 320, leyenda=True)
        fig.update_layout(margin=dict(t=40))
        fig.update_yaxes(title_text="GWh/día", range=[45, 70], dtick=5)
        return fig
