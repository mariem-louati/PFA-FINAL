"""
vente.py  —  Script unifié : données + 2 graphes circulaires + JSON dashboard
  • graph_barres_test.png  → tous les 500 000 produits regroupés en tranches de CA Net
  • graph_cercle_test.png  → répartition du CA Net par taux de remise
  • dashboard_data.json    → données pour le dashboard HTML interactif
  • resultats_final.csv    → export brut de tous les produits
"""
# ==============================
#  IMPORTS
# ==============================
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")          # rendu fichier, sans fenêtre GUI
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import Patch
import json, time, os, sys

# ==============================
#  CONFIGURATION
# ==============================
NB_LIGNES    = 500_000   # nombre de produits à simuler
NB_BUCKETS   = 60        # tranches pour les deux graphes circulaires
OUTPUT_CSV     = "resultats_final.csv"
OUTPUT_JSON    = "dashboard_data.json"
GRAPH_BARRES   = "graph_barres_test.png"    # barres  — 1 barre par produit
GRAPH_TRANCHES = "graph_tranches_test.png"  # circulaire — 500k produits en tranches
GRAPH_CERCLE   = "graph_cercle_test.png"    # circulaire — par taux de remise

# ==============================
#  CHRONO HELPER
# ==============================
def etape(msg):
    print(f"\n⏳ {msg}", flush=True)
    return time.time()

def ok(t0, extra=""):
    print(f"   ✔ Fait en {time.time()-t0:.2f}s{' — ' + extra if extra else ''}", flush=True)

# ==============================
#  1. GÉNÉRATION DES DONNÉES
# ==============================
t = etape(f"Génération de {NB_LIGNES:,} produits...")
rng = np.random.default_rng(seed=42)

ids       = np.arange(1, NB_LIGNES + 1)
prix      = np.round(rng.uniform(5, 100, NB_LIGNES), 2)
quantite  = rng.integers(1, 11, NB_LIGNES)
remise    = rng.choice([0, 5, 10, 15, 20, 25, 30, 35, 40], NB_LIGNES)

ca_brut = prix * quantite
ca_net  = np.round(ca_brut * (1 - remise / 100), 4)
tva     = np.round(ca_net * 0.20, 4)

df = pd.DataFrame({
    "ID":       ids,
    "Prix":     prix,
    "Quantite": quantite,
    "Remise":   remise,
    "CA_Brut":  ca_brut,
    "CA_Net":   ca_net,
    "TVA":      tva,
})
ok(t, f"{NB_LIGNES:,} lignes")

# ==============================
#  2. ANALYSE STATISTIQUE
# ==============================
ca_total   = float(df["CA_Net"].sum())
ca_moyen   = float(df["CA_Net"].mean())
idx_max    = int(df["CA_Net"].idxmax())
idx_min    = int(df["CA_Net"].idxmin())
meilleur   = df.loc[idx_max]
moins_bon  = df.loc[idx_min]
percentiles = df["CA_Net"].quantile([0.25, 0.5, 0.75])

print(f"\n📊 CA Total  = {ca_total:,.2f} €")
print(f"   CA Moyen  = {ca_moyen:.2f} €")
print(f"   Meilleur  : ID {int(meilleur['ID'])} → {meilleur['CA_Net']:.2f} €")
print(f"   Moins bon : ID {int(moins_bon['ID'])} → {moins_bon['CA_Net']:.2f} €")

# ==============================
#  3. EXPORT CSV
# ==============================
t = etape(f"Export CSV → {OUTPUT_CSV}")
df.to_csv(OUTPUT_CSV, index=False)
ok(t, f"{NB_LIGNES:,} lignes")

# ==============================
#  4. GRAPHIQUE EN BARRES
#     → 1 barre par produit
#     → rouge = meilleur produit (CA Net le plus élevé)
# ==============================
t = etape("Graphique en barres (500 000 produits)...")

# ── Stratégie : tracer avec matplotlib en mode raster vectoriel ──────
# On utilise imshow sur un tableau numpy au lieu de ax.bar()
# → génère exactement 500 000 colonnes colorées en quelques secondes
# → taille PNG fixe ~200 Ko, indépendante du nombre de produits

n = len(df)
val_max  = float(meilleur["CA_Net"])
val_min  = float(df["CA_Net"].min())
vals     = df.sort_values("ID")["CA_Net"].values   # ordre ID croissant

