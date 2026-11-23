# Demanda eléctrica de la región Caribe · Tablero interactivo

Tablero desarrollado en **Shiny para Python** que analiza qué ha pasado con la demanda de energía eléctrica
en la región Caribe de Colombia entre 2018 y 2025, qué factores la mueven (temperatura, actividad económica
y El Niño) y cuánta potencia adicional habría que sumar si el clima se vuelve más extremo.

## Contenido del tablero
- **Portada:** título e integrantes del equipo.
- **1. Contexto:** evolución de la demanda, crecimiento anual y efecto de El Niño 2023–24.
- **2. Factores:** relación de la demanda con la temperatura, el ISE y el índice ONI, con filtro por fase climática.
- **3. Predicción:** modelo de regresión log-lineal, comparación real vs. modelo por año, estabilidad del efecto
  según el periodo de entrenamiento (2018–2024 / 2018–2025) y análisis de sensibilidad.
- **4. Simulación:** escenarios A, B y C, simulador interactivo, MW adicionales y meses críticos
  (temporada alta mayo–agosto vs. temporada baja), con recomendaciones.

## Ejecución
```bash
cd tablero
pip install -r requirements.txt
shiny run app.py --launch-browser
```

## Estructura
- `tablero/`: aplicación (`app.py`, una página por archivo, `modelo_demanda.py`, `escenarios.py`, `tema.py`) y la base de datos en Excel.
- `documento/`: documento técnico (Quarto) y PDF compilado.
- `presentacion/`: diapositivas con guion.

## Datos y fuentes
XM (Sinergox), DANE, NASA POWER, IDEAM y NOAA CPC.

## Integrantes
- Isabel Buelvas de la Hoz (T00077937)
- Luisa Acosta Romero (T00082202)
- Maria Espitaleta Julio (T00078486)
- Lineth Villalba Dominiquett (T00083377)
