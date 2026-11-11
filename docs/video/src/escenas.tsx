import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import datos from "./datos.json";
import { ARISTAS, Bipartito, DIG, INICIAL, ORDEN, PASOS, PISTAS_C, PISTAS_M, SOL_C, TableroSudoku, Tablero, anillo, nombreUnidad, totalCandidatos } from "./piezas";
import { C, Encabezado, Fondo, MONO, SANS, Tarjeta, prog } from "./tema";

const esPistaM = (r: number, c: number) => PISTAS_M[r][c] !== 0;
const N_PISTAS = PISTAS_M.flat().filter(Boolean).length;
const quitados = (p: (typeof PASOS)[number]) => {
  const m = new Map<string, number>();
  p.celdas.forEach(([r, c], i) => p.antes[i].filter((k) => !p.despues[i].includes(k)).forEach((k) => m.set(`${r},${c},${k}`, 0)));
  return m;
};
const conProgreso = (m: Map<string, number>, t: number) => new Map([...m.keys()].map((k) => [k, t]));
const fijos = (t: Tablero) => t.flat().filter((c) => c.length === 1).length;

/* ---------------------------------------------------------------- Portada */
export const Intro: React.FC = () => {
  const frame = useCurrentFrame();
  const cx = 960;
  const cy = 540;
  const R = 480;
  const lineas = prog(frame, 0, 120);
  const sub = prog(frame, 40, 30);
  return (
    <AbsoluteFill>
      <Fondo acento={C.indigo} />
      <svg width={1920} height={1080} style={{ position: "absolute", opacity: 0.55 }}>
        {ARISTAS.slice(0, Math.floor(ARISTAS.length * lineas)).map(([a, b], i) => {
          const [x1, y1] = anillo(a, cx, cy, R);
          const [x2, y2] = anillo(b, cx, cy, R);
          return <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} stroke={DIG[SOL_C[Math.floor(a / 9)][a % 9]]} strokeOpacity={0.22} strokeWidth={1.2} />;
        })}
        {Array.from({ length: 81 }, (_, i) => {
          const [x, y] = anillo(i, cx, cy, R);
          const a = prog(frame, i * 0.6, 20);
          return <circle key={i} cx={x} cy={y} r={11 * a} fill={DIG[SOL_C[Math.floor(i / 9)][i % 9]]} />;
        })}
      </svg>
      <AbsoluteFill style={{ background: "radial-gradient(circle at center, rgba(6,10,19,0.92) 0%, rgba(6,10,19,0.6) 32%, transparent 60%)" }} />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
        {["Sudokus como", "problema de grafos"].map((l, i) => {
          const a = prog(frame, 10 + i * 9, 32);
          return (
            <div key={l} style={{ overflow: "hidden", paddingBottom: 8 }}>
              <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 104, lineHeight: 1.05, letterSpacing: -3.5, color: C.texto, translate: `0 ${(1 - a) * 140}px`, textAlign: "center" }}>{l}</div>
            </div>
          );
        })}
        <div style={{ fontFamily: SANS, fontSize: 36, color: C.tenue, marginTop: 24, opacity: sub, translate: `0 ${(1 - sub) * 20}px` }}>
          <span style={{ color: C.indigo, fontWeight: 700 }}>Emparejamientos</span> y teorema de Berge ·{" "}
          <span style={{ color: C.violeta, fontWeight: 700 }}>Coloración</span> DSatur
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/* ---------------------------------------------------------------- Tablero inicial */
export const TableroInicial: React.FC = () => {
  const frame = useCurrentFrame();
  const cand = prog(frame, 50, 40);
  const vacio: Tablero = INICIAL.map((f, r) => f.map((cs, c) => (esPistaM(r, c) ? cs : [])));
  return (
    <AbsoluteFill>
      <Fondo acento={C.indigo} />
      <Encabezado etiqueta="Método 1 · Emparejamiento máximo" titulo="Cada casilla vacía empieza con sus candidatos" color={C.indigo} />
      <div style={{ position: "absolute", left: 120, top: 270 }}>
        <TableroSudoku tablero={cand > 0 ? INICIAL : vacio} pistas={esPistaM} aparicion={(r, c) => (esPistaM(r, c) ? prog(frame, (r * 9 + c) * 0.35, 14) : cand)} />
      </div>
      <div style={{ position: "absolute", left: 900, top: 330, width: 880, display: "flex", flexDirection: "column", gap: 28 }}>
        {[
          [`${N_PISTAS}`, "pistas en sudoku_3.txt", C.texto],
          [`${totalCandidatos(INICIAL) - N_PISTAS}`, "candidatos por descartar", C.indigo],
          ["27", "unidades: 9 filas, 9 columnas y 9 bloques", C.violeta],
        ].map(([n, t, col], i) => {
          const a = prog(frame, 20 + i * 18, 28);
          return (
            <Tarjeta key={t} style={{ padding: "28px 40px", display: "flex", alignItems: "baseline", gap: 26, opacity: a, translate: `${(1 - a) * 50}px 0` }}>
              <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 76, color: col, minWidth: 170 }}>{n}</div>
              <div style={{ fontFamily: SANS, fontSize: 34, color: C.texto }}>{t}</div>
            </Tarjeta>
          );
        })}
        <div style={{ fontFamily: SANS, fontSize: 32, color: C.tenue, lineHeight: 1.4, opacity: prog(frame, 80, 30) }}>
          Cada unidad impone «todos distintos»: se modela como un grafo bipartito entre sus 9 casillas y los valores 1–9.
        </div>
      </div>
    </AbsoluteFill>
  );
};