# Normaliser les valeurs entre 0 et 1 pour la hauteur des barres
val_range = val_max - val_min if val_max != val_min else 1.0
heights   = ((vals - val_min) / val_range * 99).astype(int).clip(0, 99)  # 0..99

# Image : hauteur=100px, largeur=n px (1px par produit)
# Fond blanc, barres colorées depuis le bas
IMG_H = 100
img   = np.ones((IMG_H, n, 3), dtype=np.uint8) * 245  # fond gris clair

color_std  = np.array([31,  119, 180], dtype=np.uint8)   # bleu
color_best = np.array([214,  39,  33], dtype=np.uint8)   # rouge
color_neg  = np.array([255, 152, 150], dtype=np.uint8)   # rose

for i, (val, h) in enumerate(zip(vals, heights)):
    c = color_best if val == val_max else (color_neg if val < 0 else color_std)
    img[IMG_H - h - 1 : IMG_H, i] = c   # dessiner la barre depuis le bas

fig, ax = plt.subplots(figsize=(24, 8))
ax.imshow(img, aspect="auto", interpolation="nearest",
          extent=[0, n, val_min, val_max])

# Ligne zéro
ax.axhline(0, color="black", linewidth=1.2, zorder=3)

# Annotation meilleur
idx_best = int(np.argmax(vals))
ax.annotate(
    f"★ Meilleur : ID {int(meilleur['ID'])}\n{val_max:,.0f} €",
    xy=(idx_best, val_max),
    xytext=(idx_best + n * 0.05, val_max * 0.80),
    fontsize=14, color="#D62728", fontweight="bold",
    arrowprops=dict(arrowstyle="->", color="#D62728", lw=2),
)

ax.yaxis.set_major_formatter(
    mticker.FuncFormatter(lambda y, _: f"{int(y):,} €".replace(",", " "))
)
ax.set_title(
    f"CA Net par produit — {n:,} produits",
    fontsize=20, fontweight="bold", pad=20,
)
ax.set_xlabel("ID Produit (ordre croissant)", fontsize=14, labelpad=10)
ax.set_ylabel("CA Net (€)", fontsize=14, labelpad=10)

legende = [
    Patch(color="#D62728", label="Meilleur produit"),
    Patch(color="#1F77B4", label="CA Net positif"),
    Patch(color="#FF9896", label="CA Net négatif"),
]
ax.legend(handles=legende, loc="upper right", fontsize=12, framealpha=0.9)
plt.tight_layout()
plt.savefig(GRAPH_BARRES, dpi=100, bbox_inches="tight")
plt.close()
ok(t, f"{GRAPH_BARRES} ({n:,} barres)")

# ==============================
#  5. GRAPHIQUE CIRCULAIRE — 500 000 PRODUITS EN TRANCHES DE CA NET
#     Chaque part = une tranche de valeur CA Net
#     Taille de la part = CA Net cumulé de la tranche
#     1 part spéciale dorée = le meilleur produit isolé
# ==============================
t = etape(f"Graphique circulaire — {NB_LIGNES:,} produits en {NB_BUCKETS} tranches...")

# Trier par CA Net décroissant
df_sorted_pie = df[["ID", "CA_Net"]].sort_values("CA_Net", ascending=False).reset_index(drop=True)

# Meilleur produit isolé
best_id  = int(df_sorted_pie.iloc[0]["ID"])
best_ca  = float(df_sorted_pie.iloc[0]["CA_Net"])

# Les 499 999 autres → NB_BUCKETS tranches par valeur CA Net
others_pie = df_sorted_pie.iloc[1:].copy()
others_pie["bucket"] = pd.cut(
    others_pie["CA_Net"], bins=NB_BUCKETS, labels=False, include_lowest=True
)

bucket_labels = []
bucket_values = []
bucket_counts = []

for b, grp in others_pie.groupby("bucket", observed=True):
    lo = float(grp["CA_Net"].min())
    hi = float(grp["CA_Net"].max())
    bucket_labels.append(f"{lo:.0f} – {hi:.0f} €\n({len(grp):,} prod.)")
    bucket_values.append(float(grp["CA_Net"].sum()))
    bucket_counts.append(len(grp))

