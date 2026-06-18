#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#*====================================================================================================================
#* sem_solver.py
#* Programa para resolver ecuaciones estructurales SEM
#*
#* python sem_solver.py \
#*   --csv semdata.csv \
#*   --defects_col defects \
#*   --coverage_col coverage \
#*   --maturity m1_ci_defects_per_size m2_effort_hours_per_size m3_qa_obs_per_size \
#*   --log_defects \
#*   --out_prefix sem_solver
#*
#*====================================================================================================================
#* Pre-requisitos y ambiente virtual de ejecución
#*
#* 	python -m venv ufasta                      # Crea ambiente virtual ufasta
#* 	source ./ufasta/bin/activate               # Activa ambiente virtual
#* 	pip install semopy pandas numpy scipy      # Instala pre-requisitos en ambiente virtual
#*
#*====================================================================================================================
#*
#* Calidad de Software FIM481
#*
#* Copyright Dr. Pedro E. Colla (2025,2026)   
#*
#* License: MIT
#*
#*====================================================================================================================
import argparse
import numpy as np
import pandas as pd
from scipy.stats import chi2

from semopy import Model, calc_stats


def build_specs(maturity_inds, use_direct_path: bool):
    """
    maturity_inds: list of indicator column names for latent M.
    """
    if len(maturity_inds) < 3:
        raise ValueError("Recomendado: al menos 3 indicadores para identificar  la variable latente Madurez.")

    meas = "M =~ " + " + ".join(maturity_inds)

    # Modelo estructural: coverage depende de madurez
    # Defectos dependen de madurez; opcionalmente de coverage (efecto directo)

    if use_direct_path:
        struct = """
        coverage ~ M
        defects  ~ M + coverage
        """
    else:
        struct = """
        coverage ~ M
        defects  ~ M
        """

    return f"""
    # Measurement (CFA)
    {meas}

    # Structural
    {struct}
    """



import time

def fit_model(df, spec, label="Model"):
    print(f"\n[{label}] Construyendo modelo...")
    model = Model(spec)

    print(f"[{label}] Iniciando optimización ML...")
    t0 = time.time()

    res = model.fit(df)

    t1 = time.time()
    print(f"[{label}] Optimización finalizada en {t1 - t0:.2f} segundos")

    print(f"[{label}] Extrayendo parámetros...")
    est = model.inspect(std_est=True)

    print(f"[{label}] Calculando fit statistics...")
    #stats = calc_stats(model, df)
    stats = calc_stats(model)
    
    print(f"[{label}] Listo.\n")

    return model, est, stats
def pick_fit(stats):
    cols = stats.columns
    def get(name):
        return float(stats.loc["Value", name]) if name in cols else None

    return {
        "DoF": get("DoF"),
        "chi2": get("chi2"),
        "p": get("chi2 p-value"),
        "CFI": get("CFI"),
        "TLI": get("TLI"),
        "RMSEA": get("RMSEA"),
        "SRMR": get("SRMR"),
        "AIC": get("AIC"),
        "BIC": get("BIC"),
    }


from scipy.stats import chi2

