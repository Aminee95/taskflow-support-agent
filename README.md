# TaskFlow Support Agent

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

## Résultats et itérations

Le système est évalué sur un jeu de 20 tickets annotés (catégorie et décision d'escalade attendues), couvrant 5 types de demandes : facturation, bug technique, question produit, plainte, demande de fonctionnalité.

| Itération | Précision catégorisation | Précision escalade | Réponse dès le 1er coup |
|---|---|---|---|
| v1 (prompt Routeur initial) | 85% | 85% | 85% |
| v2 (clarification facturation + découplage urgence/escalade) | 95% | 85% | 75% |

**Ce que cette itération montre** : le passage de v1 à v2 a nettement amélioré la catégorisation, mais a déplacé (sans les réduire) les erreurs d'escalade — un rappel que corriger un prompt sur un cas précis peut avoir des effets de bord ailleurs dans le système. Investigation en cours sur les tickets T004, T010 et T015 pour identifier si le problème vient du Routeur ou d'un excès de permissivité du Vérificateur.

## Limites actuelles et pistes d'amélioration

- Le Vérificateur peut occasionnellement valider une réponse insuffisamment fondée sur des bugs non documentés (à confirmer par le diagnostic en cours)
- Pas encore de gestion du contexte multi-tours (chaque ticket est traité indépendamment)
- Base de connaissance volontairement restreinte (documentation synthétique de ~2 pages)

## État du projet

🚧 En cours de développement — Semaine 4 : itération et diagnostic des erreurs restantes.