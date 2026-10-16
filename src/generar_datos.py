"""
generar_datos.py
================
Genera los archivos de datos de ENTRADA del proyecto ETL de SuperMart Colombia.

Qué hace:
    1. Crea productos.csv y tiendas.csv (catálogos del enunciado).
    2. Crea ventas_crudas.csv: las 7 ventas del enunciado + 33 ventas nuevas
       generadas al azar (pero siempre con IDs de producto/tienda válidos).
    3. Introduce, A PROPÓSITO, algunos errores en las ventas (fechas con otro
       formato, clientes vacíos, un ID repetido, etc.) para que el pipeline
       ETL tenga datos "sucios" que limpiar.
    4. Escribe LEEME_datos.txt con la lista exacta de errores introducidos.

Cómo se ejecuta (desde cualquier carpeta):
    python src/generar_datos.py

Requisitos:
    Python 3.8+ y pandas  ->  pip install pandas

Notas de diseño:
    - Los datos son REPRODUCIBLES: se usa una semilla fija, así que cada vez
      que se ejecuta el script se obtiene exactamente el mismo resultado.
    - Los archivos se guardan en UTF-8 con BOM ("utf-8-sig") para que Excel
      muestre bien las tildes (Electrónicos, Bogotá, María...).
    - Todo se trabaja como TEXTO. Así pandas no cambia por su cuenta el
      formato de las fechas ni de los precios (15.50 no se vuelve 15.5).
"""

import logging
import random
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd

# ----------------------------------------------------------------------
# CONFIGURACIÓN GENERAL
# Si algo hay que ajustar (rutas, rangos, cantidad de datos), se cambia
# aquí arriba y no hace falta tocar la lógica del programa.
# ----------------------------------------------------------------------
SEMILLA = 42                      # misma semilla = mismos datos siempre
ENCODING = "utf-8-sig"            # UTF-8 con BOM: compatible con Excel

# Ruta del proyecto calculada a partir de la ubicación de este archivo.
# Así funciona sin importar desde qué carpeta se ejecute el script.
RAIZ_PROYECTO = Path(__file__).resolve().parent.parent
CARPETA_DATOS = RAIZ_PROYECTO / "data"

# Rango de ventas nuevas a generar (los IDs 1001-1007 ya vienen del enunciado)
PRIMER_ORDER_ID_NUEVO = 1008
ULTIMO_ORDER_ID_NUEVO = 1040

# Las fechas nuevas caerán entre el 14 y el 31 de marzo de 2024
FECHA_INICIO = date(2024, 3, 14)
DIAS_DE_RANGO = 17                # 14 de marzo + 17 días = 31 de marzo

CANTIDAD_MIN = 1
CANTIDAD_MAX = 4
TOTAL_CLIENTES = 12               # C001 ... C012

# ----------------------------------------------------------------------
# DATOS DEL ENUNCIADO
# ----------------------------------------------------------------------
COLUMNAS_VENTAS = [
    "order_id", "fecha", "producto_id", "cantidad",
    "precio_unitario", "cliente_id", "tienda_id",
]

# Las 7 ventas originales tal como aparecen en el enunciado.
# Observa que la venta 1003 ya trae dos "defectos": la fecha usa "/" y no
# tiene cliente. Se dejan así a propósito.
VENTAS_BASE = [
    ("1001", "2024-03-15", "P123", "2", "15.50", "C001", "T005"),
    ("1002", "2024-03-15", "P456", "1", "25.00", "C002", "T003"),
    ("1003", "2024/03/16", "P789", "3", "10.00", "",     "T001"),
    ("1004", "2024-03-16", "P123", "1", "15.50", "C003", "T002"),
    ("1005", "2024-03-17", "P999", "2", "30.00", "C004", "T004"),
    ("1006", "2024-03-17", "P321", "1", "45.00", "C005", "T001"),
    ("1007", "2024-03-18", "P456", "2", "25.00", "C001", "T003"),
]

