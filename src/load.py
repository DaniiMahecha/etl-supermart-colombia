"""Fase 3: Carga (L) del pipeline ETL de SuperMart Colombia."""

import os
import sys

import pandas as pd

# Columnas del Data Mart (solo las útiles para análisis); se usan las que existan
COLUMNAS_DATA_MART = [
    "order_id", "fecha", "anio", "mes", "dia_semana",
    "ciudad", "region", "tienda_id",
    "categoria", "subcategoria", "marca",
    "cantidad", "precio_unitario", "venta_total", "categoria_venta",
    "cliente_id",
]

# Mínimo indispensable para armar el resumen ejecutivo
COLUMNAS_REQUERIDAS = ["order_id", "ciudad", "categoria", "venta_total"]


def cargar_resultados(tabla_final, carpeta_salida):
    """Guarda en carpeta_salida: ventas_transformadas.csv, data_mart.csv y
    resumen_ejecutivo.csv. No devuelve nada."""
    # Validaciones de entrada
    if tabla_final is None or tabla_final.empty:
        sys.exit("ERROR (carga): la tabla final está vacía, no hay nada que guardar.")
    faltantes = [c for c in COLUMNAS_REQUERIDAS if c not in tabla_final.columns]
    if faltantes:
        sys.exit(f"ERROR (carga): la tabla final no tiene las columnas: {', '.join(faltantes)}")

    os.makedirs(carpeta_salida, exist_ok=True)
    print("=== CARGA DE RESULTADOS ===")

    try:
        # 1. Dataset transformado completo
        ruta = os.path.join(carpeta_salida, "ventas_transformadas.csv")
        tabla_final.to_csv(ruta, index=False, encoding="utf-8-sig")
        print(f"  ventas_transformadas.csv: {len(tabla_final)} filas")

        # 2. Data Mart: solo columnas útiles para análisis
        cols = [c for c in COLUMNAS_DATA_MART if c in tabla_final.columns]
        data_mart = tabla_final[cols]
        ruta = os.path.join(carpeta_salida, "data_mart.csv")
        data_mart.to_csv(ruta, index=False, encoding="utf-8-sig")
        print(f"  data_mart.csv: {len(data_mart)} filas, {len(cols)} columnas")

        # 3. Resumen ejecutivo: ventas agregadas por ciudad y categoría
        resumen = (
            tabla_final
            .groupby(["ciudad", "categoria"], as_index=False)
            .agg(
                ventas_totales=("venta_total", "sum"),
                num_transacciones=("order_id", "count"),
                ticket_promedio=("venta_total", "mean"),
            )
            .sort_values("ventas_totales", ascending=False)
            .round(2)
        )
        ruta = os.path.join(carpeta_salida, "resumen_ejecutivo.csv")
        resumen.to_csv(ruta, index=False, encoding="utf-8-sig")
        print(f"  resumen_ejecutivo.csv: {len(resumen)} filas")
    except OSError as e:
        sys.exit(f"ERROR (carga): no se pudo escribir en '{carpeta_salida}': {e}")

    print("Carga completada.\n")
