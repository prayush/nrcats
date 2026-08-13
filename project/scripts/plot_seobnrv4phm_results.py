#!/usr/bin/env python
import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def main():
    parser = argparse.ArgumentParser(description="Plot SEOBNRv4PHM match results")
    parser.add_argument("--csv", default="../results_seobnrv4phm/batch_aligned_all.csv")
    parser.add_argument("--outdir", default="../figs")
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    df = pd.read_csv(args.csv)

    # Filter for quasi-circular (categories b, d) to analyze the q~4 hotspot
    df_qc = df[df["category"].isin(["b", "d"])]

    if not df_qc.empty:
        plt.figure(figsize=(10, 6))
        sns.scatterplot(
            data=df_qc,
            x="q",
            y="match_22",
            hue="catalog",
            style="catalog",
            alpha=0.7,
            s=50,
        )
        plt.yscale("log")
        # Invert y-axis for mismatch representation if desired, or just plot mismatch
        plt.gca().invert_yaxis()
        plt.ylabel("1 - Match (2,2)")  # Actually this is match, let's plot mismatch
        plt.close()

        plt.figure(figsize=(10, 6))
        df_qc["mismatch_22"] = 1 - df_qc["match_22"]
        sns.scatterplot(
            data=df_qc,
            x="q",
            y="mismatch_22",
            hue="catalog",
            style="catalog",
            alpha=0.7,
            s=50,
        )
        plt.yscale("log")
        plt.ylabel("Mismatch (2,2) with SEOBNRv4PHM")
        plt.xlabel("Mass Ratio (q)")
        plt.title("SEOBNRv4PHM Mismatch vs Mass Ratio (Quasi-Circular)")
        plt.grid(True, which="both", ls="--", alpha=0.5)
        plt.tight_layout()
        plt.savefig(os.path.join(args.outdir, "seobnrv4phm_mismatch_vs_q.png"))
        print("Saved seobnrv4phm_mismatch_vs_q.png")

    # Plot eccentricity dependence for category 'a', 'c'
    df_ecc = df[df["category"].isin(["a", "c"])]
    if not df_ecc.empty:
        plt.figure(figsize=(10, 6))
        df_ecc["mismatch_22"] = 1 - df_ecc["match_22"]
        sns.scatterplot(
            data=df_ecc,
            x="eccentricity",
            y="mismatch_22",
            hue="catalog",
            style="catalog",
            alpha=0.7,
            s=50,
        )
        plt.xscale("log")
        plt.yscale("log")
        plt.ylabel("Mismatch (2,2) with SEOBNRv4PHM")
        plt.xlabel("Eccentricity")
        plt.title("SEOBNRv4PHM Mismatch vs Eccentricity")
        plt.grid(True, which="both", ls="--", alpha=0.5)
        plt.tight_layout()
        plt.savefig(os.path.join(args.outdir, "seobnrv4phm_mismatch_vs_ecc.png"))
        print("Saved seobnrv4phm_mismatch_vs_ecc.png")


if __name__ == "__main__":
    main()