PRODUCTOS: List[Dict[str, str]] = [
    {"producto_id": "P123", "categoria": "Electrónicos", "subcategoria": "Smartphones",      "marca": "Samsung"},
    {"producto_id": "P456", "categoria": "Hogar",        "subcategoria": "Electrodomésticos", "marca": "LG"},
    {"producto_id": "P789", "categoria": "Alimentos",    "subcategoria": "Bebidas",           "marca": "Coca-Cola"},
    {"producto_id": "P321", "categoria": "Ropa",         "subcategoria": "Calzado",           "marca": "Nike"},
    {"producto_id": "P999", "categoria": "Electrónicos", "subcategoria": "Tablets",           "marca": "Apple"},
]

TIENDAS: List[Dict[str, object]] = [
    {"tienda_id": "T001", "ciudad": "Bogotá",       "region": "Cundinamarca", "area_m2": 500, "gerente": "María González"},
    {"tienda_id": "T002", "ciudad": "Medellín",     "region": "Antioquia",    "area_m2": 450, "gerente": "Carlos Rodríguez"},
    {"tienda_id": "T003", "ciudad": "Cali",         "region": "Valle",        "area_m2": 400, "gerente": "Ana Martínez"},
    {"tienda_id": "T004", "ciudad": "Barranquilla", "region": "Atlántico",    "area_m2": 350, "gerente": "Pedro López"},
    {"tienda_id": "T005", "ciudad": "Cartagena",    "region": "Bolívar",      "area_m2": 300, "gerente": "Laura Ramírez"},
]

# Precio fijo de cada producto: así una misma venta nunca tiene un precio
# distinto al de su producto. Se deriva de VENTAS_BASE para no repetir datos.
PRECIOS: Dict[str, str] = {fila[2]: fila[4] for fila in VENTAS_BASE}


# ----------------------------------------------------------------------
# FUNCIONES
# Cada función hace UNA sola cosa. Eso facilita probarlas y entenderlas.
# ----------------------------------------------------------------------
def construir_ventas_base() -> pd.DataFrame:
    """Devuelve las 7 ventas originales del enunciado como DataFrame."""
    return pd.DataFrame(VENTAS_BASE, columns=COLUMNAS_VENTAS)


def generar_ventas_nuevas(rng: random.Random) -> pd.DataFrame:
    """
    Genera ventas nuevas con datos aleatorios pero VÁLIDOS.

    Args:
        rng: generador aleatorio con semilla (garantiza datos reproducibles).

    Returns:
        DataFrame con las mismas columnas que las ventas base, todo en texto.
    """
    ids_productos = list(PRECIOS)
    ids_tiendas = [tienda["tienda_id"] for tienda in TIENDAS]
    ids_clientes = [f"C{n:03d}" for n in range(1, TOTAL_CLIENTES + 1)]

    filas = []
    for order_id in range(PRIMER_ORDER_ID_NUEVO, ULTIMO_ORDER_ID_NUEVO + 1):
        producto = rng.choice(ids_productos)
        fecha = FECHA_INICIO + timedelta(days=rng.randint(0, DIAS_DE_RANGO))
        filas.append((
            str(order_id),
            fecha.isoformat(),                       # formato AAAA-MM-DD
            producto,
            str(rng.randint(CANTIDAD_MIN, CANTIDAD_MAX)),
            PRECIOS[producto],
            rng.choice(ids_clientes),
            rng.choice(ids_tiendas),
        ))
    return pd.DataFrame(filas, columns=COLUMNAS_VENTAS)


