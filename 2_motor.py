# -*- coding: utf-8 -*-
"""
PASO 3 · MOTOR DE DECISIÓN  (módulos 5–8 y 15: priorización, optimizador, stress test, sensibilidad, confianza)

Lee  salidas/preparado/  (lo deja 1_preparar.py) y escribe  salidas/motor/.

  0. Celdas de Vulnerabilidad sin dato ni promedio regional: usan el valor estimado desde el
     histórico (prior_historico.csv) cuando alcanza el mínimo de registros; si no, el valor fijo.
  1. Puntaje transparente de cada alternativa (medida × municipio o corredor)
  2. Mochila 0/1 exacta: la mejor combinación que cabe en el presupuesto (medidas indivisibles)
  3. Stress test SSP3-7.0/2060: se repite con los pesos del stress test (entra la robustez)
  4. Simulación: datos vacíos, pesos y efectividad varían al azar  → frecuencia de cada medida
  5. Portafolio robusto: el de mínimo arrepentimiento (regret) frente a todos los escenarios simulados
  6. Valor de la información: qué dato vacío, y desde qué valor, cambiaría la decisión
  7. Contrafactuales: presupuesto ±, quitar medidas, regla de máximo de intervenciones, equidad

Uso:   python 2_motor.py
"""
import json
import os
import sys

import numpy as np
import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8")   # para que Windows muestre bien los símbolos
except Exception:
    pass

AQUI = os.path.dirname(os.path.abspath(__file__))
PREP = os.path.join(AQUI, "salidas", "preparado")
SAL = os.path.join(AQUI, "salidas", "motor")
MUNICIPIOS = ["Rionegro", "Guarne", "Marinilla"]
CRITERIOS = ["Necesidad", "Brecha CA", "Evidencia", "Cobertura", "Cobeneficios", "Robustez 2060"]
ALINEACION_CA = {"CA": 1.0, "S+CA": 1.0}        # medidas que fortalecen capacidad cuentan la brecha completa


# ==============================================================================================
# CARGA
# ==============================================================================================
def cargar():
    if not os.path.exists(os.path.join(PREP, "ficha_larga.csv")):
        sys.exit("Primero ejecute: python 1_preparar.py")
    rd = lambda f: pd.read_csv(os.path.join(PREP, f), encoding="utf-8-sig")
    ficha, prom, med, evid, pesos = (rd("ficha_larga.csv"), rd("promedios_regionales.csv"), rd("medidas.csv"),
                                     rd("evidencia.csv"), rd("pesos.csv"))
    med["Cobeneficios (otras dimensiones)"] = med["Cobeneficios (otras dimensiones)"].fillna("")
    par = json.load(open(os.path.join(PREP, "parametros.json"), encoding="utf-8"))
    par["n_simulaciones"] = int(par["n_simulaciones"]); par["semilla"] = int(par["semilla"])
    ruta_hist = os.path.join(PREP, "prior_historico.csv")
    prior_hist = rd("prior_historico.csv") if os.path.exists(ruta_hist) else pd.DataFrame(
        columns=["Municipio", "dimension", "registros", "valor_estimado"])
    return ficha, prom, med, evid, pesos, par, prior_hist


