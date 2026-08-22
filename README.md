# TaskFlow Support Agent

🔗 **[Voir la démo en ligne](https://taskflow-support-agent-gpqsr4zvpadheplzbvaavx.streamlit.app/)**

Système multi-agents (LangGraph) qui automatise le traitement des tickets de support client pour TaskFlow, un SaaS fictif de gestion de projet.

## Le problème

Automatiser la lecture, la catégorisation et la réponse aux tickets clients, tout en sachant reconnaître quand une réponse doit être escaladée à un humain plutôt que d'être générée à tort. La contrainte centrale du projet : **le système ne doit jamais inventer une réponse non fondée sur la documentation.**

## Architecture

```
Ticket client entrant
        │
        ▼
  [Agent Routeur] ── catégorise le ticket + évalue l'urgence
        │
        ├── Si plainte / cas sensible ──────────────► [Escalade humaine]
        │
        ▼
  [Agent Chercheur] ── recherche dans la doc (RAG) et rédige une réponse
        │
        ▼
  [Agent Vérificateur] ── vérifie que la réponse est fondée sur la doc
        │
        ├── Fondée ──────────────────────────────────► Réponse envoyée
        ├── Non fondée + tentatives restantes ────────► Retour au Chercheur (boucle)
        └── Non fondée + tentatives épuisées ─────────► [Escalade humaine]
```

Le mécanisme central : une **boucle de correction conditionnelle**. Si le Vérificateur juge une réponse non fondée, le système retente automatiquement (dans la limite de 2 tentatives) avant d'escalader à un humain plutôt que de risquer une hallucination.

## Stack technique

- Python, LangChain, LangGraph
- ChromaDB (base vectorielle, embeddings OpenAI `text-embedding-3-small`)
- OpenAI `gpt-4o-mini` (agents)
- Streamlit (interface, déployée sur Streamlit Community Cloud)

## Installation

Cloner le dépôt et se placer dans le dossier du projet :

```bash
git clone https://github.com/Aminee95/taskflow-support-agent.git
cd taskflow-support-agent
```

Créer et activer un environnement virtuel Python :

```bash
python -m venv venv
venv\Scripts\activate
```

> Sous macOS/Linux : `source venv/bin/activate`

Installer les dépendances :

```bash
pip install -r requirements.txt
```

Configurer les variables d'environnement :

```bash
cp .env.example .env
```

Puis renseigner votre clé API OpenAI dans le fichier `.env`.

## Utilisation

Construire la base de connaissances à partir de la documentation produit :

```bash
python src/ingest.py
```

Lancer le système complet sur quelques tickets d'exemple :

```bash
python src/graphe.py
```

Lancer l'évaluation chiffrée sur l'ensemble du jeu de test :

```bash
python src/evaluer.py
```

Diagnostiquer en détail le raisonnement de chaque agent sur des tickets précis :

```bash
python src/debug_tickets.py
```

Lancer l'interface web en local :

```bash
streamlit run src/app.py
```

## Résultats et itérations

Le système est évalué sur un jeu de 20 tickets annotés (catégorie et décision d'escalade attendues), couvrant 5 types de demandes : facturation, bug technique, question produit, plainte, demande de fonctionnalité.

| Itération | Changement apporté | Précision catégorisation | Précision escalade | Réponse dès le 1er coup |
|---|---|---|---|---|
| v1 | Prompt Routeur initial | 85% | 85% | 85% |
| v2 | Clarification catégorie facturation + découplage urgence/escalade | 95% | 85% | 75% |
| v3 | Routeur ne présume plus l'escalade sur simple remboursement ; Chercheur interdit d'extrapoler une cause à effet non écrite dans le contexte ; k=3→5 | 90% | 90% | 70% |
| v4 | Chunks élargis (500→800 caractères) pour ne plus couper les sections courtes ; correction d'une annotation de test elle-même incorrecte (T003) | 90% | **100%** | 70% |

**Ce que ces itérations montrent** :
- Une correction ciblée sur un cas précis peut faire reculer une autre métrique ailleurs (v1→v2 : la catégorisation progresse mais le taux de réponse du 1er coup recule) — un rappel qu'itérer sur un système multi-agents demande de mesurer l'ensemble des métriques, pas une seule isolément.
- Un bug de "hallucination" peut en réalité être un problème de retrieval (chunking trop agressif qui coupe une info pertinente hors contexte), pas un problème de prompt — diagnostiquer la bonne couche du système est essentiel avant de corriger.
- Une évaluation rigoureuse peut aussi révéler une erreur dans les **données de test elles-mêmes** : le ticket T003 était annoté comme nécessitant une escalade humaine, alors que la documentation prévoit un remboursement automatique pour ce cas précis. Corriger cette annotation était plus juste que de forcer le système à s'y conformer.

**Erreur restante (T002, T005)** : ces deux tickets oscillent entre plusieurs catégories selon les itérations sans converger totalement, un signe que la frontière entre "facturation" et "question produit" reste ambiguë pour certaines formulations. Piste d'amélioration identifiée mais non résolue : ajouter des exemples few-shot dans le prompt du Routeur plutôt que de continuer à ajuster les règles en texte libre.

## Limites actuelles et pistes d'amélioration

- Deux tickets (T002, T005) oscillent encore entre les catégories "facturation" et "question_produit" selon les formulations
- Pas encore de gestion du contexte multi-tours (chaque ticket est traité indépendamment)
- Base de connaissance volontairement restreinte (documentation synthétique de ~2 pages)
- Sur le déploiement en ligne, la base vectorielle est reconstruite à chaque redémarrage du serveur (pas de persistance entre sessions sur l'hébergement gratuit)

## État du projet

✅ Projet complet — pipeline RAG, système multi-agents avec boucle de correction, évaluation chiffrée sur 4 itérations, interface déployée en ligne.