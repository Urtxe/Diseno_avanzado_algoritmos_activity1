# Actividad 1: Diseño, análisis y comparación de algoritmos LCS

Este proyecto implementa las tres versiones solicitadas:

- **A:** recursión directa sin memoización (`lcs_recursiva`).
- **B:** divide y conquista de Hirschberg (`lcs_hirschberg`).
- **C:** programación dinámica tabular (`lcs_tabular`).

## Requisitos y ejecución

Instalar **Python 3.9 o posterior**. No son necesarias librerías de terceros.

Abrir una terminal en esta carpeta y ejecutar **un único comando**:

```bash
python main.py
```

En Windows, si `python` no está disponible en el PATH, puede usarse `py main.py`.

Ese comando ejecuta los tests, genera cinco parejas de cadenas en `datos.json`, mide los algoritmos y escribe `resultados.csv`. Las longitudes son **10, 14, 18, 128 y 1024** caracteres para _cada_ cadena de la pareja. Se utiliza un generador aleatorio con semilla fija `20261117`, y el alfabeto `ABCD`, por lo que las entradas son reproducibles.

Pruebas de corrección independientes:

```bash
python main.py --test
```

## Metodología experimental

- Cada medición se hace en un **proceso independiente** para evitar que el consumo anterior de memoria afecte a la nueva ejecución.
- Tiempo: `time.process_time()`, tres repeticiones, **mediana**, en segundos.
- Memoria: `tracemalloc.get_traced_memory()` tras una ejecución independiente, **máximo de memoria asignada por Python mientras se ejecuta el algoritmo**, en MiB (1 MiB = 1024^2 bytes). **No equivale a la memoria residente total del proceso**.
- Tiempo límite de CPU/espera para cada intento de cálculo: **2,5 segundos de reloj**; para medir memoria, el límite es **10 segundos de reloj** (el seguimiento de asignaciones puede ralentizar la ejecución).
- Si un proceso supera su límite, se registra `TIEMPO_AGOTADO` en lugar de un dato medido. No se extrapolan cifras.
- El script comprueba que la subsecuencia obtenida esté presente, en orden, en ambas cadenas. En las pruebas pequeñas se verifica también la longitud óptima frente a la versión tabular.

**Importante:** la tabla resultante es un ejemplo de medición real en el entorno donde se ejecutó. Los valores numéricos varían según ordenador, versión de Python y carga del sistema.

## Repositorio del proyecto

El código fuente, los conjuntos de datos utilizados en los experimentos y los resultados obtenidos están disponibles en el siguiente repositorio público:
github.com/Urtxe/Diseno_avanzado_algoritmos_activity1El proyecto puede ejecutarse localmente con Python 3.9 o posterior mediante el comando python main.py, sin instalar dependencias externas.
