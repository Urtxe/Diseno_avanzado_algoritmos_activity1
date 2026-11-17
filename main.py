"""Actividad 1: LCS por recursión, Hirschberg y programación dinámica.

Ejecutar el experimento completo: python main.py
Pruebas de corrección: python main.py --test
No utiliza dependencias externas (Python 3.9+).
"""

import argparse
import csv
import json
import random
import statistics
import subprocess
import sys
import time
import tracemalloc
from pathlib import Path

TAMANOS = [10, 14, 18, 128, 1024]
SEMILLA = 20261117
ALFABETO = "ABCD"
LIMITE_SEGUNDOS = 2.5
DIRECTORIO = Path(__file__).resolve().parent


def lcs_recursiva(a, b):
    """Devuelve una LCS sin reutilizar subproblemas."""
    if not a or not b:
        return ""
    if a[-1] == b[-1]:
        return lcs_recursiva(a[:-1], b[:-1]) + a[-1]
    izquierda = lcs_recursiva(a[:-1], b)
    derecha = lcs_recursiva(a, b[:-1])
    return izquierda if len(izquierda) >= len(derecha) else derecha


def _ultima_fila(a, b):
    """Última fila de la DP LCS, usando memoria lineal en len(b)."""
    anterior = [0] * (len(b) + 1)
    for caracter_a in a:
        actual = [0] * (len(b) + 1)
        for j, caracter_b in enumerate(b, start=1):
            if caracter_a == caracter_b:
                actual[j] = anterior[j - 1] + 1
            else:
                actual[j] = max(anterior[j], actual[j - 1])
        anterior = actual
    return anterior


def _hirschberg(a, b):
    if not a or not b:
        return ""
    if len(a) == 1:
        return a if a in b else ""
    mitad = len(a) // 2
    anterior = _ultima_fila(a[:mitad], b)
    posterior = _ultima_fila(a[mitad:][::-1], b[::-1])
    k = max(range(len(b) + 1), key=lambda j: anterior[j] + posterior[len(b) - j])
    # Liberar filas antes de entrar en las llamadas recursivas.
    del anterior, posterior
    return _hirschberg(a[:mitad], b[:k]) + _hirschberg(a[mitad:], b[k:])


def lcs_hirschberg(a, b):
    """Una LCS con divide y conquista y tablas auxiliares de dos filas."""
    if len(b) > len(a):
        a, b = b, a
    return _hirschberg(a, b)


def lcs_tabular(a, b):
    """Una LCS reconstruida a partir de la tabla completa."""
    filas, columnas = len(a), len(b)
    tabla = [[0] * (columnas + 1) for _ in range(filas + 1)]
    for i in range(1, filas + 1):
        for j in range(1, columnas + 1):
            if a[i - 1] == b[j - 1]:
                tabla[i][j] = tabla[i - 1][j - 1] + 1
            else:
                tabla[i][j] = max(tabla[i - 1][j], tabla[i][j - 1])
    i, j = filas, columnas
    resultado = []
    while i > 0 and j > 0:
        if a[i - 1] == b[j - 1]:
            resultado.append(a[i - 1])
            i -= 1
            j -= 1
        elif tabla[i - 1][j] >= tabla[i][j - 1]:
            i -= 1
        else:
            j -= 1
    return "".join(reversed(resultado))


ALGORITMOS = {"A": lcs_recursiva, "B": lcs_hirschberg, "C": lcs_tabular}


def generar_datos():
    rng = random.Random(SEMILLA)
    return [
        {"id": f"P{i}", "n": n, "a": "".join(rng.choices(ALFABETO, k=n)),
         "b": "".join(rng.choices(ALFABETO, k=n))}
        for i, n in enumerate(TAMANOS, 1)
    ]


def es_subsecuencia(corta, larga):
    it = iter(larga)
    return all(any(c == x for x in it) for c in corta)


def validar(resultado, a, b):
    if not (es_subsecuencia(resultado, a) and es_subsecuencia(resultado, b)):
        raise AssertionError("El resultado no es subsecuencia de ambas cadenas")


