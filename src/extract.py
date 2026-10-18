"""Fase 1: Extracción (E) del pipeline ETL de SuperMart Colombia."""

import os
import sys

import pandas as pd

# Archivo esperado -> (clave del diccionario, columnas mínimas requeridas)
ARCHIVOS = {
    "ventas_crudas.csv": (
        "ventas",
        ["order_id", "fecha", "producto_id", "cantidad",
         "precio_unitario", "cliente_id", "tienda_id"],
    ),
    "productos.csv": (
        "productos",
        ["producto_id", "categoria", "subcategoria", "marca"],
    ),
    "tiendas.csv": (
        "tiendas",
        ["tienda_id", "ciudad", "region", "area_m2", "gerente"],
    ),
}


def extraer_datos(carpeta_datos):
    """Lee los 3 CSV de la carpeta y devuelve {"ventas", "productos", "tiendas"}.

    Si falta un archivo, está vacío o tiene un formato incorrecto, el programa
    se detiene con un mensaje claro (nunca devuelve tablas vacías).
    """
    # 1. Verificar que la carpeta exista
    if not os.path.isdir(carpeta_datos):
        sys.exit(f"ERROR: la carpeta de datos '{carpeta_datos}' no existe.")

    # 2. Verificar que estén los 3 archivos antes de leer cualquiera
    faltantes = [
        nombre for nombre in ARCHIVOS
        if not os.path.isfile(os.path.join(carpeta_datos, nombre))
    ]
    if faltantes:
        sys.exit(
            f"ERROR: faltan archivos en '{carpeta_datos}': {', '.join(faltantes)}"
        )

    # 3. Leer cada archivo
    tablas = {}
    print("=== EXTRACCIÓN DE DATOS ===")
    for nombre, (clave, columnas) in ARCHIVOS.items():
        ruta = os.path.join(carpeta_datos, nombre)
        try:
            df = pd.read_csv(ruta, encoding="utf-8-sig")
        except pd.errors.EmptyDataError:
            sys.exit(f"ERROR: el archivo '{nombre}' está vacío.")
        except (pd.errors.ParserError, UnicodeDecodeError) as e:
            sys.exit(f"ERROR: formato incorrecto en '{nombre}': {e}")
        except OSError as e:
            sys.exit(f"ERROR: no se pudo leer '{nombre}': {e}")

        # Limpiar espacios en los nombres de columnas
        df.columns = df.columns.str.strip()

        # Validar columnas requeridas
        columnas_faltantes = [c for c in columnas if c not in df.columns]
        if columnas_faltantes:
            sys.exit(
                f"ERROR: a '{nombre}' le faltan las columnas: "
                f"{', '.join(columnas_faltantes)}"
            )

        if df.empty:
            sys.exit(f"ERROR: el archivo '{nombre}' no contiene registros.")

        print(f"  {nombre}: {len(df)} registros, {len(df.columns)} columnas")
        tablas[clave] = df

    print("Extracción completada.\n")
    return tablas
