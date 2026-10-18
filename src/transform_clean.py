"""Fase 2: Limpieza y cálculo de métricas del pipeline ETL de SuperMart Colombia."""

import pandas as pd
import numpy as np


def limpiar_ventas(ventas):
    """
    Limpia los datos de ventas y calcula las métricas correspondientes.

    Parámetros:
        ventas: DataFrame de pandas con las ventas originales.

    Devuelve:
        ventas_limpias: DataFrame con los datos transformados.
        indicadores: Diccionario con indicadores de calidad.
    """

    # Trabajar sobre una copia para no modificar los datos originales.
    ventas_limpias = ventas.copy()

    # Registrar el número inicial de filas.
    filas_iniciales = len(ventas_limpias)

    # 1. Identificar los clientes vacíos o nulos.
    clientes_vacios = (
        ventas_limpias["cliente_id"].isna()
        | ventas_limpias["cliente_id"]
        .astype("string")
        .str.strip()
        .eq("")
    )

    clientes_desconocidos = int(clientes_vacios.sum())

    # Reemplazar los clientes faltantes.
    ventas_limpias.loc[
        clientes_vacios, "cliente_id"
    ] = "CLIENTE_DESCONOCIDO"

    # 2. Convertir las fechas a un formato uniforme.
    fechas = (
        ventas_limpias["fecha"]
        .astype("string")
        .str.strip()
        .str.replace("/", "-", regex=False)
    )

    ventas_limpias["fecha"] = pd.to_datetime(
        fechas,
        format="%Y-%m-%d",
        errors="coerce"
    )

    # 3. Eliminar order_id duplicados y conservar el primero.
    duplicados_eliminados = int(
        ventas_limpias["order_id"].duplicated().sum()
    )

    ventas_limpias = ventas_limpias.drop_duplicates(
        subset=["order_id"],
        keep="first"
    ).copy()

    # 4. Calcular el total de cada venta.
    ventas_limpias["venta_total"] = (
        ventas_limpias["cantidad"]
        * ventas_limpias["precio_unitario"]
    )

    # 5. Clasificar las ventas por su monto.
    ventas_limpias["categoria_venta"] = pd.cut(
        ventas_limpias["venta_total"],
        bins=[-np.inf, 20, 50, np.inf],
        labels=["Baja", "Media", "Alta"],
        right=False
    )

    # 6. Crear los indicadores de calidad.
    indicadores = {
        "filas_iniciales": filas_iniciales,
        "duplicados_eliminados": duplicados_eliminados,
        "clientes_desconocidos": clientes_desconocidos
    }

    # Devolver la tabla limpia y los indicadores.
    return ventas_limpias, indicadores
