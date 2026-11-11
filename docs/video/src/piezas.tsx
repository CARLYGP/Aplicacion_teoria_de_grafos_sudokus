import React from "react";
import datos from "./datos.json";
import { C, MONO, SANS } from "./tema";

export const DIG = ["", "#EF4444", "#F97316", "#EAB308", "#22C55E", "#14B8A6", "#0EA5E9", "#6366F1", "#A855F7", "#EC4899"];

export type Tablero = number[][][]; // [fila][columna] -> candidatos
export const PISTAS_M: number[][] = datos.pistas;
export const PASOS = datos.pasos;
export const INICIAL: Tablero = datos.inicial;
export const ORDEN: number[][] = datos.orden; // [fila, columna, color, saturación]
export const SOL_C: number[][] = datos.solucionC;
export const ARISTAS: number[][] = datos.aristas;
export const PISTAS_C = new Map<number, number>(datos.pistasColor.map(([v, x, y]) => [x * 9 + y, v]));

export const totalCandidatos = (t: Tablero) => t.reduce((s, f) => s + f.reduce((a, c) => a + c.length, 0), 0);

/** Tablero de Sudoku con candidatos, pistas, unidad resaltada y candidatos tachados (rojo que se apaga). */
export const TableroSudoku: React.FC<{
  tablero: Tablero;
  pistas: (r: number, c: number) => boolean;
  celda?: number;
  resaltar?: number[][];
  tachados?: Map<string, number>;
  aparicion?: (r: number, c: number) => number;
  sinCandidatos?: boolean;
}> = ({ tablero, pistas, celda = 76, resaltar = [], tachados, aparicion, sinCandidatos }) => {
  const res = new Set(resaltar.map(([r, c]) => r * 9 + c));
  const lado = celda * 9;
  return (
    <div style={{ position: "relative", width: lado, height: lado, borderRadius: 18, background: "rgba(255,255,255,0.035)", boxShadow: "0 40px 100px rgba(0,0,0,0.55)", border: "1px solid rgba(255,255,255,0.08)" }}>
      {tablero.map((fila, r) =>
        fila.map((cs, c) => {
          const a = aparicion ? aparicion(r, c) : 1;
          const fijo = cs.length === 1;
          const v = cs[0];
          const pista = pistas(r, c);
          return (
            <div key={r * 9 + c} style={{ position: "absolute", left: c * celda, top: r * celda, width: celda, height: celda, background: res.has(r * 9 + c) ? "rgba(255,255,255,0.07)" : "transparent", opacity: a }}>
              {fijo ? (
                <div
                  style={{
                    position: "absolute",
                    inset: 7,
                    borderRadius: 12,
                    background: pista ? "transparent" : DIG[v] + "26",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontFamily: SANS,
                    fontWeight: 800,
                    fontSize: celda * 0.5,
                    color: pista ? C.texto : DIG[v],
                  }}
                >
                  {v}
                </div>
              ) : (
                !sinCandidatos &&
                [1, 2, 3, 4, 5, 6, 7, 8, 9].map((k) => {
                  const t = tachados?.get(`${r},${c},${k}`);
                  const vivo = cs.includes(k);
                  if (!vivo && t === undefined) return null;
                  return (
                    <div
                      key={k}
                      style={{
                        position: "absolute",
                        left: 6 + ((k - 1) % 3) * ((celda - 12) / 3),
                        top: 4 + Math.floor((k - 1) / 3) * ((celda - 8) / 3),
                        width: (celda - 12) / 3,
                        textAlign: "center",
                        fontFamily: MONO,
                        fontSize: celda * 0.2,
                        color: t !== undefined ? C.rosa : C.tenue,
                        opacity: t !== undefined ? 1 - t : 1,
                        textDecoration: t !== undefined ? "line-through" : "none",
                        scale: t !== undefined ? String(1 + 0.4 * t) : "1",
                      }}
                    >
                      {k}
                    </div>
                  );
                })
              )}
            </div>
          );
        }),
      )}
      <svg width={lado} height={lado} style={{ position: "absolute", left: 0, top: 0 }}>
        {Array.from({ length: 10 }, (_, i) => (
          <g key={i}>
            <line x1={i * celda} x2={i * celda} y1={0} y2={lado} stroke={i % 3 === 0 ? "rgba(160,176,210,0.55)" : "rgba(255,255,255,0.08)"} strokeWidth={i % 3 === 0 ? 3 : 1} />
            <line y1={i * celda} y2={i * celda} x1={0} x2={lado} stroke={i % 3 === 0 ? "rgba(160,176,210,0.55)" : "rgba(255,255,255,0.08)"} strokeWidth={i % 3 === 0 ? 3 : 1} />
          </g>
        ))}
      </svg>
    </div>
  );
};