/* ---------------------------------------------------------------- Un paso en detalle */
const FASES = [
  ["Aristas = candidatos de cada casilla", C.tenue],
  ["Emparejamiento máximo (Hopcroft-Karp)", "#FFFFFF"],
  ["Berge: fuera las aristas que no están en ningún emparejamiento máximo", C.rosa],
  ["Lo que sobrevive vuelve al tablero", C.verde],
] as const;
export const DUR_FASE = 50;

export const PasoDetalle: React.FC = () => {
  const frame = useCurrentFrame();
  const paso = PASOS[0];
  const fase = Math.min(3, Math.floor(Math.max(0, frame - 20) / DUR_FASE));
  const t = Math.min(1, ((Math.max(0, frame - 20)) % DUR_FASE) / (DUR_FASE * 0.7));
  const q = quitados(paso);
  const tablero = fase === 3 ? paso.tablero : INICIAL;
  return (
    <AbsoluteFill>
      <Fondo acento={C.indigo} />
      <Encabezado etiqueta={`Paso 1 de ${PASOS.length} · ${nombreUnidad(paso.celdas)}`} titulo="Teorema de Berge, paso a paso" color={C.indigo} />
      <div style={{ position: "absolute", left: 120, top: 270 }}>
        <TableroSudoku tablero={tablero} pistas={esPistaM} resaltar={paso.celdas} tachados={fase === 2 ? conProgreso(q, t) : undefined} />
      </div>
      <Tarjeta style={{ position: "absolute", left: 870, top: 270, width: 930, height: 684, opacity: prog(frame, 0, 20) }}>
        <div style={{ position: "absolute", left: 40, top: 30, fontFamily: MONO, fontSize: 22, color: C.tenue, letterSpacing: 2 }}>
          {nombreUnidad(paso.celdas).toUpperCase()} · CASILLAS ↔ VALORES
        </div>
        <div style={{ position: "absolute", left: 20, top: 80 }}>
          <Bipartito paso={paso} fase={fase} t={t} w={890} h={480} />
        </div>
        <div style={{ position: "absolute", left: 40, right: 40, bottom: 34, display: "flex", gap: 16, alignItems: "center" }}>
          <div style={{ fontFamily: MONO, fontSize: 24, color: FASES[fase][1], fontWeight: 700 }}>{fase + 1}/4</div>
          <div style={{ fontFamily: SANS, fontSize: 30, color: C.texto, fontWeight: 600 }}>{FASES[fase][0]}</div>
        </div>
      </Tarjeta>
    </AbsoluteFill>
  );
};

/* ---------------------------------------------------------------- Propagación acelerada */
export const F_PASO = 3;