# Ordre croissant de CA min → du plus petit au plus grand
# (déjà dans l'ordre groupby, on renverse pour aller du plus grand au plus petit)
bucket_labels.reverse()
bucket_values.reverse()
bucket_counts.reverse()

# Palette : dégradé bleu→vert→orange→rouge selon rang
def tranche_color(i, total):
    t = i / max(total - 1, 1)
    if t < 0.2:  return "#4f8ef7"
    if t < 0.4:  return "#4fd1c5"
    if t < 0.6:  return "#3ecf8e"
    if t < 0.8:  return "#f5874f"
    return "#e05252"

nb_t = len(bucket_values)
palette_tranches = [tranche_color(i, nb_t) for i in range(nb_t)]

# Combiner : meilleur en premier (doré), puis tranches
all_labels = [f"★ Meilleur\nID {best_id}\n{best_ca:,.2f} €"] + bucket_labels
all_values = [best_ca] + bucket_values
all_colors = ["#f5c842"] + palette_tranches
explode    = [0.06] + [0.015] * nb_t

fig, ax = plt.subplots(figsize=(22, 22))

wedges, texts, autotexts = ax.pie(
    all_values,
    labels=None,
    autopct=lambda pct: f"{pct:.2f}%" if pct > 1.5 else "",
    startangle=90,
    colors=all_colors,
    explode=explode,
    pctdistance=0.80,
    wedgeprops=dict(linewidth=1.2, edgecolor="white"),
)
for at in autotexts:
    at.set_fontsize(11)
    at.set_fontweight("bold")
    at.set_color("white")

# Annotation spéciale meilleur produit
ang_best = (wedges[0].theta1 + wedges[0].theta2) / 2
rad = np.deg2rad(ang_best)
x_ann = np.cos(rad) * 0.65
y_ann = np.sin(rad) * 0.65
ax.annotate(
    f"★ ID {best_id}\n{best_ca:,.2f} €",
    xy=(np.cos(rad) * 0.95, np.sin(rad) * 0.95),
    xytext=(np.cos(rad) * 1.35, np.sin(rad) * 1.35),
    fontsize=16, color="#f5c842", fontweight="bold",
    arrowprops=dict(arrowstyle="->", color="#f5c842", lw=2),
    bbox=dict(boxstyle="round,pad=0.3", fc="#1a1a2e", ec="#f5c842", lw=1.5),
)

# Légende compacte : seulement meilleur + quelques tranches clés
legend_items = [
    Patch(color="#f5c842", label=f"★ Meilleur produit — ID {best_id} ({best_ca:,.2f} €)"),
    Patch(color="#4f8ef7", label="Tranches haute valeur"),
    Patch(color="#3ecf8e", label="Tranches valeur moyenne"),
    Patch(color="#e05252", label="Tranches basse valeur"),
]
ax.legend(handles=legend_items, title="Légende", title_fontsize=18,
          fontsize=15, loc="upper left", bbox_to_anchor=(-0.3, 1.05),
          framealpha=0.95, edgecolor="#cccccc")

ax.set_title(
    f"Répartition du CA Net — {NB_LIGNES:,} produits en {NB_BUCKETS} tranches\n"
    f"Total : {ca_total:,.0f} €  |  Meilleur : ID {best_id} ({best_ca:,.2f} €)",
    fontsize=26, fontweight="bold", pad=35,
)
ax.axis("equal")
plt.tight_layout()
plt.savefig(GRAPH_TRANCHES, dpi=150, bbox_inches="tight")
plt.close()
ok(t, f"{GRAPH_TRANCHES} ({nb_t} tranches + meilleur isolé)")

# ==============================
#  6. GRAPHIQUE CIRCULAIRE
#     → répartition CA Net par taux de remise
# ==============================
t = etape("Graphique circulaire par remise...")

remise_group = df.groupby("Remise")["CA_Net"].sum().sort_values(ascending=False)
palette = [
    "#1F77B4", "#D62728", "#2CA02C", "#FF7F0E", "#9467BD",
    "#8C564B", "#E377C2", "#7F7F7F", "#BCBD22",
]
explode = [0.03] * len(remise_group)
total_remise = float(remise_group.sum())

fig, ax = plt.subplots(figsize=(18, 18))