export const nombreUnidad = (celdas: number[][]) => {
  const filas = new Set(celdas.map((c) => c[0]));
  const cols = new Set(celdas.map((c) => c[1]));
  if (filas.size === 1) return `Fila ${celdas[0][0] + 1}`;
  if (cols.size === 1) return `Columna ${celdas[0][1] + 1}`;
  return `Bloque ${Math.floor(celdas[0][0] / 3) * 3 + Math.floor(celdas[0][1] / 3) + 1}`;
};

/** Grafo bipartito casillas ↔ valores de una unidad. fase: 0 aristas, 1 emparejamiento, 2 eliminación, 3 resultado. */
export const Bipartito: React.FC<{ paso: (typeof PASOS)[number]; fase: number; t: number; w: number; h: number }> = ({ paso, fase, t, w, h }) => {
  const xs = (i: number) => 50 + (i * (w - 100)) / 8;
  const yc = 70;
  const yv = h - 70;
  const r = 30;
  return (
    <svg width={w} height={h}>
      {paso.antes.map((cs, i) =>
        cs.map((k) => {
          const eliminada = !paso.despues[i].includes(k);
          const esM = paso.empar[i] === k;
          let color = "rgba(140,155,190,0.45)";
          let ancho = 1.6;
          let op = 1;
          if (fase === 0) op = Math.max(0, Math.min(1, t * 1.8 - i * 0.08));
          else if (fase === 1) {
            if (esM) {
              color = "#FFFFFF";
              ancho = 2 + 3 * t;
            }
          } else if (fase === 2) {
            if (eliminada) {
              color = C.rosa;
              ancho = 3;
              op = 1 - t * 0.85;
            } else if (esM) {
              color = "#FFFFFF";
              ancho = 5;
            }
          } else {
            if (eliminada) return null;
            if (paso.despues[i].length === 1) {
              color = DIG[k];
              ancho = 5;
            }
          }
          return <line key={`${i}-${k}`} x1={xs(i)} y1={yc + r} x2={xs(k - 1)} y2={yv - r} stroke={color} strokeWidth={ancho} opacity={op} strokeLinecap="round" style={esM && fase >= 1 && fase < 3 ? { filter: "drop-shadow(0 0 6px rgba(255,255,255,0.7))" } : undefined} />;
        }),
      )}
      {paso.celdas.map(([fr, cc], i) => {
        const fijo = fase === 3 && paso.despues[i].length === 1;
        const pista = paso.antes[i].length === 1;
        return (
          <g key={i}>
            <circle cx={xs(i)} cy={yc} r={r} fill={fijo ? DIG[paso.despues[i][0]] : pista ? "#2A3550" : "#1C2540"} stroke="rgba(170,185,220,0.6)" strokeWidth={2} />
            <text x={xs(i)} y={yc + 8} textAnchor="middle" fontFamily={pista || fijo ? SANS : MONO} fontWeight={700} fontSize={pista || fijo ? 26 : 17} fill={C.texto}>
              {pista ? paso.antes[i][0] : fijo ? paso.despues[i][0] : `${fr + 1},${cc + 1}`}
            </text>
          </g>
        );
      })}
      {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((k) => (
        <g key={k}>
          <circle cx={xs(k - 1)} cy={yv} r={r} fill={DIG[k]} />
          <text x={xs(k - 1)} y={yv + 9} textAnchor="middle" fontFamily={SANS} fontWeight={800} fontSize={26} fill="#fff">
            {k}
          </text>
        </g>
      ))}
    </svg>
  );
};

/** Posición del nodo i en el anillo de 81 nodos. */
export const anillo = (i: number, cx: number, cy: number, R: number) => {
  const a = -Math.PI / 2 + (i * 2 * Math.PI) / 81;
  return [cx + R * Math.cos(a), cy + R * Math.sin(a)];
};