export const Propagacion: React.FC = () => {
  const frame = useCurrentFrame();
  const resto = PASOS.slice(1);
  const j = Math.min(resto.length - 1, Math.floor(frame / F_PASO));
  const sub = (frame % F_PASO) / (F_PASO - 1);
  const paso = resto[j];
  const terminado = frame >= resto.length * F_PASO;
  const antes = j === 0 ? PASOS[0].tablero : resto[j - 1].tablero;
  const tablero = terminado || sub >= 1 ? paso.tablero : antes;
  const cand = totalCandidatos(tablero);
  const fij = fijos(tablero);
  return (
    <AbsoluteFill>
      <Fondo acento={C.indigo} />
      <Encabezado etiqueta="Propagación hasta el punto fijo" titulo="Sin adivinar y sin retroceder" color={C.indigo} />
      <div style={{ position: "absolute", left: 120, top: 270 }}>
        <TableroSudoku tablero={tablero} pistas={esPistaM} resaltar={terminado ? [] : paso.celdas} tachados={terminado ? undefined : conProgreso(quitados(paso), sub)} />
      </div>
      <div style={{ position: "absolute", left: 900, top: 290, width: 880, display: "flex", flexDirection: "column", gap: 26 }}>
        <Tarjeta style={{ padding: "26px 40px" }}>
          <div style={{ fontFamily: MONO, fontSize: 22, color: C.tenue, letterSpacing: 2 }}>PASO QUE CAMBIA ALGO</div>
          <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 84, color: C.indigo, fontVariantNumeric: "tabular-nums" }}>
            {terminado ? PASOS.length : j + 2}
            <span style={{ fontSize: 40, color: C.tenue, fontWeight: 600 }}> / {PASOS.length}</span>
          </div>
          <div style={{ height: 10, borderRadius: 5, background: "rgba(255,255,255,0.08)", marginTop: 10 }}>
            <div style={{ height: 10, borderRadius: 5, width: `${((terminado ? PASOS.length : j + 2) / PASOS.length) * 100}%`, background: `linear-gradient(90deg, ${C.indigo}, ${C.violeta})` }} />
          </div>
        </Tarjeta>
        <div style={{ display: "flex", gap: 26 }}>
          <Tarjeta style={{ flex: 1, padding: "26px 34px" }}>
            <div style={{ fontFamily: MONO, fontSize: 20, color: C.tenue, letterSpacing: 2 }}>CASILLAS RESUELTAS</div>
            <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 72, color: C.verde, fontVariantNumeric: "tabular-nums" }}>{fij}<span style={{ fontSize: 34, color: C.tenue }}> / 81</span></div>
          </Tarjeta>
          <Tarjeta style={{ flex: 1, padding: "26px 34px" }}>
            <div style={{ fontFamily: MONO, fontSize: 20, color: C.tenue, letterSpacing: 2 }}>CANDIDATOS VIVOS</div>
            <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 72, color: C.rosa, fontVariantNumeric: "tabular-nums" }}>{cand - fij}</div>
          </Tarjeta>
        </div>
        <div style={{ fontFamily: SANS, fontSize: 32, color: terminado ? C.verde : C.tenue, fontWeight: terminado ? 700 : 400, lineHeight: 1.4 }}>
          {terminado
            ? `Resuelto: ${datos.llamadas} llamadas a la restricción, ${PASOS.length} con cambios.`
            : `${nombreUnidad(paso.celdas)}: cada eliminación avisa a las unidades vecinas, que se vuelven a revisar.`}
        </div>
      </div>
    </AbsoluteFill>
  );
};

/* ---------------------------------------------------------------- Del tablero al grafo */
const RCX = 1250;
const RCY = 585;
const RR = 400;

export const DeTableroAGrafo: React.FC = () => {
  const frame = useCurrentFrame();
  const aristas = prog(frame, 90, 70);
  const celda = 66;
  const gx = 120;
  const gy = 290;
  return (
    <AbsoluteFill>
      <Fondo acento={C.violeta} />
      <Encabezado etiqueta="Método 2 · Coloración de grafos" titulo="81 casillas, 81 nodos, 810 aristas" color={C.violeta} />
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        {ARISTAS.slice(0, Math.floor(ARISTAS.length * aristas)).map(([a, b], i) => {
          const [x1, y1] = anillo(a, RCX, RCY, RR);
          const [x2, y2] = anillo(b, RCX, RCY, RR);
          return <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} stroke="rgba(150,165,210,0.16)" strokeWidth={1.2} />;
        })}
        {Array.from({ length: 81 }, (_, i) => {
          const r = Math.floor(i / 9);
          const c = i % 9;
          const m = prog(frame, 20 + i * 0.7, 45);
          const [ax, ay] = anillo(i, RCX, RCY, RR);
          const x = interpolate(m, [0, 1], [gx + c * celda + celda / 2, ax]);
          const y = interpolate(m, [0, 1], [gy + r * celda + celda / 2, ay]);
          const pista = PISTAS_C.get(i);
          const rad = interpolate(m, [0, 1], [celda * 0.42, 15]);
          return (
            <g key={i}>
              <circle cx={x} cy={y} r={rad} fill={pista ? DIG[pista] : "#1C2540"} stroke="rgba(170,185,220,0.5)" strokeWidth={1.5} />
              {pista ? (
                <text x={x} y={y + rad * 0.36} textAnchor="middle" fontFamily={SANS} fontWeight={800} fontSize={rad} fill="#fff">
                  {pista}
                </text>
              ) : null}
            </g>
          );
        })}
      </svg>
      <div style={{ position: "absolute", left: 120, top: 900, width: 620, fontFamily: SANS, fontSize: 30, lineHeight: 1.4, color: C.tenue, opacity: prog(frame, 100, 30) }}>
        Cada casilla se une con sus <span style={{ color: C.texto, fontWeight: 700 }}>20 vecinas</span> de fila, columna y bloque. Llenar el Sudoku = colorear sin que dos vecinos compartan color.
      </div>
    </AbsoluteFill>
  );
};

