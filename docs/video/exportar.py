"""Exporta a src/datos.json los pasos reales de los dos algoritmos para el video de Remotion.

Uso (desde la raíz del repo):  python docs/video/exportar.py
"""
import json
import sys
from pathlib import Path

import networkx as nx

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "animacion"))
import generar as g  # noqa: E402  (ejecuta el código del repositorio y registra cada paso)


def emparejamiento(paso):
    G = nx.Graph()
    tops = [f"x{i}" for i in range(9)]
    G.add_nodes_from(tops)
    for i, cs in enumerate(paso["antes"]):
        for k in cs:
            G.add_edge(f"x{i}", k)
    m = nx.bipartite.maximum_matching(G, top_nodes=tops)
    return [m.get(f"x{i}") for i in range(9)]


def main():
    grid, inicial, pasos, sol_m, llamadas = g.correr_emparejamiento()
    orden, sol_c, aristas = g.correr_coloracion()
    lista = lambda t: [[sorted(c) for c in fila] for fila in t]  # noqa: E731
    utiles = [p for p in pasos if p["antes"] != p["despues"]]
    datos = {
        "llamadas": llamadas,
        "pistas": grid.tolist(),
        "inicial": lista(inicial),
        "pasos": [{"celdas": [list(map(int, c)) for c in p["celdas"]], "antes": [sorted(a) for a in p["antes"]],
                   "despues": [sorted(b) for b in p["despues"]], "empar": emparejamiento(p), "tablero": lista(p["tablero"])}
                  for p in utiles],
        "solucionM": [list(map(int, f)) for f in sol_m],
        "pistasColor": [[v, x, y] for v, x, y in g.PISTAS_COLOR],
        "orden": [list(o) for o in orden],
        "solucionC": sol_c,
        "aristas": aristas,
    }
    (AQUI / "src" / "datos.json").write_text(json.dumps(datos, separators=(",", ":"), default=int), encoding="utf-8")
    print(f"{len(utiles)} pasos útiles de {llamadas} llamadas · {len(orden)} nodos coloreados · {len(aristas)} aristas")


if __name__ == "__main__":
    main()
