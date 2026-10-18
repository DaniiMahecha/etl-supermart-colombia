"""
main.py
=======
Punto de entrada del pipeline ETL de SuperMart Colombia.

Cómo se ejecuta (desde la carpeta del proyecto):
    python main.py

Qué hace: llama, en orden, a la función de cada integrante del equipo y se
asegura de que cada una reciba y devuelva lo que la siguiente espera.

    Etapa                          Archivo (en src/)    Función                Responsable
    -----------------------------  -------------------  ---------------------  ------------
    1. Extracción                  extract.py           extraer_datos          Juan Arango
    2. Limpieza                    transform_clean.py   limpiar_ventas         Juan Esteban
    3. Enriquecimiento y validación transform_enrich.py enriquecer_y_validar   Luisa
    4. Carga                       load.py              cargar_resultados      Juan Arango
    5. Reportes                    reports.py           generar_reportes       Carlos

=======================================================================
CONTRATO ENTRE MÓDULOS (lo que cada función recibe y devuelve)
=======================================================================
Todas las tablas son DataFrames de pandas. Los CSV se leen y se guardan con
encoding="utf-8-sig" (así Excel muestra bien las tildes).

1) extraer_datos(carpeta_datos) -> dict
   - Recibe la ruta de la carpeta data/.
   - Lee ventas_crudas.csv, productos.csv y tiendas.csv con pandas.
   - Muestra cuántos registros tiene cada archivo.
   - Si falta un archivo o tiene formato incorrecto, NO devuelve tablas
     vacías: lanza el error con un mensaje claro.
   - Devuelve: {"ventas": df, "productos": df, "tiendas": df}

2) limpiar_ventas(ventas) -> (ventas_limpias, indicadores)
   - Convierte la columna fecha a tipo fecha (acepta "2024-03-15" y "2024/03/15").
   - cliente_id vacío -> "CLIENTE_DESCONOCIDO".
   - Elimina order_id duplicados (se conserva la primera aparición).
   - Crea venta_total = cantidad x precio_unitario.
   - Crea categoria_venta: "Baja" (< 20), "Media" (20 a 50), "Alta" (>= 50).
   - indicadores: diccionario con números, por ejemplo
     {"filas_iniciales": 41, "duplicados_eliminados": 1, "clientes_desconocidos": 5}

3) enriquecer_y_validar(ventas_limpias, productos, tiendas) -> (tabla_final, indicadores)
   - Valida y ELIMINA (contándolas en indicadores) las filas con cantidad <= 0,
     fecha inválida, producto_id que no existe en productos o tienda_id que
     no existe en tiendas.
   - Une la información de productos y tiendas.
   - Crea anio, mes y dia_semana (texto en español: Lunes ... Domingo).
   - indicadores: por ejemplo {"filas_invalidas_eliminadas": 2, "productos_inexistentes": 1}
   - tabla_final tiene EXACTAMENTE estas columnas:
     order_id, fecha, producto_id, cantidad, precio_unitario, cliente_id,
     tienda_id, venta_total, categoria_venta, categoria, subcategoria, marca,
     ciudad, region, area_m2, gerente, anio, mes, dia_semana

4) cargar_resultados(tabla_final, carpeta_salida) -> None
   - Guarda en carpeta_salida: ventas_transformadas.csv (dataset completo),
     data_mart.csv (columnas útiles para análisis) y resumen_ejecutivo.csv
     (datos agregados, por ejemplo ventas por ciudad y categoría).

5) generar_reportes(tabla_final, indicadores_calidad, carpeta_salida) -> None
   - Guarda en carpeta_salida/graficos las 4 imágenes (.png): ventas por ciudad,
     ventas por categoría, transacciones por día de la semana y distribución
     de montos. No usar plt.show(): se guarda con savefig y se cierra con plt.close().
   - Guarda carpeta_salida/reporte_ejecutivo.txt con métricas principales,
     ciudad y categoría líder e indicadores de calidad (todos los del diccionario).

Reglas generales: ninguna ruta escrita a mano (usar las que reciben como
parámetro) y ningún código suelto al importar el archivo (todo dentro de funciones).
"""