def lr_test(fit_restricted, fit_full):
    chi2_r, df_r = fit_restricted["chi2"], fit_restricted["DoF"]
    chi2_f, df_f = fit_full["chi2"], fit_full["DoF"]

    if None in (chi2_r, df_r, chi2_f, df_f):
        return {"ok": False, "reason": "Faltan chi2/DoF"}

    dchi2 = chi2_r - chi2_f
    ddf = df_r - df_f

    if ddf <= 0:
        return {"ok": False, "reason": f"ddf<=0 (ddf={ddf})"}

    if dchi2 < 0:
        return {
            "ok": False,
            "reason": "dchi2<0; estadísticos no comparables / modelo no anidado / ajuste inadmisible",
            "dchi2": dchi2,
            "ddf": ddf,
            "chi2_restricted": chi2_r,
            "chi2_full": chi2_f,
        }

    pval = 1.0 - chi2.cdf(dchi2, ddf)
    return {"ok": True, "dchi2": dchi2, "ddf": ddf, "p": pval}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True, help="Archivo CSV con defects, coverage e indicadores de madurez.")
    ap.add_argument("--sep", default=",")
    ap.add_argument("--defects_col", default="defects")
    ap.add_argument("--coverage_col", default="coverage")
    ap.add_argument("--maturity", nargs="+", required=True, help="Columnas indicadores de Madurez, ej: m1 m2 m3 m4")
    ap.add_argument("--log_defects", action="store_true", help="Usa log1p(defects) para aproximar normalidad.")
    ap.add_argument("--out_prefix", default="sem_out")
    args = ap.parse_args()

    df = pd.read_csv(args.csv, sep=args.sep).copy()

    # Renombrar a nombres usados por el modelo
    if args.defects_col not in df.columns or args.coverage_col not in df.columns:
        raise SystemExit("No encuentro defects_col o coverage_col en el CSV.")
    for c in args.maturity:
        if c not in df.columns:
            raise SystemExit(f"No encuentro indicador de madurez: {c}")

    df = df.rename(columns={args.defects_col: "defects", args.coverage_col: "coverage"})

    # Transformación sugerida si defects son conteos sesgados
    if args.log_defects:
        df["defects"] = np.log1p(df["defects"])

    # Filtrar a columnas necesarias y asegurar numéricas
    cols = ["defects", "coverage"] + args.maturity
    df = df[cols].dropna()
    for c in cols:
        df[c] = pd.to_numeric(df[c], errors="raise")

    # Specs
    spec_full = build_specs(args.maturity, use_direct_path=True)   # Modelo A
    spec_rest = build_specs(args.maturity, use_direct_path=False)  # Modelo B (beta=0)

    print("\n=== Modelo A (con efecto directo coverage -> defects) ===")
    print(spec_full.strip())

    #modelA, estA, statsA = fit_model(df, spec_full)
    modelA, estA, statsA = fit_model(df, spec_full, label="Modelo A")
    
    fitA = pick_fit(statsA)

    print("\nFit A:", fitA)
    print("\nParámetros A (std_est=True):")
    print(estA)

    print("\n=== Modelo B (SIN efecto directo; defects depende solo de Madurez) ===")
    print(spec_rest.strip())

    #modelB, estB, statsB = fit_model(df, spec_rest)
    modelB, estB, statsB = fit_model(df, spec_rest, label="Modelo B")

    fitB = pick_fit(statsB)

    print("\nFit B:", fitB)
    print("\nParámetros B (std_est=True):")
    print(estB)

    # Test anidado (si aplica)

    lrt = lr_test(fit_restricted=fitB, fit_full=fitA)

    if lrt is None:
       print("\n[i] No pude calcular LRT.")
    else:
       if lrt.get("ok", False):
          print("\n=== Likelihood Ratio Test (B vs A) ===")
          print(lrt)
          if lrt["p"] > 0.05:
             print("Interpretación: no hay evidencia fuerte de que el efecto directo sea necesario (preferible Modelo B).")
          else:
             print("Interpretación: el efecto directo coverage->defects mejora el ajuste (preferible Modelo A).")
       else:
          print("\n[i] LRT no válido para estos modelos/estadísticos.")
          print("Motivo:", lrt.get("reason"))
          # Igual mostramos info útil si está
          for k in ("dchi2", "ddf", "chi2_restricted", "chi2_full"):
              if k in lrt:
                 print(f"{k}: {lrt[k]}")
          print("Sugerencia: comparar AIC/BIC y el p-value del path defects ~ coverage en Modelo A.")



    # Export

    estA.to_csv(f"{args.out_prefix}_A_params.csv", index=False)
    estB.to_csv(f"{args.out_prefix}_B_params.csv", index=False)
    pd.DataFrame([fitA]).to_csv(f"{args.out_prefix}_A_fit.csv", index=False)
    pd.DataFrame([fitB]).to_csv(f"{args.out_prefix}_B_fit.csv", index=False)

    print(f"\n[i] Exportados: {args.out_prefix}_A_params.csv, {args.out_prefix}_B_params.csv, fit csvs.")


if __name__ == "__main__":
    main()
