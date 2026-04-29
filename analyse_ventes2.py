import csv
import random
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ─────────────────────────────────────────────
# 1. Générer ventes.csv
# ─────────────────────────────────────────────
produits = list(range(101, 1101))  # 1000 produits
lignes = []

random.seed(42)
for i, pid in enumerate(produits):
    prix = round(random.uniform(5, 100), 2)
    quantite = random.randint(1, 50)
    remise = random.choice([0, 2.5, 5, 10, 15, 20])
    lignes.append([pid, prix, quantite, remise])

with open("ventes.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["ID", "Prix", "Quantite", "Remise"])
    writer.writerows(lignes)

print("✔ ventes.csv généré avec succès.\n")

# ─────────────────────────────────────────────
# 2-7. Calculs & export results_final.csv
# ─────────────────────────────────────────────
TAUX_TVA = 0.20

resultats = []

with open("ventes.csv", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        pid      = int(row["ID"])
        prix     = float(row["Prix"])
        qte      = int(row["Quantite"])
        remise   = float(row["Remise"])

        ca_brut  = round(prix * qte, 2)                          # 2
        ca_net   = round(ca_brut * (1 - remise / 100), 2)        # 3
        tva      = round(ca_net * TAUX_TVA, 2)                   # 4
        benefice = ca_net                                         # proxy bénéfice = CA Net

        resultats.append({
            "ID": pid,
            "Prix": prix,
            "Quantite": qte,
            "Remise": remise,
            "CA_Brut": ca_brut,
            "CA_Net": ca_net,
            "TVA": tva,
            "CA_TTC": round(ca_net + tva, 2),
        })

# 5. CA Total
ca_total = round(sum(r["CA_Net"] for r in resultats), 2)
print(f"💰 CA Total de l'entreprise : {ca_total} €\n")

# 6. Produit avec le plus gros bénéfice
meilleur = max(resultats, key=lambda r: r["CA_Net"])
print(f"🏆 Produit avec le plus gros bénéfice : ID {meilleur['ID']}  "
      f"(CA Net = {meilleur['CA_Net']} €)\n")

# 7. Export results_final.csv
colonnes = ["ID", "Prix", "Quantite", "Remise", "CA_Brut", "CA_Net", "TVA", "CA_TTC"]
with open("results_final.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=colonnes)
    writer.writeheader()
    writer.writerows(resultats)

print("✔ results_final.csv exporté avec succès.\n")

# ─────────────────────────────────────────────
# BONUS – Graphiques Matplotlib
# ─────────────────────────────────────────────
ids    = [r["ID"]     for r in resultats]
ca_net = [r["CA_Net"] for r in resultats]
tva    = [r["TVA"]    for r in resultats]

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("Analyse des ventes – Tableau de bord", fontsize=14, fontweight="bold")

# Graphique 1 : CA Net par produit
couleurs = ["#e74c3c" if r["ID"] == meilleur["ID"] else "#3498db" for r in resultats]
axes[0].bar([str(i) for i in ids], ca_net, color=couleurs, edgecolor="white")
axes[0].set_title("CA Net par produit (€)")
axes[0].set_xlabel("ID Produit")
axes[0].set_ylabel("CA Net (€)")
axes[0].tick_params(axis="x", rotation=90)
patch_best  = mpatches.Patch(color="#e74c3c", label=f"Meilleur (ID {meilleur['ID']})")
patch_other = mpatches.Patch(color="#3498db", label="Autres produits")
axes[0].legend(handles=[patch_best, patch_other])

# Graphique 2 : CA Net vs TVA (barres groupées)
x = range(len(ids))
w = 0.4
axes[1].bar([i - w/2 for i in x], ca_net, width=w, label="CA Net",  color="#2ecc71", edgecolor="white")
axes[1].bar([i + w/2 for i in x], tva,    width=w, label="TVA 20%", color="#f39c12", edgecolor="white")
axes[1].set_title("CA Net vs TVA par produit (€)")
axes[1].set_xlabel("Produit (index)")
axes[1].set_ylabel("Montant (€)")
axes[1].legend()

plt.tight_layout()
plt.savefig("graphiques_ventes.png", dpi=120)
plt.close()
print("✔ graphiques_ventes.png généré avec succès.")