import logging
import sys
import time
from pathlib import Path
from typing import Any, Callable, Dict, Tuple

# ----------------------------------------------------------------------
# CONFIGURACIÓN
# ----------------------------------------------------------------------
RAIZ_PROYECTO = Path(__file__).resolve().parent
CARPETA_DATOS = RAIZ_PROYECTO / "data"
CARPETA_SALIDA = RAIZ_PROYECTO / "output"
CARPETA_SRC = RAIZ_PROYECTO / "src"

TABLAS_ESPERADAS = ("ventas", "productos", "tiendas")

# Si una etapa falla, el mensaje indica a quién preguntarle.
RESPONSABLES = {
    "Extracción": "Juan Arango",
    "Limpieza": "Juan Esteban",
    "Enriquecimiento y validación": "Luisa",
    "Carga": "Juan Arango",
    "Reportes": "Carlos",
}


# ----------------------------------------------------------------------
# FUNCIONES DE APOYO
# ----------------------------------------------------------------------
def configurar_logging() -> None:
    """Define el formato de los mensajes que se ven en pantalla."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S",
    )


def importar_modulos() -> Dict[str, Callable[..., Any]]:
    """
    Importa la función de cada integrante.

    Si falta un archivo o una función, se explica cuál y se termina el
    programa, en lugar de mostrar un error técnico difícil de entender.
    """
    # Permite importar los archivos de src/ por su nombre (import extract)
    if str(CARPETA_SRC) not in sys.path:
        sys.path.insert(0, str(CARPETA_SRC))

    try:
        from extract import extraer_datos
        from transform_clean import limpiar_ventas
        from transform_enrich import enriquecer_y_validar
        from load import cargar_resultados
        from reports import generar_reportes
    except ImportError as exc:
        logging.error("No se pudo importar una parte del pipeline: %s", exc)
        modulos_del_proyecto = (
            "extract", "transform_clean", "transform_enrich", "load", "reports"
        )
        if isinstance(exc, ModuleNotFoundError) and exc.name not in modulos_del_proyecto:
            # No falta un archivo del proyecto: falta una librería externa
            # (pandas, matplotlib...) en el Python que está ejecutando este programa.
            logging.error("Falta instalar la librería '%s' en este Python.", exc.name)
            logging.error(
                'Instálala desde la carpeta del proyecto con:  "%s" -m pip install -r requirements.txt',
                sys.executable,
            )
        else:
            logging.error(
                "Revisa que existan en src/ los 5 archivos (extract.py, "
                "transform_clean.py, transform_enrich.py, load.py, reports.py) "
                "y que cada uno tenga la función indicada en el contrato."
            )
        raise SystemExit(1)

    return {
        "extraer_datos": extraer_datos,
        "limpiar_ventas": limpiar_ventas,
        "enriquecer_y_validar": enriquecer_y_validar,
        "cargar_resultados": cargar_resultados,
        "generar_reportes": generar_reportes,
    }


def ejecutar_etapa(nombre: str, funcion: Callable[..., Any], *argumentos: Any) -> Any:
    """
    Ejecuta una etapa del pipeline midiendo el tiempo y controlando errores.

    Si la etapa falla, se muestra el detalle del error junto con el nombre
    del responsable, y el programa termina con código de error 1.
    """
    logging.info(">>> Etapa: %s", nombre)
    inicio = time.perf_counter()
    try:
        resultado = funcion(*argumentos)
    except SystemExit as exc:
        # Algunos módulos terminan con sys.exit("mensaje claro"): se muestra ese
        # mensaje junto con el responsable y se termina con código de error 1.
        logging.error(
            "La etapa '%s' se detuvo: %s (responsable: %s)",
            nombre, exc.code, RESPONSABLES[nombre],
        )
        raise SystemExit(1)
    except Exception:
        logging.exception(
            "Falló la etapa '%s' (responsable: %s)", nombre, RESPONSABLES[nombre]
        )
        raise SystemExit(1)
    logging.info("    '%s' terminada en %.2f s", nombre, time.perf_counter() - inicio)
    return resultado


def verificar_tablas(datos: Any) -> None:
    """Comprueba que la extracción devolvió las 3 tablas esperadas."""
    if not isinstance(datos, dict) or not all(t in datos for t in TABLAS_ESPERADAS):
        logging.error(
            "La etapa 'Extracción' debe devolver un diccionario con las claves "
            "%s (responsable: %s).", TABLAS_ESPERADAS, RESPONSABLES["Extracción"]
        )
        raise SystemExit(1)


def desempaquetar(resultado: Any, nombre: str) -> Tuple[Any, Dict[str, Any]]:
    """Comprueba que una etapa devolvió (tabla, indicadores) y los separa."""
    if not (isinstance(resultado, tuple) and len(resultado) == 2):
        logging.error(
            "La etapa '%s' debe devolver (tabla, indicadores), pero devolvió: %s "
            "(responsable: %s).", nombre, type(resultado).__name__, RESPONSABLES[nombre]
        )
        raise SystemExit(1)
    tabla, indicadores = resultado
    if not isinstance(indicadores, dict):
        logging.error(
            "En la etapa '%s' el segundo valor devuelto debe ser un diccionario "
            "de indicadores (responsable: %s).", nombre, RESPONSABLES[nombre]
        )
        raise SystemExit(1)
    return tabla, indicadores


def listar_archivos_generados() -> None:
    """Muestra qué archivos quedaron en output/ al terminar."""
    archivos = sorted(
        p for p in CARPETA_SALIDA.rglob("*") if p.is_file() and p.name != ".gitkeep"
    )
    logging.info("Archivos generados en output/ (%d):", len(archivos))
    for archivo in archivos:
        logging.info("  - %s", archivo.relative_to(RAIZ_PROYECTO))


# ----------------------------------------------------------------------
# PIPELINE
# ----------------------------------------------------------------------
def main() -> None:
    """Ejecuta el pipeline completo: extraer, limpiar, enriquecer, cargar y reportar."""
    configurar_logging()
    inicio = time.perf_counter()
    logging.info("=== Pipeline ETL - SuperMart Colombia ===")

    if not CARPETA_DATOS.is_dir():
        logging.error("No existe la carpeta de datos: %s", CARPETA_DATOS)
        raise SystemExit(1)
    CARPETA_SALIDA.mkdir(exist_ok=True)

    fn = importar_modulos()

    # Fase 1: Extracción (E)
    datos = ejecutar_etapa("Extracción", fn["extraer_datos"], CARPETA_DATOS)
    verificar_tablas(datos)

    # Fase 2: Transformación (T). Los indicadores de calidad se van acumulando.
    resultado = ejecutar_etapa("Limpieza", fn["limpiar_ventas"], datos["ventas"])
    ventas_limpias, calidad_limpieza = desempaquetar(resultado, "Limpieza")

    resultado = ejecutar_etapa(
        "Enriquecimiento y validación",
        fn["enriquecer_y_validar"],
        ventas_limpias, datos["productos"], datos["tiendas"],
    )
    tabla_final, calidad_enriquecimiento = desempaquetar(
        resultado, "Enriquecimiento y validación"
    )

    indicadores_calidad = {**calidad_limpieza, **calidad_enriquecimiento}
    logging.info("Filas en la tabla final: %d", len(tabla_final))

    # Fase 3: Carga (L)
    ejecutar_etapa("Carga", fn["cargar_resultados"], tabla_final, CARPETA_SALIDA)

    # Fase 4: Análisis y reportes
    ejecutar_etapa(
        "Reportes", fn["generar_reportes"], tabla_final, indicadores_calidad, CARPETA_SALIDA
    )

    listar_archivos_generados()
    logging.info("Pipeline completado en %.2f s", time.perf_counter() - inicio)


# Solo se ejecuta cuando se corre este archivo directamente (python main.py)
if __name__ == "__main__":
    main()
