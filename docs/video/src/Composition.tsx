import React from "react";
import { AbsoluteFill, Composition, Still } from "remotion";
import { TransitionSeries, springTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { slide } from "@remotion/transitions/slide";
import datos from "./datos.json";
import { Cierre, Comparacion, DSatur, DUR_FASE, DeTableroAGrafo, F_NODO, F_PASO, Intro, LEAD, PasoDetalle, Propagacion, TableroInicial } from "./escenas";
import { ARISTAS, DIG, ORDEN, PASOS, PISTAS_C, SOL_C, TableroSudoku, anillo } from "./piezas";
import { C, Fondo, MONO, SANS } from "./tema";

const T = 20;
const ESCENAS: [string, React.FC, number][] = [
  ["Portada", Intro, 160],
  ["Tablero", TableroInicial, 170],
  ["Paso en detalle", PasoDetalle, 20 + 4 * DUR_FASE + 20],
  ["Propagación", Propagacion, (PASOS.length - 1) * F_PASO + 90],
  ["Del tablero al grafo", DeTableroAGrafo, 210],
  ["DSatur", DSatur, LEAD + ORDEN.length * F_NODO + 80],
  ["Comparación", Comparacion, 200],
  ["Cierre", Cierre, 130],
];
const DURACION = ESCENAS.reduce((s, e) => s + e[2], 0) - T * (ESCENAS.length - 1);

export const SudokuVideo: React.FC = () => (
  <TransitionSeries>
    {ESCENAS.flatMap(([nombre, Escena, dur], i) => {
      const nodos = [
        <TransitionSeries.Sequence key={nombre} name={nombre} durationInFrames={dur}>
          <Escena />
        </TransitionSeries.Sequence>,
      ];
      if (i < ESCENAS.length - 1)
        nodos.push(
          <TransitionSeries.Transition
            key={nombre + "-t"}
            presentation={(i % 2 === 0 ? fade() : slide({ direction: "from-right" })) as ReturnType<typeof fade>}
            timing={springTiming({ config: { damping: 200 }, durationInFrames: T })}
          />,
        );
      return nodos;
    })}
  </TransitionSeries>
);

const solucion = SOL_C.map((f) => f.map((v) => [v]));

/** Anillo coloreado con el tablero resuelto en el centro. */
const GrafoConTablero: React.FC<{ cx: number; cy: number; R: number; celda: number; nodo: number }> = ({ cx, cy, R, celda, nodo }) => (
  <>
    <svg width={cx * 2 + R} height={cy * 2 + R} style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }}>
      <circle cx={cx} cy={cy} r={R + 60} fill={C.indigo} opacity={0.08} style={{ filter: "blur(40px)" }} />
      {ARISTAS.map(([a, b], i) => {
        const [x1, y1] = anillo(a, cx, cy, R);
        const [x2, y2] = anillo(b, cx, cy, R);
        return <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} stroke={DIG[SOL_C[Math.floor(a / 9)][a % 9]]} strokeOpacity={0.3} strokeWidth={1.3} />;
      })}
      {Array.from({ length: 81 }, (_, i) => {
        const [x, y] = anillo(i, cx, cy, R);
        const v = SOL_C[Math.floor(i / 9)][i % 9];
        return <circle key={i} cx={x} cy={y} r={nodo} fill={DIG[v]} stroke={C.fondo} strokeWidth={2} style={{ filter: `drop-shadow(0 0 6px ${DIG[v]}aa)` }} />;
      })}
    </svg>
    <div style={{ position: "absolute", left: cx - (celda * 9) / 2, top: cy - (celda * 9) / 2, background: C.fondo, borderRadius: 18 }}>
      <TableroSudoku tablero={solucion} pistas={(r, c) => PISTAS_C.has(r * 9 + c)} celda={celda} sinCandidatos />
    </div>
  </>
);

export const PortadaBanner: React.FC = () => (
  <AbsoluteFill>
    <Fondo acento={C.indigo} />
    <GrafoConTablero cx={1220} cy={320} R={268} celda={32} nodo={9} />
    <div style={{ position: "absolute", left: 90, top: 140 }}>
      <div style={{ fontFamily: MONO, fontSize: 22, letterSpacing: 4, color: C.indigo }}>TEORÍA DE GRAFOS · ALGORITMOS</div>
      <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 88, lineHeight: 1.02, letterSpacing: -3, color: C.texto, marginTop: 18 }}>
        Sudokus como
        <br />
        problema de grafos
      </div>
      <div style={{ fontFamily: SANS, fontSize: 28, color: C.tenue, marginTop: 22 }}>Emparejamientos y teorema de Berge · Coloración DSatur</div>
      <div style={{ display: "flex", gap: 16, marginTop: 40 }}>
        {[
          ["NODOS · ARISTAS", "81 · 810", C.violeta],
          ["LLAMADAS", String(datos.llamadas), C.indigo],
          ["NODOS COLOREADOS", String(ORDEN.length), C.rosa],
        ].map(([e, v, c]) => (
          <div key={e} style={{ padding: "16px 24px", borderRadius: 16, background: "rgba(8,12,22,0.72)", border: `1px solid ${c}66` }}>
            <div style={{ fontFamily: MONO, fontSize: 16, color: C.tenue, letterSpacing: 2 }}>{e}</div>
            <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 34, color: c }}>{v}</div>
          </div>
        ))}
      </div>
    </div>
  </AbsoluteFill>
);

export const PortadaTarjeta: React.FC = () => (
  <AbsoluteFill>
    <Fondo acento={C.indigo} />
    <GrafoConTablero cx={600} cy={450} R={372} celda={44} nodo={13} />
  </AbsoluteFill>
);

export const Composiciones: React.FC = () => (
  <>
    <Composition id="Sudoku" component={SudokuVideo} durationInFrames={DURACION} fps={30} width={1920} height={1080} />
    <Still id="PortadaBanner" component={PortadaBanner} width={1600} height={640} />
    <Still id="PortadaTarjeta" component={PortadaTarjeta} width={1200} height={900} />
  </>
);
