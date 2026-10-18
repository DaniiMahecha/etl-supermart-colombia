"""Fase 2: Enriquecimiento y validación del pipeline ETL de SuperMart Colombia."""

import sys

import pandas as pd

# Columnas que debe traer cada tabla de entrada
COLUMNAS_VENTAS = [
    "order_id", "fecha", "producto_id", "cantidad", "precio_unitario",
    "cliente_id", "tienda_id", "venta_total", "categoria_venta",
]
COLUMNAS_PRODUCTOS = ["producto_id", "categoria", "subcategoria", "marca"]
COLUMNAS_TIENDAS = ["tienda_id", "ciudad", "region", "area_m2", "gerente"]

# Columnas EXACTAS (y en este orden) que debe tener la tabla final
COLUMNAS_FINALES = [
    "order_id", "fecha", "producto_id", "cantidad", "precio_unitario",
    "cliente_id", "tienda_id", "venta_total", "categoria_venta",
    "categoria", "subcategoria", "marca",
    "ciudad", "region", "area_m2", "gerente",
    "anio", "mes", "dia_semana",
]

# pandas numera los días: lunes = 0 ... domingo = 6
DIAS_ES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]


def enriquecer_y_validar(ventas_limpias, productos, tiendas):
    """Valida las ventas limpias, las une con productos y tiendas y crea columnas de tiempo.

    Parámetros:
        ventas_limpias: DataFrame que devuelve limpiar_ventas.
        productos: DataFrame de productos.
        tiendas: DataFrame de tiendas.

    Devuelve:
        tabla_final: DataFrame con exactamente las columnas de COLUMNAS_FINALES.
        indicadores: diccionario {"filas_invalidas_eliminadas": n}
    """
    # 0. VALIDAR LA ENTRADA: que sean tablas y que traigan las columnas esperadas
    entradas = [
        ("ventas_limpias", ventas_limpias, COLUMNAS_VENTAS),
        ("productos", productos, COLUMNAS_PRODUCTOS),
        ("tiendas", tiendas, COLUMNAS_TIENDAS),
    ]
    for nombre, tabla_entrada, columnas in entradas:
        if not isinstance(tabla_entrada, pd.DataFrame):
            sys.exit(f"ERROR (enriquecimiento): '{nombre}' no es una tabla de pandas.")
        faltantes = [c for c in columnas if c not in tabla_entrada.columns]
        if faltantes:
            sys.exit(
                f"ERROR (enriquecimiento): a '{nombre}' le faltan las columnas: "
                f"{', '.join(faltantes)}"
            )

    # Trabajar sobre copias para no modificar las tablas originales
    ventas = ventas_limpias.copy()
    productos = productos.copy()
    tiendas = tiendas.copy()

    filas_iniciales = len(ventas)

    # 1. VALIDACIÓN: marcar las filas válidas (True = se queda)
    # 1a. Cantidad mayor que 0 (si no es número, se vuelve NaN y queda inválida)
    cantidad_num = pd.to_numeric(ventas["cantidad"], errors="coerce")
    cantidad_ok = cantidad_num > 0

    # 1b. Fecha válida (NaT = fecha imposible que dejó Esteban)
    fecha_ok = pd.to_datetime(ventas["fecha"], errors="coerce").notna()

    # 1c. El producto debe existir en la tabla productos
    producto_ok = ventas["producto_id"].isin(productos["producto_id"])

    # 1d. La tienda debe existir en la tabla tiendas
    tienda_ok = ventas["tienda_id"].isin(tiendas["tienda_id"])

    # Una fila se queda solo si cumple las 4 reglas
    validas = cantidad_ok & fecha_ok & producto_ok & tienda_ok
    ventas = ventas[validas].copy()

    filas_invalidas = filas_iniciales - len(ventas)

    # 2. UNIÓN (JOIN) con productos y tiendas
    # Se evitan claves repetidas para que el join no duplique ventas
    productos = productos.drop_duplicates(subset=["producto_id"], keep="first")
    tiendas = tiendas.drop_duplicates(subset=["tienda_id"], keep="first")

    tabla = ventas.merge(productos, on="producto_id", how="left")
    tabla = tabla.merge(tiendas, on="tienda_id", how="left")

    # 3. DIMENSIONES TEMPORALES
    fecha = pd.to_datetime(tabla["fecha"])
    tabla["fecha"] = fecha
    tabla["anio"] = fecha.dt.year
    tabla["mes"] = fecha.dt.month
    tabla["dia_semana"] = fecha.dt.dayofweek.map(lambda d: DIAS_ES[d])

    # 4. Dejar EXACTAMENTE las columnas pedidas, en el orden pedido
    tabla_final = tabla[COLUMNAS_FINALES].reset_index(drop=True)

    indicadores = {"filas_invalidas_eliminadas": int(filas_invalidas)}

    return tabla_final, indicadores