def inyectar_errores(ventas: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """
    Introduce errores controlados en las ventas para practicar la limpieza.

    Se identifican las filas por order_id (no por posición) para que el
    resultado sea fácil de documentar y no dependa del orden de las filas.

    Returns:
        (ventas con errores, lista de descripciones para el archivo LEEME)
    """
    ventas = ventas.copy()
    errores: List[str] = []

    # Errores ya presentes en el enunciado (los documentamos para el equipo)
    errores.append("1003 | fecha     | usa '/' en vez de '-' (viene así en el enunciado)")
    errores.append("1003 | cliente_id| vacío (viene así en el enunciado)")

    # 1) Fechas con "/" en lugar de "-"
    for order_id in ("1010", "1015", "1022", "1030"):
        filtro = ventas["order_id"] == order_id
        ventas.loc[filtro, "fecha"] = ventas.loc[filtro, "fecha"].str.replace("-", "/", regex=False)
        errores.append(f"{order_id} | fecha     | usa '/' en vez de '-'")

    # 2) Clientes vacíos (el ETL debe asignar CLIENTE_DESCONOCIDO)
    for order_id in ("1012", "1019", "1027", "1035"):
        ventas.loc[ventas["order_id"] == order_id, "cliente_id"] = ""
        errores.append(f"{order_id} | cliente_id| vacío")

    # 3) Cantidad inválida (negativa): prueba la validación de rangos
    ventas.loc[ventas["order_id"] == "1025", "cantidad"] = "-1"
    errores.append("1025 | cantidad  | valor negativo (-1)")

    # 4) Producto que NO existe en productos.csv: prueba la integridad referencial
    ventas.loc[ventas["order_id"] == "1033", "producto_id"] = "P000"
    errores.append("1033 | producto_id| 'P000' no existe en productos.csv")

    # 5) order_id duplicado: se copia una fila completa al final del archivo
    fila_repetida = ventas[ventas["order_id"] == "1020"]
    ventas = pd.concat([ventas, fila_repetida], ignore_index=True)
    errores.append("1020 | order_id  | aparece DOS veces (fila duplicada al final)")

    return ventas, errores


def guardar_csv(df: pd.DataFrame, nombre_archivo: str) -> Path:
    """Guarda un DataFrame como CSV en la carpeta data/ y devuelve su ruta."""
    CARPETA_DATOS.mkdir(parents=True, exist_ok=True)   # crea data/ si no existe
    ruta = CARPETA_DATOS / nombre_archivo
    df.to_csv(ruta, index=False, encoding=ENCODING)
    logging.info("Guardado %s (%d filas)", ruta.name, len(df))
    return ruta


def escribir_leeme(errores: List[str], total_filas: int) -> None:
    """Escribe LEEME_datos.txt con los errores introducidos a propósito."""
    lineas = [
        "DATOS DE ENTRADA - PROYECTO ETL SUPERMART COLOMBIA",
        "=" * 52,
        f"ventas_crudas.csv tiene {total_filas} filas (incluye 1 fila duplicada).",
        "productos.csv tiene 5 productos y tiendas.csv tiene 5 tiendas.",
        "",
        "Errores introducidos A PROPÓSITO (el pipeline debe detectarlos/corregirlos):",
        "order_id | columna | problema",
        "-" * 52,
        *errores,
        "",
        "Recomendaciones:",
        "- Leer los CSV con pandas usando encoding='utf-8-sig'.",
        "- No abrir ni guardar estos archivos con Excel: cambia el formato de las fechas.",
    ]
    ruta = CARPETA_DATOS / "LEEME_datos.txt"
    ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    logging.info("Guardado %s", ruta.name)


def main() -> None:
    """Punto de entrada: arma todos los datos y los guarda en disco."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    rng = random.Random(SEMILLA)   # generador propio, no afecta otros usos de random

    try:
        base = construir_ventas_base()
        nuevas = generar_ventas_nuevas(rng)
        ventas = pd.concat([base, nuevas], ignore_index=True)
        ventas, errores = inyectar_errores(ventas)

        guardar_csv(ventas, "ventas_crudas.csv")
        guardar_csv(pd.DataFrame(PRODUCTOS), "productos.csv")
        guardar_csv(pd.DataFrame(TIENDAS), "tiendas.csv")
        escribir_leeme(errores, len(ventas))
    except OSError as exc:
        # Errores de disco o permisos: se informa de forma clara y se termina
        logging.error("No se pudo escribir en %s: %s", CARPETA_DATOS, exc)
        raise SystemExit(1)

    logging.info("Listo. Archivos generados en: %s", CARPETA_DATOS)


# Esta condición hace que main() solo se ejecute cuando corres el archivo
# directamente (python src/generar_datos.py), y no si otro módulo lo importa.
if __name__ == "__main__":
    main()