# 📊 Analyse des Ventes E-commerce

Projet Python d'analyse de données de ventes : génération de fichiers CSV, calculs financiers (CA Brut, CA Net, TVA, CA TTC), identification du meilleur produit et visualisation graphique.
<p aligner ="center">
  <img src="image.png" width="500">
</p>

---

## 🗂️ Structure du projet

```
projet/
├── analyse_ventes2.py     # Script principal (recommandé)
├── app.py                 # Interface web Streamlit (optionnel)
├── ventes.csv             # Généré automatiquement
├── results_final.csv      # Export des résultats calculés
└── graphiques_ventes.png  # Graphiques générés
```

---

## ⚙️ Fonctionnalités

- **Génération de données** : création d'un fichier `ventes.csv` avec 1000 produits (prix, quantité, remise aléatoires)
- **Calculs financiers** :
  - CA Brut = Prix × Quantité
  - CA Net = CA Brut × (1 − Remise / 100)
  - TVA = CA Net × 20 %
  - CA TTC = CA Net + TVA
- **Analyse** : CA total de l'entreprise + identification du produit le plus rentable
- **Export CSV** : résultats complets dans `results_final.csv`
- **Visualisation** : deux graphiques matplotlib sauvegardés en PNG

---

## 🚀 Installation

### Prérequis

- Python 3.8+
- pip

### Installer les dépendances

```bash
pip install matplotlib
```

Pour l'interface Streamlit (optionnel) :

```bash
pip install streamlit pandas
```

---

## ▶️ Utilisation

### Script principal

```bash
python analyse_ventes2.py
```

Ce script génère automatiquement les données, effectue les calculs, exporte les résultats et sauvegarde les graphiques.

### Interface web (optionnel)

```bash
streamlit run app.py
```

L'interface permet d'importer votre propre fichier CSV, visualiser les données et télécharger les résultats calculés.

---

## 📁 Format du fichier CSV d'entrée

Le fichier CSV doit contenir les colonnes suivantes (séparateur : virgule) :

| Colonne   | Type  | Description              |
|-----------|-------|--------------------------|
| ID        | int   | Identifiant du produit   |
| Prix      | float | Prix unitaire en €       |
| Quantite  | int   | Quantité vendue          |
| Remise    | float | Remise en % (ex: 10.0)   |

**Exemple :**
```
ID,Prix,Quantite,Remise
101,25.50,3,10
102,49.99,1,0
103,12.00,5,5
```

---

## 📤 Fichier de sortie

`results_final.csv` contient les colonnes d'origine plus les colonnes calculées :

| Colonne  | Description              |
|----------|--------------------------|
| CA_Brut  | Chiffre d'affaires brut  |
| CA_Net   | Chiffre d'affaires net   |
| TVA      | Montant de la TVA (20 %) |
| CA_TTC   | Montant toutes taxes comprises |

---

## 📈 Graphiques générés

Le script produit un fichier `graphiques_ventes.png` avec :

- **Graphique 1 — Barres** : CA Net par produit, avec le meilleur produit mis en évidence en rouge
- **Graphique 2 — Courbes** : comparaison CA Net vs TVA sur l'ensemble des produits

---

## 🗃️ Description des scripts

| Fichier              | Rôle                                                        |
|----------------------|-------------------------------------------------------------|
| `analyse_ventes2.py` | Script principal recommandé — complet et scalable           |
| `app.py`             | Interface Streamlit pour import CSV et visualisation web    |

---

## 🧪 Exemple de sortie console

```
✔ ventes.csv généré avec succès.

💰 CA Total de l'entreprise : 142 873.45 €

🏆 Produit avec le plus gros bénéfice : ID 587 (CA Net = 4 230.00 €)

✔ results_final.csv exporté avec succès.
✔ graphiques_ventes.png généré avec succès.
```

---

## 📄 Licence

Projet libre d'utilisation à des fins pédagogiques.