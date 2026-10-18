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

3. **Instalar las librerías** (se usa `python -m pip` para instalarlas en el mismo Python que ejecutará el proyecto):
   ```
   python -m pip install -r requirements.txt
   ```

4. **Ejecutar el pipeline completo:**
   ```
   python main.py
   ```
   En pantalla se muestra cada etapa con su tiempo de ejecución. Si una etapa falla, el mensaje indica cuál fue y quién es el responsable de esa parte.

5. **Revisar los resultados** en la carpeta `output/`.

> Los datos de entrada ya vienen incluidos en `data/`. Si se quieren regenerar (son reproducibles, siempre salen los mismos), se puede ejecutar `python src/generar_datos.py`.

## Solución de problemas

**Error `No module named 'matplotlib'` (o `pandas`, `numpy`, `seaborn`)**

Significa que las librerías están instaladas en un Python distinto del que ejecuta `main.py`. Pasa con frecuencia cuando hay varias versiones de Python en el computador: `pip install` instala en una y el editor (por ejemplo VS Code) ejecuta con otra.

Solución: instalar las librerías con el **mismo Python que ejecuta el proyecto**, usando `python -m pip` desde la carpeta del proyecto:
```
python -m pip install -r requirements.txt
```
Si se usa la ruta completa del intérprete en PowerShell, el comando lleva `&` al inicio:
```
& "C:\ruta\a\python.exe" -m pip install -r requirements.txt
```
Para saber qué Python usa VS Code: abrir la paleta de comandos (`Ctrl+Shift+P`) y elegir *Python: Select Interpreter*, o mirar la versión que aparece abajo a la derecha de la ventana. Además, cuando falta una librería, `main.py` muestra en el mensaje de error el comando exacto con el Python que está usando.

**Error `No se pudo importar una parte del pipeline` con el mensaje "Revisa que existan en `src/` los 5 archivos"**

Falta alguno de los archivos del proyecto en `src/` (`extract.py`, `transform_clean.py`, `transform_enrich.py`, `load.py` o `reports.py`), o está en otra carpeta. Verificar que los cinco estén dentro de `src/`.

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

Resultados de la ejecución sobre los datos de ejemplo incluidos en `data/` (el detalle completo está en `output/reporte_ejecutivo.txt`):

| Métrica | Valor |
|---|---|
| Transacciones analizadas | 38 (de 41 iniciales) |
| Ventas totales | 1,975.00 |
| Promedio por venta | 51.97 |
| Ciudad líder en ventas | Barranquilla: 572.50 (29.0% del total) |
| Categoría líder en ventas | Electrónicos: 970.00 (49.1% del total) |
| Día con más transacciones | Viernes: 11 transacciones |

**Calidad de los datos:** de las 41 filas iniciales se eliminó 1 duplicado y 2 filas inválidas (una con cantidad negativa y otra con un producto que no existe en el catálogo), y 5 ventas sin cliente quedaron asignadas a `CLIENTE_DESCONOCIDO`. En total, 38 filas pasaron a la tabla final.

## Hallazgos y conclusiones

Los hallazgos se basan en el conjunto de datos de ejemplo generado para este ejercicio.

1. **Electrónicos concentra casi la mitad de las ventas** (49.1%), y Tablets es la subcategoría que más vende (660.00).
2. **Barranquilla lidera en ventas totales, pero Cartagena tiene el ticket promedio más alto.** Barranquilla suma 572.50 en 9 transacciones, mientras que Cartagena promedia 78.50 por venta con solo 6 transacciones. Medellín queda al final, con 118.50 en ventas y un ticket promedio de 19.75.
3. **Las ventas se concentran de jueves a sábado:** estos tres días reúnen 27 de las 38 transacciones (71.1%). El viernes es el día más fuerte, con 11 transacciones y 598.00 en ventas.
4. **Las ventas de monto alto pesan mucho:** 17 de las 38 ventas son Altas (50 o más), 15 son Medias y 6 son Bajas.
5. **La calidad de los datos de origen necesita mejorar:** el 7.3% de las filas (3 de 41) debió eliminarse y el 12.2% de las ventas (5 de 41) llegó sin cliente identificado.

### Recomendaciones

- Reforzar inventario y personal de jueves a sábado, que es cuando se concentra la demanda.
- Revisar el surtido y los precios en Medellín, donde el ticket promedio es muy inferior al del resto de ciudades.
- Impulsar la categoría Electrónicos, en especial Tablets, que es la que más aporta a las ventas.
- Exigir el registro del cliente y validar cantidades y códigos de producto en el punto de venta, para reducir los errores en origen.

## Tecnologías

Python · pandas · numpy · matplotlib · seaborn · Git