# ==============================================================================================
# MÓDULO 5 · ALTERNATIVAS Y CRITERIOS
# ==============================================================================================
def construir_alternativas(ficha, prom, med, evid, par, prior_hist):
    """Cada alternativa guarda, para cada criterio, de dónde sale su valor (dato o celda vacía)."""
    val = {(r.municipio, r.dimension, r.componente): (r.valor, r.origen) for r in ficha.itertuples()}
    reg = dict(zip(prom.dimension, prom.v_promedio))
    hist = {(r.Municipio, r.dimension): (float(r.valor_estimado), int(r.registros)) for r in prior_hist.itertuples()}
    vacias = {}                                     # celda vacía -> valor del caso base y regla usada

    def celda(m, d, comp):
        v, o = val.get((m, d, comp), (None, "NO DISPONIBLE"))
        if o != "NO DISPONIBLE" and not pd.isna(v):
            return ("dato", float(v), o)
        k = f"{m} · {d} · {comp}"
        if comp == "Vulnerabilidad" and d in reg:
            vacias[k] = (reg[d], "promedio regional oficial")
        elif comp == "Vulnerabilidad" and (m, d) in hist:
            valor, n = hist[(m, d)]
            vacias[k] = (valor, f"estimado desde histórico (n={n} registros)")
        else:
            vacias[k] = (par["valor_vacio_base"], "valor de referencia (parámetro)")
        return ("vacia", k, None)

    alts = []
    max_cob = max(len([c for c in str(x).split(";") if c.strip()]) for x in med["Cobeneficios (otras dimensiones)"])
    for m in med.itertuples(index=False):
        mid, dim, costo, escala, actua = m[0], m[1], float(m[4]), m[5], m[6]
        cobs = [c.strip() for c in str(m[7]).split(";") if c.strip()]
        territorios = [("Corredor", MUNICIPIOS)] if escala == "corredor" else [(x, [x]) for x in MUNICIPIOS]
        for terr, munis in territorios:
            V = [celda(x, dim, "Vulnerabilidad") for x in munis]
            CA = [celda(x, dim, "Capacidad adaptativa") for x in munis]
            ROB = []
            for x in munis:
                r0, r1 = celda(x, dim, "Riesgo hoy"), celda(x, dim, "Riesgo SSP3-7.0 2060")
                if r0[0] == "dato" and r1[0] == "dato":
                    ROB.append(("dato", 1.0 if r1[1] > r0[1] else 0.5 if r1[1] == r0[1] else 0.0, "derivado"))
                else:
                    k = f"{x} · {dim} · Robustez 2060"
                    vacias[k] = (par["valor_vacio_base"], "valor de referencia (parámetro)")
                    ROB.append(("vacia", k, None))
            ev = [float(evid[(evid.ID == mid) & (evid.Municipio == x)].Evidencia.iloc[0]) for x in munis]
            n_datos = sum(c[0] == "dato" for c in V + CA)
            # desempate [SUPUESTO]: municipio con amenaza registrada en la dimensión de la medida o de sus cobeneficios
            desempate = int(len(munis) == 1 and any(val.get((munis[0], d, "Amenaza"), (None, "NO DISPONIBLE"))[1]
                                                    != "NO DISPONIBLE" for d in [dim] + cobs))
            alts.append(dict(
                alt=f"{mid}-{terr[:3].upper()}", id=mid, medida=m[2], dimension=dim, territorio=terr, municipios=munis,
                costo=costo, actua_sobre=actua, V=V, CA=CA, ROB=ROB,
                evidencia=float(np.mean(ev)), cobertura=len(munis) / 3, cobeneficios=len(cobs) / max_cob,
                cobeneficios_txt="; ".join(cobs), n_datos=n_datos, desempate=desempate,
                elegible=bool(n_datos > 0 or np.mean(ev) >= par["umbral_evidencia"]),
                indicador=m[9], estado_indicador=m[10]))
    return alts, vacias


def matriz_criterios(alts, valores_vacias, alin_S):
    """Matriz (alternativas × 6 criterios) en 0–1, dado un valor para cada celda vacía."""
    f = lambda c: c[1] if c[0] == "dato" else valores_vacias[c[1]]
    X = np.zeros((len(alts), len(CRITERIOS)))
    for i, a in enumerate(alts):
        V = np.mean([f(c) for c in a["V"]]); CA = np.mean([f(c) for c in a["CA"]]); R = np.mean([f(c) for c in a["ROB"]])
        alin = ALINEACION_CA.get(a["actua_sobre"], alin_S)
        X[i] = [V, (1 - CA) * alin, a["evidencia"], a["cobertura"], a["cobeneficios"], R]
    return X


def beneficio(alts, puntaje, alfa):
    """Beneficio = puntaje × (costo/1000)^α  (+ desempate mínimo entre alternativas idénticas)."""
    c = np.array([a["costo"] for a in alts]); e = np.array([a["desempate"] for a in alts])
    return puntaje * (c / 1000.0) ** alfa + 1e-6 * e


