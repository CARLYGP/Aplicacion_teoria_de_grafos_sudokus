"""Genera el video y los GIF del README a partir de la ejecución REAL de los dos solucionadores.

No modifica los algoritmos: registra cada paso desde fuera.
  * Emparejamiento (main (1).py): una subclase de Model guarda los candidatos de cada fila, columna o
    bloque antes y después de cada llamada a check_constraint (emparejamiento máximo + teorema de Berge).
  * Coloración (Coloracion/): se envuelve Node.set_color para guardar en qué orden colorea DSatur
    cada nodo y con qué saturación.

Uso (desde la raíz del repo):  python docs/animacion/generar.py
Requiere: numpy, networkx, pillow, imageio-ffmpeg
"""
import importlib.util
import math
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg
import networkx as nx
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

RAIZ = Path(__file__).resolve().parents[2]
DOCS = RAIZ / "docs"
sys.path.insert(0, str(RAIZ / "Coloracion"))
import Functions as F  # noqa: E402
import Graph as gp  # noqa: E402
import Sudoku as sk  # noqa: E402

spec = importlib.util.spec_from_file_location("emparejamiento", RAIZ / "main (1).py")
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)

# --- Estilo ---------------------------------------------------------------------------------------
W, H, S, FPS = 1280, 720, 2, 30
FONDO = (11, 17, 30)
PANEL = (18, 26, 44)
LINEA = (40, 54, 82)
TEXTO = (232, 238, 248)
TENUE = (128, 146, 176)
ROJO = (244, 63, 94)
COLORES = [None, (239, 68, 68), (249, 115, 22), (234, 179, 8), (34, 197, 94), (20, 184, 166),
           (14, 165, 233), (99, 102, 241), (168, 85, 247), (236, 72, 153)]
FT = "C:/Windows/Fonts/"


def fuente(nombre, tam):
    return ImageFont.truetype(FT + nombre, int(tam * S))


F_TIT = fuente("segoeuib.ttf", 30)
F_SUB = fuente("segoeui.ttf", 18)
F_DIG = fuente("segoeuib.ttf", 30)
F_CAN = fuente("segoeui.ttf", 12)
F_NOD = fuente("segoeuib.ttf", 13)
F_PEQ = fuente("segoeui.ttf", 14)
F_GRANDE = fuente("segoeuib.ttf", 52)