/* ---------------------------------------------------------------- DSatur */
export const F_NODO = 6;
export const LEAD = 20;

export const DSatur: React.FC = () => {
  const frame = useCurrentFrame();
  const k = Math.max(-1, Math.min(ORDEN.length - 1, Math.floor((frame - LEAD) / F_NODO)));
  const sub = k >= 0 ? ((frame - LEAD) % F_NODO) / F_NODO : 0;
  const coloreados = new Map<number, number>();
  PISTAS_C.forEach((v, i) => coloreados.set(i, v));
  for (let j = 0; j <= k; j++) coloreados.set(ORDEN[j][0] * 9 + ORDEN[j][1], SOL_C[ORDEN[j][0]][ORDEN[j][1]]);
  const actual = k >= 0 ? ORDEN[k][0] * 9 + ORDEN[k][1] : -1;
  const vecinos = new Set<number>();
  ARISTAS.forEach(([a, b]) => {
    if (a === actual) vecinos.add(b);
    if (b === actual) vecinos.add(a);
  });
  const terminado = frame >= LEAD + ORDEN.length * F_NODO;
  const mini: Tablero = Array.from({ length: 9 }, (_, r) => Array.from({ length: 9 }, (_, c) => (coloreados.has(r * 9 + c) ? [coloreados.get(r * 9 + c)!] : [])));
  return (
    <AbsoluteFill>
      <Fondo acento={C.violeta} />
      <Encabezado etiqueta="DSatur modificado" titulo="Siempre el nodo más restringido" color={C.violeta} />
      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        {ARISTAS.map(([a, b], i) => {
          const activa = !terminado && (a === actual || b === actual);
          const [x1, y1] = anillo(a, RCX, RCY, RR);
          const [x2, y2] = anillo(b, RCX, RCY, RR);
          const ca = coloreados.get(a);
          const color = activa ? DIG[SOL_C[Math.floor(actual / 9)][actual % 9]] : terminado && ca ? DIG[ca] : "rgba(150,165,210,1)";
          return <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} stroke={color} strokeOpacity={activa ? 0.9 : terminado ? 0.28 : 0.12} strokeWidth={activa ? 2.2 : 1.2} />;
        })}
        {Array.from({ length: 81 }, (_, i) => {
          const [x, y] = anillo(i, RCX, RCY, RR);
          const v = coloreados.get(i);
          const esActual = i === actual && !terminado;
          const r = esActual ? 15 + 10 * Math.sin(Math.PI * sub) : vecinos.has(i) && !terminado ? 17 : 15;
          return (
            <g key={i}>
              {esActual && <circle cx={x} cy={y} r={34} fill="none" stroke={DIG[v!]} strokeWidth={3} opacity={1 - sub} />}
              <circle cx={x} cy={y} r={r} fill={v ? DIG[v] : "#1C2540"} stroke={vecinos.has(i) && !terminado ? "#fff" : "rgba(170,185,220,0.5)"} strokeWidth={vecinos.has(i) && !terminado ? 2.5 : 1.5} style={v ? { filter: `drop-shadow(0 0 8px ${DIG[v]}88)` } : undefined} />
            </g>
          );
        })}
      </svg>
      <div style={{ position: "absolute", left: RCX - 170, top: RCY - 70, width: 340, textAlign: "center" }}>
        {k >= 0 && !terminado ? (
          <>
            <div style={{ fontFamily: MONO, fontSize: 22, color: C.tenue }}>casilla ({ORDEN[k][0] + 1},{ORDEN[k][1] + 1})</div>
            <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 80, color: DIG[SOL_C[ORDEN[k][0]][ORDEN[k][1]]] }}>{SOL_C[ORDEN[k][0]][ORDEN[k][1]]}</div>
            <div style={{ fontFamily: MONO, fontSize: 22, color: C.tenue }}>saturación {ORDEN[k][3]}</div>
          </>
        ) : terminado ? (
          <>
            <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 70, color: C.verde }}>81 / 81</div>
            <div style={{ fontFamily: MONO, fontSize: 22, color: C.tenue }}>coloración propia con 9 colores</div>
          </>
        ) : null}
      </div>
      <div style={{ position: "absolute", left: 120, top: 290 }}>
        <TableroSudoku tablero={mini} pistas={(r, c) => PISTAS_C.has(r * 9 + c)} celda={52} resaltar={actual >= 0 && !terminado ? [[Math.floor(actual / 9), actual % 9]] : []} sinCandidatos />
      </div>
      <Tarjeta style={{ position: "absolute", left: 120, top: 790, width: 468, padding: "22px 30px" }}>
        <div style={{ fontFamily: MONO, fontSize: 20, color: C.tenue, letterSpacing: 2 }}>NODOS COLOREADOS</div>
        <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 62, color: C.violeta, fontVariantNumeric: "tabular-nums" }}>
          {k + 1}<span style={{ fontSize: 30, color: C.tenue }}> / {ORDEN.length} sin pista</span>
        </div>
      </Tarjeta>
    </AbsoluteFill>
  );
};

