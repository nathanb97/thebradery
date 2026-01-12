# Data/ IA engineer

## ***Use Case : "Product Intelligence Platform"***

### **🎯 Contexte**

Chez TheBradery, nous gérons un catalogue de milliers de produits premium de marques comme Sandro, Maje, AMI Paris, etc. Certains produits ont des descriptions manquantes ou trop basiques, ce qui impacte notre SEO et nos conversions.

**Votre mission** : Développer un système complet pour enrichir et rechercher ces produits via IA.

---

## **📋 ÉTAPE 1 : Application d'enrichissement (Streamlit)**

### **Objectif**

Créer une application Streamlit permettant d'enrichir les descriptions de produits via IA et de sauvegarder les résultats dans une base de données.
🆘 Faites une interface très basique, ne perdez pas de temps sur ça 🆘

### **Fonctionnalités attendues**

**Analyse & Filtrage**

- Charger le dataset `products.csv` fourni (1000 produits)
- Afficher des statistiques sur le catalogue
- Permettre de filtrer les produits à enrichir (par qualité de description, catégorie, marque, etc.)

**Enrichissement IA**

- Utiliser une IA (OpenAI, Anthropic, ou autre) pour améliorer les descriptions
- Générer des informations complémentaires pertinentes pour l'e-commerce

**Sauvegarde**

- Persister les enrichissements dans une base de données de votre choix
- Permettre d'exporter les résultats

### **Ce qu'on veut voir**

- Une interface intuitive et efficace
- Une gestion intelligente des appels IA (erreurs, performance)

---

## **🔌 ÉTAPE 2 : API de recherche (FastAPI)**

### **Objectif**

Développer une API REST avec au moins un endpoint permettant de rechercher des produits dans la table des descriptions enrichies.

### **Endpoint principal attendu**

**Recherche de produits** avec possibilité de :

- Rechercher par mots-clés
- Filtrer par product_type, vendor ..
- Retourner les données enrichies

### **Ce qu'on veut voir**

- Une API REST bien conçue et documentée
- Des résultats de recherche pertinents
- Une gestion propre des cas d'erreur
- (Bonus) D'autres endpoints utiles que vous jugeriez pertinents

---

## **📦 Dataset fourni**

**`products.csv`** contenant 1000 produits 

[BigQuery Data Warehouse (5).csv](attachment:61b4c56d-b905-4331-9c5a-f60b837201bd:BigQuery_Data_Warehouse_(5).csv)

---

## **📝 Livrables**

1. **Code source** (GitHub repo ou ZIP)
    - Application Streamlit fonctionnelle
    - API FastAPI fonctionnelle
    - Base de données avec quelque produits enrichis + enrichissement pendant présentation
2. **Documentation** (README.md)
    - Instructions pour lancer le projet
    - Choix techniques et architecture
    - Exemples d'utilisation de l'API
3. **Démo**
    - Présentation live lors de l'entretien

---

## **⚙️ Contraintes techniques**

- **Streamlit** pour l'interface
- **FastAPI** pour l'API
- LLM de votre choix (Modèle open-source sur votre machine pour éviter un coût)
- Base de données de votre choix

---

## **🚀 Pour commencer**

1. Récupérez le dataset `products.csv` fourni
2. Configurez votre environnement Python
3. Choisissez vos outils (BDD, LLM provider, etc.)
4. Développez les 2 étapes
5. Préparez votre démo

## Stack possible

- Streamlit
- FastAPI + Uvicorn + Pydantic
- DuckDB (ou PSQL)
- Ollama (modèles locaux gratuits)

### **Questions ?** N'hésitez pas à nous contacter si besoin de clarifications.

ok je veux que tu fasse une dernière page streamlit avec interrogation de l'api
