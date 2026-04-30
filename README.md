# 📊 Analyse des Ventes E-commerce

Projet Python d'analyse de données de ventes : génération de fichiers CSV, calculs financiers (CA Brut, CA Net, TVA), identification du meilleur produit et visualisation graphique avec dashboard HTML interactif.

<p align="center">
  <img src="image.png" width="500">
</p>

---

## 🗂️ Structure du projet

```
projet/
├── vente.py               # Script principal unifié (génération + graphes + JSON)
├── dashboard.html         # Dashboard interactif HTML (graphe circulaire 500k produits)
├── lancer.bat             # Lanceur Windows automatique (double-clic pour tout démarrer)
├── resultats_final.csv    # Export CSV des 500 000 produits calculés
├── dashboard_data.json    # Données JSON pour le dashboard HTML
├── graph_barres_test.png  # Graphique barres — 500 000 produits (rendu rapide)
├── graph_tranches_test.png# Graphique circulaire — 500k produits en 60 tranches
└── graph_cercle_test.png  # Graphique circulaire — répartition par taux de remise
```

---

## ⚙️ Fonctionnalités

- **Génération de données** : création de 500 000 produits avec prix, quantité et remise aléatoires
- **Calculs financiers** :
  - CA Brut = Prix × Quantité
  - CA Net = CA Brut × (1 − Remise / 100)
  - TVA = CA Net × 20 %
- **Analyse statistique** : CA total, CA moyen, médiane, percentiles P25/P75, meilleur et moins bon produit
- **Export CSV** : résultats complets dans `resultats_final.csv`
- **Export JSON** : données structurées pour le dashboard dans `dashboard_data.json`
- **3 graphiques** générés automatiquement (voir section Graphiques)
- **Dashboard HTML interactif** avec graphe circulaire, KPIs et recherche par ID produit

---

## 🚀 Installation

### Prérequis

- Python 3.8+
- pip

### Installer les dépendances

```bash
pip install pandas numpy matplotlib
```

---

## ▶️ Utilisation

### Méthode recommandée — Windows (double-clic)

```
lancer.bat
```

Le fichier `.bat` effectue automatiquement :
1. Vérifie que Python est installé
2. Installe les dépendances manquantes (`pandas`, `numpy`, `matplotlib`)
3. Libère le port 8000 s'il est déjà occupé
4. Exécute `vente.py` (génération données + graphes + JSON)
5. Lance le serveur HTTP local
6. Ouvre automatiquement le dashboard dans le navigateur

### Méthode manuelle

```bash
# Étape 1 — Générer les données et les graphes
python vente.py

# Étape 2 — Lancer le serveur HTTP
python -m http.server 8000 --bind 127.0.0.1

# Étape 3 — Ouvrir dans le navigateur
http://localhost:8000/dashboard.html
```

---

## 📈 Graphiques générés

Le script `vente.py` produit **3 fichiers PNG** :

### `graph_barres_test.png` — Barres 500 000 produits
- 1 pixel de largeur par produit (technique `imshow` numpy)
- **Rouge** = meilleur produit, **Bleu** = CA Net positif, **Rose** = CA Net négatif
- Annotation flèche sur le meilleur produit
- ⚡ Généré en ~5 secondes (technique pixel-par-pixel, pas de `ax.bar()`)

### `graph_tranches_test.png` — Circulaire 500k en tranches
- Les 500 000 produits regroupés en **60 tranches** de CA Net
- 1 part dorée isolée `★` = le meilleur produit seul
- Dégradé de couleur : bleu (haute valeur) → vert → orange → rouge (basse valeur)

### `graph_cercle_test.png` — Circulaire par taux de remise
- Chaque part = un taux de remise (0 %, 5 %, 10 %… 40 %)
- Taille de la part = CA Net total généré par ce groupe de remise
- Affiche % et valeur € dans chaque part

---

## 🖥️ Dashboard HTML interactif (`dashboard.html`)

Interface web dark mode avec :

| Élément | Description |
|---|---|
| **KPIs** | CA Total, CA Moyen, Meilleur, Moins bon, Médiane, Nb produits |
| **Graphe circulaire D3.js** | 500 000 produits en 60 tranches + meilleur isolé en doré |
| **Carte meilleur produit** | ID, CA Net, part du total, rang, comparaison vs moyenne |
| **Recherche par ID** | Trouver n'importe quel produit parmi les 500 000 instantanément |
| **Légende interactive** | Toutes les tranches avec hover et tooltip détaillé |

> Le dashboard se lance via `lancer.bat` ou manuellement avec `python -m http.server 8000`.

---

## 📁 Format des données générées

Chaque produit contient les colonnes suivantes :

| Colonne   | Type  | Description                        |
|-----------|-------|------------------------------------|
| ID        | int   | Identifiant unique (1 à 500 000)   |
| Prix      | float | Prix unitaire entre 5 € et 100 €   |
| Quantite  | int   | Quantité vendue (1 à 10)           |
| Remise    | int   | Remise en % parmi 0,5,10…40        |
| CA_Brut   | float | Prix × Quantité                    |
| CA_Net    | float | CA Brut × (1 − Remise/100)         |
| TVA       | float | CA Net × 20 %                      |

---

## 🗃️ Description des fichiers

| Fichier               | Rôle                                                              |
|-----------------------|-------------------------------------------------------------------|
| `vente.py`            | Script unique unifié — données + 3 graphes + JSON + CSV          |
| `dashboard.html`      | Dashboard HTML interactif D3.js — aucune modification nécessaire |
| `lancer.bat`          | Lanceur Windows — vérifie dépendances, port, ouvre navigateur    |
| `dashboard_data.json` | Données JSON consommées par le dashboard                         |
| `resultats_final.csv` | Export brut de tous les produits avec calculs                    |

---

## 🧪 Exemple de sortie console

```
=== Dashboard Ventes ===

⏳ Génération de 500,000 produits...
   ✔ Fait en 1.20s — 500,000 lignes

📊 CA Total  = 137 524 830.45 €
   CA Moyen  = 275.05 €
   Meilleur  : ID 48273 → 998.40 €
   Moins bon : ID 194853 → 3.01 €

⏳ Export CSV → resultats_final.csv
   ✔ Fait en 2.00s — 500,000 lignes

⏳ Graphique en barres (500 000 produits)...
   ✔ Fait en 5.20s — graph_barres_test.png

⏳ Graphique circulaire — 500,000 produits en 60 tranches...
   ✔ Fait en 8.40s — graph_tranches_test.png

⏳ Graphique circulaire par remise...
   ✔ Fait en 2.10s — graph_cercle_test.png

⏳ Préparation JSON dashboard...
   ✔ Fait en 12.30s — dashboard_data.json (38.2 MB)

====================================================
  ✅ Tout généré avec succès !
     resultats_final.csv
     dashboard_data.json
     graph_barres_test.png
     graph_tranches_test.png
     graph_cercle_test.png
====================================================
```

---

## ⚠️ Notes techniques

- `matplotlib.use("Agg")` est activé pour éviter tout crash sur serveur sans interface graphique
- Le graphe barres utilise `imshow()` numpy au lieu de `ax.bar()` — cela évite le crash RAM sur 500 000 éléments (passage de 20+ minutes à ~5 secondes)
- Le port 8000 est libéré automatiquement par `lancer.bat` s'il est déjà occupé
- Le JSON `dashboard_data.json` contient tous les 500 000 produits pour la recherche — taille ~38 Mo normale

---

## 📄 Licence

Projet libre d'utilisation à des fins pédagogiques.

## 👥 Auteurs

- Mariem Louati
- Emna Jazzar
- Molka Haouami