/* ---------------------------------------------------------------- Comparación */
export const Comparacion: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const metodos = [
    { n: "Emparejamiento + Berge", c: C.indigo, d: [["Modelo", "27 grafos bipartitos"], ["Búsqueda", "ninguna: propagación"], ["Trabajo", `${datos.llamadas} llamadas, ${PASOS.length} con cambios`], ["Pistas", `${N_PISTAS}`]] },
    { n: "Coloración DSatur", c: C.violeta, d: [["Modelo", "1 grafo de 81 nodos"], ["Búsqueda", "voraz, sin retroceso"], ["Trabajo", `${ORDEN.length} nodos coloreados`], ["Pistas", `${PISTAS_C.size}`]] },
  ];
  return (
    <AbsoluteFill>
      <Fondo acento={C.indigo} />
      <Encabezado etiqueta="Dos formas de verlo" titulo="El mismo problema, dos grafos" color={C.indigo} />
      <div style={{ position: "absolute", left: 120, right: 120, top: 290, display: "flex", gap: 50 }}>
        {metodos.map((m, i) => {
          const a = prog(frame, 8 + i * 12, 30);
          return (
            <Tarjeta key={m.n} color={m.c} style={{ flex: 1, padding: "40px 50px", opacity: a, translate: `0 ${(1 - a) * 50}px` }}>
              <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 48, color: m.c, marginBottom: 26 }}>{m.n}</div>
              {m.d.map(([e, v], j) => (
                <div key={e} style={{ display: "flex", justifyContent: "space-between", padding: "20px 0", borderTop: "1px solid rgba(255,255,255,0.08)", opacity: prog(frame, 24 + i * 12 + j * 6, 20) }}>
                  <div style={{ fontFamily: MONO, fontSize: 24, color: C.tenue }}>{e}</div>
                  <div style={{ fontFamily: SANS, fontSize: 32, color: C.texto, fontWeight: 600 }}>{v}</div>
                </div>
              ))}
            </Tarjeta>
          );
        })}
      </div>
      <div style={{ position: "absolute", left: 160, right: 160, bottom: 110, textAlign: "center", fontFamily: SANS, fontSize: 32, lineHeight: 1.45, color: C.tenue, opacity: prog(frame, 2.4 * fps, 30) }}>
        La coloración es más simple de implementar, pero al ser voraz puede quedarse sin colores en Sudokus difíciles; la propagación por emparejamientos es exacta.
      </div>
    </AbsoluteFill>
  );
};

/* ---------------------------------------------------------------- Cierre */
export const Cierre: React.FC = () => {
  const frame = useCurrentFrame();
  const a = prog(frame, 0, 30);
  return (
    <AbsoluteFill>
      <Fondo acento={C.violeta} />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
        <div style={{ overflow: "hidden", paddingBottom: 10 }}>
          <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 100, letterSpacing: -3, color: C.texto, translate: `0 ${(1 - a) * 130}px` }}>Teoría de grafos · Sudoku</div>
        </div>
        <div style={{ fontFamily: MONO, fontSize: 28, color: C.indigo, opacity: prog(frame, 14, 30), marginTop: 10 }}>Python · NetworkX · Teorema de Berge · DSatur</div>
        <div style={{ fontFamily: SANS, fontSize: 30, color: C.tenue, opacity: prog(frame, 24, 30), marginTop: 36 }}>Gabriel Fandiño · Carlos Galán · Rosa Galicia — Universidad del Rosario</div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
