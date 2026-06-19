#!/usr/usr/bin/env python3
"""
Analyze Figure 4 Hotspots:
Identifies regions in (q, chi_eff) parameter space where the (2,2) mismatch
is consistently highest across different NR catalogs.
"""

import argparse
import os
import sys
import pandas as pd
import numpy as np


def main(csv_path: str):
    if not os.path.exists(csv_path):
        print(f"Error: Could not find results CSV at {csv_path}")
        sys.exit(1)

    df = pd.read_csv(csv_path)

    # Filter for quasi-circular systems
    df_qc = df[df["eccentricity"] < 1e-3].copy()
    if len(df_qc) == 0:
        print("Error: No quasi-circular simulations found.")
        sys.exit(1)

    # Compute mismatch (1 - F)
    df_qc["mismatch_22"] = 1.0 - df_qc["match_22"]

    # Define bins
    q_bins = np.linspace(1.0, 4.0, 7)  # 6 bins
    chi_eff_bins = np.linspace(-1.0, 1.0, 9)  # 8 bins

    print("=== Parameter Space Hotspot Analysis (q vs chi_eff) ===")

    for catalog in ["SXS", "RIT", "MAYA"]:
        df_cat = df_qc[df_qc["catalog"] == catalog]
        if len(df_cat) == 0:
            continue

        # Bin the data
        df_cat["q_bin"] = pd.cut(df_cat["q"], bins=q_bins)
        df_cat["chi_bin"] = pd.cut(df_cat["chi_eff"], bins=chi_eff_bins)

        # Compute mean mismatch per bin
        heatmap = (
            df_cat.groupby(["q_bin", "chi_bin"])["mismatch_22"]
            .agg(["mean", "count"])
            .dropna()
        )

        if len(heatmap) == 0:
            continue

        # Find the top 3 hotspots with at least 2 simulations
        valid_bins = heatmap[heatmap["count"] >= 2]
        if len(valid_bins) > 0:
            hotspots = valid_bins.sort_values(by="mean", ascending=False).head(3)
            print(f"\nCatalog: {catalog} (N={len(df_cat)})")
            for index, row in hotspots.iterrows():
                q_range = index[0]
                chi_range = index[1]
                print(
                    f"  q in {q_range}, chi_eff in {chi_range} -> Mean Mismatch: {row['mean']:.4e} (N={int(row['count'])})"
                )
        else:
            print(f"\nCatalog: {catalog} (N={len(df_cat)})")
            print("  No bins with >= 2 simulations to evaluate.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Identify parameter space hotspots.")
    parser.add_argument(
        "--csv",
        default="../results/batch_aligned_all.csv",
        help="Path to batch results CSV.",
    )
    args = parser.parse_args()

    # Ensure correct path resolution relative to script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_abs = os.path.join(script_dir, args.csv)

    main(csv_abs)
