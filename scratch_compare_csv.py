import pandas as pd

df_sur = (
    pd.read_csv("project/results/batch_aligned_all.csv")
    if "all" in str(pd.read_csv("project/results/batch_aligned_sxs.csv"))
    else pd.read_csv("project/results/batch_aligned_sxs.csv")
)
df_seo = pd.read_csv("project/results_seobnrv4phm/batch_aligned_all.csv")

print("Surrogate results count (SXS):", len(df_sur[df_sur["catalog"] == "SXS"]))
print("SEOBNRv4PHM results count (SXS):", len(df_seo[df_seo["catalog"] == "SXS"]))

# check mismatches > 0.1 at q ~ 4 for Surrogate
sur_sxs = df_sur[df_sur["catalog"] == "SXS"].copy()
sur_sxs["mismatch_22"] = 1 - sur_sxs["match_22"]
high_mm = sur_sxs[(sur_sxs["q"] > 3.5) & (sur_sxs["mismatch_22"] > 0.05)]
print("\nSXS sims with high mismatch vs surrogate near q=4:")
print(high_mm[["sim_id", "q", "mismatch_22"]])

print("\nStatus of these sims in SEOBNRv4PHM results:")
seo_sxs = df_seo[df_seo["catalog"] == "SXS"].copy()
for sid in high_mm["sim_id"]:
    row = seo_sxs[seo_sxs["sim_id"] == sid]
    if len(row) == 0:
        print(f"{sid}: NOT FOUND")
    else:
        err = row["error"].iloc[0]
        match = row["match_22"].iloc[0]
        print(f"{sid}: Match={match}, Error={err}")

print("\nOther catalogs in SEOBNRv4PHM:")
print(df_seo["catalog"].value_counts())
