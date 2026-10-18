"""Generación de gráficos y reporte ejecutivo para el proyecto ETL de SuperMart."""

import os
import matplotlib.pyplot as plt
import pandas as pd


def generar_reportes(tabla_final, indicadores_calidad, carpeta_salida):
    """Genera las 4 gráficas y el reporte ejecutivo del pipeline.

    Parámetros:
        tabla_final: DataFrame final (salida de enriquecer_y_validar).
        indicadores_calidad: diccionario {nombre: valor} con los indicadores de
            calidad de los datos (se imprimen todos en el reporte).
        carpeta_salida: carpeta donde se guardan los resultados.

    Guarda:
        carpeta_salida/graficos/*.png   las 4 visualizaciones
        carpeta_salida/reporte_ejecutivo.txt
    No devuelve nada.
    """
    # 1. Validar la entrada: debe ser una tabla con las columnas necesarias
    if not isinstance(tabla_final, pd.DataFrame):
        raise TypeError("tabla_final debe ser una tabla de pandas (DataFrame).")

    columnas_requeridas = ["venta_total", "ciudad", "categoria", "dia_semana"]
    faltantes = [columna for columna in columnas_requeridas if columna not in tabla_final.columns]
    if faltantes:
        raise ValueError(
            "Faltan columnas necesarias en tabla_final: " + ", ".join(faltantes)
        )

    # 2. Crear las carpetas de salida si no existen
    os.makedirs(carpeta_salida, exist_ok=True)
    carpeta_graficos = os.path.join(carpeta_salida, "graficos")
    os.makedirs(carpeta_graficos, exist_ok=True)

    # 3. Preparar los datos: se trabaja sobre una copia y los montos como números
    datos = tabla_final.copy()
    datos["venta_total"] = pd.to_numeric(datos["venta_total"], errors="coerce")
    ventas_validas = datos.dropna(subset=["venta_total"])

    # Cambia los valores vacíos por "Sin dato" para que no se pierdan en los gráficos
    def etiqueta_no_vacia(serie):
        return serie.astype("string").fillna("Sin dato").replace("", "Sin dato")

    # Ventas totales por ciudad y por categoría, de mayor a menor
    ventas_ciudad = (
        ventas_validas.assign(ciudad=etiqueta_no_vacia(ventas_validas["ciudad"]))
        .groupby("ciudad")["venta_total"].sum().sort_values(ascending=False)
    )
    ventas_categoria = (
        ventas_validas.assign(categoria=etiqueta_no_vacia(ventas_validas["categoria"]))
        .groupby("categoria")["venta_total"].sum().sort_values(ascending=False)
    )

    # Función auxiliar: crea la figura, la guarda como PNG y SIEMPRE la cierra
    # (no se usa plt.show() para que el pipeline no se detenga esperando)
    def guardar_grafico(nombre_archivo, dibujar):
        figura, eje = plt.subplots(figsize=(10, 6))
        try:
            dibujar(eje)
            figura.tight_layout()
            figura.savefig(
                os.path.join(carpeta_graficos, nombre_archivo),
                dpi=300,
                bbox_inches="tight",
            )
        finally:
            plt.close(figura)

    def grafico_barras(eje, serie, titulo, etiqueta_x, etiqueta_y, rotacion=35):
        if serie.empty:
            eje.text(0.5, 0.5, "No hay datos para representar", ha="center", va="center")
            eje.set_axis_off()
        else:
            serie.plot(kind="bar", ax=eje, color="#2878B5")
            eje.tick_params(axis="x", labelrotation=rotacion)
            eje.set_xlabel(etiqueta_x)
            eje.set_ylabel(etiqueta_y)
        eje.set_title(titulo)

    # Gráfico 1: barras, ventas totales por ciudad
    guardar_grafico(
        "ventas_por_ciudad.png",
        lambda eje: grafico_barras(
            eje, ventas_ciudad, "Ventas totales por ciudad", "Ciudad", "Ventas totales"
        ),
    )

    # Gráfico 2: pastel, distribución de ventas por categoría
    def dibujar_pastel(eje):
        if ventas_categoria.empty or ventas_categoria.sum() == 0:
            eje.text(0.5, 0.5, "No hay datos para representar", ha="center", va="center")
            eje.set_axis_off()
            eje.set_title("Distribución de ventas por categoría")
            return
        eje.pie(
            ventas_categoria,
            labels=ventas_categoria.index,
            autopct="%1.1f%%",
            startangle=90,
        )
        eje.set_title("Distribución de ventas por categoría")
        eje.axis("equal")

    guardar_grafico("ventas_por_categoria.png", dibujar_pastel)

    # Gráfico 3: barras, transacciones por día de la semana.
    # IMPORTANTE: estos nombres deben coincidir EXACTAMENTE (con tildes) con los
    # de la columna dia_semana; si no, esos días aparecen en cero en el gráfico.
    orden_dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    transacciones_dia = (
        etiqueta_no_vacia(datos["dia_semana"])
        .value_counts()
        .reindex(orden_dias, fill_value=0)
    )
    guardar_grafico(
        "transacciones_por_dia_semana.png",
        lambda eje: grafico_barras(
            eje,
            transacciones_dia,
            "Transacciones por día de la semana",
            "Día de la semana",
            "Número de transacciones",
            rotacion=0,
        ),
    )

    # Gráfico 4: histograma, distribución de los montos de venta
    def dibujar_histograma(eje):
        if ventas_validas.empty:
            eje.text(0.5, 0.5, "No hay montos válidos para representar", ha="center", va="center")
        else:
            eje.hist(ventas_validas["venta_total"], bins=20, color="#55A868", edgecolor="white")
        eje.set_title("Distribución de montos de venta")
        eje.set_xlabel("Monto de venta")
        eje.set_ylabel("Frecuencia")

    guardar_grafico("distribucion_montos.png", dibujar_histograma)

    # 4. Reporte ejecutivo en texto: métricas, líderes e indicadores de calidad
    ventas_totales = ventas_validas["venta_total"].sum()
    promedio_venta = ventas_validas["venta_total"].mean()
    ciudad_lider = ventas_ciudad.index[0] if not ventas_ciudad.empty else "Sin datos"
    categoria_lider = ventas_categoria.index[0] if not ventas_categoria.empty else "Sin datos"

    lineas_reporte = [
        "REPORTE EJECUTIVO - SUPERMART COLOMBIA",
        "=" * 44,
        "",
        "MÉTRICAS PRINCIPALES",
        f"Transacciones: {len(datos)}",
        f"Transacciones con monto válido: {len(ventas_validas)}",
        f"Ventas totales: {ventas_totales:,.2f}",
        f"Promedio por venta: {promedio_venta:,.2f}" if pd.notna(promedio_venta) else "Promedio por venta: Sin datos",
        "",
        "TOP PERFORMERS",
        f"Ciudad líder: {ciudad_lider}" + (f" ({ventas_ciudad.iloc[0]:,.2f})" if not ventas_ciudad.empty else ""),
        f"Categoría líder: {categoria_lider}" + (f" ({ventas_categoria.iloc[0]:,.2f})" if not ventas_categoria.empty else ""),
        "",
        "INDICADORES DE CALIDAD DE LOS DATOS",
    ]

    if isinstance(indicadores_calidad, dict) and indicadores_calidad:
        lineas_reporte.extend(
            f"{str(nombre).replace('_', ' ').capitalize()}: {valor}"
            for nombre, valor in indicadores_calidad.items()
        )
    else:
        lineas_reporte.append("No se recibieron indicadores de calidad.")

    # 5. Guardar el reporte (utf-8-sig para que las tildes se vean bien)
    ruta_reporte = os.path.join(carpeta_salida, "reporte_ejecutivo.txt")
    with open(ruta_reporte, "w", encoding="utf-8-sig") as archivo:
        archivo.write("\n".join(lineas_reporte) + "\n")