wedges, texts, autotexts = ax.pie(
    remise_group,
    labels=None,
    autopct=lambda pct: f"{pct:.1f}%\n({pct / 100 * total_remise:,.0f} €)",
    startangle=90,
    colors=palette[:len(remise_group)],
    explode=explode,
    pctdistance=0.72,
    wedgeprops=dict(linewidth=2, edgecolor="white"),
)
for at in autotexts:
    at.set_fontsize(16)
    at.set_fontweight("bold")
    at.set_color("white")

legend_labels = [
    f"Remise {int(r)}%  —  {v:,.0f} €  ({v / total_remise * 100:.1f}%)"
    for r, v in remise_group.items()
]
ax.legend(wedges, legend_labels, title="Taux de remise",
          title_fontsize=20, fontsize=17,
          loc="upper left", bbox_to_anchor=(-0.35, 1.05),
          framealpha=0.95, edgecolor="#cccccc")

ax.set_title(
    f"Répartition du CA Net par taux de remise\nTotal : {total_remise:,.0f} €",
    fontsize=28, fontweight="bold", pad=30,
)
ax.axis("equal")
plt.tight_layout()
plt.savefig(GRAPH_CERCLE, dpi=150, bbox_inches="tight")
plt.close()
ok(t, GRAPH_CERCLE)

# ==============================
#  6. EXPORT JSON POUR LE DASHBOARD
# ==============================
t = etape("Préparation JSON dashboard...")

df_sorted = df[["ID", "CA_Net"]].sort_values("CA_Net", ascending=False).reset_index(drop=True)
best_row  = df_sorted.iloc[0]

others = df_sorted.iloc[1:].copy()
others["bucket"] = pd.cut(others["CA_Net"], bins=NB_BUCKETS, labels=False, include_lowest=True)
buckets = []
for b, grp in others.groupby("bucket", observed=True):
    lo = float(grp["CA_Net"].min())
    hi = float(grp["CA_Net"].max())
    buckets.append({
        "label":  f"{lo:.0f}EUR - {hi:.0f}EUR",
        "ca_sum": round(float(grp["CA_Net"].sum()), 2),
        "count":  int(len(grp)),
        "ca_min": round(lo, 2),
        "ca_max": round(hi, 2),
    })
buckets.sort(key=lambda x: x["ca_min"])

# ── Fichier principal (léger) : KPIs + buckets seulement ─────────────
payload = {
    "meta": {
        "nb_produits": NB_LIGNES,
        "ca_total":    round(ca_total, 2),
        "ca_moyen":    round(ca_moyen, 2),
        "ca_max":      round(float(meilleur["CA_Net"]), 2),
        "ca_min":      round(float(moins_bon["CA_Net"]), 2),
        "id_best":     int(meilleur["ID"]),
        "id_worst":    int(moins_bon["ID"]),
        "p25":         round(float(percentiles[0.25]), 2),
        "p50":         round(float(percentiles[0.50]), 2),
        "p75":         round(float(percentiles[0.75]), 2),
        "nb_buckets":  NB_BUCKETS,
    },
    "best": {
        "id": int(best_row["ID"]),
        "ca": round(float(best_row["CA_Net"]), 2),
    },
    "buckets": buckets,
}

with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(payload, f, separators=(",", ":"))

size_main = os.path.getsize(OUTPUT_JSON) / 1_048_576
ok(t, f"{OUTPUT_JSON} ({size_main:.1f} MB)")

# ── Fichier recherche (chargé à la demande par le dashboard) ─────────
t = etape("Export search_data.json (recherche par ID)...")
search_payload = {
    "all": [[int(r.ID), round(float(r.CA_Net), 2)] for r in df_sorted.itertuples(index=False)]
}
with open("search_data.json", "w", encoding="utf-8") as f:
    json.dump(search_payload, f, separators=(",", ":"))

size_search = os.path.getsize("search_data.json") / 1_048_576
ok(t, f"search_data.json ({size_search:.1f} MB)")

# ==============================
#  RÉSUMÉ FINAL
# ==============================
print("\n" + "="*52)
print("  ✅ Tout généré avec succès !")
print(f"     {OUTPUT_CSV}")
print(f"     {OUTPUT_JSON}")
print(f"     {GRAPH_BARRES}")
print(f"     {GRAPH_TRANCHES}")
print(f"     {GRAPH_CERCLE}")
print("="*52)