# ==============================================================================================
# MÓDULO 6 · OPTIMIZADOR (mochila 0/1 exacta por programación dinámica)
# ==============================================================================================
def mochila(alts, b, presupuesto, elegibles, min_1_municipal=False, max_intervenciones=False, excluir=()):
    cap = int(round(presupuesto / 100))
    best = {(0, 0): (0.0, ())}                       # (bloques de $100 M usados, municipios cubiertos) -> (valor, elegidas)
    for i, a in enumerate(alts):
        if not elegibles[i] or a["alt"] in excluir or a["id"] in excluir:
            continue
        c = int(round(a["costo"] / 100))
        mk = 0 if a["territorio"] == "Corredor" else 1 << MUNICIPIOS.index(a["territorio"])
        v_i = b[i] + (1000.0 if max_intervenciones else 0.0)
        nuevo = dict(best)
        for (u, m), (v, s) in best.items():
            if u + c <= cap:
                k = (u + c, m | mk)
                if k not in nuevo or v + v_i > nuevo[k][0] + 1e-12:
                    nuevo[k] = (v + v_i, s + (i,))
        best = nuevo
    cands = [(v, s) for (u, m), (v, s) in best.items() if not min_1_municipal or m == 7]
    return sorted(max(cands, key=lambda t: t[0])[1]) if cands else []


