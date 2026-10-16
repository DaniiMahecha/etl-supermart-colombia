# Pipeline ETL para el análisis de ventas de SuperMart Colombia

Proyecto de la **Actividad de aprendizaje 2** (Universidad EAN). Pipeline ETL (Extract, Transform, Load) en Python que toma datos de ventas dispersos en archivos CSV, los limpia, los enriquece, los guarda en formatos listos para análisis y genera visualizaciones y un reporte ejecutivo de forma automática.

**Empresa:** EAN TechRetail Solutions · **Cliente:** SuperMart Colombia

## Equipo

| Integrante | Responsabilidad | Archivo |
|---|---|---|
| Daniel | Datos de entrada, integración (`main.py`), repositorio y entrega | `src/generar_datos.py`, `main.py` |
| Juan Arango | Extracción de datos y carga de resultados | `src/extract.py`, `src/load.py` |
| Juan Esteban | Limpieza de datos y cálculo de métricas | `src/transform_clean.py` |
| Luisa | Validación, enriquecimiento y control de calidad | `src/transform_enrich.py` |
| Carlos | Visualizaciones y reporte ejecutivo | `src/reports.py` |

## Estructura del proyecto

```
etl_supermart/
├── data/                        Datos de entrada (CSV)
│   ├── ventas_crudas.csv
│   ├── productos.csv
│   ├── tiendas.csv
│   └── LEEME_datos.txt          Lista de errores introducidos a propósito
├── output/                      Resultados generados por el pipeline
│   ├── ventas_transformadas.csv
│   ├── data_mart.csv
│   ├── resumen_ejecutivo.csv
│   ├── reporte_ejecutivo.txt
│   └── graficos/                Las 4 visualizaciones (.png)
├── src/                         Código de cada etapa
│   ├── generar_datos.py
│   ├── extract.py
│   ├── transform_clean.py
│   ├── transform_enrich.py
│   ├── load.py
│   └── reports.py
├── main.py                      Ejecuta el pipeline completo
├── requirements.txt
└── README.md
```

## Requisitos

- Python 3.8 o superior
- Librerías: `pandas`, `numpy`, `matplotlib`, `seaborn` (listadas en `requirements.txt`)

## Instrucciones de ejecución

1. **Descargar el proyecto** (clonar el repositorio o descomprimir el ZIP) y abrir una terminal en la carpeta `etl_supermart`.

2. **(Opcional, recomendado) Crear un entorno virtual:**

   Windows:
   ```
   python -m venv .venv
   .venv\Scripts\activate
   ```
   macOS / Linux:
   ```
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Instalar las librerías:**
   ```
   pip install -r requirements.txt
   ```

4. **Ejecutar el pipeline completo:**
   ```
   python main.py
   ```
   En pantalla se muestra cada etapa con su tiempo de ejecución. Si una etapa falla, el mensaje indica cuál fue y quién es el responsable de esa parte.

5. **Revisar los resultados** en la carpeta `output/`.

> Los datos de entrada ya vienen incluidos en `data/`. Si se quieren regenerar (son reproducibles, siempre salen los mismos), se puede ejecutar `python src/generar_datos.py`.

## Cómo funciona el pipeline

| Fase | Etapa | Qué hace |
|---|---|---|
| E | Extracción | Lee los 3 CSV con pandas, maneja errores de archivo no encontrado o formato incorrecto y muestra cuántos registros tiene cada archivo. |
| T | Limpieza | Unifica el formato de las fechas, asigna `CLIENTE_DESCONOCIDO` a los clientes vacíos, elimina IDs de orden duplicados, calcula `venta_total` y clasifica cada venta como Baja (menos de $20), Media ($20 a $50) o Alta ($50 o más). |
| T | Enriquecimiento y validación | Elimina filas inválidas (cantidades no positivas, fechas inválidas, productos o tiendas inexistentes), une la información de productos y tiendas y crea las dimensiones temporales (año, mes, día de la semana). |
| L | Carga | Guarda el dataset transformado completo, un Data Mart para análisis y un resumen ejecutivo agregado (todos en CSV). |
| — | Reportes | Genera 4 gráficos (ventas por ciudad, ventas por categoría, transacciones por día de la semana y distribución de montos) y un reporte ejecutivo en texto. |

Cada etapa es una función independiente. Las entradas y salidas de cada una (el "contrato" entre módulos) están documentadas al inicio de `main.py`.

## Datos de entrada

| Archivo | Contenido | Registros |
|---|---|---|
| `ventas_crudas.csv` | Ventas: orden, fecha, producto, cantidad, precio, cliente y tienda | 41 |
| `productos.csv` | Categoría, subcategoría y marca de cada producto | 5 |
| `tiendas.csv` | Ciudad, región, área y gerente de cada tienda | 5 |

Las ventas incluyen **errores introducidos a propósito** para que el pipeline los detecte y corrija: fechas con otro formato (`/` en lugar de `-`), clientes vacíos, un `order_id` duplicado, una cantidad negativa y un producto que no existe en el catálogo. El detalle está en `data/LEEME_datos.txt`.

Los archivos se guardan en UTF-8 con BOM (`utf-8-sig`) para que las tildes se vean bien al abrirlos en Excel. Se recomienda **no guardar los CSV desde Excel**, porque modifica el formato de las fechas.

## Archivos de salida

| Archivo | Descripción |
|---|---|
| `output/ventas_transformadas.csv` | Dataset transformado completo |
| `output/data_mart.csv` | Data Mart optimizado para análisis |
| `output/resumen_ejecutivo.csv` | Resumen ejecutivo agregado |
| `output/reporte_ejecutivo.txt` | Reporte con métricas, líderes e indicadores de calidad |
| `output/graficos/` | Las 4 visualizaciones en formato `.png` |

## Resultados principales

> **PENDIENTE: completar después de ejecutar el pipeline con el código final** (tomar los datos de `output/reporte_ejecutivo.txt`).

- Ventas totales: _por completar_
- Ciudad líder en ventas: _por completar_
- Categoría líder en ventas: _por completar_
- Día de la semana con más transacciones: _por completar_
- Indicadores de calidad de datos (duplicados eliminados, filas inválidas, clientes desconocidos): _por completar_

## Hallazgos y conclusiones

> **PENDIENTE: completar con los hallazgos del equipo antes de la demo.**

- _por completar_

## Tecnologías

Python · pandas · numpy · matplotlib · seaborn · Git