def suave(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def mezcla(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def lienzo():
    im = Image.new("RGB", (W * S, H * S), FONDO)
    return im, ImageDraw.Draw(im, "RGBA")


def P(x, y):
    return (x * S, y * S)


def circulo(d, x, y, r, relleno, borde=None, ancho=0):
    d.ellipse((S * (x - r), S * (y - r), S * (x + r), S * (y + r)), fill=relleno, outline=borde, width=int(ancho * S))


def texto(d, xy, t, f, c, anchor="la"):
    d.text(P(*xy), t, font=f, fill=c, anchor=anchor)


def encabezado(d, titulo, sub):
    texto(d, (60, 34), titulo, F_TIT, TEXTO)
    texto(d, (60, 76), sub, F_SUB, TENUE)


# --- Salida ---------------------------------------------------------------------------------------
class Video:
    def __init__(self, ruta):
        self.ruta = ruta
        self.n = 0
        self.marcas = {}
        self.p = subprocess.Popen(
            [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
             "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "20",
             "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(ruta)], stdin=subprocess.PIPE)

    def cuadro(self, im, veces=1, guardar=None):
        peq = im.resize((W, H), Image.LANCZOS)
        if guardar:
            peq.save(DOCS / guardar)
        datos = peq.tobytes()
        for _ in range(veces):
            self.p.stdin.write(datos)
            self.n += 1

    def marca(self, nombre):
        self.marcas[nombre] = self.n / FPS

    def cerrar(self):
        self.p.stdin.close()
        self.p.wait()


# --- Datos: ejecución real de los algoritmos ---------------------------------------------------------
def leer_sudoku(ruta):
    return np.array([list(map(int, l.split())) for l in Path(ruta).read_text().splitlines() if l.strip()])


def es_valido(g):
    g = np.array(g)
    unidades = [g[r, :] for r in range(9)] + [g[:, c] for c in range(9)] + \
               [g[r:r + 3, c:c + 3].ravel() for r in (0, 3, 6) for c in (0, 3, 6)]
    return all(sorted(u) == list(range(1, 10)) for u in unidades)


def cands(v):
    return set(v["values"]) if "values" in v else {v["value"]}


class ModeloVisual(M.Model):
    """Model original + registro de cada llamada a check_constraint."""

    def __init__(self):
        super().__init__()
        self.pasos = []

    def foto(self):
        return [[cands(self.search_space[r, c]) for c in range(9)] for r in range(9)]

    def check_constraint(self, opts, operator):
        idx = opts["idx"]
        celdas = [tuple(x) for x in np.argwhere(idx)]       # mismo orden fila-mayor que search_space[idx]
        antes = [cands(self.search_space[c]) for c in celdas]
        super().check_constraint(opts, operator)
        despues = [cands(self.search_space[c]) for c in celdas]
        self.pasos.append({"celdas": celdas, "antes": antes, "despues": despues, "tablero": self.foto()})


def correr_emparejamiento():
    grid = leer_sudoku(RAIZ / "sudoku_3.txt")
    m = ModeloVisual()
    m.build_search_space(grid, [1, 2, 3, 4, 5, 6, 7, 8, 9], 0)
    for r in range(9):
        idx = np.zeros((9, 9), bool); idx[r, :] = True
        m.subscribe({"idx": idx}, m.check_constraint, {"idx": idx}, "alldifferent")
    for c in range(9):
        idx = np.zeros((9, 9), bool); idx[:, c] = True
        m.subscribe({"idx": idx}, m.check_constraint, {"idx": idx}, "alldifferent")
    for r in range(3):
        for c in range(3):
            idx = np.zeros((9, 9), bool); idx[r * 3:r * 3 + 3, c * 3:c * 3 + 3] = True
            m.subscribe({"idx": idx}, m.check_constraint, {"idx": idx}, "alldifferent")
    inicial = m.foto()
    m.solve()
    sol = m.get_solution()
    assert es_valido(sol), "el emparejamiento no dejó una solución válida"
    return grid, inicial, m.pasos, sol, m.nof_calls


PISTAS_COLOR = [(5, 0, 0), (3, 0, 1), (7, 0, 4), (6, 1, 0), (1, 1, 3), (9, 1, 4), (5, 1, 5), (9, 2, 1), (8, 2, 2),
                (6, 2, 7), (8, 3, 0), (6, 3, 4), (3, 3, 8), (4, 4, 0), (8, 4, 3), (3, 4, 5), (1, 4, 8), (7, 5, 0),
                (2, 5, 4), (6, 5, 8), (6, 6, 1), (2, 6, 6), (8, 6, 7), (4, 7, 3), (1, 7, 4), (9, 7, 5), (5, 7, 8),
                (8, 8, 4), (7, 8, 7), (9, 8, 8)]   # el ejemplo de Coloracion/Functions.py


def correr_coloracion():
    s = sk.Sudoku(3)
    for v, x, y in PISTAS_COLOR:
        s.set_in(v, x, y)
    g = F.S2G(s)
    orden, original = [], gp.Node.set_color

    def registrar(nodo, color):
        orden.append((int(nodo.name[0]), int(nodo.name[1]), F.colors.index(color), F.chrom(g, nodo)))
        original(nodo, color)

    gp.Node.set_color = registrar
    try:
        F.coloring(g)
    finally:
        gp.Node.set_color = original
    sol = F.G2S(g)
    tablero = [[sol.squares[r * 9 + c].value for c in range(9)] for r in range(9)]
    assert es_valido(tablero), "la coloración no dejó una solución válida"
    aristas = [(int(a.name[0]) * 9 + int(a.name[1]), int(b.name[0]) * 9 + int(b.name[1])) for a, b in g.edges]
    return orden, tablero, aristas


# --- Tablero --------------------------------------------------------------------------------------
GX, GY, CEL = 66, 138, 58


def centro_celda(r, c):
    return GX + c * CEL + CEL / 2, GY + r * CEL + CEL / 2


def dibujar_tablero(d, valores, pistas, candidatos=None, resaltar=None, tinte=None, aparicion=None, pistas_color=False):
    """valores[r][c] = dígito o 0; candidatos[r][c] = set; resaltar = celdas de la unidad activa."""
    d.rounded_rectangle((S * (GX - 10), S * (GY - 10), S * (GX + 9 * CEL + 10), S * (GY + 9 * CEL + 10)), 14 * S, fill=PANEL)
    if resaltar:
        for r, c in resaltar:
            d.rectangle((S * (GX + c * CEL), S * (GY + r * CEL), S * (GX + c * CEL + CEL), S * (GY + r * CEL + CEL)),
                        fill=(255, 255, 255, 18))
    for r in range(9):
        for c in range(9):
            v = valores[r][c]
            x, y = centro_celda(r, c)
            if v:
                a = 1.0 if not aparicion or (r, c) not in aparicion else aparicion[(r, c)]
                if (r, c) in pistas:
                    texto(d, (x, y), str(v), F_DIG, mezcla(PANEL, COLORES[v] if pistas_color else TEXTO, a), "mm")
                else:
                    col = COLORES[v]
                    d.rounded_rectangle((S * (x - 25), S * (y - 25), S * (x + 25), S * (y + 25)), 9 * S,
                                        fill=col + (int(46 * a),))
                    texto(d, (x, y), str(v), F_DIG, mezcla(PANEL, col, a), "mm")
            elif candidatos:
                for k in candidatos[r][c]:
                    cx = x - 17 + ((k - 1) % 3) * 17
                    cy = y - 17 + ((k - 1) // 3) * 17
                    col = TENUE
                    if tinte and (r, c, k) in tinte:
                        col = mezcla(ROJO, PANEL, tinte[(r, c, k)])
                    texto(d, (cx, cy), str(k), F_CAN, col, "mm")
    for i in range(10):
        ancho = 3 if i % 3 == 0 else 1
        col = (92, 110, 144) if i % 3 == 0 else LINEA
        d.line((S * (GX + i * CEL), S * GY, S * (GX + i * CEL), S * (GY + 9 * CEL)), fill=col, width=ancho * S)
        d.line((S * GX, S * (GY + i * CEL), S * (GX + 9 * CEL), S * (GY + i * CEL)), fill=col, width=ancho * S)


# --- Escenas ---------------------------------------------------------------------------------------
def portada(v, seg=3.5):
    n = int(FPS * seg)
    for k in range(n):
        im, d = lienzo()
        a = suave(k / (FPS * 0.8))
        # decoración: anillo de 9 colores
        for i in range(1, 10):
            ang = -math.pi / 2 + (i - 1) * 2 * math.pi / 9 + k * 0.004
            x, y = 640 + 470 * math.cos(ang), 345 + 235 * math.sin(ang)
            circulo(d, x, y, 10 * a, COLORES[i] + (int(200 * a),))
        texto(d, (640, 300), "Resolviendo Sudokus", F_GRANDE, mezcla(FONDO, TEXTO, a), "mm")
        texto(d, (640, 362), "con teoría de grafos", F_GRANDE, mezcla(FONDO, TEXTO, a), "mm")
        texto(d, (640, 430), "Emparejamiento máximo (teorema de Berge)  ·  Coloración de grafos (DSatur)", F_SUB,
              mezcla(FONDO, TENUE, a), "mm")
        texto(d, (640, 640), "Gabriel Fandiño · Carlos Galán · Rosa Galicia  —  Universidad del Rosario", F_PEQ,
              mezcla(FONDO, TENUE, a), "mm")
        v.cuadro(im)


def nombre_unidad(celdas):
    rs = {r for r, _ in celdas}; cs = {c for _, c in celdas}
    if len(rs) == 1:
        return f"Fila {next(iter(rs)) + 1}"
    if len(cs) == 1:
        return f"Columna {next(iter(cs)) + 1}"
    return f"Bloque {min(rs) // 3 * 3 + min(cs) // 3 + 1}"


BX0, BX1, BYC, BYV = 700, 1210, 250, 560


def pos_bip(i, fila):
    x = BX0 + i * (BX1 - BX0) / 8
    return x, (BYC if fila == "c" else BYV)


def dibujar_bipartito(d, paso, fase, tiempo):
    """fase: 0 aristas apareciendo, 1 emparejamiento, 2 eliminación, 3 resultado."""
    celdas, antes, despues = paso["celdas"], paso["antes"], paso["despues"]
    d.rounded_rectangle(P(670, 138) + P(1240, 660), 14 * S, fill=PANEL)
    texto(d, (690, 158), nombre_unidad(celdas) + ": casillas ↔ valores", F_SUB, TEXTO)
    texto(d, (690, 186), "grafo bipartito · restricción «todos distintos»", F_PEQ, TENUE)
    G = nx.Graph()
    tops = [f"x{i}" for i in range(9)]
    G.add_nodes_from(tops)
    for i, cs in enumerate(antes):
        for k in cs:
            G.add_edge(f"x{i}", k)
    empar = nx.bipartite.maximum_matching(G, top_nodes=tops)
    for i, cs in enumerate(antes):
        x0, y0 = pos_bip(i, "c")
        for k in sorted(cs):
            x1, y1 = pos_bip(k - 1, "v")
            eliminada = k not in despues[i]
            es_m = empar.get(f"x{i}") == k
            if fase == 0:
                a = suave(tiempo * 1.6 - i * 0.07)
                col, w = (110, 128, 160, int(150 * a)), 1.2
            elif fase == 1:
                col, w = ((255, 255, 255, int(70 + 185 * suave(tiempo))), 3.2) if es_m else ((110, 128, 160, 120), 1.2)
            elif fase == 2:
                if eliminada:
                    a = suave(tiempo)
                    col, w = ROJO + (int(230 * (1 - a) + 25),), 2.2
                else:
                    col, w = ((255, 255, 255, 255), 3.2) if es_m else ((110, 128, 160, 120), 1.2)
            else:
                if eliminada:
                    continue
                col, w = (COLORES[k] + (230,), 3.2) if len(despues[i]) == 1 else ((110, 128, 160, 140), 1.2)
            d.line(P(x0, y0 + 16) + P(x1, y1 - 16), fill=col, width=max(1, int(w * S)))
    for i, (r, c) in enumerate(celdas):
        x, y = pos_bip(i, "c")
        fijo = len(despues[i]) == 1 and fase == 3
        relleno = COLORES[next(iter(despues[i]))] if fijo else (44, 58, 88)
        circulo(d, x, y, 16, relleno, (150, 168, 200), 1)
        etiqueta = str(next(iter(antes[i]))) if len(antes[i]) == 1 else f"{r + 1},{c + 1}"
        texto(d, (x, y), etiqueta, F_NOD, TEXTO, "mm")
    for k in range(1, 10):
        x, y = pos_bip(k - 1, "v")
        circulo(d, x, y, 16, COLORES[k])
        texto(d, (x, y), str(k), F_NOD, (255, 255, 255), "mm")
    texto(d, (690, 610), {0: "Candidatos de cada casilla", 1: "Emparejamiento máximo (Hopcroft-Karp)",
                          2: "Berge: fuera las aristas que no están en ningún emparejamiento máximo",
                          3: "Valores que sobreviven"}[fase], F_PEQ, TENUE)


def valores_de(tablero):
    return [[next(iter(c)) if len(c) == 1 else 0 for c in fila] for fila in tablero]


def escena_emparejamiento(v, grid, inicial, pasos, n_llamadas):
    pistas = {(r, c) for r in range(9) for c in range(9) if grid[r, c]}
    utiles = [p for p in pasos if p["antes"] != p["despues"]]
    v.marca("emparejamiento_ini")
    # 1) tablero con candidatos
    for k in range(int(FPS * 2.2)):
        im, d = lienzo()
        encabezado(d, "1. Emparejamiento máximo y teorema de Berge",
                   f"{len(pistas)} pistas. Cada casilla vacía empieza con sus candidatos posibles.")
        dibujar_tablero(d, valores_de(inicial), pistas, candidatos=inicial)
        a = suave(k / FPS)
        d.rounded_rectangle(P(670, 138) + P(1240, 660), 14 * S, fill=PANEL + (int(255 * a),))
        texto(d, (955, 380), "Cada fila, columna y bloque", F_SUB, mezcla(PANEL, TEXTO, a), "mm")
        texto(d, (955, 410), "es un grafo bipartito casillas ↔ valores", F_SUB, mezcla(PANEL, TEXTO, a), "mm")
        v.cuadro(im)
    tablero = inicial
    # 2) los primeros pasos, en detalle (4 fases cada uno)
    for j, paso in enumerate(utiles[:3]):
        quitados = {(r, c, k) for (r, c), a, b in zip(paso["celdas"], paso["antes"], paso["despues"]) for k in a - b}
        for fase, seg in ((0, 1.3), (1, 1.2), (2, 1.6), (3, 1.1)):
            n = int(FPS * seg)
            for k in range(n):
                t = k / max(1, n - 1)
                im, d = lienzo()
                encabezado(d, "1. Emparejamiento máximo y teorema de Berge",
                           f"Paso {j + 1} de {len(utiles)} que cambian algo ({n_llamadas} llamadas en total)")
                tinte = {q: suave(t) for q in quitados} if fase == 2 else None
                base = paso["tablero"] if fase == 3 else tablero
                dibujar_tablero(d, valores_de(base), pistas, candidatos=base if fase != 2 else tablero,
                                resaltar=paso["celdas"], tinte=tinte)
                dibujar_bipartito(d, paso, fase, t)
                v.cuadro(im, guardar="bipartito.png" if (j == 0 and fase == 2 and k == n // 2) else None)
        tablero = paso["tablero"]
    # 3) el resto, acelerado
    resto = utiles[3:]
    for j, paso in enumerate(resto):
        quitados = {(r, c, k) for (r, c), a, b in zip(paso["celdas"], paso["antes"], paso["despues"]) for k in a - b}
        n = 6 if j < 12 else 4
        for k in range(n):
            t = k / (n - 1)
            im, d = lienzo()
            encabezado(d, "1. Emparejamiento máximo y teorema de Berge",
                       f"Paso {j + 4} de {len(utiles)} · propagando hasta que nada cambie")
            dibujar_tablero(d, valores_de(tablero if k < n - 1 else paso["tablero"]), pistas,
                            candidatos=tablero if k < n - 1 else paso["tablero"], resaltar=paso["celdas"],
                            tinte={q: suave(t) for q in quitados})
            dibujar_bipartito(d, paso, 3 if k == n - 1 else 2, t)
            v.cuadro(im)
        tablero = paso["tablero"]
    # 4) resuelto
    for k in range(int(FPS * 2.5)):
        im, d = lienzo()
        encabezado(d, "1. Emparejamiento máximo y teorema de Berge",
                   f"Resuelto solo con propagación: {n_llamadas} llamadas, sin adivinar ni retroceder.")
        dibujar_tablero(d, valores_de(tablero), pistas)
        d.rounded_rectangle(P(670, 138) + P(1240, 660), 14 * S, fill=PANEL)
        texto(d, (955, 330), "81 / 81", F_GRANDE, (34, 197, 94), "mm")
        texto(d, (955, 390), "casillas válidas", F_SUB, TEXTO, "mm")
        texto(d, (955, 430), "filas, columnas y bloques con 1-9 exactos", F_PEQ, TENUE, "mm")
        v.cuadro(im, guardar="emparejamiento_resuelto.png" if k == 30 else None)
    v.marca("emparejamiento_fin")


RCX, RCY, RR = 955, 430, 204


def pos_anillo(i):
    ang = -math.pi / 2 + i * 2 * math.pi / 81
    return RCX + RR * math.cos(ang), RCY + RR * math.sin(ang)


def capa_aristas(aristas, alfa):
    capa = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    for a, b in aristas:
        d.line(P(*pos_anillo(a)) + P(*pos_anillo(b)), fill=(120, 140, 180, alfa), width=S)
    return capa


def vecinos(i, aristas_idx):
    return aristas_idx[i]


def escena_coloracion(v, orden, final, aristas):
    pistas = {(x, y): val for val, x, y in PISTAS_COLOR}
    ady = {i: set() for i in range(81)}
    for a, b in aristas:
        ady[a].add(b); ady[b].add(a)
    capa_tenue = capa_aristas(aristas, 26)
    v.marca("coloracion_ini")
    color_de = {r * 9 + c: val for (r, c), val in pistas.items()}

    def nodos(d, actual=None, pop=1.0):
        for i in range(81):
            x, y = pos_anillo(i)
            val = color_de.get(i)
            if val:
                rad = 7 if i != actual else 7 + 6 * (1 - pop)
                circulo(d, x, y, rad, COLORES[val])
            else:
                circulo(d, x, y, 5, (44, 58, 88), (110, 128, 160), 1)

    def valores():
        t = [[0] * 9 for _ in range(9)]
        for i, val in color_de.items():
            t[i // 9][i % 9] = val
        return t

    # 1) construir el grafo: una casilla y sus 20 vecinas
    foco = 4 * 9 + 4
    vec = sorted(ady[foco])
    n = int(FPS * 3.2)
    for k in range(n):
        t = k / (n - 1)
        im, d = lienzo()
        encabezado(d, "2. Coloración de grafos", "Cada casilla es un nodo; se une a sus 20 vecinas de fila, columna y bloque.")
        dibujar_tablero(d, valores(), set(pistas), pistas_color=True, resaltar=[(j // 9, j % 9) for j in vec[:int(len(vec) * suave(t * 1.3))]])
        d.rounded_rectangle(P(670, 138) + P(1240, 660), 14 * S, fill=PANEL)
        x0, y0 = pos_anillo(foco)
        for j in vec[:int(len(vec) * suave(t * 1.3))]:
            d.line(P(x0, y0) + P(*pos_anillo(j)), fill=(255, 255, 255, 170), width=int(1.6 * S))
        nodos(d)
        circulo(d, x0, y0, 9, (255, 255, 255))
        texto(d, (690, 158), "Casilla (5,5) y sus vecinas", F_SUB, TEXTO)
        v.cuadro(im)
    # 2) todas las aristas
    n = int(FPS * 2.4)
    for k in range(n):
        a = suave(k / (n - 1))
        im, d = lienzo()
        encabezado(d, "2. Coloración de grafos", f"81 nodos y {len(aristas)} aristas. Colorear = asignar números sin choques.")
        dibujar_tablero(d, valores(), set(pistas), pistas_color=True)
        d.rounded_rectangle(P(670, 138) + P(1240, 660), 14 * S, fill=PANEL)
        im.paste(capa_tenue, (0, 0), capa_tenue.point(lambda p: int(p * a)) if a < 1 else capa_tenue)
        d = ImageDraw.Draw(im, "RGBA")
        nodos(d)
        texto(d, (690, 158), "Grafo del Sudoku", F_SUB, TEXTO)
        texto(d, (690, 186), "las 30 pistas ya traen color", F_PEQ, TENUE)
        v.cuadro(im, guardar="grafo_sudoku.png" if k == n - 1 else None)
    # 3) DSatur
    for paso, (r, c, val, sat) in enumerate(orden):
        i = r * 9 + c
        n = 9 if paso < 8 else 6
        for k in range(n):
            t = k / (n - 1)
            if k == n // 2:
                color_de[i] = val
            im, d = lienzo()
            encabezado(d, "2. Coloración de grafos · DSatur modificado",
                       f"Paso {paso + 1}/{len(orden)}: elige la casilla con más colores distintos a su alrededor.")
            ap = {(r, c): suave(t * 2 - 1)} if i in color_de else {}
            dibujar_tablero(d, valores(), set(pistas), pistas_color=True, resaltar=[(r, c)], aparicion=ap)
            d.rounded_rectangle(P(670, 138) + P(1240, 660), 14 * S, fill=PANEL)
            im.paste(capa_tenue, (0, 0), capa_tenue)
            d = ImageDraw.Draw(im, "RGBA")
            x0, y0 = pos_anillo(i)
            brillo = COLORES[val] if i in color_de else (255, 255, 255)
            for j in ady[i]:
                d.line(P(x0, y0) + P(*pos_anillo(j)), fill=brillo + (int(170 * (1 - 0.5 * t)),), width=int(1.4 * S))
            nodos(d, actual=i, pop=suave(t * 2 - 1))
            texto(d, (690, 158), f"Casilla ({r + 1},{c + 1})", F_SUB, TEXTO)
            texto(d, (690, 186), f"saturación {sat}: {sat} colores distintos entre sus vecinas", F_PEQ, TENUE)
            if i in color_de:
                circulo(d, 1214, 166, 14, COLORES[val])
                texto(d, (1214, 166), str(val), F_NOD, (255, 255, 255), "mm")
            v.cuadro(im)
    # 4) final
    capa_color = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    dc = ImageDraw.Draw(capa_color)
    for a, b in aristas:
        dc.line(P(*pos_anillo(a)) + P(*pos_anillo(b)), fill=COLORES[color_de[a]] + (40,), width=S)
    for k in range(int(FPS * 3)):
        im, d = lienzo()
        encabezado(d, "2. Coloración de grafos · DSatur modificado",
                   f"{len(orden)} nodos coloreados; ninguna arista une dos nodos del mismo color.")
        dibujar_tablero(d, final, set(pistas), pistas_color=True)
        d.rounded_rectangle(P(670, 138) + P(1240, 660), 14 * S, fill=PANEL)
        im.paste(capa_color, (0, 0), capa_color)
        d = ImageDraw.Draw(im, "RGBA")
        nodos(d)
        texto(d, (690, 158), "Coloración propia con 9 colores", F_SUB, TEXTO)
        v.cuadro(im, guardar="grafo_coloreado.png" if k == 45 else None)
    v.marca("coloracion_fin")


def cierre(v, n_llamadas, n_color, seg=4):
    for k in range(int(FPS * seg)):
        im, d = lienzo()
        a = suave(k / (FPS * 0.6))
        texto(d, (640, 200), "Dos caminos, la misma solución válida", F_TIT, mezcla(FONDO, TEXTO, a), "mm")
        for x, tit, l1, l2, col in ((400, "Emparejamiento", f"{n_llamadas} llamadas de propagación",
                                     "sin búsqueda ni retroceso", (14, 165, 233)),
                                    (880, "Coloración DSatur", f"{n_color} nodos coloreados",
                                     "implementación más simple", (168, 85, 247))):
            d.rounded_rectangle(P(x - 200, 260) + P(x + 200, 470), 16 * S, fill=PANEL, outline=col + (int(255 * a),), width=2 * S)
            texto(d, (x, 310), tit, F_SUB, mezcla(PANEL, col, a), "mm")
            texto(d, (x, 375), l1, F_SUB, mezcla(PANEL, TEXTO, a), "mm")
            texto(d, (x, 415), l2, F_PEQ, mezcla(PANEL, TENUE, a), "mm")
        texto(d, (640, 560), "github.com/CARLYGP/Aplicacion_teoria_de_grafos_sudokus", F_PEQ, mezcla(FONDO, TENUE, a), "mm")
        v.cuadro(im)


def gif(mp4, ini, fin, salida, ancho=720, fps=12):
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-ss", f"{ini:.2f}", "-t", f"{fin - ini:.2f}",
                    "-i", str(mp4), "-vf",
                    f"fps={fps},scale={ancho}:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128:stats_mode=diff[p];"
                    "[b][p]paletteuse=dither=sierra2_4a:diff_mode=rectangle", str(salida)], check=True)


def portada_png(orden, final, aristas, llamadas):
    """Imagen de portada del README (1600 × 640): tablero resuelto + el grafo de 81 nodos coloreado."""
    PW, PH = 1600, 640
    im = Image.new("RGB", (PW * S, PH * S), FONDO)
    # resplandor suave detrás del grafo
    halo = Image.new("L", im.size, 0)
    ImageDraw.Draw(halo).ellipse(P(1300 - 300, 320 - 300) + P(1300 + 300, 320 + 300), fill=70)
    halo = halo.filter(ImageFilter.GaussianBlur(90 * S))
    im = Image.composite(Image.new("RGB", im.size, (40, 52, 110)), im, halo)
    capa = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    cx, cy, rr = 1300, 320, 236

    def pos(i):
        ang = -math.pi / 2 + i * 2 * math.pi / 81
        return cx + rr * math.cos(ang), cy + rr * math.sin(ang)

    color = {r * 9 + c: COLORES[final[r][c]] for r in range(9) for c in range(9)}
    for a, b in aristas:
        ca, cb = color[a], color[b]
        d.line(P(*pos(a)) + P(*pos(b)), fill=mezcla(ca, cb, 0.5) + (62,), width=S)
    im = Image.alpha_composite(im.convert("RGBA"), capa)
    d = ImageDraw.Draw(im)
    for i in range(81):
        x, y = pos(i)
        circulo(d, x, y, 8.5, color[i], FONDO, 2)
    texto(d, (cx, cy - 14), "81 nodos", F_TIT, TEXTO, "mm")
    texto(d, (cx, cy + 22), "810 aristas", F_SUB, TENUE, "mm")
    # tablero resuelto
    pistas = {(x, y) for _, x, y in PISTAS_COLOR}
    bx, by, cel = 700, 150, 38
    d.rounded_rectangle(P(bx - 10, by - 10) + P(bx + 9 * cel + 10, by + 9 * cel + 10), 14 * S, fill=PANEL)
    f_dig = fuente("segoeuib.ttf", 20)
    for r in range(9):
        for c in range(9):
            v_ = final[r][c]
            x, y = bx + c * cel + cel / 2, by + r * cel + cel / 2
            if (r, c) not in pistas:
                d.rounded_rectangle(P(x - 16, y - 16) + P(x + 16, y + 16), 6 * S, fill=mezcla(PANEL, COLORES[v_], 0.22))
            texto(d, (x, y), str(v_), f_dig, TEXTO if (r, c) in pistas else COLORES[v_], "mm")
    for i in range(10):
        ancho = 3 if i % 3 == 0 else 1
        col = (92, 110, 144) if i % 3 == 0 else LINEA
        d.line(P(bx + i * cel, by) + P(bx + i * cel, by + 9 * cel), fill=col, width=ancho * S)
        d.line(P(bx, by + i * cel) + P(bx + 9 * cel, by + i * cel), fill=col, width=ancho * S)
    # texto
    f_mega = fuente("segoeuib.ttf", 54)
    texto(d, (80, 196), "Sudokus como", f_mega, TEXTO)
    texto(d, (80, 268), "problema de grafos", f_mega, TEXTO)
    texto(d, (84, 360), "Emparejamientos y teorema de Berge · Coloración DSatur", F_SUB, (245, 158, 11))
    for i, (et, val) in enumerate((("métodos", "2"), ("llamadas de propagación", str(llamadas)), ("nodos coloreados", str(len(orden))))):
        x = 84 + i * 168
        d.rounded_rectangle(P(x, 420) + P(x + 152, 490), 10 * S, fill=PANEL, outline=LINEA, width=S)
        texto(d, (x + 14, 436), et, fuente("segoeui.ttf", 12), TENUE)
        texto(d, (x + 14, 456), val, fuente("segoeuib.ttf", 18), TEXTO)
    im.convert("RGB").resize((PW, PH), Image.LANCZOS).save(DOCS / "portada.png")


def main():
    grid, inicial, pasos, sol_m, llamadas = correr_emparejamiento()
    orden, sol_c, aristas = correr_coloracion()
    portada_png(orden, sol_c, aristas, llamadas)
    if "--portada" in sys.argv:
        return
    print(f"Emparejamiento: {llamadas} llamadas, {sum(p['antes'] != p['despues'] for p in pasos)} con cambios | "
          f"Coloración: {len(orden)} nodos, {len(aristas)} aristas | ambas soluciones válidas")
    mp4 = DOCS / "sudoku_grafos.mp4"
    v = Video(mp4)
    portada(v)
    escena_emparejamiento(v, grid, inicial, pasos, llamadas)
    escena_coloracion(v, orden, sol_c, aristas)
    cierre(v, llamadas, len(orden))
    v.cerrar()
    m = v.marcas
    gif(mp4, m["emparejamiento_ini"], m["emparejamiento_ini"] + 22, DOCS / "emparejamiento.gif", ancho=640, fps=10)
    gif(mp4, m["coloracion_ini"], m["coloracion_fin"], DOCS / "coloracion.gif", ancho=640, fps=10)
    for f in ("sudoku_grafos.mp4", "emparejamiento.gif", "coloracion.gif"):
        print(f, f"{(DOCS / f).stat().st_size / 1e6:.1f} MB")
    print(f"duración {v.n / FPS:.1f} s")


if __name__ == "__main__":
    main()