# ==============================================================================================
# PROGRAMA PRINCIPAL
# ==============================================================================================
def main():
    ficha, prom, med, evid, pesos, par, prior_hist = cargar()
    P, alfa0, alinS = par["presupuesto"], par["alfa"], par["alineacion_S"]
    rng = np.random.default_rng(par["semilla"]); N = par["n_simulaciones"]
    os.makedirs(SAL, exist_ok=True)

    alts, vacias = construir_alternativas(ficha, prom, med, evid, par, prior_hist)
    eleg = np.array([a["elegible"] for a in alts])
    base_vac = {k: v[0] for k, v in vacias.items()}
    X0 = matriz_criterios(alts, base_vac, alinS)
    w_ref = pesos.set_index("criterio").loc[CRITERIOS, "referencia"].values.astype(float)
    w_str = pesos.set_index("criterio").loc[CRITERIOS, "stress_ssp370_2060"].values.astype(float)
    nombres = lambda s: [alts[i]["alt"] for i in s]
    costo = lambda s: float(sum(alts[i]["costo"] for i in s))

    # ---------------------------------------------------------------- 1–2. Referencia y stress test
    p_ref, p_str = X0 @ w_ref, X0 @ w_str
    if P < min(a["costo"] for a in alts if a["elegible"]):
        sys.exit(f"El presupuesto (${P:,.0f} M) no alcanza para ninguna medida. Revise la hoja Parametros.")
    sel_ref = mochila(alts, beneficio(alts, p_ref, alfa0), P, eleg)
    sel_str = mochila(alts, beneficio(alts, p_str, alfa0), P, eleg)
    entra, sale = set(nombres(sel_str)) - set(nombres(sel_ref)), set(nombres(sel_ref)) - set(nombres(sel_str))
    veredicto = "SE MANTIENE" if not entra and not sale else (
        "SE REEMPLAZA" if len(sale) > len(sel_ref) / 2 else "SE MODIFICA")
    # hasta qué peso de robustez aguanta la decisión de referencia
    otros = w_ref.copy(); otros[-1] = 0; otros = otros / otros.sum()
    aguante = []
    for r in np.round(np.arange(0, 0.61, 0.05), 2):
        w = otros * (1 - r); w[-1] = r
        s = mochila(alts, beneficio(alts, X0 @ w, alfa0), P, eleg)
        aguante.append(dict(peso_robustez=float(r), portafolio=nombres(s), igual_a_referencia=set(s) == set(sel_ref)))

    # ---------------------------------------------------------------- 3. Simulación (mitad pesos de hoy, mitad 2060)
    claves = sorted(vacias)
    F = {k: np.zeros(len(alts)) for k in ("datos", "pesos", "efectividad", "conjunta")}
    Fm = {mid: 0 for mid in med.ID}
    cuenta, B_sim, opt_sim = {}, [], []
    for t in range(N):
        w_c = w_ref if t % 2 == 0 else w_str
        vv = {k: rng.uniform() for k in claves}
        X = matriz_criterios(alts, vv, alinS)
        wr = rng.dirichlet(30 * np.clip(w_c, 1e-3, None)); ar = rng.uniform()
        for k, (XX, ww, aa) in {"datos": (X, w_c, alfa0), "pesos": (X0, wr, alfa0),
                                "efectividad": (X0, w_c, ar), "conjunta": (X, wr, ar)}.items():
            b = beneficio(alts, XX @ ww, aa)
            s = mochila(alts, b, P, eleg)
            F[k][s] += 1
            if k == "conjunta":
                key = tuple(nombres(s)); cuenta[key] = cuenta.get(key, 0) + 1
                B_sim.append(b); opt_sim.append(b[s].sum())
                for mid in {alts[i]["id"] for i in s}:
                    Fm[mid] += 1
    for k in F:
        F[k] /= N
    Fm = {k: v / N for k, v in Fm.items()}
    B_sim, opt_sim = np.array(B_sim), np.array(opt_sim)

    # ---------------------------------------------------------------- 4. Portafolio robusto (mínimo arrepentimiento)
    idx = {a["alt"]: i for i, a in enumerate(alts)}
    cands = set(cuenta) | {tuple(nombres(sel_ref)), tuple(nombres(sel_str))}
    filas = []
    for c in cands:
        ii = [idx[x] for x in c]
        reg = (opt_sim - B_sim[:, ii].sum(axis=1)) / opt_sim
        filas.append(dict(portafolio=" + ".join(c), n=len(ii), costo=costo(ii), regret_medio=reg.mean(),
                          regret_p90=np.quantile(reg, 0.9), regret_max=reg.max(), pct_casi_optimo=(reg <= 0.10).mean(),
                          veces_optimo=cuenta.get(c, 0) / N, desempate=sum(alts[i]["desempate"] for i in ii)))
    regret = pd.DataFrame(filas).sort_values(["regret_p90", "regret_medio"]).reset_index(drop=True)
    # [SUPUESTO] portafolios a ≤0,01 del mejor regret p90 son equivalentes; entre ellos se usa el desempate
    equiv = regret[regret.regret_p90 <= regret.regret_p90.min() + 0.01].sort_values(
        ["desempate", "regret_p90"], ascending=[False, True])
    sel_rob = sorted(idx[x] for x in equiv.portafolio.iloc[0].split(" + "))

    # ---------------------------------------------------------------- 5. Valor de la información
    grid = np.round(np.arange(0, 1.0001, 0.01), 2)
    ids = lambda ns: sorted(n.split("-")[0] for n in ns)
    ref_n = nombres(sel_ref)
    voi = []
    for k in claves:
        if k.endswith("Robustez 2060"):
            continue                                   # no usada con los pesos de referencia (robustez = 0)
        outs = {}
        for v in grid:
            vv = dict(base_vac); vv[k] = v
            outs[v] = nombres(mochila(alts, beneficio(alts, matriz_criterios(alts, vv, alinS) @ w_ref, alfa0), P, eleg))
        def umbral(pred):
            up = [v for v in grid if v > base_vac[k] and pred(outs[v])]
            dn = [v for v in grid if v < base_vac[k] and pred(outs[v])]
            return (float(min(up)) if up else None), (float(max(dn)) if dn else None)
        cu, cd = umbral(lambda o: ids(o) != ids(ref_n))
        lu, ld = umbral(lambda o: set(o) != set(ref_n))
        if any(x is not None for x in (cu, cd, lu, ld)):
            ej = outs[cu if cu is not None else lu if lu is not None else cd if cd is not None else ld]
            voi.append(dict(celda_vacia=k, valor_caso_base=base_vac[k], regla_caso_base=vacias[k][1],
                            cambia_QUE_si_sube_a=cu, cambia_QUE_si_baja_a=cd,
                            cambia_DONDE_si_sube_a=lu if lu != cu else None, cambia_DONDE_si_baja_a=ld if ld != cd else None,
                            portafolio_resultante=" + ".join(ej)))
    voi = pd.DataFrame(voi)

    # ---------------------------------------------------------------- 6. Contrafactuales
    b0 = beneficio(alts, p_ref, alfa0); cf = []
    def add(nombre, s, nota=""):
        cf.append(dict(caso=nombre, portafolio=" + ".join(nombres(s)), n=len(s), costo=costo(s), nota=nota))
    add("Referencia", sel_ref)
    for d in (-1000, -500, 500, 1000):
        add(f"Presupuesto {P + d:,.0f} M", mochila(alts, b0, P + d, eleg))
    add("Regla del reto: máximo de intervenciones", mochila(alts, beneficio(alts, p_ref, 0.0), P, eleg, max_intervenciones=True),
        "α=0 y prioridad al número de medidas")
    add("Equidad: ≥1 medida municipal en cada municipio", mochila(alts, b0, P, eleg, min_1_municipal=True))
    add("Sin regla de evidencia mínima", mochila(alts, b0, P, np.ones(len(alts), bool)))
    for i in sel_ref:
        add(f"Sin {alts[i]['alt']}", mochila(alts, b0, P, eleg, excluir=(alts[i]["alt"],)))
    for a_ in (0.0, 1.0):
        add(f"Efectividad α={a_:.0f}", mochila(alts, beneficio(alts, p_ref, a_), P, eleg),
            "α=0: cada medida vale igual; α=1: beneficio proporcional a la inversión")
    cf = pd.DataFrame(cf)

    # ---------------------------------------------------------------- 7. Tabla de alternativas + confianza
    rows = []
    for i, a in enumerate(alts):
        fq = F["conjunta"][i]
        # [SUPUESTO] confianza: Alta = sale en ≥60% de simulaciones y tiene dato V/CA;
        #            Media = sale en ≥30%, o tiene V y CA con dato en todos sus municipios (anclada en datos, sensible a supuestos);
        #            Baja = lo demás
        completa = a["n_datos"] >= 2 * len(a["municipios"])
        conf = "Alta" if fq >= 0.6 and a["n_datos"] > 0 else "Media" if (fq >= 0.3 or completa) else "Baja"
        rob_txt = ("Se refuerza (riesgo sube a 2060)" if any(c[0] == "dato" and c[1] == 1.0 for c in a["ROB"]) else
                   "No evaluable (sin dato 2060)" if all(c[0] == "vacia" for c in a["ROB"]) else "Estable")
        rows.append(dict(alternativa=a["alt"], medida=a["medida"], dimension=a["dimension"], territorio=a["territorio"],
                         costo_M=a["costo"], actua_sobre=a["actua_sobre"],
                         **{c: round(float(X0[i, j]), 3) for j, c in enumerate(CRITERIOS)},
                         datos_V_CA=a["n_datos"], elegible=a["elegible"],
                         puntaje_ref=round(float(p_ref[i]), 4), puntaje_2060=round(float(p_str[i]), 4),
                         en_referencia=i in sel_ref, en_2060=i in sel_str, en_robusto=i in sel_rob,
                         frec_datos=round(F["datos"][i], 3), frec_pesos=round(F["pesos"][i], 3),
                         frec_efectividad=round(F["efectividad"][i], 3), frec_conjunta=round(fq, 3),
                         confianza=conf, robustez_2060=rob_txt, cobeneficios=a["cobeneficios_txt"],
                         indicador=a["indicador"], estado_indicador=a["estado_indicador"]))
    tabla = pd.DataFrame(rows).sort_values(["en_robusto", "puntaje_ref"], ascending=False)

    # ---------------------------------------------------------------- guardar
    tabla.to_csv(os.path.join(SAL, "alternativas.csv"), index=False, encoding="utf-8-sig")
    tabla[tabla.en_robusto].to_csv(os.path.join(SAL, "portafolio_recomendado.csv"), index=False, encoding="utf-8-sig")
    regret.to_csv(os.path.join(SAL, "regret_portafolios.csv"), index=False, encoding="utf-8-sig")
    voi.to_csv(os.path.join(SAL, "datos_que_cambian_la_decision.csv"), index=False, encoding="utf-8-sig")
    cf.to_csv(os.path.join(SAL, "contrafactuales.csv"), index=False, encoding="utf-8-sig")
    pd.DataFrame([dict(celda=k, valor_caso_base=v[0], regla=v[1]) for k, v in sorted(vacias.items())]).to_csv(
        os.path.join(SAL, "celdas_vacias_usadas.csv"), index=False, encoding="utf-8-sig")
    resumen = dict(presupuesto=P, referencia=nombres(sel_ref), stress_2060=nombres(sel_str), veredicto_2060=veredicto,
                   entra_2060=sorted(entra), sale_2060=sorted(sale), robusto=nombres(sel_rob),
                   costo_robusto=costo(sel_rob), aguante_robustez=aguante, frecuencia_por_medida=Fm,
                   portafolios_equivalentes=equiv.portafolio.tolist())
    json.dump(resumen, open(os.path.join(SAL, "resumen.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # ---------------------------------------------------------------- pantalla
    L = "=" * 86
    print(L + "\n PASO 3 · MOTOR DE DECISIÓN\n" + L)
    print(f"\nAlternativas: {len(alts)} (15 medidas × municipio o corredor) · compiten (regla de evidencia): {eleg.sum()}")
    print(f"Celdas vacías usadas por el modelo: {len(vacias)} · simulaciones: {N}")
    cols = ["alternativa", "territorio", "costo_M"] + CRITERIOS[:-1] + ["puntaje_ref", "frec_conjunta", "en_robusto"]
    print("\n1) Las 15 mejores alternativas por puntaje de referencia")
    print(tabla.sort_values("puntaje_ref", ascending=False)[cols].head(15).to_string(index=False))

    def mostrar(titulo, s):
        print(f"\n{titulo}")
        for i in s:
            a = alts[i]
            print(f"   {a['alt']:8s} {a['territorio']:10s} ${a['costo']:>6,.0f} M  {a['medida'][:62]}")
        print(f"   {'TOTAL':8s} {'':10s} ${costo(s):>6,.0f} M  de ${P:,.0f} M  "
              f"({'OK, dentro del presupuesto' if costo(s) <= P else 'EXCEDE'}) · {len(s)} intervenciones")
    mostrar("2) Portafolio de REFERENCIA (clima de hoy)", sel_ref)
    mostrar("3) Portafolio STRESS TEST SSP3-7.0/2060 (robustez 25%)", sel_str)
    print(f"   → Veredicto: {veredicto}" + (f" · entra {sorted(entra)} · sale {sorted(sale)}" if entra or sale else ""))
    lim = [x["peso_robustez"] for x in aguante if not x["igual_a_referencia"]]
    print(f"   → La decisión de referencia se mantiene hasta un peso de robustez de "
          f"{(min(lim) - 0.05) * 100:.0f}%" if lim else "   → Se mantiene con cualquier peso de robustez hasta 60%")
    mostrar("4) Portafolio ROBUSTO recomendado (mínimo arrepentimiento en 3.000 escenarios)", sel_rob)
    print("\n   Portafolios casi equivalentes (regret p90 a ≤0,01 del mejor; ◄ = elegido por la regla de desempate):")
    elegido = equiv.portafolio.iloc[0]
    for r in equiv.sort_values("regret_p90").itertuples():
        print(f"     regret p90 {r.regret_p90:.3f} · casi óptimo en {r.pct_casi_optimo:.0%} de escenarios · {r.portafolio}"
              + ("  ◄" if r.portafolio == elegido else ""))
    print("\n5) ¿Qué tan seguido sale cada MEDIDA en el portafolio óptimo? (simulación conjunta)")
    for mid, f_ in sorted(Fm.items(), key=lambda kv: -kv[1]):
        nombre = med[med.ID == mid].Medida.iloc[0]
        etiqueta = "estable" if f_ >= 0.6 else "sensible" if f_ >= 0.2 else "marginal" if f_ > 0 else "nunca"
        print(f"   {mid} {f_:>5.0%}  {etiqueta:9s} {nombre[:60]}")
    print("\n6) Datos vacíos que cambiarían la decisión (valor de la información)")
    if len(voi):
        for r in voi.itertuples():
            partes = []
            ok = lambda x: x is not None and not pd.isna(x)
            if ok(r.cambia_QUE_si_sube_a): partes.append(f"cambia QUÉ medidas si sube a ≥{r.cambia_QUE_si_sube_a:.2f}")
            if ok(r.cambia_QUE_si_baja_a): partes.append(f"cambia QUÉ medidas si baja a ≤{r.cambia_QUE_si_baja_a:.2f}")
            if ok(r.cambia_DONDE_si_sube_a): partes.append(f"cambia DÓNDE si sube a ≥{r.cambia_DONDE_si_sube_a:.2f}")
            if ok(r.cambia_DONDE_si_baja_a): partes.append(f"cambia DÓNDE si baja a ≤{r.cambia_DONDE_si_baja_a:.2f}")
            print(f"   {r.celda_vacia:52s} (hoy {r.valor_caso_base:.2f}): {'; '.join(partes)}")
    else:
        print("   Ninguno: la decisión no cambia con ningún valor de las celdas vacías")
    print("\n7) Contrafactuales")
    for r in cf.itertuples():
        print(f"   {r.caso:48s} ${r.costo:>6,.0f} M  {r.portafolio}")
    print(f"\nOK · resultados en {os.path.relpath(SAL, AQUI)}/  → siguiente paso: python 3_reportes.py")


if __name__ == "__main__":
    main()