def probar():
    casos = [("", "", 0), ("ABC", "", 0), ("", "ABC", 0),
             ("ABC", "ABC", 3), ("ABC", "DEF", 0),
             ("ABCBDAB", "BDCABA", 4), ("XMJYAUZ", "MZJAWXU", 4)]
    rng = random.Random(1234)
    for _ in range(30):
        x = "".join(rng.choices(ALFABETO, k=rng.randint(0, 8)))
        y = "".join(rng.choices(ALFABETO, k=rng.randint(0, 8)))
        esperada = len(lcs_tabular(x, y))
        casos.append((x, y, esperada))
    for a, b, esperada in casos:
        for nombre, funcion in ALGORITMOS.items():
            salida = funcion(a, b)
            validar(salida, a, b)
            if len(salida) != esperada:
                raise AssertionError(f"Fallo {nombre}: {a!r}, {b!r}")
    print(f"OK: {len(casos)} casos x 3 algoritmos = {len(casos)*3} comprobaciones.")


def trabajo(modo, algoritmo, identificador):
    sys.setrecursionlimit(10000)
    pareja = next(p for p in generar_datos() if p["id"] == identificador)
    funcion = ALGORITMOS[algoritmo]
    if modo == "cpu":
        inicio = time.process_time()
        resultado = funcion(pareja["a"], pareja["b"])
        segundos = time.process_time() - inicio
        info = {"cpu_s": segundos}
    elif modo == "mem":
        tracemalloc.start()
        resultado = funcion(pareja["a"], pareja["b"])
        _, pico = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        info = {"mem_pico_mib": pico / (1024 * 1024)}
    else:
        raise ValueError(modo)
    validar(resultado, pareja["a"], pareja["b"])
    info.update({"longitud_lcs": len(resultado), "resultado": resultado})
    print(json.dumps(info))


def ejecutar_worker(modo, algoritmo, identificador):
    comando = [sys.executable, str(Path(__file__).resolve()), "--worker", modo, algoritmo, identificador]
    try:
        proceso = subprocess.run(comando, capture_output=True, text=True,
                                 timeout=(10.0 if modo == "mem" else LIMITE_SEGUNDOS), check=False)
    except subprocess.TimeoutExpired:
        return None, "TIEMPO_AGOTADO"
    if proceso.returncode != 0:
        return None, "ERROR: " + proceso.stderr.strip().splitlines()[-1][:100]
    try:
        return json.loads(proceso.stdout), "OK"
    except json.JSONDecodeError:
        return None, "SALIDA_INVALIDA"


def experimento():
    probar()
    datos = generar_datos()
    (DIRECTORIO / "datos.json").write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")
    registros = []
    for pareja in datos:
        for clave in ALGORITMOS:
            ejecuciones = []
            estado = "OK"
            # Tres repeticiones de CPU; una ejecución independiente para memoria.
            for _ in range(3):
                respuesta, estado = ejecutar_worker("cpu", clave, pareja["id"])
                if estado != "OK":
                    break
                ejecuciones.append(respuesta)
            memoria = None
            if estado == "OK":
                memoria, estado = ejecutar_worker("mem", clave, pareja["id"])
            if estado == "OK":
                longitudes = {int(r["longitud_lcs"]) for r in ejecuciones + [memoria]}
                assert len(longitudes) == 1
                registro = {"caso": pareja["id"], "longitud_cadena": pareja["n"],
                            "version": clave, "cpu_mediana_s": round(statistics.median(r["cpu_s"] for r in ejecuciones), 6),
                            "mem_pico_mib": round(memoria["mem_pico_mib"], 6),
                            "longitud_lcs": longitudes.pop(), "estado": "OK"}
            else:
                registro = {"caso": pareja["id"], "longitud_cadena": pareja["n"],
                            "version": clave, "cpu_mediana_s": "", "mem_pico_mib": "",
                            "longitud_lcs": "", "estado": estado}
            registros.append(registro)
            print(registro, flush=True)
    with (DIRECTORIO / "resultados.csv").open("w", newline="", encoding="utf-8") as archivo:
        writer = csv.DictWriter(archivo, fieldnames=list(registros[0]))
        writer.writeheader()
        writer.writerows(registros)
    print("Resultados guardados en", DIRECTORIO / "resultados.csv")


def main():
    parser = argparse.ArgumentParser(description="Actividad 1: comparación de tres algoritmos LCS")
    parser.add_argument("--test", action="store_true", help="Pruebas de corrección")
    parser.add_argument("--worker", nargs=3, metavar=("METRICA", "VERSION", "CASO"))
    args = parser.parse_args()
    if args.worker:
        trabajo(*args.worker)
    elif args.test:
        probar()
    else:
        experimento()


if __name__ == "__main__":
    main()
