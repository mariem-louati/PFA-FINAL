"""
vente.py — Script unifié
Génère : CSV + 3 graphiques PNG + dashboard_data.json + search_data.json
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import Patch
import json, time, os, subprocess, platform

# ==============================
#  CONFIGURATION
# ==============================
NB_LIGNES    = 500_000
NB_BUCKETS   = 60
SEED         = 42
OUTPUT_CSV   = "resultats_final.csv"
OUTPUT_JSON  = "dashboard_data.json"
OUTPUT_SEARCH= "search_data.json"
GRAPH_BARRES = "graph_barres_test.png"
GRAPH_TRANCHES="graph_tranches_test.png"
GRAPH_CERCLE = "graph_cercle_test.png"

def etape(msg):
    print(f"\n⏳ {msg}", flush=True)
    return time.time()

def ok(t0, extra=""):
    print(f"   ✔ Fait en {time.time()-t0:.2f}s{' — '+extra if extra else ''}", flush=True)

# ==============================
#  1. GÉNÉRATION DES DONNÉES
# ==============================
t = etape(f"Génération de {NB_LIGNES:,} produits (seed={SEED})...")
rng      = np.random.default_rng(seed=SEED)
prix     = np.round(rng.uniform(5, 100, NB_LIGNES), 2)
quantite = rng.integers(1, 11, NB_LIGNES)
remise   = rng.choice([0, 5, 10, 15, 20, 25, 30, 35, 40], NB_LIGNES)
ca_brut  = prix * quantite
ca_net   = np.round(ca_brut * (1 - remise / 100), 2)

df = pd.DataFrame({
    "ID":      np.arange(1, NB_LIGNES + 1),
    "Prix":    prix,
    "Quantite":quantite,
    "Remise":  remise,
    "CA_Brut": ca_brut,
    "CA_Net":  ca_net,
    "TVA":     np.round(ca_net * 0.20, 2),
})
ok(t, f"{NB_LIGNES:,} lignes")

# ==============================
#  2. ANALYSE — SOURCE UNIQUE
# ==============================
# Tri une seule fois → toutes les sections utilisent ce même tri
df_sorted    = df[["ID","CA_Net"]].sort_values("CA_Net", ascending=False).reset_index(drop=True)

# Meilleur et moins bon — tirés du même df_sorted
BEST_ID      = int(df_sorted.iloc[0]["ID"])
BEST_CA      = float(df_sorted.iloc[0]["CA_Net"])
WORST_ID     = int(df_sorted.iloc[-1]["ID"])
WORST_CA     = float(df_sorted.iloc[-1]["CA_Net"])

ca_total     = float(df["CA_Net"].sum())
ca_moyen     = float(df["CA_Net"].mean())
percentiles  = df["CA_Net"].quantile([0.25, 0.5, 0.75])

print(f"\n📊 CA Total  = {ca_total:,.2f} €")
print(f"   CA Moyen  = {ca_moyen:.2f} €")
print(f"   Meilleur  : ID {BEST_ID} → {BEST_CA:.2f} €")
print(f"   Moins bon : ID {WORST_ID} → {WORST_CA:.2f} €")

# ==============================
#  3. EXPORT CSV
# ==============================
t = etape(f"Export CSV...")
df.to_csv(OUTPUT_CSV, index=False)
ok(t, f"{OUTPUT_CSV}")

# ==============================
#  4. GRAPHIQUE BARRES (imshow)
# ==============================
t = etape("Graphique barres...")
vals      = df.sort_values("ID")["CA_Net"].values
val_min   = float(df_sorted.iloc[-1]["CA_Net"])
val_range = BEST_CA - val_min if BEST_CA != val_min else 1.0
heights   = ((vals - val_min) / val_range * 99).astype(int).clip(0, 99)
IMG_H     = 100
n         = NB_LIGNES
img       = np.ones((IMG_H, n, 3), dtype=np.uint8) * 245
c_std     = np.array([31, 119, 180], dtype=np.uint8)
c_best    = np.array([214, 39, 33],  dtype=np.uint8)
c_neg     = np.array([255, 152, 150],dtype=np.uint8)
for i, (val, h) in enumerate(zip(vals, heights)):
    c = c_best if val == BEST_CA else (c_neg if val < 0 else c_std)
    img[IMG_H - h - 1: IMG_H, i] = c

fig, ax = plt.subplots(figsize=(24, 8))
ax.imshow(img, aspect="auto", interpolation="nearest", extent=[0, n, val_min, BEST_CA])
ax.axhline(0, color="black", linewidth=1.2, zorder=3)
idx_best = int(np.argmax(vals))
ax.annotate(
    f"★ Meilleur : ID {BEST_ID}\n{BEST_CA:,.2f} €",
    xy=(idx_best, BEST_CA),
    xytext=(idx_best + n * 0.05, BEST_CA * 0.80),
    fontsize=14, color="#D62728", fontweight="bold",
    arrowprops=dict(arrowstyle="->", color="#D62728", lw=2),
)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda y,_: f"{int(y):,} €".replace(",", " ")))
ax.set_title(f"CA Net par produit — {n:,} produits", fontsize=20, fontweight="bold", pad=20)
ax.set_xlabel("ID Produit (ordre croissant)", fontsize=14, labelpad=10)
ax.set_ylabel("CA Net (€)", fontsize=14, labelpad=10)
ax.legend(handles=[
    Patch(color="#D62728", label=f"Meilleur (ID {BEST_ID})"),
    Patch(color="#1F77B4", label="CA Net positif"),
    Patch(color="#FF9896", label="CA Net négatif"),
], loc="upper right", fontsize=12, framealpha=0.9)
plt.tight_layout()
plt.savefig(GRAPH_BARRES, dpi=100, bbox_inches="tight")
plt.close()
ok(t, GRAPH_BARRES)

# ==============================
#  5. GRAPHIQUE CIRCULAIRE TRANCHES
# ==============================
t = etape("Graphique circulaire — tranches...")
others_pie = df_sorted.iloc[1:].copy()
others_pie["bucket"] = pd.cut(others_pie["CA_Net"], bins=NB_BUCKETS, labels=False, include_lowest=True)
blabels, bvalues = [], []
for b, grp in others_pie.groupby("bucket", observed=True):
    lo, hi = float(grp["CA_Net"].min()), float(grp["CA_Net"].max())
    blabels.append(f"{lo:.0f}–{hi:.0f}€ ({len(grp):,})")
    bvalues.append(float(grp["CA_Net"].sum()))
blabels.reverse(); bvalues.reverse()
nb_t = len(bvalues)

def tc(i, total):
    t2 = i / max(total-1, 1)
    if t2 < 0.2: return "#4f8ef7"
    if t2 < 0.4: return "#4fd1c5"
    if t2 < 0.6: return "#3ecf8e"
    if t2 < 0.8: return "#f5874f"
    return "#e05252"

colors  = ["#f5c842"] + [tc(i, nb_t) for i in range(nb_t)]
values  = [BEST_CA]   + bvalues
explode = [0.06]      + [0.015] * nb_t

fig, ax = plt.subplots(figsize=(22, 22))
wedges, _, autotexts = ax.pie(
    values, labels=None,
    autopct=lambda p: f"{p:.2f}%" if p > 1.5 else "",
    startangle=90, colors=colors, explode=explode,
    pctdistance=0.80, wedgeprops=dict(linewidth=1.2, edgecolor="white"),
)
for at in autotexts:
    at.set_fontsize(11); at.set_fontweight("bold"); at.set_color("white")

ang  = np.deg2rad((wedges[0].theta1 + wedges[0].theta2) / 2)
ax.annotate(
    f"★ ID {BEST_ID}\n{BEST_CA:,.2f} €",
    xy=(np.cos(ang)*0.95, np.sin(ang)*0.95),
    xytext=(np.cos(ang)*1.35, np.sin(ang)*1.35),
    fontsize=16, color="#f5c842", fontweight="bold",
    arrowprops=dict(arrowstyle="->", color="#f5c842", lw=2),
    bbox=dict(boxstyle="round,pad=0.3", fc="#1a1a2e", ec="#f5c842", lw=1.5),
)
ax.legend(handles=[
    Patch(color="#f5c842", label=f"★ Meilleur — ID {BEST_ID} ({BEST_CA:,.2f} €)"),
    Patch(color="#4f8ef7", label="Tranches haute valeur"),
    Patch(color="#3ecf8e", label="Tranches valeur moyenne"),
    Patch(color="#e05252", label="Tranches basse valeur"),
], title="Légende", title_fontsize=18, fontsize=15,
   loc="upper left", bbox_to_anchor=(-0.3, 1.05), framealpha=0.95)
ax.set_title(
    f"Répartition CA Net — {NB_LIGNES:,} produits en {NB_BUCKETS} tranches\n"
    f"Total : {ca_total:,.0f} €  |  Meilleur : ID {BEST_ID} ({BEST_CA:,.2f} €)",
    fontsize=26, fontweight="bold", pad=35,
)
ax.axis("equal")
plt.tight_layout()
plt.savefig(GRAPH_TRANCHES, dpi=150, bbox_inches="tight")
plt.close()
ok(t, GRAPH_TRANCHES)

# ==============================
#  6. GRAPHIQUE CIRCULAIRE REMISE
# ==============================
t = etape("Graphique circulaire — remises...")
rg     = df.groupby("Remise")["CA_Net"].sum().sort_values(ascending=False)
total_r= float(rg.sum())
palette= ["#1F77B4","#D62728","#2CA02C","#FF7F0E","#9467BD","#8C564B","#E377C2","#7F7F7F","#BCBD22"]
fig, ax= plt.subplots(figsize=(18, 18))
wedges, _, autotexts = ax.pie(
    rg, labels=None,
    autopct=lambda p: f"{p:.1f}%\n({p/100*total_r:,.0f} €)",
    startangle=90, colors=palette[:len(rg)],
    explode=[0.03]*len(rg), pctdistance=0.72,
    wedgeprops=dict(linewidth=2, edgecolor="white"),
)
for at in autotexts:
    at.set_fontsize(16); at.set_fontweight("bold"); at.set_color("white")
ax.legend(wedges,
    [f"Remise {int(r)}%  —  {v:,.0f} €  ({v/total_r*100:.1f}%)" for r,v in rg.items()],
    title="Taux de remise", title_fontsize=20, fontsize=17,
    loc="upper left", bbox_to_anchor=(-0.35, 1.05), framealpha=0.95)
ax.set_title(f"Répartition CA Net par remise\nTotal : {total_r:,.0f} €", fontsize=28, fontweight="bold", pad=30)
ax.axis("equal")
plt.tight_layout()
plt.savefig(GRAPH_CERCLE, dpi=150, bbox_inches="tight")
plt.close()
ok(t, GRAPH_CERCLE)

# ==============================
#  7. EXPORT JSON DASHBOARD
# ==============================
t = etape("Export JSON dashboard...")

# Tranches pour le dashboard — même logique que graphe
others_dash = df_sorted.iloc[1:].copy()
others_dash["bucket"] = pd.cut(others_dash["CA_Net"], bins=NB_BUCKETS, labels=False, include_lowest=True)
buckets = []
for b, grp in others_dash.groupby("bucket", observed=True):
    lo, hi = float(grp["CA_Net"].min()), float(grp["CA_Net"].max())
    buckets.append({
        "label":  f"{lo:.0f}EUR - {hi:.0f}EUR",
        "ca_sum": round(float(grp["CA_Net"].sum()), 2),
        "count":  int(len(grp)),
        "ca_min": round(lo, 2),
        "ca_max": round(hi, 2),
    })
buckets.sort(key=lambda x: x["ca_min"])

# JSON principal (léger)
payload = {
    "meta": {
        "nb_produits": NB_LIGNES,
        "ca_total":    round(ca_total, 2),
        "ca_moyen":    round(ca_moyen, 2),
        "ca_max":      round(BEST_CA, 2),
        "ca_min":      round(WORST_CA, 2),
        "id_best":     BEST_ID,
        "id_worst":    WORST_ID,
        "p25":         round(float(percentiles[0.25]), 2),
        "p50":         round(float(percentiles[0.50]), 2),
        "p75":         round(float(percentiles[0.75]), 2),
        "nb_buckets":  NB_BUCKETS,
    },
    "best":    {"id": BEST_ID, "ca": round(BEST_CA, 2)},
    "buckets": buckets,
}
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(payload, f, separators=(",", ":"))
ok(t, f"{OUTPUT_JSON} ({os.path.getsize(OUTPUT_JSON)/1e6:.1f} MB)")

# JSON recherche (chargé à la demande)
t = etape("Export JSON recherche...")
with open(OUTPUT_SEARCH, "w", encoding="utf-8") as f:
    json.dump({"all": [[int(r.ID), float(r.CA_Net)] for r in df_sorted.itertuples(index=False)]},
              f, separators=(",", ":"))
ok(t, f"{OUTPUT_SEARCH} ({os.path.getsize(OUTPUT_SEARCH)/1e6:.1f} MB)")

# ==============================
#  RÉSUMÉ + OUVERTURE GRAPHES
# ==============================
print("\n" + "="*52)
print(f"  ✅ Tout généré — Meilleur : ID {BEST_ID} ({BEST_CA:.2f} €)")
print(f"     {OUTPUT_CSV}  |  {OUTPUT_JSON}")
print(f"     {GRAPH_BARRES}")
print(f"     {GRAPH_TRANCHES}")
print(f"     {GRAPH_CERCLE}")
print("="*52)

def open_file(path):
    try:
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception as e:
        print(f"  ⚠ Impossible d'ouvrir {path} : {e}")

print("\n🖼  Ouverture des graphiques...")
open_file(GRAPH_BARRES)
open_file(GRAPH_TRANCHES)
open_file(GRAPH_CERCLE)
print("   Les 3 graphiques s'ouvrent dans votre visionneuse.")